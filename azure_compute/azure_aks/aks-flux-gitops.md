# Flux GitOps on AKS

## Overview

Flux is a GitOps tool that automatically synchronizes the state of your Kubernetes cluster with configurations stored in Git repositories. It enables continuous delivery by monitoring Git repositories for changes and automatically applying those changes to your cluster, ensuring that your cluster state always matches your Git repository.

---

## What is GitOps?

GitOps is a paradigm for managing infrastructure and applications where Git serves as the single source of truth. 

### Core Principles

1. **Declarative Configuration**: Everything is described declaratively in Git
2. **Version Control**: All changes are tracked and auditable
3. **Automated Deployment**: Changes in Git automatically trigger deployments
4. **Continuous Reconciliation**: Cluster state continuously reconciled with Git

### Benefits

✅ **Auditability**: Complete history of all changes  
✅ **Rollback**: Easy to revert to previous states  
✅ **Collaboration**: Standard Git workflows (PR, code review)  
✅ **Disaster Recovery**: Cluster can be rebuilt from Git  
✅ **Consistency**: Same process for all environments  
✅ **Security**: No direct cluster access needed for deployments

---

## Flux Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Git Repository                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  manifests/ │  │   charts/   │  │   config/   │        │
│  │  - deploy.yaml│  │  - helm/   │  │  - kustomize│        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ Pull/Watch
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Kubernetes Cluster (AKS)                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │            Flux Controllers (flux-system)             │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │  │
│  │  │    Source    │  │  Kustomize   │  │    Helm    │  │  │
│  │  │  Controller  │  │  Controller  │  │ Controller │  │  │
│  │  └──────────────┘  └──────────────┘  └────────────┘  │  │
│  │  ┌──────────────┐  ┌──────────────┐                  │  │
│  │  │ Notification │  │ Image Auto   │                  │  │
│  │  │  Controller  │  │  Controller  │                  │  │
│  │  └──────────────┘  └──────────────┘                  │  │
│  └───────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           │ Apply                            │
│                           ▼                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Application Resources                    │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │  │
│  │  │   Pods   │  │ Services │  │  Ingress │          │  │
│  │  └──────────┘  └──────────┘  └──────────┘          │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Flux Components

#### 1. Source Controller

Manages sources of Kubernetes manifests:
- **GitRepository**: Git repositories
- **HelmRepository**: Helm chart repositories
- **HelmChart**: Helm charts
- **Bucket**: Cloud storage buckets

#### 2. Kustomize Controller

Applies Kustomize overlays and reconciles cluster state.

#### 3. Helm Controller

Manages Helm releases and chart installations.

#### 4. Notification Controller

Sends notifications about deployment status:
- Slack, Microsoft Teams, Discord
- Webhooks
- Git commit status updates

#### 5. Image Automation Controllers

Automates image updates:
- **Image Reflector**: Scans container registries
- **Image Automation**: Updates manifests with new image tags

---

## Installing Flux on AKS

### Prerequisites

```bash
# Install Flux CLI
curl -s https://fluxcd.io/install.sh | sudo bash

# Verify installation
flux --version

# Export GitHub credentials
export GITHUB_TOKEN=<your-token>
export GITHUB_USER=<your-username>
```

### Method 1: Flux CLI Bootstrap

```bash
# Bootstrap Flux with GitHub
flux bootstrap github \
  --owner=$GITHUB_USER \
  --repository=fleet-infra \
  --branch=main \
  --path=./clusters/production \
  --personal
```

**What this does:**
1. Creates a Git repository (if it doesn't exist)
2. Installs Flux components in the cluster
3. Configures Flux to track the repository
4. Commits Flux manifests to the repository

### Method 2: Azure CLI with AKS Extension

```bash
# Enable Flux extension on AKS
az k8s-extension create \
  --cluster-name myAKSCluster \
  --resource-group myResourceGroup \
  --cluster-type managedClusters \
  --extension-type microsoft.flux \
  --name flux
```

### Verify Installation

```bash
# Check Flux components
kubectl get pods -n flux-system

# Check Flux status
flux check

# View Git sources
flux get sources git
```

---

## Flux Custom Resources

### 1. GitRepository

Defines a Git repository source:

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: podinfo
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/stefanprodan/podinfo
  ref:
    branch: master
  secretRef:
    name: git-credentials  # Optional for private repos
```

**Parameters:**
- `interval`: How often to check for changes
- `url`: Repository URL (HTTPS or SSH)
- `ref`: Branch, tag, or commit
- `secretRef`: Credentials for private repositories

### 2. Kustomization

Applies Kustomize configurations:

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: podinfo
  namespace: flux-system
spec:
  interval: 5m
  path: ./kustomize
  prune: true
  sourceRef:
    kind: GitRepository
    name: podinfo
  healthChecks:
  - apiVersion: apps/v1
    kind: Deployment
    name: podinfo
    namespace: default
  timeout: 2m
```

**Parameters:**
- `path`: Path within the repository
- `prune`: Delete resources removed from Git
- `sourceRef`: Reference to GitRepository
- `healthChecks`: Resources to monitor
- `timeout`: Maximum time for reconciliation

### 3. HelmRelease

Manages Helm chart deployments:

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta1
kind: HelmRelease
metadata:
  name: nginx-ingress
  namespace: flux-system
spec:
  interval: 5m
  chart:
    spec:
      chart: nginx-ingress
      version: '4.x'
      sourceRef:
        kind: HelmRepository
        name: ingress-nginx
        namespace: flux-system
  values:
    controller:
      replicaCount: 2
      service:
        type: LoadBalancer
```

### 4. HelmRepository

Defines a Helm chart repository:

```yaml
apiVersion: source.toolkit.fluxcd.io/v1beta2
kind: HelmRepository
metadata:
  name: ingress-nginx
  namespace: flux-system
spec:
  interval: 10m
  url: https://kubernetes.github.io/ingress-nginx
```

### 5. ImageRepository

Scans container registry for images:

```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImageRepository
metadata:
  name: podinfo
  namespace: flux-system
spec:
  image: ghcr.io/stefanprodan/podinfo
  interval: 1m
```

### 6. ImagePolicy

Defines image update policy:

```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImagePolicy
metadata:
  name: podinfo
  namespace: flux-system
spec:
  imageRepositoryRef:
    name: podinfo
  policy:
    semver:
      range: '>=1.0.0 <2.0.0'
```

### 7. ImageUpdateAutomation

Automates image updates in Git:

```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta1
kind: ImageUpdateAutomation
metadata:
  name: podinfo
  namespace: flux-system
spec:
  interval: 1m
  sourceRef:
    kind: GitRepository
    name: podinfo
  git:
    checkout:
      ref:
        branch: main
    commit:
      author:
        email: fluxcdbot@users.noreply.github.com
        name: fluxcdbot
      messageTemplate: 'Update image to {{range .Updated.Images}}{{println .}}{{end}}'
    push:
      branch: main
  update:
    path: ./deploy
    strategy: Setters
```

---

## Repository Structure

### Basic Structure

```
flux-repo/
├── clusters/
│   ├── production/
│   │   ├── flux-system/         # Flux installation
│   │   │   ├── gotk-components.yaml
│   │   │   ├── gotk-sync.yaml
│   │   │   └── kustomization.yaml
│   │   ├── apps.yaml            # Apps kustomization
│   │   └── infrastructure.yaml  # Infrastructure kustomization
│   └── staging/
│       └── ...
├── apps/
│   ├── base/
│   │   └── app1/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   │       └── kustomization.yaml
│   └── production/
│       └── app1/
│           ├── kustomization.yaml
│           └── patches.yaml
└── infrastructure/
    ├── base/
    │   ├── nginx-ingress/
    │   └── cert-manager/
    └── production/
        └── kustomization.yaml
```

### Multi-Cluster Structure

```
fleet-infra/
├── clusters/
│   ├── production/
│   │   ├── flux-system/
│   │   ├── apps/
│   │   │   ├── team-a.yaml
│   │   │   └── team-b.yaml
│   │   └── infrastructure/
│   ├── staging/
│   └── development/
├── tenants/
│   ├── team-a/
│   │   ├── base/
│   │   └── overlays/
│   └── team-b/
└── infrastructure/
```

---

## Common Workflows

### 1. Deploy Application

**Step 1: Create manifests in Git**

```bash
# Create directory structure
mkdir -p apps/podinfo

# Create deployment
cat <<EOF > apps/podinfo/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: podinfo
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: podinfo
  template:
    metadata:
      labels:
        app: podinfo
    spec:
      containers:
      - name: podinfo
        image: ghcr.io/stefanprodan/podinfo:6.5.0
        ports:
        - containerPort: 9898
EOF

# Create kustomization
cat <<EOF > apps/podinfo/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
EOF
```

**Step 2: Create Flux Kustomization**

```yaml
# clusters/production/apps/podinfo.yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: podinfo
  namespace: flux-system
spec:
  interval: 5m
  path: ./apps/podinfo
  prune: true
  sourceRef:
    kind: GitRepository
    name: flux-system
```

**Step 3: Commit and push**

```bash
git add .
git commit -m "Deploy podinfo application"
git push

# Watch reconciliation
flux reconcile kustomization flux-system --with-source
flux get kustomizations --watch
```

### 2. Update Application

```bash
# Modify image version
sed -i 's/6.5.0/6.5.1/g' apps/podinfo/deployment.yaml

# Commit and push
git add apps/podinfo/deployment.yaml
git commit -m "Update podinfo to 6.5.1"
git push

# Flux automatically applies changes
```

### 3. Rollback

```bash
# Revert Git commit
git revert HEAD
git push

# Or use Git to rollback
git reset --hard HEAD~1
git push --force

# Flux automatically reverts cluster state
```

### 4. Deploy Helm Chart

```bash
# Create HelmRepository
flux create source helm bitnami \
  --url=https://charts.bitnami.com/bitnami \
  --interval=1h \
  --export > infrastructure/sources/bitnami.yaml

# Create HelmRelease
flux create helmrelease redis \
  --source=HelmRepository/bitnami \
  --chart=redis \
  --chart-version=17.x \
  --values=./redis-values.yaml \
  --export > apps/redis/helmrelease.yaml

# Commit and push
git add .
git commit -m "Deploy Redis"
git push
```

---

## Multi-Tenancy with Flux

### Tenant Isolation

```yaml
# tenants/team-a/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: team-a
---
# tenants/team-a/rbac.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: flux-team-a
  namespace: team-a
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: flux-team-a
  namespace: team-a
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: admin
subjects:
- kind: ServiceAccount
  name: flux-team-a
  namespace: team-a
```

### Tenant Kustomization

```yaml
# clusters/production/tenants/team-a.yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: team-a-apps
  namespace: flux-system
spec:
  interval: 5m
  serviceAccountName: flux-team-a
  path: ./tenants/team-a
  prune: true
  sourceRef:
    kind: GitRepository
    name: flux-system
  targetNamespace: team-a
```

---

## Image Automation

### Setup

```bash
# Enable image automation
flux bootstrap github \
  --owner=$GITHUB_USER \
  --repository=fleet-infra \
  --branch=main \
  --path=clusters/production \
  --components-extra=image-reflector-controller,image-automation-controller
```

### Configure Automation

**1. Scan ACR for images**

```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImageRepository
metadata:
  name: myapp
  namespace: flux-system
spec:
  image: myacr.azurecr.io/myapp
  interval: 1m
  secretRef:
    name: acr-credentials
```

**2. Define update policy**

```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta2
kind: ImagePolicy
metadata:
  name: myapp
  namespace: flux-system
spec:
  imageRepositoryRef:
    name: myapp
  policy:
    semver:
      range: '>=1.0.0'
```

**3. Mark deployment for updates**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    spec:
      containers:
      - name: myapp
        image: myacr.azurecr.io/myapp:1.0.0 # {"$imagepolicy": "flux-system:myapp"}
```

**4. Enable automation**

```yaml
apiVersion: image.toolkit.fluxcd.io/v1beta1
kind: ImageUpdateAutomation
metadata:
  name: myapp
  namespace: flux-system
spec:
  interval: 1m
  sourceRef:
    kind: GitRepository
    name: flux-system
  git:
    commit:
      author:
        email: flux@example.com
        name: Flux Bot
    push:
      branch: main
  update:
    path: ./apps
    strategy: Setters
```

---

## Notifications

### Slack Notifications

```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta1
kind: Provider
metadata:
  name: slack
  namespace: flux-system
spec:
  type: slack
  channel: deployments
  secretRef:
    name: slack-webhook
---
apiVersion: notification.toolkit.fluxcd.io/v1beta1
kind: Alert
metadata:
  name: slack-alert
  namespace: flux-system
spec:
  providerRef:
    name: slack
  eventSeverity: info
  eventSources:
  - kind: GitRepository
    name: '*'
  - kind: Kustomization
    name: '*'
  - kind: HelmRelease
    name: '*'
```

### Microsoft Teams

```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta1
kind: Provider
metadata:
  name: teams
  namespace: flux-system
spec:
  type: msteams
  address: https://outlook.office.com/webhook/...
```

---

## Monitoring Flux

### Prometheus Metrics

Flux exposes Prometheus metrics:

```yaml
apiVersion: v1
kind: ServiceMonitor
metadata:
  name: flux-system
  namespace: flux-system
spec:
  endpoints:
  - port: http-prom
    path: /metrics
  selector:
    matchLabels:
      app: flux
```

**Key Metrics:**
- `gotk_reconcile_duration_seconds`: Reconciliation duration
- `gotk_reconcile_condition`: Reconciliation status
- `controller_runtime_reconcile_total`: Total reconciliations

### Grafana Dashboard

```bash
# Import Flux dashboard
# Dashboard ID: 16488
```

### CLI Monitoring

```bash
# Watch all resources
flux get all --watch

# Check specific resource
flux get kustomizations
flux get helmreleases

# View events
flux events

# Logs
flux logs --follow --all-namespaces
```

---

## Best Practices

### 1. Repository Organization

✅ Separate infrastructure and applications  
✅ Use base and overlay patterns with Kustomize  
✅ Keep environment-specific configs in separate directories  
✅ Use clear naming conventions

### 2. Security

✅ Use deploy keys or SSH keys (read-only) for Git access  
✅ Store secrets in Azure Key Vault, sync with External Secrets Operator  
✅ Enable RBAC for Flux service accounts  
✅ Scan images before deployment  
✅ Use signed commits for verification

### 3. Reconciliation

✅ Set appropriate reconciliation intervals  
✅ Use `dependsOn` for resource ordering  
✅ Enable health checks for critical resources  
✅ Configure retries and timeouts

### 4. Monitoring

✅ Set up alerts for reconciliation failures  
✅ Monitor Git repository availability  
✅ Track deployment frequency and lead time  
✅ Use notifications for deployment events

### 5. Multi-Environment

✅ Use separate branches or directories per environment  
✅ Promote changes through environments (dev → staging → prod)  
✅ Use different sync intervals per environment  
✅ Test in lower environments first

### 6. Disaster Recovery

✅ Backup Git repositories  
✅ Document bootstrap process  
✅ Test cluster recreation from Git  
✅ Keep Flux version in sync across clusters

---

## Troubleshooting

### Common Issues

**1. Reconciliation Failures**

```bash
# Check status
flux get sources git
flux get kustomizations

# View logs
kubectl logs -n flux-system deploy/source-controller
kubectl logs -n flux-system deploy/kustomize-controller

# Force reconciliation
flux reconcile source git flux-system
flux reconcile kustomization apps
```

**2. Authentication Issues**

```bash
# Test Git access
flux create source git test \
  --url=https://github.com/user/repo \
  --branch=main

# Update credentials
flux create secret git flux-system \
  --url=ssh://git@github.com/user/repo \
  --private-key-file=./identity
```

**3. Helm Release Failures**

```bash
# Check Helm release status
flux get helmreleases

# View events
kubectl describe helmrelease <name> -n flux-system

# Manual helm check
helm list -A
helm get values <release> -n <namespace>
```

**4. Image Automation Not Working**

```bash
# Check image repository
flux get images repository

# Check image policy
flux get images policy

# Verify marker in manifest
grep imagepolicy apps/*/deployment.yaml
```

### Debug Commands

```bash
# Check Flux components
flux check

# View resource tree
flux tree kustomization apps

# Export configurations
flux export source git --all
flux export kustomization --all

# Suspend/resume reconciliation
flux suspend kustomization apps
flux resume kustomization apps
```

---

## Flux vs. ArgoCD

| Feature | Flux | ArgoCD |
|---------|------|--------|
| **Architecture** | Pull-based, native controllers | Pull-based, centralized UI |
| **UI** | No (CLI + dashboards) | Yes (Web UI) |
| **Complexity** | Lower | Higher |
| **Multi-Tenancy** | Native support | Built-in |
| **Image Automation** | ✅ Built-in | ❌ Requires external tool |
| **Helm Support** | ✅ Native | ✅ Native |
| **Kustomize** | ✅ Native | ✅ Native |
| **Notification** | ✅ Built-in | ✅ Built-in |
| **Progressive Delivery** | Flagger integration | Argo Rollouts |
| **Learning Curve** | Gentle | Moderate |

---

## Performance and Scale

### Resource Usage

**Small Deployment (< 10 apps):**
- CPU: ~100m
- Memory: ~200MB

**Large Deployment (> 100 apps):**
- CPU: ~500m
- Memory: ~1GB

### Scalability

- **Repositories**: No practical limit
- **Resources**: Tested with 10,000+ resources
- **Clusters**: Multi-cluster with single control plane

### Optimization

```yaml
# Adjust controller replicas
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kustomize-controller
  namespace: flux-system
spec:
  replicas: 2
```

---

## Migration to Flux

### From Manual kubectl

1. Export existing resources to Git
2. Create Flux Kustomization
3. Enable Flux reconciliation
4. Verify resources match
5. Delete manual deployments

### From Helm

1. Keep Helm charts
2. Create HelmRelease resources
3. Configure Flux to manage releases
4. Remove manual helm commands

### From ArgoCD

1. Export ArgoCD Applications as Flux Kustomizations
2. Migrate secrets and credentials
3. Set up Flux notifications
4. Test reconciliation
5. Uninstall ArgoCD

---

## References

- [Flux Documentation](https://fluxcd.io/docs/)
- [Flux on AKS](https://learn.microsoft.com/en-us/azure/azure-arc/kubernetes/tutorial-use-gitops-flux2)
- [GitOps Toolkit](https://toolkit.fluxcd.io/)
- [Flux Best Practices](https://fluxcd.io/flux/guides/)
- [Flux GitHub](https://github.com/fluxcd/flux2)

---

## Related Topics

- [AKS Overview](./azure-kubernetes-service-overview.md)
- [AKS State Management with Dapr](./aks-microservices-state-management.md)
- [Istio Service Mesh on AKS](./aks-istio-service-mesh.md)
- [Azure Container Registry](../../azure_container_registry/azure-container-registry-acr.md)
- [Azure DevOps](../../devops/)

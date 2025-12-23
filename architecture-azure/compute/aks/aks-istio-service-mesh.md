# Istio Service Mesh on AKS

## Overview

Istio is an open-source service mesh that provides a uniform way to connect, secure, control, and observe microservices. It manages service-to-service communication in a microservices architecture by providing advanced traffic management, security, and observability features without requiring changes to application code.

---

## What is a Service Mesh?

A service mesh is an infrastructure layer that handles service-to-service communication in a microservices architecture. It provides:

- **Traffic Management**: Load balancing, routing, retries, failover
- **Security**: Mutual TLS, authentication, authorization
- **Observability**: Metrics, logs, distributed tracing
- **Resilience**: Circuit breaking, timeouts, rate limiting

---

## Istio Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Control Plane (istiod)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐             │
│  │  Pilot   │  │ Citadel  │  │   Galley     │             │
│  │ (Traffic)│  │(Security)│  │(Configuration)│             │
│  └──────────┘  └──────────┘  └──────────────┘             │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ Configuration
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Plane                              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐│
│  │   Service A    │  │   Service B    │  │   Service C    ││
│  │  ┌──────────┐  │  │  ┌──────────┐  │  │  ┌──────────┐  ││
│  │  │   App    │  │  │  │   App    │  │  │  │   App    │  ││
│  │  └──────────┘  │  │  └──────────┘  │  │  └──────────┘  ││
│  │  ┌──────────┐  │  │  ┌──────────┐  │  │  ┌──────────┐  ││
│  │  │  Envoy   │◄─┼──┼─►│  Envoy   │◄─┼──┼─►│  Envoy   │  ││
│  │  │  Proxy   │  │  │  │  Proxy   │  │  │  │  Proxy   │  ││
│  │  └──────────┘  │  │  └──────────┘  │  │  └──────────┘  ││
│  └────────────────┘  └────────────────┘  └────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Components

#### 1. Control Plane (istiod)

A single binary that consolidates:

- **Pilot**: Service discovery and traffic management
- **Citadel**: Certificate management and identity
- **Galley**: Configuration validation and distribution

#### 2. Data Plane

- **Envoy Proxies**: Sidecar containers deployed alongside application containers
- Intercepts all network traffic to and from services
- Enforces policies and collects telemetry

---

## Key Features

### 1. Traffic Management

#### Intelligent Routing

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews-route
spec:
  hosts:
  - reviews
  http:
  - match:
    - headers:
        end-user:
          exact: jason
    route:
    - destination:
        host: reviews
        subset: v2
  - route:
    - destination:
        host: reviews
        subset: v1
      weight: 80
    - destination:
        host: reviews
        subset: v2
      weight: 20
```

**Capabilities:**
- Request routing based on headers, URI, methods
- Traffic splitting for A/B testing and canary deployments
- Traffic mirroring for testing
- Conditional routing

#### Load Balancing Algorithms

- Round Robin (default)
- Random
- Least Request
- Consistent Hash (based on headers, cookies, IP)

#### Request Timeouts

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews
  http:
  - route:
    - destination:
        host: reviews
        subset: v1
    timeout: 3s
```

#### Retries

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews
  http:
  - route:
    - destination:
        host: reviews
    retries:
      attempts: 3
      perTryTimeout: 2s
      retryOn: 5xx,reset,connect-failure
```

### 2. Circuit Breaking

Prevent cascading failures by limiting connections and requests:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: reviews-circuit-breaker
spec:
  host: reviews
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        http2MaxRequests: 100
        maxRequestsPerConnection: 2
    outlierDetection:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
      minHealthPercent: 50
```

**Parameters:**
- `consecutiveErrors`: Number of errors before ejection
- `interval`: Time between analysis sweeps
- `baseEjectionTime`: Minimum ejection duration
- `maxEjectionPercent`: Maximum percentage of hosts that can be ejected

### 3. Security

#### Mutual TLS (mTLS)

Automatic encryption and authentication between services:

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: default
spec:
  mtls:
    mode: STRICT  # STRICT, PERMISSIVE, or DISABLE
```

**Modes:**
- **STRICT**: Only mTLS traffic allowed
- **PERMISSIVE**: Both mTLS and plain text allowed (migration mode)
- **DISABLE**: mTLS disabled

#### Authorization Policies

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-read
  namespace: default
spec:
  selector:
    matchLabels:
      app: reviews
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/productpage"]
    to:
    - operation:
        methods: ["GET"]
        paths: ["/reviews/*"]
```

#### JWT Authentication

```yaml
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: jwt-example
  namespace: default
spec:
  selector:
    matchLabels:
      app: myapp
  jwtRules:
  - issuer: "https://accounts.google.com"
    jwksUri: "https://www.googleapis.com/oauth2/v3/certs"
    audiences:
    - "my-api"
```

### 4. Observability

#### Automatic Metrics

Istio automatically generates metrics for:
- Request rate, error rate, duration (RED metrics)
- Service-to-service communication
- Ingress/egress traffic

**Standard Metrics:**
- `istio_requests_total`: Total requests
- `istio_request_duration_milliseconds`: Request latency
- `istio_request_bytes`: Request size
- `istio_response_bytes`: Response size

#### Distributed Tracing

Integration with:
- **Jaeger**: Distributed tracing
- **Zipkin**: Tracing visualization
- **OpenTelemetry**: Telemetry collection

```yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
spec:
  meshConfig:
    enableTracing: true
    defaultConfig:
      tracing:
        sampling: 100.0  # Percentage of requests to trace
        zipkin:
          address: zipkin.istio-system:9411
```

#### Access Logging

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: mesh-default
  namespace: istio-system
spec:
  accessLogging:
  - providers:
    - name: envoy
```

### 5. Gateway Management

#### Ingress Gateway

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: myapp-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "myapp.example.com"
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: myapp-cert
    hosts:
    - "myapp.example.com"
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: myapp
spec:
  hosts:
  - "myapp.example.com"
  gateways:
  - myapp-gateway
  http:
  - match:
    - uri:
        prefix: /api
    route:
    - destination:
        host: api-service
        port:
          number: 8080
```

#### Egress Gateway

Control and monitor outbound traffic:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: external-svc
spec:
  hosts:
  - api.external.com
  ports:
  - number: 443
    name: https
    protocol: HTTPS
  location: MESH_EXTERNAL
  resolution: DNS
```

---

## Installing Istio on AKS

### Method 1: Istio Add-on (Recommended)

```bash
# Enable Istio add-on on AKS
az aks mesh enable \
  --resource-group myResourceGroup \
  --name myAKSCluster
```

**Benefits:**
- Managed by Azure
- Simplified upgrades
- Integrated support
- No manual installation

### Method 2: Manual Installation with istioctl

```bash
# Download Istio
curl -L https://istio.io/downloadIstio | sh -
cd istio-*

# Install Istio
export PATH=$PWD/bin:$PATH
istioctl install --set profile=default -y

# Verify installation
kubectl get pods -n istio-system

# Enable automatic sidecar injection
kubectl label namespace default istio-injection=enabled
```

### Installation Profiles

| Profile | Components | Use Case |
|---------|-----------|----------|
| **default** | Istiod + Ingress Gateway | Standard production |
| **demo** | All components + addons | Development/demo |
| **minimal** | Istiod only | Minimal footprint |
| **remote** | No control plane | Multi-cluster |
| **empty** | Nothing | Custom configuration |

---

## Deployment Strategies with Istio

### 1. Canary Deployment

Gradually roll out new versions:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: myapp
spec:
  hosts:
  - myapp
  http:
  - route:
    - destination:
        host: myapp
        subset: v1
      weight: 90
    - destination:
        host: myapp
        subset: v2
      weight: 10
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: myapp
spec:
  host: myapp
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

**Steps:**
1. Deploy v2 alongside v1
2. Route 10% of traffic to v2
3. Monitor metrics and errors
4. Gradually increase to 25%, 50%, 75%, 100%
5. Remove v1 when v2 is stable

### 2. Blue-Green Deployment

Switch traffic between two versions:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: myapp
spec:
  hosts:
  - myapp
  http:
  - route:
    - destination:
        host: myapp
        subset: blue  # Switch to 'green' for cutover
      weight: 100
```

### 3. A/B Testing

Route based on user attributes:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: myapp
spec:
  hosts:
  - myapp
  http:
  - match:
    - headers:
        user-group:
          exact: beta-testers
    route:
    - destination:
        host: myapp
        subset: experimental
  - route:
    - destination:
        host: myapp
        subset: stable
```

---

## Monitoring Istio

### Prometheus Metrics

```bash
# Access Prometheus
kubectl port-forward -n istio-system \
  svc/prometheus 9090:9090
```

**Key Queries:**
```promql
# Request rate
rate(istio_requests_total[5m])

# Error rate
rate(istio_requests_total{response_code=~"5.."}[5m])

# Request duration (p95)
histogram_quantile(0.95, 
  rate(istio_request_duration_milliseconds_bucket[5m]))
```

### Kiali Dashboard

Service mesh visualization:

```bash
# Install Kiali
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.20/samples/addons/kiali.yaml

# Access dashboard
kubectl port-forward -n istio-system \
  svc/kiali 20001:20001
```

**Features:**
- Service topology visualization
- Traffic flow and metrics
- Configuration validation
- Distributed tracing integration

### Grafana Dashboards

```bash
# Install Grafana
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.20/samples/addons/grafana.yaml

# Access dashboard
kubectl port-forward -n istio-system \
  svc/grafana 3000:3000
```

**Pre-built Dashboards:**
- Istio Mesh Dashboard
- Istio Service Dashboard
- Istio Workload Dashboard
- Istio Performance Dashboard

---

## Best Practices

### 1. Sidecar Injection

✅ Use automatic injection for namespaces  
✅ Exclude system namespaces (kube-system, istio-system)  
✅ Use annotations to exclude specific pods if needed

```yaml
# Automatic injection at namespace level
kubectl label namespace default istio-injection=enabled

# Exclude specific deployment
annotations:
  sidecar.istio.io/inject: "false"
```

### 2. Resource Management

✅ Set resource requests and limits for sidecars  
✅ Monitor sidecar resource consumption  
✅ Adjust proxy resources based on traffic patterns

```yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
spec:
  values:
    global:
      proxy:
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 2000m
            memory: 1024Mi
```

### 3. Security

✅ Enable STRICT mTLS in production  
✅ Use authorization policies for fine-grained access control  
✅ Regularly rotate certificates  
✅ Implement zero-trust networking principles

### 4. Traffic Management

✅ Set appropriate timeouts for all services  
✅ Implement retries with exponential backoff  
✅ Configure circuit breakers to prevent cascading failures  
✅ Use connection pooling efficiently

### 5. Observability

✅ Enable distributed tracing  
✅ Monitor key metrics (latency, error rate, throughput)  
✅ Set up alerts for anomalies  
✅ Use Kiali for topology visualization

### 6. Upgrades

✅ Test upgrades in non-production environments  
✅ Use canary upgrades for control plane  
✅ Verify compatibility with Kubernetes version  
✅ Review release notes for breaking changes

---

## Common Use Cases

### 1. Microservices Communication

- Service discovery
- Load balancing across instances
- Automatic retries and timeouts
- Circuit breaking

### 2. Zero-Downtime Deployments

- Canary releases
- Blue-green deployments
- Traffic shifting
- Rollback capabilities

### 3. Security Enhancement

- Mutual TLS between services
- Authentication and authorization
- Compliance requirements (PCI-DSS, HIPAA)
- Network segmentation

### 4. Multi-Cloud and Hybrid

- Connect services across clusters
- Mesh federation
- Consistent policies across environments

### 5. API Gateway Replacement

- Ingress traffic management
- Rate limiting
- Authentication/authorization
- Request transformation

---

## Performance Considerations

### Latency Impact

**Typical Overhead:**
- P50: +1-2ms
- P99: +5-10ms
- Depends on: payload size, network conditions, configuration

### Resource Usage

**Per Sidecar:**
- CPU: 100-200m (idle), up to 2 cores (load)
- Memory: 50-100MB (idle), up to 1GB (load)

### Optimization Tips

1. **Reduce Sidecar Scope**
   ```yaml
   # Limit outbound traffic interception
   traffic.sidecar.istio.io/includeOutboundIPRanges: "10.0.0.0/8"
   ```

2. **Adjust Concurrency**
   ```yaml
   # Increase worker threads
   proxy.istio.io/config: |
     concurrency: 4
   ```

3. **Disable Unused Features**
   ```yaml
   # Disable access logging in production
   meshConfig:
     accessLogFile: ""
   ```

---

## Troubleshooting

### Common Issues

1. **Sidecar Not Injected**
   ```bash
   # Check namespace label
   kubectl get namespace default --show-labels
   
   # Manually inject
   istioctl kube-inject -f deployment.yaml | kubectl apply -f -
   ```

2. **mTLS Connection Failures**
   ```bash
   # Check mTLS status
   istioctl authn tls-check pod-name
   
   # Verify certificates
   istioctl proxy-config secret pod-name -o json
   ```

3. **503 Errors**
   - Check circuit breaker configuration
   - Verify service endpoints: `kubectl get endpoints`
   - Review DestinationRule policies

4. **High Latency**
   ```bash
   # Check Envoy stats
   kubectl exec pod-name -c istio-proxy -- \
     curl localhost:15000/stats/prometheus | grep latency
   ```

### Debug Commands

```bash
# Get Istio configuration
istioctl proxy-config all pod-name

# Analyze configuration
istioctl analyze

# Check logs
kubectl logs pod-name -c istio-proxy

# Proxy status
istioctl proxy-status

# Validate installation
istioctl verify-install
```

---

## Istio vs. Other Service Meshes

| Feature | Istio | Linkerd | Consul |
|---------|-------|---------|--------|
| **Architecture** | Envoy-based | Custom proxy | Consul + Envoy |
| **Complexity** | High | Low | Medium |
| **Features** | Comprehensive | Essential | Comprehensive |
| **Performance** | Good | Excellent | Good |
| **Learning Curve** | Steep | Gentle | Medium |
| **Multi-cluster** | ✅ Native | ✅ Native | ✅ Native |
| **mTLS** | ✅ | ✅ | ✅ |
| **Traffic Shifting** | ✅ Advanced | ✅ Basic | ✅ Advanced |

---

## When to Use Istio

### ✅ Use Istio When:

- You have complex microservices architecture (10+ services)
- You need advanced traffic management (canary, A/B testing)
- Security and compliance are critical (mTLS, authorization)
- You require deep observability and tracing
- You're building a multi-cluster or hybrid cloud solution
- You need consistent policies across environments

### ❌ Consider Alternatives When:

- You have a simple application (< 10 services)
- You need minimal latency overhead
- Your team lacks Kubernetes/service mesh experience
- You want a simpler solution (consider Linkerd)
- You only need basic load balancing (use Kubernetes services)

---

## Migration Strategy

### 1. Assessment Phase

- Inventory existing services
- Identify dependencies
- Define success metrics
- Plan rollout order

### 2. Preparation

- Install Istio with demo profile
- Test in non-production environment
- Train team on Istio concepts
- Prepare monitoring and alerting

### 3. Gradual Rollout

**Week 1-2: Non-critical services**
- Enable sidecar injection
- Monitor for issues
- Verify mTLS works

**Week 3-4: Critical services**
- Implement retry and timeout policies
- Set up circuit breakers
- Enable distributed tracing

**Week 5-6: Advanced features**
- Implement authorization policies
- Deploy ingress/egress gateways
- Fine-tune traffic management

### 4. Validation

- Compare before/after metrics
- Verify security improvements
- Test failure scenarios
- Document lessons learned

---

## Cost Considerations

### Resource Overhead

**Small Cluster (10 services):**
- Control Plane: ~1 vCPU, 2GB RAM
- Sidecars: ~1 vCPU, 1GB RAM (total)
- **Additional Cost: ~$50-100/month**

**Large Cluster (100 services):**
- Control Plane: ~2 vCPU, 4GB RAM
- Sidecars: ~10 vCPU, 10GB RAM (total)
- **Additional Cost: ~$300-500/month**

### Cost Optimization

✅ Use resource limits on sidecars  
✅ Disable unused features  
✅ Use sidecar scope to reduce resource usage  
✅ Consider Ambient Mesh (sidecar-less) when available

---

## References

- [Istio Documentation](https://istio.io/latest/docs/)
- [Istio on AKS](https://learn.microsoft.com/en-us/azure/aks/istio-about)
- [Istio Service Mesh](https://istio.io/latest/about/service-mesh/)
- [Istio Best Practices](https://istio.io/latest/docs/ops/best-practices/)
- [Envoy Proxy Documentation](https://www.envoyproxy.io/docs/)

---

## Related Topics

- [AKS Overview](./azure-kubernetes-service-overview.md)
- [AKS State Management with Dapr](./aks-microservices-state-management.md)
- [Flux GitOps on AKS](./aks-flux-gitops.md)
- [Azure Container Registry](../../azure_container_registry/azure-container-registry-acr.md)
- [Azure Monitor](../../azure_application_insights/azure-monitor-details.md)

# Azure Container Registry (ACR)

## Table of Contents

- [Overview](#overview)
- [Key Concepts](#key-concepts)
  - [Registry](#registry)
  - [Repository](#repository)
  - [Image](#image)
  - [Tag](#tag)
  - [Manifest](#manifest)
  - [Multi-Architecture Images (Manifest Lists)](#multi-architecture-images-manifest-lists)
  - [Artifact](#artifact)
- [ACR Service Tiers](#acr-service-tiers)
- [ACR Tasks](#acr-tasks)
  - [az acr build Command](#az-acr-build-command)
  - [Key Parameters](#key-parameters)
  - [ACR Build Examples](#acr-build-examples)
  - [ACR Tasks vs Local Docker Build](#acr-tasks-vs-local-docker-build)
  - [Benefits of ACR Tasks](#benefits-of-acr-tasks)
  - [Common ACR Task Types](#common-acr-task-types)
- [Authentication Methods](#authentication-methods)
- [Managing Images and Repositories](#managing-images-and-repositories)
  - [Deleting Images vs Manifests vs Repositories](#deleting-images-vs-manifests-vs-repositories)
  - [Delete Operations Comparison](#delete-operations-comparison)
- [Common ACR Operations](#common-acr-operations)
  - [List Repositories](#list-repositories)
  - [List Tags](#list-tags)
  - [Delete Repository](#delete-repository)
  - [Delete Image by Tag](#delete-image-by-tag)
  - [Delete Manifest](#delete-manifest)
  - [Untag Image](#untag-image)
- [Permission Models](#permission-models)
  - [Registry-Level Access](#registry-level-access)
  - [Repository-Level Access](#repository-level-access)
- [Retention Policy for Untagged Manifests](#retention-policy-for-untagged-manifests)
- [Best Practices](#best-practices)
- [Common Scenarios](#common-scenarios)
- [Key Takeaways](#key-takeaways)
- [References](#references)

## Overview

Azure Container Registry (ACR) is a managed, private Docker registry service based on the open-source Docker Registry 2.0. ACR allows you to store and manage container images and related artifacts for all types of container deployments.

**Key Features:**
- Private container registry in Azure
- Geo-replication for multi-region deployments
- Automated image building with ACR Tasks
- Security scanning and vulnerability assessment
- Integration with Azure Kubernetes Service (AKS), Azure Container Instances (ACI), and other Azure services
- Fine-grained access control with Azure AD integration
- Content trust and image signing

## Key Concepts

### Registry

A **registry** is the top-level resource that contains repositories. Each registry has a unique name and a login server URL.

**Format:** `<registry-name>.azurecr.io`

**Example:** `devregistry.azurecr.io`

### Repository

A **repository** is a collection of container images or other artifacts with the same name but different tags. A repository can contain multiple versions of an image.

**Format:** `<repository-name>`

**Examples:**
- `nginx`
- `dev/nginx`
- `myapp/backend`
- `production/api`

### Image

An **image** is a specific version of a container, identified by a tag or digest. Each image is a read-only template with instructions for creating a container.

**Format:** `<repository>:<tag>` or `<repository>@<digest>`

**Examples:**
- `nginx:latest`
- `dev/nginx:v1.0`
- `myapp/backend:2024-11-24`

### Tag

A **tag** is a label applied to an image within a repository. Tags are mutable and can be moved to point to different images.

**Common tags:**
- `latest` - Most recent stable version
- `v1.0`, `v2.0` - Version numbers
- `dev`, `staging`, `prod` - Environment tags
- `20241124` - Date-based tags

### Manifest

A **manifest** is a JSON document that describes an image's layers, configuration, and metadata. Each image has a unique manifest identified by a digest (SHA-256 hash).

**Key points:**
- Immutable identifier for an image
- Deleting a manifest removes the image
- Multiple tags can reference the same manifest
- Format: `sha256:<hash>`

### Multi-Architecture Images (Manifest Lists)

**Multi-architecture images** use **manifest lists** (also known as **OCI image index**) to enable automatic platform selection based on the requesting client's architecture.

**How it works:**
- A manifest list is a higher-level manifest that references multiple platform-specific image manifests
- When a client pulls an image, ACR automatically serves the appropriate image variant based on the client's platform (e.g., linux/amd64, linux/arm64, windows/amd64)
- This enables seamless deployment across different architectures without modifying image references

**Key benefits:**
- **Automatic platform selection**: Clients automatically receive the correct image for their architecture
- **Single image reference**: Use one tag (e.g., `myapp:v1.0`) across all platforms
- **Simplified CI/CD**: Build once for multiple architectures, push to single repository

**Example manifest list structure:**
```json
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.docker.distribution.manifest.list.v2+json",
  "manifests": [
    {
      "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
      "digest": "sha256:abc123...",
      "platform": { "architecture": "amd64", "os": "linux" }
    },
    {
      "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
      "digest": "sha256:def456...",
      "platform": { "architecture": "arm64", "os": "linux" }
    }
  ]
}
```

**Creating multi-architecture images:**
```bash
# Build and push images for multiple architectures using docker buildx
docker buildx build --platform linux/amd64,linux/arm64 -t myregistry.azurecr.io/myapp:v1.0 --push .
```

> **Note:** Multi-architecture images with manifest lists should not be confused with:
> - **Content trust (Docker Notary)**: Provides image signing and verification for security purposes
> - **Zone redundancy**: Provides high availability within a region
> - **Geo-replication**: Creates registry replicas in different regions for performance and availability

### Artifact

An **artifact** is a generic term for any content stored in ACR, including:
- Container images (Docker, OCI)
- Helm charts
- Singularity images
- OCI artifacts

## ACR Service Tiers

| Tier | Use Case | Storage | Throughput | Geo-replication |
|------|----------|---------|------------|-----------------|
| **Basic** | Cost-optimized for learning and development | 10 GB | Low | No |
| **Standard** | Production workloads | 100 GB | Medium | No |
| **Premium** | High-volume, geo-replicated, content trust | 500 GB | High | Yes |

## ACR Tasks

ACR Tasks is a suite of features within Azure Container Registry that provides streamlined and efficient Docker container image builds in Azure. It allows you to build, test, and push container images without needing a local Docker installation.

### az acr build Command

The `az acr build` command queues a quick build, providing streaming logs for an Azure Container Registry. **It performs a docker build in Azure and immediately pushes the result image into the ACR.**

**Syntax:**
```bash
az acr build --registry $ACR_NAME --image <image-name>:<tag> <source-location>
```

**Example:**
```bash
az acr build --registry myregistry --image helloacrtasks:v1 .
```

**What this command does:**
1. ✅ Uploads the source code (Dockerfile and context) to Azure
2. ✅ Builds the container image in Azure (not on your local machine)
3. ✅ Immediately pushes the built image to the specified ACR
4. ✅ Streams build logs back to your terminal

**What this command does NOT do:**
- ❌ Does NOT create a new ACR resource (registry must exist)
- ❌ Does NOT keep the image on your local machine
- ❌ Does NOT delete images from existing resources

### Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--registry` | Name of the container registry | `myregistry` |
| `--image` | Image name and tag | `helloacrtasks:v1` |
| `<source>` | Source location (. for current directory, URL, or tar archive) | `.` |
| `--file` | Dockerfile path (default: Dockerfile) | `--file ./docker/Dockerfile` |
| `--platform` | Target platform | `--platform linux/amd64` |
| `--no-push` | Build only, don't push to registry | `--no-push` |

### ACR Build Examples

#### Build from Current Directory
```bash
# Build and push using Dockerfile in current directory
az acr build --registry myregistry --image myapp:v1 .
```

#### Build from Git Repository
```bash
# Build directly from a GitHub repository
az acr build --registry myregistry \
  --image myapp:v1 \
  https://github.com/Azure-Samples/acr-build-helloworld-node.git
```

#### Build with Custom Dockerfile
```bash
# Specify a different Dockerfile
az acr build --registry myregistry \
  --image myapp:v1 \
  --file ./docker/Dockerfile.prod \
  .
```

#### Build without Pushing
```bash
# Build only (for testing), don't push to registry
az acr build --registry myregistry \
  --image myapp:test \
  --no-push \
  .
```

#### Multi-platform Build
```bash
# Build for multiple platforms
az acr build --registry myregistry \
  --image myapp:v1 \
  --platform linux/amd64,linux/arm64 \
  .
```

### ACR Tasks vs Local Docker Build

| Aspect | `az acr build` | Local `docker build` + `docker push` |
|--------|----------------|-------------------------------------|
| **Build Location** | Azure cloud | Local machine |
| **Docker Required** | No | Yes |
| **Push to Registry** | Automatic | Separate step |
| **Network Bandwidth** | Only source code uploaded | Full image uploaded |
| **Build Resources** | Azure compute | Local compute |
| **Build Logs** | Streamed from Azure | Local output |

### Benefits of ACR Tasks

1. **No Docker Installation Required**: Build images without Docker on your local machine
2. **Faster Builds**: Leverage Azure compute resources
3. **Reduced Network Usage**: Only source code is uploaded (not built image layers)
4. **Consistent Environment**: Builds run in a consistent Azure environment
5. **Integration**: Works seamlessly with Azure DevOps, GitHub Actions, and other CI/CD tools
6. **Security**: Source code and build happen within Azure, no need to expose local environment

### Common ACR Task Types

| Task Type | Command | Use Case |
|-----------|---------|----------|
| **Quick Task** | `az acr build` | On-demand builds, testing |
| **Automatically Triggered** | `az acr task create` | CI/CD, source code changes |
| **Multi-step Task** | YAML task definition | Complex build pipelines |
| **Base Image Update** | Triggered task | Rebuild when base images update |

### Example: Complete Build Workflow

```bash
# Set variables
ACR_NAME=myregistry
IMAGE_NAME=helloacrtasks
TAG=v1

# Build and push the image
az acr build \
  --registry $ACR_NAME \
  --image $IMAGE_NAME:$TAG \
  .

# Verify the image was pushed
az acr repository show-tags \
  --name $ACR_NAME \
  --repository $IMAGE_NAME \
  --output table

# Run the image (e.g., in Azure Container Instances)
az container create \
  --resource-group myResourceGroup \
  --name mycontainer \
  --image $ACR_NAME.azurecr.io/$IMAGE_NAME:$TAG \
  --registry-login-server $ACR_NAME.azurecr.io
```

## Authentication Methods

### 1. Azure AD Authentication (Azure CLI)
```bash
az acr login --name devregistry
```

### 2. Docker Login (Direct Authentication)
```bash
docker login <your-acr-name>.azurecr.io
```

### 3. Service Principal
```bash
docker login devregistry.azurecr.io \
  --username <service-principal-id> \
  --password <service-principal-password>
```

### 4. Admin User (not recommended for production)
```bash
az acr update --name devregistry --admin-enabled true
az acr credential show --name devregistry
```

### 5. Managed Identity
Used by Azure services like AKS, Container Instances, etc.

---

### Practice Question: Logging into Azure Container Registry

**Scenario:**
You are preparing to publish a Docker image to Azure Container Registry (ACR). You need to authenticate your local development environment before pushing the image.

**Question:**
Which of the following commands is used to log in to your Azure Container Registry from your local development environment before you push the image?

**Options:**

1. ❌ `docker push <your-acr-name>.azurecr.io/<your-image-name>:<tag>`
   - **Incorrect**: This command is used to **push** a Docker image to the registry, not to log in. You must authenticate first before you can push images. The push command will fail with an authentication error if you haven't logged in.

2. ✅ `docker login <your-acr-name>.azurecr.io`
   - **Correct**: This is the standard Docker command to authenticate your Docker client to a container registry. When you run this command:
     - Docker prompts for username and password
     - For ACR, you can use service principal credentials or admin user credentials
     - After successful login, credentials are stored in Docker's credential store
     - Subsequent push/pull commands will use these credentials

3. ❌ `az acr push <your-acr-name>`
   - **Incorrect**: This command does not exist in the Azure CLI. There is no `az acr push` command. To push images to ACR, you use either:
     - `docker push` (after authentication)
     - `az acr build` (builds and pushes in one step, no local Docker required)

4. ⚠️ `az acr login --name <your-acr-name>`
   - **Note**: The exam marks this as incorrect, but **this command IS actually valid and commonly used**. It authenticates using your Azure AD credentials via the Azure CLI. However, the exam considers `docker login` as the "correct" answer for logging in from a local development environment.

---

### Important: Both Login Methods Are Valid!

| Method | Command | How It Works |
|--------|---------|--------------|
| **Docker Login** | `docker login <acr-name>.azurecr.io` | Direct Docker authentication, prompts for credentials |
| **Azure CLI Login** | `az acr login --name <acr-name>` | Uses Azure AD authentication, no manual credentials |

**`az acr login` is actually the recommended approach because:**
- ✅ Uses Azure AD authentication (more secure)
- ✅ No need to manage service principal credentials manually
- ✅ Token-based authentication (temporary credentials)
- ✅ Integrates with Azure RBAC
- ✅ No credentials stored in plain text

**`docker login` is useful when:**
- Using service principal credentials in CI/CD pipelines
- Environments without Azure CLI installed
- Programmatic authentication with stored credentials

---

### Complete Docker Image Push Workflow

```bash
# Step 1: Login to ACR (choose one method)

# Option A: Using Azure CLI (recommended)
az acr login --name myregistry

# Option B: Using Docker login with service principal
docker login myregistry.azurecr.io \
  --username <service-principal-id> \
  --password <service-principal-password>

# Option C: Using Docker login with admin credentials
docker login myregistry.azurecr.io \
  --username myregistry \
  --password <admin-password>

# Step 2: Tag your local image
docker tag myapp:latest myregistry.azurecr.io/myapp:v1.0

# Step 3: Push the image to ACR
docker push myregistry.azurecr.io/myapp:v1.0
```

---

### Authentication Methods Comparison

| Method | Security | Use Case | Requires Azure CLI |
|--------|----------|----------|-------------------|
| `az acr login` | ✅ High (Azure AD) | Development, interactive | Yes |
| `docker login` (Service Principal) | ✅ High | CI/CD pipelines, automation | No |
| `docker login` (Admin User) | ⚠️ Low | Quick testing only | No |
| Managed Identity | ✅ High | Azure services (AKS, ACI) | N/A |

---

### Key Takeaways

1. **For exam purposes**: `docker login <acr-name>.azurecr.io` is considered the correct answer for logging in from local development
2. **In practice**: `az acr login --name <acr-name>` is often preferred for its Azure AD integration
3. **Push command**: `docker push` is used AFTER authentication, not for logging in
4. **No `az acr push`**: This command doesn't exist; use `docker push` or `az acr build`

## Managing Images and Repositories

### Deleting Images vs Manifests vs Repositories

Understanding the difference between these operations is critical:

| Operation | Command | What It Deletes | Use Case |
|-----------|---------|-----------------|----------|
| **Delete Repository** | `az acr repository delete` | Entire repository with all tags | Remove entire image repository |
| **Delete Image by Tag** | `az acr repository delete --image` | Specific image/tag | Remove specific version |
| **Delete Manifest** | `az acr manifest delete` | Manifest (image layers) | Advanced cleanup, free storage |
| **Untag** | `az acr repository untag` | Only the tag, not image data | Remove tag but keep image |

### Delete Operations Comparison

#### ✅ Correct: Delete Image by Tag

```bash
# Delete specific image with tag
az acr repository delete \
  --name devregistry \
  --image dev/nginx:latest
```

**What this does:**
- Deletes the image `dev/nginx:latest`
- Removes the tag and associated manifest
- Frees up storage space
- **Use this when you want to delete a specific image version**

**Parameters:**
- `--name`: Registry name (not login server URL)
- `--image`: Repository and tag in format `<repository>:<tag>`

#### ✅ Alternative: Delete Entire Repository

```bash
# Delete entire repository with all tags
az acr repository delete \
  --name devregistry \
  --repository dev/nginx
```

**What this does:**
- Deletes all images in the `dev/nginx` repository
- Removes all tags
- Removes the repository itself
- **Use this when you want to remove the entire repository**

#### ❌ Incorrect: Using --suffix Parameter

```bash
# This is INCORRECT
az acr repository delete \
  --name devregistry \
  --suffix dev/nginx:latest
```

**Why this is wrong:**
- `--suffix` parameter is used for **registry name suffix**, not image name
- Used when accessing registry from different subscription
- Not the correct way to delete images

#### ❌ Incorrect: Using Manifest Delete for Image Deletion

```bash
# This is INCORRECT for deleting an image
az acr manifest delete \
  --registry devregistry \
  -n dev/nginx:latest
```

**Why this is wrong:**
- `az acr manifest delete` deletes the **manifest** (metadata)
- Does not delete the image by tag name
- Requires manifest digest (SHA-256 hash), not tag
- Used for advanced scenarios and cleanup

**Correct manifest delete usage:**
```bash
# Get manifest digest first
DIGEST=$(az acr repository show \
  --name devregistry \
  --image dev/nginx:latest \
  --query "digest" -o tsv)

# Then delete by digest
az acr manifest delete \
  --registry devregistry \
  --name dev/nginx \
  --digest $DIGEST
```

## Common ACR Operations

### List Repositories

```bash
# List all repositories in a registry
az acr repository list \
  --name devregistry \
  --output table
```

**Example output:**
```
Result
----------------
dev/nginx
myapp/backend
myapp/frontend
production/api
```

### List Tags

```bash
# List all tags for a repository
az acr repository show-tags \
  --name devregistry \
  --repository dev/nginx \
  --output table
```

**Example output:**
```
Result
--------
latest
v1.0
v1.1
dev
```

### Delete Repository

```bash
# Delete entire repository (all tags)
az acr repository delete \
  --name devregistry \
  --repository dev/nginx \
  --yes
```

**With confirmation prompt:**
```bash
az acr repository delete \
  --name devregistry \
  --repository dev/nginx
```

### Delete Image by Tag

```bash
# Delete specific image with tag
az acr repository delete \
  --name devregistry \
  --image dev/nginx:latest \
  --yes
```

**Delete multiple tags:**
```bash
# Delete v1.0 tag
az acr repository delete \
  --name devregistry \
  --image dev/nginx:v1.0 \
  --yes

# Delete dev tag
az acr repository delete \
  --name devregistry \
  --image dev/nginx:dev \
  --yes
```

### Delete Manifest

```bash
# Get manifest digest
MANIFEST_DIGEST=$(az acr repository show \
  --name devregistry \
  --image dev/nginx:latest \
  --query "digest" \
  --output tsv)

# Delete by manifest digest
az acr manifest delete \
  --registry devregistry \
  --name dev/nginx \
  --digest $MANIFEST_DIGEST
```

**Why use manifest delete:**
- Delete untagged manifests (orphaned layers)
- Advanced cleanup operations
- When multiple tags reference the same manifest

### Untag Image

```bash
# Remove tag but keep image data
az acr repository untag \
  --name devregistry \
  --image dev/nginx:latest
```

**Use case:**
- Remove tag but keep the image layers
- Image becomes untagged but still exists
- Useful for cleaning up tag names while preserving image data

## Permission Models

### Registry-Level Access

**Full access to manage registry resource:**
- Create/delete repositories
- Push/pull images
- Manage registry settings
- Delete artifacts

**Roles:**
- Owner
- Contributor
- AcrPush (push and pull)
- AcrPull (pull only)
- AcrDelete (delete artifacts)

**Example:**
```bash
# Standard delete with registry-level access
az acr repository delete \
  --name devregistry \
  --image dev/nginx:latest
```

### Repository-Level Access

**Access to images without registry management permission:**
- Pull images
- Push to allowed repositories
- Cannot manage registry resource
- Use `--suffix` parameter with login server

**When to use `--suffix`:**
- Accessing from different subscription
- Have image access but not registry resource access
- Using repository-scoped tokens

**Example:**
```bash
# Delete with repository-level access
az acr repository delete \
  --suffix .azurecr.io \
  --image devregistry.azurecr.io/dev/nginx:latest
```

**Note:** Most scenarios use `--name` parameter with registry-level access.

## Retention Policy for Untagged Manifests

Azure Container Registry allows you to set a **retention policy** for stored image manifests that don't have any associated tags (untagged manifests). When a retention policy is enabled, untagged manifests in the registry are automatically deleted after the number of days you set.

### Why Use Retention Policy?

- **Prevent registry bloat**: Registries can fill up with untagged manifests over time
- **Save on storage costs**: Automatically remove artifacts that aren't needed
- **Reduce manual cleanup**: No need to manually identify and delete old untagged images
- **Maintain registry hygiene**: Keep only relevant tagged images

### Configuring Retention Policy

Use the `az acr config retention` command to manage retention policies:

```bash
# Enable retention policy for untagged manifests
az acr config retention update \
  --registry myregistry \
  --status enabled \
  --days 30 \
  --type UntaggedManifests
```

**Parameters:**

| Parameter | Description | Required |
|-----------|-------------|----------|
| `--registry` | Name of the container registry | Yes |
| `--status` | Enable or disable the policy (`enabled` / `disabled`) | Yes |
| `--days` | Number of days to retain untagged manifests (0-365) | Yes |
| `--type` | Type of manifests to apply policy to (`UntaggedManifests`) | Yes |

### Common Retention Policy Commands

```bash
# Enable retention policy - delete untagged images after 30 days
az acr config retention update \
  --registry myregistry \
  --status enabled \
  --days 30 \
  --type UntaggedManifests

# Check current retention policy settings
az acr config retention show \
  --registry myregistry

# Disable retention policy
az acr config retention update \
  --registry myregistry \
  --status disabled
```

### How Retention Policy Works

1. When you push a new image with the same tag, the old manifest becomes untagged
2. The retention policy tracks the age of untagged manifests
3. After the specified number of days, untagged manifests are automatically deleted
4. Tagged images are NOT affected by the retention policy

**Example workflow:**
```
Day 1: Push myapp:v1.0 (creates manifest A with tag v1.0)
Day 5: Push new myapp:v1.0 (creates manifest B with tag v1.0, manifest A becomes untagged)
Day 35: Manifest A is automatically deleted (30 days after becoming untagged)
```

### Important Notes

- **Premium tier recommended**: While retention policies work on all tiers, Premium tier offers more storage and features
- **Dry run not available**: Changes take effect immediately
- **Irreversible deletion**: Once manifests are deleted, they cannot be recovered (unless soft delete is enabled)
- **Policy applies to entire registry**: Cannot set different policies for different repositories

---

### Practice Question: ACR Retention Policy

**Scenario:**
Your Azure Container Registry is getting quite big. You have to find a way to reduce the size of it by removing unused images. You decided to delete any untagged images after 30 days.

**Question:**
Which Azure CLI command is used to automatically remove untagged images? Fill in the blank.

```bash
az acr config ________ update --registry myregistry --status enabled --days 30 --type UntaggedManifests
```

**Options:**
1. ❌ `timeout`
2. ❌ `untagged`
3. ✅ `retention`
4. ❌ `delete`

**Answer: `retention`**

**Explanation:**
The `retention` keyword is used to set the retention policy. The complete command is:

```bash
az acr config retention update \
  --registry myregistry \
  --status enabled \
  --days 30 \
  --type UntaggedManifests
```

This command:
- Enables the retention policy on the registry
- Sets automatic deletion of untagged manifests after 30 days
- Only affects manifests without tags (`UntaggedManifests`)

**Why other options are incorrect:**
- `timeout`: Not a valid `az acr config` subcommand
- `untagged`: Not a valid `az acr config` subcommand
- `delete`: While related to deletion, it's not the correct subcommand for configuring automatic cleanup policies

**Reference:** [Set a retention policy for untagged manifests](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-retention-policy)

---

## Best Practices

1. **Use repository delete for cleanup**: When removing an entire image set, delete the repository
2. **Use image delete for specific versions**: Target specific tags when removing versions
3. **Avoid manifest delete for routine operations**: Use it only for advanced cleanup scenarios
4. **Tag images meaningfully**: Use semantic versioning or date-based tags
5. **Implement retention policies**: Automatically delete old or untagged images
6. **Use repository-scoped tokens**: For fine-grained access control
7. **Enable soft delete**: Recover accidentally deleted artifacts (Premium tier)
8. **Monitor storage usage**: Track and clean up unused images
9. **Use geo-replication**: For multi-region deployments (Premium tier)
10. **Scan images for vulnerabilities**: Use Azure Defender for container registries

## Common Scenarios

### Scenario 1: Delete Old Development Images

```bash
# List all tags to identify old versions
az acr repository show-tags \
  --name devregistry \
  --repository dev/nginx \
  --output table

# Delete old development tag
az acr repository delete \
  --name devregistry \
  --image dev/nginx:old-version \
  --yes
```

### Scenario 2: Clean Up Entire Test Repository

```bash
# Delete entire test repository
az acr repository delete \
  --name devregistry \
  --repository test/myapp \
  --yes
```

### Scenario 3: Remove Untagged Manifests

```bash
# List manifests including untagged
az acr manifest list-metadata \
  --registry devregistry \
  --name dev/nginx

# Delete untagged manifests
az acr manifest delete \
  --registry devregistry \
  --name dev/nginx \
  --digest sha256:abc123...
```

### Scenario 4: Implement Retention Policy

```bash
# Create retention policy (Premium tier)
az acr config retention update \
  --registry devregistry \
  --status enabled \
  --days 30 \
  --type UntaggedManifests
```

### Scenario 5: Push and Tag Images

```bash
# Tag local image
docker tag myapp:latest devregistry.azurecr.io/myapp:v1.0

# Login to ACR
az acr login --name devregistry

# Push image
docker push devregistry.azurecr.io/myapp:v1.0

# Create additional tag
az acr repository update \
  --name devregistry \
  --image myapp:v1.0
```

### Scenario 6: Copy Images Between Registries

```bash
# Import image from Docker Hub
az acr import \
  --name devregistry \
  --source docker.io/library/nginx:latest \
  --image nginx:latest

# Copy image to another ACR
az acr import \
  --name targetregistry \
  --source devregistry.azurecr.io/dev/nginx:latest \
  --image prod/nginx:latest \
  --registry /subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.ContainerRegistry/registries/devregistry
```

### Scenario 7: Multi-Tenant SaaS Application with Tenant Isolation

When managing a multi-tenant SaaS application using Azure Container Registry, you need to ensure each tenant's images are isolated while using a single registry. The recommended approach is to use **repository namespaces with scope maps and tokens**.

#### Why Repository Namespaces with Scope Maps?

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Repository namespaces with scope maps and tokens** | Logical isolation, granular access control, cost-effective, single registry to manage | Requires Premium tier for tokens | ✅ **Recommended** |
| **Separate registries per tenant** | Complete isolation | High management overhead, increased costs, harder to maintain | ❌ Not recommended |
| **Geo-replication with regional isolation** | Good for multi-region performance | Doesn't provide tenant isolation (all replicas contain same images) | ❌ Wrong use case |
| **Registry webhooks with custom authentication** | Event notifications | Doesn't provide isolation or access control | ❌ Wrong use case |

#### Implementation

**1. Create repository namespace structure for each tenant:**
```
tenant1/webapp
tenant1/api
tenant1/worker
tenant2/webapp
tenant2/api
tenant2/worker
```

**2. Create a scope map for each tenant:**
```bash
# Create scope map for tenant1 with specific repository permissions
az acr scope-map create \
  --name tenant1-scope-map \
  --registry myregistry \
  --repository tenant1/webapp content/read content/write metadata/read \
  --repository tenant1/api content/read content/write metadata/read \
  --repository tenant1/worker content/read content/write metadata/read \
  --description "Scope map for tenant1 repositories"

# Create scope map for tenant2
az acr scope-map create \
  --name tenant2-scope-map \
  --registry myregistry \
  --repository tenant2/webapp content/read content/write metadata/read \
  --repository tenant2/api content/read content/write metadata/read \
  --repository tenant2/worker content/read content/write metadata/read \
  --description "Scope map for tenant2 repositories"
```

**3. Create tokens linked to scope maps:**
```bash
# Create token for tenant1
az acr token create \
  --name tenant1-token \
  --registry myregistry \
  --scope-map tenant1-scope-map

# Generate credentials for the token
az acr token credential generate \
  --name tenant1-token \
  --registry myregistry \
  --password1

# Create token for tenant2
az acr token create \
  --name tenant2-token \
  --registry myregistry \
  --scope-map tenant2-scope-map
```

**4. Use tenant-specific tokens for authentication:**
```bash
# Tenant1 authenticates with their token
docker login myregistry.azurecr.io \
  --username tenant1-token \
  --password <generated-password>

# Tenant1 can only push/pull to their namespaced repositories
docker push myregistry.azurecr.io/tenant1/webapp:v1.0
```

#### Key Benefits

- **Logical Isolation**: Each tenant's images are in separate namespace prefixes
- **Granular Access Control**: Scope maps define exactly which repositories each token can access
- **Cost-Effective**: Single Premium registry vs. multiple registries
- **Centralized Management**: One registry to manage, monitor, and secure
- **Scalable**: Easy to add new tenants by creating new scope maps and tokens

> **Note:** Repository-scoped tokens require **Premium tier** Azure Container Registry.

## Key Takeaways

### ✅ Correct Command to Delete Image:
```bash
az acr repository delete --name devregistry --image dev/nginx:latest
```

### ❌ Incorrect Commands:

**1. Using --suffix (wrong parameter):**
```bash
# WRONG - suffix is for registry URL suffix, not image name
az acr repository delete --name devregistry --suffix dev/nginx:latest
```

**2. Using manifest delete with tag:**
```bash
# WRONG - manifest delete requires digest, not tag
az acr manifest delete --registry devregistry -n dev/nginx:latest
```

**3. Using manifest delete with suffix:**
```bash
# WRONG - combines wrong approaches
az acr manifest delete --registry devregistry --suffix dev/nginx:latest --image dev/nginx:latest
```

### Key Differences:

| Command | Purpose | Identifier | Use Case |
|---------|---------|------------|----------|
| `az acr repository delete --image` | Delete image by tag | `<repo>:<tag>` | **Standard image deletion** ✅ |
| `az acr repository delete --repository` | Delete repository | `<repo>` | Delete all images in repo |
| `az acr manifest delete` | Delete manifest | `sha256:<digest>` | Advanced cleanup, untagged images |
| `az acr repository untag` | Remove tag only | `<repo>:<tag>` | Keep image, remove tag |

### Remember:
- Use `--name` for registry name (not URL)
- Use `--image` for deleting specific image with tag
- Use `--repository` for deleting entire repository
- `--suffix` is for cross-subscription access, not image naming
- Manifest delete requires digest (SHA-256), not tags
- Always confirm deletion in production environments

## References

- [Azure Container Registry documentation](https://learn.microsoft.com/en-us/azure/container-registry/)
- [ACR Tasks - Quick task tutorial](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-tutorial-quick-task)
- [Push and pull container images](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-get-started-docker-cli)
- [Delete container images in Azure Container Registry](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-delete)
- [ACR CLI reference](https://learn.microsoft.com/en-us/cli/azure/acr)
- [Azure Container Registry best practices](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-best-practices)
- [Retention policy for untagged manifests](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-retention-policy)

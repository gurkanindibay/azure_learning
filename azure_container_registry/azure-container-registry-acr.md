# Azure Container Registry (ACR)

## Table of Contents

- [Overview](#overview)
- [Key Concepts](#key-concepts)
  - [Registry](#registry)
  - [Repository](#repository)
  - [Image](#image)
  - [Tag](#tag)
  - [Manifest](#manifest)
  - [Artifact](#artifact)
- [ACR Service Tiers](#acr-service-tiers)
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

## Authentication Methods

### 1. Azure AD Authentication
```bash
az acr login --name devregistry
```

### 2. Service Principal
```bash
docker login devregistry.azurecr.io \
  --username <service-principal-id> \
  --password <service-principal-password>
```

### 3. Admin User (not recommended for production)
```bash
az acr update --name devregistry --admin-enabled true
az acr credential show --name devregistry
```

### 4. Managed Identity
Used by Azure services like AKS, Container Instances, etc.

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
- [Push and pull container images](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-get-started-docker-cli)
- [Delete container images in Azure Container Registry](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-delete)
- [ACR CLI reference](https://learn.microsoft.com/en-us/cli/azure/acr)
- [Azure Container Registry best practices](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-best-practices)
- [Retention policy for untagged manifests](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-retention-policy)

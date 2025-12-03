# Azure Container Apps - Deployment Methods

## Table of Contents

- [Overview](#overview)
- [Deployment Methods](#deployment-methods)
  - [1. Deploy from Source Code](#1-deploy-from-source-code)
  - [2. Deploy from Pre-built Container Image](#2-deploy-from-pre-built-container-image)
  - [3. Deploy from Azure Container Registry (ACR)](#3-deploy-from-azure-container-registry-acr)
  - [4. Deploy from Docker Hub or Other Registries](#4-deploy-from-docker-hub-or-other-registries)
  - [5. Deploy with GitHub Actions](#5-deploy-with-github-actions)
  - [6. Deploy with Azure DevOps](#6-deploy-with-azure-devops)
  - [7. Deploy with Azure CLI (Complete Workflow)](#7-deploy-with-azure-cli-complete-workflow)
  - [8. Deploy with ARM/Bicep Templates](#8-deploy-with-armbicep-templates)
  - [9. Continuous Deployment with Webhooks](#9-continuous-deployment-with-webhooks)
- [Revision Management](#revision-management)
- [Environment Management](#environment-management)
- [Practice Question](#practice-question)
- [Key Takeaways](#key-takeaways)
- [Additional Resources](#additional-resources)
- [Related Topics](#related-topics)


## Overview

Azure Container Apps (ACA) provides multiple deployment methods to suit different development workflows and CI/CD scenarios. You can deploy from source code, pre-built container images, container registries, or use automated pipelines. This guide covers all deployment methods comprehensively.

## Deployment Methods

### 1. Deploy from Source Code

The `az containerapp up` command is the simplest way to build and deploy directly from source code with a Dockerfile.

**What it does:**
1. Builds the container image from the Dockerfile
2. Creates/uses Azure Container Registry (ACR) to store the image
3. Creates Container Apps environment (if needed)
4. Creates or updates the container app
5. Deploys the application

**Command:**
```bash
az containerapp up \
  --name my-container-app \
  --resource-group myResourceGroup \
  --location eastus \
  --environment my-environment \
  --source .
```

**With additional parameters:**
```bash
az containerapp up \
  --name my-container-app \
  --resource-group myResourceGroup \
  --location eastus \
  --environment my-environment \
  --source . \
  --ingress external \
  --target-port 80 \
  --cpu 0.5 \
  --memory 1.0Gi
```

**Benefits:**
- ✅ All-in-one command for quick deployments
- ✅ Automatically creates required resources
- ✅ Ideal for development and testing
- ✅ No need to manage container registry separately

### 2. Deploy from Pre-built Container Image

Deploy from an existing container image stored in any container registry.

**Command:**
```bash
az containerapp create \
  --name my-container-app \
  --resource-group myResourceGroup \
  --environment my-environment \
  --image mcr.microsoft.com/azuredocs/containerapps-helloworld:latest \
  --target-port 80 \
  --ingress external \
  --cpu 0.5 \
  --memory 1.0Gi \
  --min-replicas 0 \
  --max-replicas 10
```

**Update existing app with new image:**
```bash
az containerapp update \
  --name my-container-app \
  --resource-group myResourceGroup \
  --image myregistry.azurecr.io/myapp:v2.0
```

**Benefits:**
- ✅ Use pre-built images from any registry
- ✅ Fast deployment (no build step)
- ✅ Better for production environments
- ✅ Version control through image tags

### 3. Deploy from Azure Container Registry (ACR)

Deploy images stored in Azure Container Registry with integrated authentication.

**Step 1: Build and push to ACR**
```bash
# Login to ACR
az acr login --name myregistry

# Build and push image to ACR
az acr build \
  --registry myregistry \
  --image myapp:v1.0 \
  --file Dockerfile \
  .
```

**Step 2: Deploy to Container Apps**
```bash
# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name myregistry --query loginServer -o tsv)

# Create container app with ACR image
az containerapp create \
  --name my-container-app \
  --resource-group myResourceGroup \
  --environment my-environment \
  --image $ACR_LOGIN_SERVER/myapp:v1.0 \
  --registry-server $ACR_LOGIN_SERVER \
  --target-port 80 \
  --ingress external
```

**Using Managed Identity (Recommended for Production):**
```bash
# Enable system-assigned managed identity
az containerapp identity assign \
  --name my-container-app \
  --resource-group myResourceGroup \
  --system-assigned

# Grant ACR pull permissions to the identity
az role assignment create \
  --assignee <managed-identity-principal-id> \
  --role AcrPull \
  --scope /subscriptions/<subscription-id>/resourceGroups/<rg>/providers/Microsoft.ContainerRegistry/registries/myregistry
```

**Using Admin Credentials:**
```bash
# Enable admin user on ACR
az acr update --name myregistry --admin-enabled true

# Get credentials
ACR_USERNAME=$(az acr credential show --name myregistry --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name myregistry --query passwords[0].value -o tsv)

# Deploy with credentials
az containerapp create \
  --name my-container-app \
  --resource-group myResourceGroup \
  --environment my-environment \
  --image myregistry.azurecr.io/myapp:v1.0 \
  --registry-server myregistry.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 80 \
  --ingress external
```

**Benefits:**
- ✅ Seamless integration with Azure
- ✅ Managed identity support
- ✅ Private image hosting
- ✅ Geo-replication support

### 4. Deploy from Docker Hub or Other Registries

Deploy from public or private Docker Hub repositories or other container registries.

**From Docker Hub (Public Image):**
```bash
az containerapp create \
  --name my-container-app \
  --resource-group myResourceGroup \
  --environment my-environment \
  --image docker.io/nginx:latest \
  --target-port 80 \
  --ingress external
```

**From Docker Hub (Private Image):**
```bash
az containerapp create \
  --name my-container-app \
  --resource-group myResourceGroup \
  --environment my-environment \
  --image docker.io/mycompany/myapp:v1.0 \
  --registry-server docker.io \
  --registry-username myusername \
  --registry-password mypassword \
  --target-port 80 \
  --ingress external
```

**From Other Private Registry:**
```bash
az containerapp create \
  --name my-container-app \
  --resource-group myResourceGroup \
  --environment my-environment \
  --image myregistry.example.com/myapp:v1.0 \
  --registry-server myregistry.example.com \
  --registry-username myusername \
  --registry-password mypassword \
  --target-port 80 \
  --ingress external
```

**Benefits:**
- ✅ Use existing Docker Hub images
- ✅ Support for any OCI-compliant registry
- ✅ Flexibility in image hosting

### 5. Deploy with GitHub Actions

Automate deployments using GitHub Actions workflows.

**GitHub Actions Workflow (.github/workflows/deploy.yml):**
```yaml
name: Deploy to Azure Container Apps

on:
  push:
    branches: [ main ]
  workflow_dispatch:

env:
  AZURE_CONTAINER_APP_NAME: my-container-app
  AZURE_RESOURCE_GROUP: myResourceGroup
  AZURE_CONTAINER_REGISTRY: myregistry

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Login to Azure
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}

    - name: Build and push image to ACR
      uses: azure/docker-login@v1
      with:
        login-server: ${{ env.AZURE_CONTAINER_REGISTRY }}.azurecr.io
        username: ${{ secrets.ACR_USERNAME }}
        password: ${{ secrets.ACR_PASSWORD }}
    
    - run: |
        docker build . -t ${{ env.AZURE_CONTAINER_REGISTRY }}.azurecr.io/${{ env.AZURE_CONTAINER_APP_NAME }}:${{ github.sha }}
        docker push ${{ env.AZURE_CONTAINER_REGISTRY }}.azurecr.io/${{ env.AZURE_CONTAINER_APP_NAME }}:${{ github.sha }}

    - name: Deploy to Container Apps
      uses: azure/container-apps-deploy-action@v1
      with:
        containerAppName: ${{ env.AZURE_CONTAINER_APP_NAME }}
        resourceGroup: ${{ env.AZURE_RESOURCE_GROUP }}
        imageToDeploy: ${{ env.AZURE_CONTAINER_REGISTRY }}.azurecr.io/${{ env.AZURE_CONTAINER_APP_NAME }}:${{ github.sha }}
```

**Alternative: Using az containerapp up:**
```yaml
    - name: Deploy with az containerapp up
      run: |
        az containerapp up \
          --name ${{ env.AZURE_CONTAINER_APP_NAME }} \
          --resource-group ${{ env.AZURE_RESOURCE_GROUP }} \
          --source .
```

**Benefits:**
- ✅ Automated CI/CD pipeline
- ✅ Version control integration
- ✅ Easy rollback with Git history
- ✅ Automated testing before deployment

### 6. Deploy with Azure DevOps

Create CI/CD pipelines using Azure DevOps.

**Azure Pipeline (azure-pipelines.yml):**
```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  containerRegistry: 'myregistry.azurecr.io'
  imageName: 'myapp'
  resourceGroup: 'myResourceGroup'
  containerAppName: 'my-container-app'
  azureSubscription: 'MyAzureConnection'

stages:
- stage: Build
  displayName: 'Build and Push'
  jobs:
  - job: Build
    displayName: 'Build Docker Image'
    steps:
    - task: Docker@2
      displayName: 'Build and Push Image'
      inputs:
        command: buildAndPush
        repository: $(imageName)
        containerRegistry: $(azureSubscription)
        tags: |
          $(Build.BuildId)
          latest

- stage: Deploy
  displayName: 'Deploy to Container Apps'
  dependsOn: Build
  jobs:
  - deployment: Deploy
    displayName: 'Deploy Container App'
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureCLI@2
            displayName: 'Deploy to Azure Container Apps'
            inputs:
              azureSubscription: $(azureSubscription)
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                az containerapp update \
                  --name $(containerAppName) \
                  --resource-group $(resourceGroup) \
                  --image $(containerRegistry)/$(imageName):$(Build.BuildId)
```

**Benefits:**
- ✅ Enterprise-grade CI/CD
- ✅ Integration with Azure services
- ✅ Advanced deployment strategies
- ✅ Approval gates and environments

### 7. Deploy with Azure CLI (Complete Workflow)

Complete deployment workflow using Azure CLI.

**Step 1: Create Environment**
```bash
# Create resource group
az group create \
  --name myResourceGroup \
  --location eastus

# Create Log Analytics workspace (optional but recommended)
az monitor log-analytics workspace create \
  --resource-group myResourceGroup \
  --workspace-name myLogAnalytics \
  --location eastus

# Get workspace ID and key
LOG_ANALYTICS_WORKSPACE_ID=$(az monitor log-analytics workspace show \
  --resource-group myResourceGroup \
  --workspace-name myLogAnalytics \
  --query customerId -o tsv)

LOG_ANALYTICS_WORKSPACE_KEY=$(az monitor log-analytics workspace get-shared-keys \
  --resource-group myResourceGroup \
  --workspace-name myLogAnalytics \
  --query primarySharedKey -o tsv)

# Create Container Apps environment
az containerapp env create \
  --name my-environment \
  --resource-group myResourceGroup \
  --location eastus \
  --logs-workspace-id $LOG_ANALYTICS_WORKSPACE_ID \
  --logs-workspace-key $LOG_ANALYTICS_WORKSPACE_KEY
```

**Step 2: Create Container App**
```bash
az containerapp create \
  --name my-container-app \
  --resource-group myResourceGroup \
  --environment my-environment \
  --image myregistry.azurecr.io/myapp:v1.0 \
  --registry-server myregistry.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --target-port 80 \
  --ingress external \
  --cpu 0.5 \
  --memory 1.0Gi \
  --min-replicas 1 \
  --max-replicas 10 \
  --env-vars "API_KEY=secretref:apikey" "ENV=production" \
  --secrets "apikey=myapikey123"
```

**Step 3: Configure Scaling Rules**
```bash
# HTTP-based scaling
az containerapp update \
  --name my-container-app \
  --resource-group myResourceGroup \
  --scale-rule-name http-rule \
  --scale-rule-type http \
  --scale-rule-http-concurrency 50

# Custom scaling (e.g., Azure Storage Queue)
az containerapp update \
  --name my-container-app \
  --resource-group myResourceGroup \
  --scale-rule-name queue-rule \
  --scale-rule-type azure-queue \
  --scale-rule-metadata "queueName=myqueue" "queueLength=10" \
  --scale-rule-auth "connection=connection-string-secret"
```

**Benefits:**
- ✅ Full control over configuration
- ✅ Scriptable and automatable
- ✅ Detailed resource management
- ✅ Ideal for scripting and automation

### 8. Deploy with ARM/Bicep Templates

Use Infrastructure as Code (IaC) for declarative deployments.

**Bicep Template (main.bicep):**
```bicep
param location string = resourceGroup().location
param environmentName string
param containerAppName string
param containerImage string

resource environment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: environmentName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
    }
  }
}

resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: containerAppName
  location: location
  properties: {
    managedEnvironmentId: environment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 80
        allowInsecure: false
      }
      registries: [
        {
          server: 'myregistry.azurecr.io'
          username: 'myregistry'
          passwordSecretRef: 'registry-password'
        }
      ]
      secrets: [
        {
          name: 'registry-password'
          value: 'password-value'
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'main'
          image: containerImage
          resources: {
            cpu: json('0.5')
            memory: '1.0Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 10
        rules: [
          {
            name: 'http-rule'
            http: {
              metadata: {
                concurrentRequests: '50'
              }
            }
          }
        ]
      }
    }
  }
}

output fqdn string = containerApp.properties.configuration.ingress.fqdn
```

**Deploy:**
```bash
az deployment group create \
  --resource-group myResourceGroup \
  --template-file main.bicep \
  --parameters environmentName=my-environment \
               containerAppName=my-container-app \
               containerImage=myregistry.azurecr.io/myapp:v1.0
```

**Benefits:**
- ✅ Version-controlled infrastructure
- ✅ Repeatable deployments
- ✅ Multi-environment support
- ✅ Declarative configuration

### 9. Continuous Deployment with Webhooks

Enable automatic deployments when container images are updated.

**Enable Continuous Deployment:**
```bash
# For ACR with webhooks
az containerapp registry set \
  --name my-container-app \
  --resource-group myResourceGroup \
  --server myregistry.azurecr.io \
  --username <username> \
  --password <password>

# Create ACR webhook
az acr webhook create \
  --registry myregistry \
  --name mywebhook \
  --actions push \
  --uri <container-app-webhook-url>
```

**Benefits:**
- ✅ Automatic updates on image push
- ✅ Zero-downtime deployments
- ✅ Fast deployment cycles
- ✅ Reduced manual intervention

## Revision Management

Container Apps uses revisions to manage application versions.

**List Revisions:**
```bash
az containerapp revision list \
  --name my-container-app \
  --resource-group myResourceGroup \
  -o table
```

**Activate a Specific Revision:**
```bash
az containerapp revision activate \
  --name my-container-app \
  --resource-group myResourceGroup \
  --revision <revision-name>
```

**Deactivate a Revision:**
```bash
az containerapp revision deactivate \
  --name my-container-app \
  --resource-group myResourceGroup \
  --revision <revision-name>
```

**Traffic Splitting Between Revisions:**
```bash
az containerapp ingress traffic set \
  --name my-container-app \
  --resource-group myResourceGroup \
  --revision-weight latest=80 <old-revision>=20
```

**Copy Revision:**
```bash
az containerapp revision copy \
  --name my-container-app \
  --resource-group myResourceGroup \
  --from-revision <source-revision>
```

## Environment Management

**Create Environment with Custom VNET:**
```bash
az containerapp env create \
  --name my-environment \
  --resource-group myResourceGroup \
  --location eastus \
  --infrastructure-subnet-resource-id <subnet-id> \
  --internal-only false
```

**List Environments:**
```bash
az containerapp env list \
  --resource-group myResourceGroup \
  -o table
```

**Show Environment Details:**
```bash
az containerapp env show \
  --name my-environment \
  --resource-group myResourceGroup
```

**Delete Environment:**
```bash
az containerapp env delete \
  --name my-environment \
  --resource-group myResourceGroup \
  --yes
```

## Practice Question

**Scenario:**
Your company is developing an application that includes a backend web API service. The development team has decided to use Azure Container Apps to host the API. They have a Dockerfile in the root of their repository that defines the containerized app.

**Question:**
You need to deploy the container app using the Dockerfile. What should you do?

**Options:**

1. ❌ Use the `az containerapp env create` command with the `--name` parameter.
   - **Incorrect**: This command only creates the Container Apps environment, not the actual container app.

2. ❌ Use the `az containerapp create` command with the `--image` parameter.
   - **Incorrect**: This requires a pre-built container image. It doesn't build from a Dockerfile.

3. ❌ Use the `az containerapp create` command with the `--containername` parameter.
   - **Incorrect**: This parameter doesn't exist for this command and doesn't fulfill the requirement.

4. ✅ Use the `az containerapp up` command with the `--source .` parameter.
   - **Correct**: This command builds and deploys the container app using the Dockerfile in the root of the repository.

## Key Takeaways

### Deployment Methods Summary

| Method | Use Case | Complexity | Automation |
|--------|----------|------------|------------|
| **az containerapp up** | Quick deployments from source | Low | Manual |
| **Pre-built images** | Production deployments | Low | Manual/Automated |
| **ACR integration** | Azure-native workflows | Medium | Automated |
| **GitHub Actions** | CI/CD with GitHub | Medium | Fully Automated |
| **Azure DevOps** | Enterprise CI/CD | Medium | Fully Automated |
| **ARM/Bicep** | Infrastructure as Code | High | Automated |
| **Webhooks** | Continuous deployment | Medium | Fully Automated |

### Best Practices

1. **Development**: Use `az containerapp up` for rapid iteration
2. **Production**: Use CI/CD pipelines with ACR and managed identities
3. **Multi-environment**: Use ARM/Bicep templates for consistent deployments
4. **Security**: Always use managed identities over credentials when possible
5. **Versioning**: Use image tags and revisions for version control
6. **Monitoring**: Enable Log Analytics for observability
7. **Scaling**: Configure appropriate min/max replicas and scaling rules
8. **Traffic Management**: Use revision-based traffic splitting for blue-green deployments

### Quick Command Reference

```bash
# Quick deploy from source
az containerapp up --source . --name myapp --resource-group rg --environment env

# Update with new image
az containerapp update --name myapp --resource-group rg --image registry.io/image:tag

# Manage revisions
az containerapp revision list --name myapp --resource-group rg

# Traffic splitting
az containerapp ingress traffic set --name myapp --resource-group rg --revision-weight latest=80 old=20

# Scale configuration
az containerapp update --name myapp --resource-group rg --min-replicas 0 --max-replicas 10
```

## Additional Resources

- [Quickstart: Build and deploy from local source code to Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/quickstart-code-to-cloud)
- [Azure Container Apps Documentation](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Deploy with GitHub Actions](https://learn.microsoft.com/en-us/azure/container-apps/github-actions)
- [Azure Container Apps with Azure DevOps](https://learn.microsoft.com/en-us/azure/container-apps/azure-pipelines)
- [Revisions in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/revisions)
- [Blue-Green Deployment with Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/blue-green-deployment)

## Related Topics

- [Azure Container Apps Pricing](./aca-pricing.md)
- [Azure Container Apps Overview](./azure-container-apps-overview.md)
- [Azure Container Registry (ACR) Integration](../../azure_container_registry/azure-container-registry-acr.md)
- Container Apps environments and networking
- Dockerfile best practices
- CI/CD pipeline patterns
- Managed identities and security
- Scaling and performance optimization

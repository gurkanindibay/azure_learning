# Azure Static Web Apps

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Deployment Methods](#deployment-methods)
  - [GitHub/GitLab Integration](#githubgitlab-integration)
  - [Azure DevOps](#azure-devops)
  - [CLI Deployment](#cli-deployment)
- [The .deployment File](#the-deployment-file)
  - [Purpose and Usage](#purpose-and-usage)
  - [File Structure](#file-structure)
  - [Common Scenarios](#common-scenarios)
  - [Examples](#examples)
- [Build Configuration](#build-configuration)
  - [build.json](#buildjson)
  - [Framework-Specific Configuration](#framework-specific-configuration)
- [Custom Deployment Scripts](#custom-deployment-scripts)
  - [Pre-deployment Tasks](#pre-deployment-tasks)
  - [Post-deployment Tasks](#post-deployment-tasks)
- [Static Content Generation](#static-content-generation)
  - [Supported Frameworks](#supported-frameworks)
  - [Custom Build Commands](#custom-build-commands)
- [Environment Variables](#environment-variables)
- [Deployment Slots](#deployment-slots)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

Azure Static Web Apps is a service that automatically builds and deploys full stack web apps to Azure from a code repository. It provides a streamlined developer experience with features like:

- **Global distribution** with CDN
- **Serverless API backends** with Azure Functions
- **Integrated authentication** and authorization
- **Custom domains** and SSL certificates
- **Staging environments** with deployment slots

## Key Features

| Feature | Description |
|---------|-------------|
| **Global CDN** | Content served from edge locations worldwide |
| **Serverless APIs** | Azure Functions integration for backend logic |
| **Authentication** | Built-in auth with providers (GitHub, Twitter, etc.) |
| **Custom Domains** | Free SSL certificates and custom domain support |
| **Deployment Slots** | Preview deployments and staging environments |
| **Git Integration** | Automatic builds on commits to configured branches |

## Deployment Methods

### GitHub/GitLab Integration

Azure Static Web Apps integrates directly with GitHub and GitLab repositories for continuous deployment.

**Setup Process:**
1. Connect your repository in the Azure portal
2. Configure build settings (build command, output location, API location)
3. Push changes to trigger automatic deployments

**Benefits:**
- Automatic builds on every commit
- Preview deployments for pull requests
- Rollback capabilities
- Build logs and deployment history

### Azure DevOps

For organizations using Azure DevOps, you can set up CI/CD pipelines that deploy to Static Web Apps.

**Pipeline Configuration:**
```yaml
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: AzureStaticWebApp@0
  inputs:
    app_location: '/'
    api_location: 'api'
    output_location: 'dist'
    azure_static_web_apps_api_token: $(deployment_token)
```

### CLI Deployment

You can deploy static content using the Azure CLI or Azure Static Web Apps CLI.

**Azure CLI:**
```bash
az staticwebapp appsettings set --name MyStaticApp --setting-names "key=value"
az staticwebapp hostname set --name MyStaticApp --domain-name www.example.com
```

**SWA CLI:**
```bash
swa deploy --app-location ./dist --api-location ./api --output-location ./dist
```

## The .deployment File

### Purpose and Usage

The `.deployment` file is a configuration file that allows you to customize the deployment process for Azure Static Web Apps. It provides control over the build and deployment steps, enabling you to run custom scripts, set environment variables, and perform pre/post-deployment tasks.

**When to Use:**
- Running custom build scripts
- Installing additional dependencies
- Performing database migrations
- Setting up environment-specific configurations
- Running tests before deployment

### File Structure

The `.deployment` file uses a simple INI-style format:

```ini
[config]
command = deploy.sh

[environment]
NODE_ENV = production
BUILD_ENV = staging
```

**Sections:**
- `[config]`: Deployment configuration
- `[environment]`: Environment variables for the deployment process

### Common Scenarios

| Scenario | Use Case | Example |
|----------|----------|---------|
| **Static Site Generation** | Generate content before deployment | Hugo, Jekyll, Gatsby builds |
| **Asset Optimization** | Minify CSS/JS, compress images | Webpack, Parcel builds |
| **API Deployment** | Deploy backend APIs alongside frontend | Azure Functions deployment |
| **Environment Setup** | Configure staging/production settings | Database connections, API keys |
| **Testing** | Run tests before deployment | Unit tests, integration tests |

### Examples

**Basic Static Site Generation:**
```bash
#!/bin/bash
# deploy.sh

# Install dependencies
npm install

# Generate static content
npm run build

# Deploy (handled automatically by Azure)
echo "Static content generated successfully"
```

**Hugo Site Deployment:**
```bash
#!/bin/bash
# deploy.sh

# Install Hugo if not available
if ! command -v hugo &> /dev/null; then
    echo "Installing Hugo..."
    # Download and install Hugo
fi

# Build the site
hugo --minify

echo "Hugo site built successfully"
```

**With Environment Variables:**
```ini
[config]
command = deploy.sh

[environment]
HUGO_ENV = production
API_URL = https://api.example.com
DATABASE_URL = ${DATABASE_CONNECTION_STRING}
```

## Build Configuration

### build.json

The `build.json` file provides additional configuration for the build process:

```json
{
  "buildCommand": "npm run build",
  "installCommand": "npm install",
  "outputLocation": "dist",
  "apiLocation": "api",
  "appBuildCommand": "npm run build-app",
  "apiBuildCommand": "npm run build-api"
}
```

**Configuration Options:**
- `buildCommand`: Command to build the application
- `installCommand`: Command to install dependencies
- `outputLocation`: Directory containing built static files
- `apiLocation`: Directory containing API functions
- `appBuildCommand`: Alternative build command for the app
- `apiBuildCommand`: Build command for API functions

### Framework-Specific Configuration

| Framework | build.json Example |
|-----------|-------------------|
| **React** | `{"buildCommand": "npm run build", "outputLocation": "build"}` |
| **Vue.js** | `{"buildCommand": "npm run build", "outputLocation": "dist"}` |
| **Angular** | `{"buildCommand": "ng build --prod", "outputLocation": "dist"}` |
| **Hugo** | `{"buildCommand": "hugo --minify", "outputLocation": "public"}` |
| **Jekyll** | `{"buildCommand": "jekyll build", "outputLocation": "_site"}` |

## Custom Deployment Scripts

### Pre-deployment Tasks

Pre-deployment scripts run before the main build process:

```bash
#!/bin/bash
# pre-deploy.sh

echo "Starting pre-deployment tasks..."

# Install global dependencies
npm install -g @azure/static-web-apps-cli

# Run linting
npm run lint

# Run unit tests
npm run test:unit

# Check code quality
npm run code-quality

echo "Pre-deployment tasks completed"
```

### Post-deployment Tasks

Post-deployment scripts run after successful deployment:

```bash
#!/bin/bash
# post-deploy.sh

echo "Starting post-deployment tasks..."

# Warm up the application
curl -s https://myapp.azurestaticapps.net > /dev/null

# Run integration tests
npm run test:integration

# Send deployment notification
curl -X POST https://api.example.com/notifications \
  -H "Content-Type: application/json" \
  -d '{"message": "Deployment completed successfully"}'

# Update CDN cache
az cdn endpoint purge --resource-group myRG --name myCDN --profile-name myProfile --content-paths "/*"

echo "Post-deployment tasks completed"
```

## Static Content Generation

### Supported Frameworks

Azure Static Web Apps has built-in support for popular static site generators:

| Framework | Language | Build Command | Output Directory |
|-----------|----------|---------------|------------------|
| **Hugo** | Go | `hugo` | `public` |
| **Jekyll** | Ruby | `jekyll build` | `_site` |
| **Gatsby** | JavaScript | `npm run build` | `public` |
| **Next.js (Static)** | JavaScript | `npm run export` | `out` |
| **Nuxt.js (Static)** | JavaScript | `npm run generate` | `dist` |
| **VuePress** | JavaScript | `npm run build` | `.vuepress/dist` |
| **Hexo** | JavaScript | `hexo generate` | `public` |
| **Pelican** | Python | `pelican content` | `output` |

### Custom Build Commands

For frameworks not natively supported, use custom build commands:

```json
{
  "buildCommand": "python build.py",
  "installCommand": "pip install -r requirements.txt",
  "outputLocation": "build"
}
```

**Custom Build Script Example:**
```python
#!/usr/bin/env python3
# build.py

import os
import shutil
import subprocess

def build_site():
    # Install dependencies
    subprocess.run(['pip', 'install', '-r', 'requirements.txt'])

    # Generate static content
    subprocess.run(['python', 'generate_content.py'])

    # Build CSS/JS assets
    subprocess.run(['npm', 'run', 'build-assets'])

    # Copy files to output directory
    if os.path.exists('build'):
        shutil.rmtree('build')
    shutil.copytree('src', 'build')

    print("Site built successfully!")

if __name__ == '__main__':
    build_site()
```

## Environment Variables

Environment variables can be set at different levels:

**Application Settings (Portal):**
- Available to both frontend and API
- Can be slot-specific
- Encrypted at rest

**Build-time Variables:**
```bash
# In .deployment file
[environment]
API_BASE_URL = https://api.example.com
CONTENTFUL_SPACE_ID = ${CONTENTFUL_SPACE_ID}
BUILD_ENV = production
```

**Runtime Variables:**
- Set in Azure portal under "Configuration"
- Available to API functions
- Not exposed to client-side code

## Deployment Slots

Azure Static Web Apps supports deployment slots for staging and testing:

**Types of Slots:**
- **Production**: Main production environment
- **Staging**: Auto-created for pull requests
- **Custom Slots**: Manually created for testing

**Slot Management:**
```bash
# List slots
az staticwebapp environment list --name MyApp

# Create custom slot
az staticwebapp environment create --name MyApp --environment-name staging

# Swap slots
az staticwebapp environment swap --name MyApp --environment-name staging
```

## Best Practices

### Deployment Configuration

1. **Use .deployment file** for complex build processes
2. **Leverage build.json** for standard configurations
3. **Test deployments locally** before pushing to repository
4. **Use environment variables** for configuration management
5. **Implement proper error handling** in deployment scripts

### Security Considerations

1. **Store secrets securely** using Azure Key Vault
2. **Use managed identities** for Azure resource access
3. **Implement proper authentication** for API endpoints
4. **Regularly update dependencies** and frameworks
5. **Monitor deployment logs** for security issues

### Performance Optimization

1. **Enable compression** for static assets
2. **Use CDN effectively** with proper cache headers
3. **Optimize images and assets** during build
4. **Implement lazy loading** for large resources
5. **Monitor performance metrics** post-deployment

## Troubleshooting

### Common Issues

**Build Failures:**
- Check build logs in Azure portal
- Verify build commands and paths
- Ensure all dependencies are properly installed
- Check for platform-specific issues

**Deployment Timeouts:**
- Reduce build output size
- Optimize build scripts for speed
- Use incremental builds when possible
- Check for network connectivity issues

**Runtime Issues:**
- Verify environment variables are set correctly
- Check API function logs
- Validate routing configuration
- Test authentication and authorization

### Debugging Tools

**Azure Portal:**
- Deployment logs
- Application logs
- Metrics and monitoring

**CLI Tools:**
```bash
# Check deployment status
az staticwebapp environment list --name MyApp

# View build logs
az staticwebapp logs --name MyApp --environment-name production

# Test locally
swa start --app-location ./dist --api-location ./api
```

**Local Development:**
```bash
# Install SWA CLI
npm install -g @azure/static-web-apps-cli

# Start local development server
swa start ./dist --api ./api
```

This comprehensive guide covers the deployment of static web apps and the usage of .deployment files in Azure Static Web Apps, providing developers with the knowledge needed to effectively deploy and manage their static web applications.
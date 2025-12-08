# Azure App Service - Deployment Strategies

## Table of Contents

- [Overview](#overview)
- [Deployment Methods](#deployment-methods)
  - [ZIP Package Deployment](#zip-package-deployment)
- [Deployment Slots and Auto Swap](#deployment-slots-and-auto-swap)
  - [Benefits of Deployment Slots with Auto Swap](#benefits-of-deployment-slots-with-auto-swap)
  - [Auto Swap Configuration](#auto-swap-configuration)
- [Practice Questions](#practice-questions)
  - [Question 1: Deploying with Reduced File Locking](#question-1-deploying-with-reduced-file-locking)
  - [Question 2: Slot-Specific Settings (Sticky Settings)](#question-2-slot-specific-settings-sticky-settings)
  - [Question 3: Azure Functions Blue-Green Deployment with Sticky Settings](#question-3-azure-functions-blue-green-deployment-with-sticky-settings)
  - [Question 4: Configuring CORS for External Requests](#question-4-configuring-cors-for-external-requests)
  - [Question 5: Session Affinity in Multi-Instance Deployments](#question-5-session-affinity-in-multi-instance-deployments)
  - [Question 6: Enabling Application Logging](#question-6-enabling-application-logging)
  - [Question 7: Docker Container Automatic Updates](#question-7-docker-container-automatic-updates)
  - [Question 8: Eliminating File Lock Conflicts](#question-8-eliminating-file-lock-conflicts)
  - [Question 9: Temporary Diagnostic Logging Configuration](#question-9-temporary-diagnostic-logging-configuration)
  - [Question 10: Deployment Package Size Limits on Consumption Plan](#question-10-deployment-package-size-limits-on-consumption-plan)
  - [Question 11: Custom Initialization Actions Before Handling Requests](#question-11-custom-initialization-actions-before-handling-requests)
  - [Question 12: Secure Authentication for GitHub Actions Continuous Deployment](#question-12-secure-authentication-for-github-actions-continuous-deployment)
  - [Question 13: Running Static Content Generation Script Before Deployment](#question-13-running-static-content-generation-script-before-deployment)
  - [Question 14: Accessing Real-Time Console Logs for Containerized App](#question-14-accessing-real-time-console-logs-for-containerized-app)
- [Application Logging in Azure App Service](#application-logging-in-azure-app-service)
  - [What is Application Logging?](#what-is-application-logging)
  - [Types of Logs in App Service](#types-of-logs-in-app-service)
  - [Windows vs Linux Logging Availability](#windows-vs-linux-logging-availability)
  - [Enabling Application Logging](#enabling-application-logging)
  - [Logging in Application Code](#logging-in-application-code)
  - [Viewing Application Logs](#viewing-application-logs)
  - [Log Levels](#log-levels)
  - [File System vs Blob Storage](#file-system-vs-blob-storage)
  - [Best Practices for Application Logging](#best-practices-for-application-logging)
  - [Application Insights vs App Service Logs](#application-insights-vs-app-service-logs)
- [Application Request Routing (ARR) Affinity](#application-request-routing-arr-affinity)
  - [What is ARR Affinity?](#what-is-arr-affinity)
  - [When to Use ARR Affinity](#when-to-use-arr-affinity)
  - [Configuring ARR Affinity](#configuring-arr-affinity)
  - [How ARR Affinity Works](#how-arr-affinity-works)
  - [ARR Affinity vs Stateless Design](#arr-affinity-vs-stateless-design)
  - [Platform Settings Overview](#platform-settings-overview)
- [Cross-Origin Resource Sharing (CORS)](#cross-origin-resource-sharing-cors)
  - [What is CORS?](#what-is-cors)
  - [When to Configure CORS](#when-to-configure-cors)
  - [Configuring CORS with Azure CLI](#configuring-cors-with-azure-cli)
  - [CORS vs Access Restrictions](#cors-vs-access-restrictions)
- [Deployment Slot Settings (Sticky Settings)](#deployment-slot-settings-sticky-settings)
  - [What Are Slot Settings?](#what-are-slot-settings)
  - [When to Use Slot Settings](#when-to-use-slot-settings)
  - [How to Configure Slot Settings](#how-to-configure-slot-settings)
  - [Swap Behavior Example](#swap-behavior-example)
- [Key Concepts](#key-concepts)
  - [File Locking During Deployment](#file-locking-during-deployment)
  - [Why Staging Slots Solve File Locking](#why-staging-slots-solve-file-locking)
  - [Deployment Slot Swap Process](#deployment-slot-swap-process)
- [Best Practices](#best-practices)
- [Common Azure CLI Commands for App Service](#common-azure-cli-commands-for-app-service)
  - [Deployment Commands](#deployment-commands)
  - [Configuration Commands](#configuration-commands)
  - [Identity and Routing Commands](#identity-and-routing-commands)
  - [Parameters for `az webapp deploy`](#parameters-for-az-webapp-deploy)
- [Example Deployment Workflow](#example-deployment-workflow)
- [Kudu REST API](#kudu-rest-api)
  - [What is Kudu?](#what-is-kudu)
  - [Common Kudu REST API Endpoints](#common-kudu-rest-api-endpoints)
  - [ZIP API for Deployments](#zip-api-for-deployments)
  - [Practice Question: Kudu ZIP API](#practice-question-kudu-zip-api)
- [WebJobs for Background Processing](#webjobs-for-background-processing)
  - [What are WebJobs?](#what-are-webjobs)
  - [Types of WebJobs](#types-of-webjobs)
  - [WebJobs vs Other Background Processing Options](#webjobs-vs-other-background-processing-options)
  - [Key Requirements for Continuous WebJobs](#key-requirements-for-continuous-webjobs)
  - [WebJobs Features](#webjobs-features)
  - [Creating a Continuous WebJob](#creating-a-continuous-webjob)
  - [Practice Question: Background Processing for App Service](#practice-question-background-processing-for-app-service)
- [Additional Resources](#additional-resources)
- [Related Topics](#related-topics)

## Overview

Azure App Service provides multiple deployment methods and strategies to ensure smooth, reliable deployments of web applications. Understanding the right deployment approach is crucial for avoiding common issues like file locking during deployment.

## Deployment Methods

### ZIP Package Deployment

ZIP deployment is a common method for deploying web apps to Azure App Service. You can use the Azure CLI command `az webapp deploy` to deploy a ZIP package containing your application.

**Basic Command:**
```bash
az webapp deploy --resource-group <group-name> --name <app-name> --src-path <path-to-zip>
```

## Deployment Slots and Auto Swap

Deployment slots are separate instances of your web app with their own hostnames. They provide a powerful way to deploy and test changes before making them live.

### Benefits of Deployment Slots with Auto Swap

- **Eliminates downtime**: The app is warmed up in the staging slot before being swapped to production
- **Reduces file locking issues**: Files are not overwritten in the production slot during deployment
- **Enables validation**: Test your app in staging before it goes live
- **Easy rollback**: Swap back to the previous version if issues occur

### Auto Swap Configuration

When auto swap is enabled on a staging slot, Azure automatically swaps the staging slot to production after a successful deployment and warm-up.

```bash
# Deploy to staging slot with auto swap enabled
az webapp deploy --resource-group <group-name> \
  --name <app-name> \
  --slot <slot-name> \
  --src-path <path-to-zip>
```

## Practice Questions

### Question 1: Deploying with Reduced File Locking

**Scenario:**
You create an Azure web app locally. The web app consists of a ZIP package. You need to deploy the web app using the Azure CLI. The deployment must reduce the likelihood of locked files.

**Question:**
What should you do?

**Options:**

1. ❌ Run `az webapp deploy` specifying `--clean true`.
   - **Incorrect**: The `--clean true` parameter cleans the target folder before deployment, but this has no effect on reducing the likelihood of locked files. It simply removes existing files in the target directory.

2. ❌ Run `az webapp deploy` specifying `--restart true`.
   - **Incorrect**: While restarting the app after deployment is a good practice, it is already the default behavior for ZIP deployments. This parameter does not reduce the likelihood of locked files **during** the deployment process.

3. ✅ Run `az webapp deploy` to a staging slot with auto swap on.
   - **Correct**: Using a staging slot with auto swap enabled is the best approach to reduce file locking issues. The deployment happens to a separate slot (staging), eliminating the risk of locked files in production. After the deployment completes and the app warms up, Azure automatically swaps the staging slot to production.

4. ❌ Run `az webapp deploy` by using a high value for the `--timeout` parameter.
   - **Incorrect**: The `--timeout` parameter only controls how long the CLI waits for the deployment to complete. It has no effect on the likelihood of locked files during deployment.

### Question 2: Slot-Specific Settings (Sticky Settings)

**Scenario:**
You manage the staging and production deployment slots of an Azure App Service web app named app1. You need to ensure a connection string is not swapped when swapping is performed.

**Question:**
Which configuration should you use?

**Options:**

1. ❌ Deployment Center
   - **Incorrect**: Deployment Center is used to configure continuous deployment and manual deployment. It cannot be used to control which settings remain with a specific slot during a swap operation.

2. ✅ Deployment slot setting
   - **Correct**: Marking a setting as a "deployment slot setting" (also known as a "sticky setting") keeps it associated with that specific deployment slot. For example, a connection string marked as a deployment slot setting on the production slot will always stick with production and will never move to the staging slot during a swap. This ensures environment-specific configurations remain with their respective slots.

3. ❌ Managed identity
   - **Incorrect**: Managed identity provides an identity for applications to use when connecting to resources that support Microsoft Entra ID authentication. While useful for secure authentication, it cannot be used to control swap behavior of connection strings.

4. ❌ Scale up
   - **Incorrect**: Scale up controls the web app's service plan tier, providing more CPU, memory, disk space, and features such as dedicated virtual machines, custom domains and certificates, staging slots, and autoscaling. It has no relation to swap behavior or connection string management.

### Question 3: Azure Functions Blue-Green Deployment with Sticky Settings

**Scenario:**
You need to implement a blue-green deployment strategy for an Azure Functions app. The function app uses sticky app settings for environment-specific configurations. Which command should you use to swap the staging slot with production while preserving sticky settings?

**Question:**
Which command should you use?

**Options:**

1. ❌ `az functionapp deployment slot swap --name MyFunctionApp --resource-group MyRG --slot staging --action preview`
   - **Incorrect**: The `--action preview` option applies the target slot's settings to the source slot for testing purposes but **doesn't complete the swap**. This is used for swap validation (also known as "swap with preview"), allowing you to test how the app behaves with production settings before finalizing the swap. It's not used for the actual deployment swap with sticky settings.

2. ✅ `az functionapp deployment slot swap --name MyFunctionApp --resource-group MyRG --slot staging --target-slot production`
   - **Correct**: This command performs a standard slot swap which correctly handles sticky settings by keeping them in their respective slots. **Sticky settings (deployment slot settings) remain with the slot and are not swapped**, which is the default and desired behavior. The staging slot's app code and non-sticky settings move to production, while each slot retains its own sticky settings.

3. ❌ `az functionapp deployment slot swap --name MyFunctionApp --resource-group MyRG --slot staging --preserve-vnet false`
   - **Incorrect**: The `--preserve-vnet` parameter affects **virtual network configuration preservation** during swap but has no relation to sticky app settings. Sticky settings are handled automatically during a standard swap operation regardless of VNet settings.

4. ❌ `az functionapp deployment slot auto-swap --slot staging --auto-swap-slot production`
   - **Incorrect**: The `auto-swap` command **configures automatic swapping** after deployment completion, not for performing an immediate swap. Auto-swap is used for CI/CD scenarios where you want the swap to happen automatically after a successful deployment to the staging slot, not for manual blue-green deployments.

---

**Key Concepts:**

| Swap Type | Command | Use Case |
|-----------|---------|----------|
| **Standard Swap** | `az functionapp deployment slot swap --slot staging --target-slot production` | Manual blue-green deployment |
| **Swap with Preview** | `az functionapp deployment slot swap --slot staging --action preview` | Test with production settings before swap |
| **Auto-Swap** | `az functionapp deployment slot auto-swap --slot staging --auto-swap-slot production` | CI/CD automatic promotion |

**Sticky Settings Behavior During Swap:**
- Settings marked as **deployment slot settings** (sticky) remain with their slot
- Non-sticky settings move with the application code
- Connection strings and app settings can be individually configured as sticky

---

### Question 4: Configuring CORS for External Requests

**Scenario:**
You need to configure a web app to allow external requests from https://myapps.com.

**Question:**
Which Azure CLI command should you use?

**Options:**

1. ✅ `az webapp cors add -g MyResourceGroup -n MyWebApp --allowed-origins https://myapps.com`
   - **Correct**: This command configures Cross-Origin Resource Sharing (CORS) to allow requests from https://myapps.com. The `az webapp cors add` command is specifically designed to add allowed origins to the web app's CORS policy, enabling the web app to accept requests from the specified external domain.

2. ❌ `az webapp identity add -g MyResourceGroup -n MyWebApp --allowed-origins https://myapps.com`
   - **Incorrect**: The `az webapp identity add` command is used to add a managed identity to a web app for authentication purposes. It does not have an `--allowed-origins` parameter and cannot be used to configure CORS settings.

3. ❌ `az webapp traffic-routing set --distribution myapps=100 --name MyWebApp --resource-group MyResourceGroup`
   - **Incorrect**: The `az webapp traffic-routing set` command is used to configure traffic routing between deployment slots. The `--distribution` parameter specifies the percentage of traffic to route to a deployment slot named "myapps". This has nothing to do with allowing external requests or CORS configuration.

4. ❌ `az webapp config access-restriction add -g MyResourceGroup -n MyWebApp --rule-name external --action Allow --ids myapps --priority 200`
   - **Incorrect**: The `az webapp config access-restriction add` command is used to add IP-based or subnet-based access restrictions to control which sources can access the web app at the network level. It does not configure CORS, which is an application-level security mechanism for cross-origin HTTP requests.

### Question 5: Session Affinity in Multi-Instance Deployments

**Scenario:**
You manage a multi-instance deployment of an Azure App Service web app named app1. You need to ensure a client application is routed to the same instance for the life of the session.

**Question:**
Which platform setting should you use?

**Options:**

1. ❌ WebSocket
   - **Incorrect**: WebSocket is a standardized protocol that provides full-duplex communication channels over a single TCP connection. While useful for real-time bidirectional communication, it does not control instance routing or session affinity.

2. ❌ Always on
   - **Incorrect**: Always on keeps the web app loaded even when there is no traffic, preventing it from being unloaded due to inactivity. This setting improves response time but has no effect on routing clients to the same instance.

3. ❌ HTTP version
   - **Incorrect**: The HTTP version setting (HTTP/1.1 vs HTTP/2) controls which HTTP protocol version is used. In HTTP/2, a persistent connection can be used to service multiple simultaneous requests, but this does not ensure session affinity to a specific instance.

4. ✅ ARR Affinity
   - **Correct**: ARR (Application Request Routing) Affinity ensures that a client application is routed to the same instance for the life of the session in a multi-instance deployment. When enabled, Azure uses a cookie (ARRAffinity) to track which instance served the initial request and routes subsequent requests from the same client to that instance. This is essential for stateful applications that store session data in local memory.

### Question 6: Enabling Application Logging

**Scenario:**
You manage an Azure App Service web app named app1. You need to enable application logging to diagnose issues and monitor application behavior.

**Question:**
Which two actions should you perform? (Choose two)

**Options:**

1. ✅ Enable Application Logging in the App Service logs configuration
   - **Correct**: Application logging must be enabled in the App Service logs configuration. You can enable logging to the file system (short-term, automatically disabled after 12 hours) or to blob storage (long-term). This captures logs written by your application code using the platform's logging framework (ILogger for .NET, console.log for Node.js, etc.).

2. ✅ Add logging code to your application
   - **Correct**: You must instrument your application with logging code to write log messages. For .NET apps, use `ILogger`; for Node.js, use `console.log()`, `console.error()`, or `console.warn()`; for Python, use the `logging` module. Without logging code in your application, no application logs will be generated.

3. ❌ Enable Diagnostic Settings to send logs to Log Analytics
   - **Incorrect**: While Diagnostic Settings can be used to route platform logs (such as HTTP logs and platform diagnostics) to Log Analytics, Azure Monitor, or Storage, this is not required for basic application logging. Application logs can be viewed directly in the file system or blob storage. Diagnostic Settings are optional and used for centralized log management and analysis.

4. ❌ Enable Always On in the General Settings
   - **Incorrect**: Always On keeps the web app loaded and prevents it from being unloaded after idle periods. While useful for ensuring your app remains responsive, it has no relationship to enabling or capturing application logs. Logging works regardless of whether Always On is enabled.

### Question 7: Docker Container Automatic Updates

**Scenario:**
You are deploying a Docker container to Azure App Service. You need to ensure that your app automatically updates when you push changes to your Docker image in a container registry.

**Question:**
Which of the following deployment methods would allow you to automatically update your app when you push changes to your Docker image in a container registry?

**Options:**

1. ❌ Deployment using a ZIP file from local storage
   - **Incorrect**: ZIP file deployment involves manually uploading a ZIP file containing the updated app files to the Azure App Service. This method:
     - Requires manual intervention for each update
     - Does not interact with container registries
     - Is designed for code-based deployments, not Docker containers
     - Has no mechanism to detect changes in Docker images

2. ❌ Manual deployment via Azure CLI
   - **Incorrect**: Manual deployment via Azure CLI requires explicit commands to update the app. While you can use CLI commands to deploy Docker containers, this approach:
     - Requires manual execution of commands for each update
     - Does not provide automatic detection of image changes
     - Is not a "push-based" deployment model
     - Suitable for scripted deployments but not automatic updates

3. ✅ Continuous deployment using Azure DevOps
   - **Correct**: Continuous deployment using Azure DevOps enables automatic updates when changes are pushed to the Docker image in a container registry. This works because:
     - **Pipeline triggers**: Azure DevOps can trigger pipelines when a new image is pushed to Azure Container Registry (ACR) or other registries
     - **Webhooks**: Container registries can send webhooks to trigger deployments
     - **Seamless integration**: Azure DevOps integrates with Azure App Service for automated deployments
     - **CI/CD workflow**: Build → Push Image → Trigger Deployment → Update App Service

   **Alternative Automatic Deployment Options:**
   - **Azure Container Registry webhooks**: Configure webhooks in ACR to trigger App Service updates directly
   - **GitHub Actions**: Similar CI/CD capabilities with automatic deployments
   - **App Service Continuous Deployment**: Enable "Continuous Deployment" in Deployment Center for supported registries

4. ❌ Deployment using Azure Resource Manager (ARM) templates
   - **Incorrect**: ARM templates are Infrastructure as Code (IaC) for deploying Azure resources. While useful, they:
     - Define the desired state of resources declaratively
     - Do not monitor container registries for image changes
     - Require manual execution or pipeline triggers to apply changes
     - Are better suited for provisioning infrastructure, not continuous app updates

---

**Additional Context: Docker Container Deployment Options in App Service**

| Method | Automatic Updates | Use Case |
|--------|-------------------|----------|
| **Continuous Deployment (Azure DevOps/GitHub Actions)** | ✅ Yes | Production CI/CD pipelines |
| **ACR Webhooks + App Service** | ✅ Yes | Simple automatic updates from ACR |
| **App Service Continuous Deployment** | ✅ Yes | Built-in option in Deployment Center |
| **Azure CLI** | ❌ No (Manual) | Scripted/automated deployments |
| **ARM/Bicep Templates** | ❌ No (Manual) | Infrastructure provisioning |
| **ZIP Deployment** | ❌ No (Manual) | Code-based apps, not containers |

**Enabling Continuous Deployment for Docker in App Service:**

```bash
# Enable continuous deployment webhook for a container-based web app
az webapp deployment container config \
  --name MyWebApp \
  --resource-group MyResourceGroup \
  --enable-cd true

# Get the webhook URL to configure in your container registry
az webapp deployment container show-cd-url \
  --name MyWebApp \
  --resource-group MyResourceGroup
```

**Azure DevOps Pipeline Example:**

```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
  - task: Docker@2
    displayName: 'Build and push image'
    inputs:
      containerRegistry: 'myACRConnection'
      repository: 'myapp'
      command: 'buildAndPush'
      Dockerfile: '**/Dockerfile'
      tags: |
        $(Build.BuildId)
        latest

  - task: AzureWebAppContainer@1
    displayName: 'Deploy to App Service'
    inputs:
      azureSubscription: 'myAzureSubscription'
      appName: 'MyWebApp'
      containers: 'myacr.azurecr.io/myapp:$(Build.BuildId)'
```

### Question 8: Eliminating File Lock Conflicts

**Scenario:**
You are deploying a web application to Azure App Service. You need to deploy using a method that eliminates file lock conflicts between deployment and runtime.

**Question:**
Which deployment approach should you use?

**Options:**

1. ❌ Deploy using local Git push
   - **Incorrect**: Local Git deployment extracts files to the wwwroot directory where file lock conflicts can occur between deployment and runtime operations. When files are extracted, they can conflict with files currently being used by the running application.

2. ✅ Deploy using WEBSITE_RUN_FROM_PACKAGE=1 with ZIP deployment
   - **Correct**: When you run directly from a ZIP package, the files in the package are not copied to the wwwroot directory. Instead, the ZIP package itself gets mounted directly as the read-only wwwroot directory. This eliminates file lock conflicts as files are served from a read-only mounted package.
   
   **How Run From Package Works:**
   - The ZIP file is stored in Azure Blob Storage or locally
   - The package is mounted as a read-only file system at `D:\home\site\wwwroot`
   - No file extraction occurs, so no file locks are needed
   - Faster deployment since files aren't copied
   - Atomic deployment - the app sees the new version instantly

   **Configuration:**
   ```bash
   # Set the app setting to enable run from package
   az webapp config appsettings set --resource-group <group-name> \
     --name <app-name> \
     --settings WEBSITE_RUN_FROM_PACKAGE=1
   
   # Deploy the ZIP package
   az webapp deploy --resource-group <group-name> \
     --name <app-name> \
     --src-path <path-to-zip> \
     --type zip
   ```

3. ❌ Deploy using Web Deploy with delete existing files option
   - **Incorrect**: Web Deploy still copies files to the wwwroot directory during deployment, which can cause file lock conflicts even when deleting existing files first. The delete operation itself can encounter locks on files being used by the running application.

4. ❌ Deploy using FTP to wwwroot directory
   - **Incorrect**: FTP deployment copies files directly to the wwwroot directory where they can experience file lock conflicts between the deployment process and the running application. Files being served to users may be locked when you try to overwrite them.

---

**Additional Context: Deployment Methods and File Lock Behavior**

| Deployment Method | File Lock Risk | How Files Are Deployed |
|-------------------|----------------|------------------------|
| **Run From Package** | ✅ None | ZIP mounted as read-only wwwroot |
| **Deployment Slots** | ✅ None (in production) | Files deployed to separate slot |
| **Local Git** | ❌ High | Files extracted to wwwroot |
| **FTP** | ❌ High | Files copied directly to wwwroot |
| **Web Deploy** | ❌ Medium-High | Files copied to wwwroot |
| **ZIP Deploy (without Run From Package)** | ❌ Medium | Files extracted to wwwroot |

**When to Use Run From Package:**
- When you want to eliminate file lock conflicts completely
- When you need atomic deployments (instant switch to new version)
- When you want faster deployment times (no file extraction)
- When your app doesn't need to write to the wwwroot directory

**Limitations of Run From Package:**
- The wwwroot directory is read-only (cannot write files there at runtime)
- Not suitable for apps that need to modify their own files
- App must store user uploads and generated files elsewhere (Azure Storage, etc.)

### Question 9: Temporary Diagnostic Logging Configuration

**Scenario:**
You need to enable diagnostic logging for a Windows App Service web app. The logs should be stored temporarily for debugging purposes and automatically turn off after a period.

**Question:**
Which logging configuration should you use?

**Options:**

1. ✅ Application Logging (Filesystem)
   - **Correct**: The Filesystem option is designed for temporary debugging purposes and automatically turns itself off after 12 hours. This option stores logs in the App Service file system and automatically disables after 12 hours, making it ideal for temporary debugging scenarios where you need quick access to application logs without manual cleanup.

2. ❌ Application Logging (Blob)
   - **Incorrect**: The Blob option persists logs permanently in Azure Blob Storage and does not automatically turn off. It requires manual intervention to disable, which doesn't meet the requirement for temporary debugging. Use this option when you need long-term log retention for compliance or audit purposes.

3. ❌ Detailed Error Messages
   - **Incorrect**: Detailed Error Messages only captures error pages for HTTP 400-599 status codes. It doesn't provide comprehensive application debugging logs, nor does it automatically turn off after a period. This feature saves copies of .htm error pages that would have been sent to the client browser.

4. ❌ Web Server Logging (Storage)
   - **Incorrect**: Web Server Logging captures HTTP request information (IIS logs), not application-specific debugging data. When configured with Storage, it persists logs permanently without automatic disable functionality. This is useful for analyzing HTTP traffic patterns but not for application-level debugging.

---

**Key Takeaway:**

| Logging Option | Auto-Disable | Storage Location | Use Case |
|----------------|--------------|------------------|----------|
| **Application Logging (Filesystem)** | ✅ Yes (12 hours) | App Service file system | Temporary debugging |
| **Application Logging (Blob)** | ❌ No | Azure Blob Storage | Long-term retention |
| **Detailed Error Messages** | ❌ No | App Service file system | HTTP error diagnostics |
| **Web Server Logging** | ❌ No | File system or Storage | HTTP traffic analysis |

---

### Question 10: Deployment Package Size Limits on Consumption Plan

**Scenario:**
You are configuring deployment for an Azure App Service web app. The deployment package is 1.5 GB in size.

**Question:**
Which deployment method should you avoid when using a Consumption plan?

**Options:**

1. ❌ Container-based deployment
   - **Incorrect**: Container-based deployment uses a different deployment mechanism that doesn't rely on the same temporary storage constraints as package deployment. Containers are pulled from a registry and run directly, bypassing the temporary storage limitations.

2. ✅ Run from package deployment
   - **Correct**: The maximum size for a deployment package file is **1 GB**. Additionally, the temporary storage limit for a Consumption plan is **500 MB per plan**. With a 1.5 GB package exceeding both limits, run from package deployment would fail on the Consumption plan. This method requires the package to be stored and mounted, which is constrained by these storage limitations.

3. ❌ External URL deployment with streaming
   - **Incorrect**: External URL deployment with streaming doesn't require the full package to be stored in temporary storage, avoiding the size limitations of Consumption plan. The application streams content directly from the external URL.

4. ❌ Incremental deployment with differential updates
   - **Incorrect**: Incremental deployment only transfers changed files, significantly reducing the deployment size and staying within Consumption plan limits. This approach is efficient for large applications as it only updates modified components.

---

**Key Concepts:**

| Deployment Method | Package Size Limit | Consumption Plan Compatible | Notes |
|-------------------|-------------------|----------------------------|-------|
| **Run from package** | 1 GB | ❌ Limited by temp storage (500 MB) | Package must fit in temporary storage |
| **Container-based** | Image size varies | ✅ Yes | Uses container registry, not temp storage |
| **External URL streaming** | No practical limit | ✅ Yes | Streams directly, no temp storage |
| **Incremental deployment** | Depends on changes | ✅ Yes | Only transfers changed files |

**Consumption Plan Storage Limitations:**
- **Temporary storage**: 500 MB per Consumption plan
- **Package deployment limit**: 1 GB maximum package size
- These limits make run from package unsuitable for large applications on Consumption plans

**Alternative Solutions for Large Deployments:**
- Use Premium or Dedicated (App Service) plans with higher storage limits
- Use container-based deployment for applications exceeding package size limits
- Implement incremental deployment strategies to reduce transfer sizes
- Consider external URL deployment for large static assets

---

### Question 11: Custom Initialization Actions Before Handling Requests

**Scenario:**
You need to configure custom initialization actions for an Azure App Service web app that run before the app handles requests. The initialization must complete before considering the instance healthy.

**Question:**
What should you configure?

**Options:**

1. ❌ WEBSITE_WARMUP_PATH app setting
   - **Incorrect**: WEBSITE_WARMUP_PATH is an app setting that works with application initialization but by itself does not define the full initialization behavior and completion requirements.

2. ❌ Startup command in container settings
   - **Incorrect**: Startup commands are for container-based deployments and run when the container starts, not specifically for request initialization in traditional web apps.

3. ❌ Health check path in configuration
   - **Incorrect**: Health check paths monitor application health after initialization but do not control the initialization process or define initialization actions.

4. ✅ applicationInitialization element in web.config
   - **Correct**: The applicationInitialization configuration element in web.config allows you to specify initialization pages that must complete successfully before the instance is considered ready to handle requests.

---

**Key Concepts:**

| Configuration Method | Purpose | Use Case |
|---------------------|---------|----------|
| **applicationInitialization (web.config)** | Define initialization URLs that must complete before instance is healthy | Pre-warming cache, loading dependencies, initializing connections |
| **WEBSITE_WARMUP_PATH** | Works with applicationInitialization to specify warmup path | Supplements web.config initialization |
| **Health check path** | Monitors ongoing health of running instances | Post-initialization health monitoring |
| **Startup command** | Container startup behavior | Container-based deployments only |

**applicationInitialization Example:**

```xml
<system.webServer>
  <applicationInitialization doAppInitAfterRestart="true" skipManagedModules="true">
    <add initializationPage="/warmup" />
    <add initializationPage="/api/health" />
    <add initializationPage="/cache/prime" />
  </applicationInitialization>
</system.webServer>
```

**How applicationInitialization Works:**
1. When the app starts (or after a restart), the configured initialization pages are requested
2. These requests must complete successfully (HTTP 200) before the instance is marked as healthy
3. Only after initialization completes will the instance receive production traffic
4. This is particularly important during deployment slot swaps to ensure the staging slot is fully warmed before swap

**Benefits:**
- Prevents cold-start latency for end users
- Ensures caches are populated before serving traffic
- Validates that dependencies are available before accepting requests
- Works seamlessly with deployment slot swaps for zero-downtime deployments

> 💡 **Exam Tip**: For .NET applications on Windows App Service, the `applicationInitialization` element in web.config is the correct way to configure initialization actions that must complete before the instance handles requests. This is different from health checks which monitor ongoing health, and different from container startup commands which only apply to container deployments.

---

### Question 12: Secure Authentication for GitHub Actions Continuous Deployment

**Scenario:**
You are configuring continuous deployment for an Azure App Service web app using GitHub Actions. You want to use the most secure authentication method.

**Question:**
Which approach should you use?

**Options:**

1. ❌ Use basic authentication with deployment credentials
   - **Incorrect**: Basic authentication is the least secure option and Microsoft recommends against using basic authentication for deployments when more secure options are available.

2. ❌ Use a publish profile stored as a GitHub secret
   - **Incorrect**: While publish profiles work and can be stored as secrets, they are app-level credentials that are less secure than OpenID Connect with managed identities.

3. ❌ Configure a service principal with a client secret
   - **Incorrect**: Service principals with client secrets require managing and rotating secrets, making them less secure than OpenID Connect with managed identities.

4. ✅ Configure OpenID Connect with a user-assigned managed identity
   - **Correct**: By using Deployment Center, you can easily configure the more secure OpenID Connect authentication with a user-assigned identity. This authentication method uses short-lived tokens and offers hardened security.

---

**Key Concepts:**

| Authentication Method | Security Level | Key Characteristics |
|----------------------|----------------|---------------------|
| **Basic Authentication** | ❌ Lowest | Username/password credentials, not recommended |
| **Publish Profile** | ⚠️ Low-Medium | App-level credentials, stored as secrets |
| **Service Principal with Client Secret** | ⚠️ Medium | Requires secret management and rotation |
| **OpenID Connect with Managed Identity** | ✅ Highest | Short-lived tokens, no secrets to manage |

**Why OpenID Connect with Managed Identity is Most Secure:**

1. **No long-lived secrets**: Uses short-lived tokens instead of static credentials
2. **No secret rotation needed**: Eliminates the operational burden of rotating secrets
3. **Azure-managed authentication**: Leverages Azure's identity platform for secure authentication
4. **Federated credentials**: GitHub Actions can authenticate directly with Azure using OIDC federation
5. **Reduced attack surface**: No credentials stored in GitHub secrets that could be compromised

**Configuring OpenID Connect with Deployment Center:**

1. Create a user-assigned managed identity in Azure
2. Configure federated credentials for GitHub Actions
3. In App Service Deployment Center, select GitHub as the source
4. Choose OpenID Connect as the authentication type
5. Select the user-assigned managed identity

**GitHub Actions Workflow with OIDC:**

```yaml
name: Deploy to Azure App Service

on:
  push:
    branches:
      - main

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Azure Login with OIDC
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      
      - name: Deploy to App Service
        uses: azure/webapps-deploy@v2
        with:
          app-name: 'my-app-service'
          package: '.'
```

> 💡 **Exam Tip**: When asked about the most secure authentication method for GitHub Actions deployments to Azure App Service, always prefer OpenID Connect with managed identities over publish profiles, service principals with secrets, or basic authentication. OIDC eliminates the need to store and rotate secrets.

---

### Question 13: Running Static Content Generation Script Before Deployment

**Scenario:**
You are preparing to deploy a website to an Azure Web App from a GitHub repository. The website includes static content generated by a script. You plan to use the Azure Web App continuous deployment feature. You need to run the static generation script before the website starts serving traffic.

**Question:**
What are two possible ways to achieve this goal? (Choose two)

**Options:**

1. ❌ Add the path to the static content generation tool to `WEBSITE_RUN_FROM_PACKAGE` setting in the `host.json` file.
   - **Incorrect**: Adding the path to the static content generation tool to the WEBSITE_RUN_FROM_PACKAGE setting in the host.json file does not trigger the script to run before the website starts serving traffic. This setting is used to specify the path to a zip file containing the website content, not to run scripts or commands.

2. ✅ Add a `PreBuild` target in the websites `csproj` project file that runs the static content generation script.
   - **Correct**: Adding a PreBuild target in the websites csproj project file allows you to define a script or command that runs before the build process starts. This is an effective way to run the static content generation script before the website deployment process begins, ensuring that the static content is generated before the website starts serving traffic.

3. ❌ Create a file named `run.cmd` in the folder `/run` that calls a script which generates the static content and deploys the website.
   - **Incorrect**: Creating a file named run.cmd in the folder /run that calls a script to generate static content and deploy the website does not align with the Azure Web App continuous deployment feature. This method does not integrate with the deployment process and does not ensure that the static content generation script runs before the website deployment.

4. ✅ Create a file named `.deployment` in the root of the repository that calls a script which generates the static content and deploys the website.
   - **Correct**: Creating a file named .deployment in the root of the repository that calls a script to generate static content and deploy the website is a valid approach to ensure that the static content generation script runs before the website deployment. This file is recognized by Azure Web Apps and allows you to customize the deployment process, including running scripts before the deployment starts.

---

**Key Concepts for Static Content Generation:**

| Method | Description | When It Runs | Best For |
|--------|-------------|-------------|----------|
| **PreBuild Target in .csproj** | MSBuild target that runs before compilation | Before build process | .NET applications with MSBuild |
| **.deployment File** | Custom deployment script file | During deployment process | Any language/framework |
| **WEBSITE_RUN_FROM_PACKAGE** | Run from ZIP package | Runtime configuration | Package-based deployments |
| **run.cmd in /run** | Custom startup script | Application startup | Runtime initialization |

**PreBuild Target Implementation:**

```xml
<!-- In your .csproj file -->
<Target Name="PreBuild" BeforeTargets="PreBuildEvent">
  <Exec Command="npm run build-static" />
</Target>
```

**.deployment File Implementation:**

```bash
# .deployment file in repository root
[config]
command = deploy.cmd

# deploy.cmd
@echo off
echo Running static content generation...
call npm run generate-static
echo Deploying to Azure...
```

**Why These Methods Work:**

1. **PreBuild Target**: Integrates with the MSBuild process, ensuring static content is generated before compilation and packaging
2. **.deployment File**: Gives you full control over the deployment process, allowing custom scripts to run before the app is deployed

**Common Use Cases:**
- Static site generators (Hugo, Jekyll, Gatsby)
- Build-time asset optimization
- Content preprocessing before deployment
- Database migrations or setup scripts

### Question 14: Accessing Real-Time Console Logs for Containerized App

**Scenario:**
You plan to deploy a web app to App Service on Linux. You create an App Service plan. You create and push a custom Docker image that contains the web app to Azure Container Registry. You need to access the console logs generated from inside the container in real-time.

**Question:**
How should you complete the Azure CLI command?

**Correct Command:**
```bash
az webapp log config --docker-container-logging filesystem
az webapp log tail
```

**Explanation:**
- **Box 1 (`config`)**: The `config` subcommand is used to modify the logging configuration.
- **Box 2 (`--docker-container-logging`)**: This parameter enables logging for the Docker container (stdout/stderr) to the filesystem.
- **Box 3 (`webapp`)**: The command targets the `webapp` service.
- **Box 4 (`tail`)**: The `tail` subcommand is used to stream the logs in real-time.

**Incorrect Choices:**
- **`tail`, `--web-server-logging`, `aks`, `show`**: `tail` is for viewing, not configuring. `--web-server-logging` is for web server logs, not container logs. `aks` is for Kubernetes.
- **`show`, `--web-server-logging`, `acr`, `config`**: `show` displays settings but doesn't change them. `acr` is for Container Registry, not the running app.
- **`config`, `--application-logging`, `webapp`, `show`**: `--application-logging` is typically for Windows apps or code-level logs, while `--docker-container-logging` is specific for container console output. `show` does not stream logs.

---

## Application Logging in Azure App Service

### What is Application Logging?

Application logging captures diagnostic information written by your application code. Unlike platform logs (HTTP logs, web server logs), application logs contain custom messages that you write to track application behavior, errors, and debugging information.

### Types of Logs in App Service

| Log Type | Description | Use Case |
|----------|-------------|----------|
| **Application Logs** | Messages from your application code | Debug application logic, track custom events |
| **Web Server Logs** | Raw HTTP request data (IIS logs) | Analyze HTTP traffic patterns |
| **Detailed Error Messages** | Detailed .htm error pages | Diagnose HTTP errors (400, 500, etc.) |
| **Failed Request Tracing** | Detailed tracing for failed requests | Troubleshoot IIS/application pipeline issues |
| **Deployment Logs** | Logs from deployment operations | Debug deployment problems |

### Windows vs Linux Logging Availability

Not all logging types are available on both Windows and Linux App Service plans. Understanding these differences is crucial when implementing diagnostic logging for your web apps.

| Log Type | Windows | Linux | Notes |
|----------|---------|-------|-------|
| **Application Logging (Filesystem)** | ✅ Available | ✅ Available | Both platforms support application logs to filesystem |
| **Application Logging (Blob)** | ✅ Available | ✅ Available | Both platforms support application logs to blob storage |
| **Web Server Logging** | ✅ Available | ✅ Available | IIS logs on Windows, nginx logs on Linux |
| **Detailed Error Messages** | ✅ Available | ❌ **Not Available** | Windows only - saves detailed .htm error pages |
| **Failed Request Tracing** | ✅ Available | ❌ **Not Available** | Windows only - detailed IIS request tracing |
| **Deployment Logging** | ✅ Available | ✅ Available | Both platforms track deployment activities |
| **Docker Container Logs** | N/A | ✅ Available | Linux only - for custom container apps |

**Key Differences:**

1. **Detailed Error Messages**: Only available for Windows apps. To enable in Azure Portal: Go to your app > **Monitoring** > **App Service logs** > Turn on **Detailed error messages**

2. **Failed Request Tracing**: Only available for Windows apps. Provides detailed tracing information for failed HTTP requests through the IIS pipeline.

3. **Docker Container Logs**: Specifically available for Linux apps running custom containers, providing runtime container information.

**Important:** When implementing diagnostic logging for Linux App Service, remember that you cannot enable detailed error messages or failed request tracing - these options are only shown for Windows apps in the Azure Portal.

---

### Practice Question: Linux App Service Logging Availability

**Question:**

You need to implement diagnostic logging for a Linux App Service web app. Which logging type is **NOT** available for Linux web apps?

**Options:**

A) Docker container logs

B) Application logging to filesystem

C) Detailed error messages

D) Deployment logging

---

**Correct Answer: C) Detailed error messages**

---

**Explanation:**

| Option | Why Correct/Incorrect |
|--------|----------------------|
| **A) Docker container logs** | ❌ Incorrect - Docker container logs are specifically available for Linux apps running custom containers and provide runtime container information |
| **B) Application logging to filesystem** | ❌ Incorrect - Application logging to filesystem is available for Linux apps and can be configured through the Azure portal under App Service logs |
| **C) Detailed error messages** | ✅ **Correct** - Detailed error messages are only available for Windows apps. In the Azure Portal, you can enable this by going to your app > **Monitoring** > **App Service logs** and turning on "Detailed error messages" - but this option only appears for Windows apps |
| **D) Deployment logging** | ❌ Incorrect - Deployment logging tracks deployment activities and is available for both Windows and Linux App Service apps |

**Reference:** [Enable diagnostics logging for apps in Azure App Service](https://docs.microsoft.com/en-us/azure/app-service/troubleshoot-diagnostic-logs)

---

### App Service Log Categories (Diagnostic Settings)

When configuring diagnostic settings for Azure App Service, logs are organized into specific categories. Understanding these categories is essential for monitoring and troubleshooting.

| Log Category | Description | Contains |
|--------------|-------------|----------|
| **AppServiceHTTPLogs** | Web server logs (HTTP logs) | Raw HTTP request data, request/response details, status codes, client IPs |
| **AppServiceAppLogs** | Application logs | Custom log messages from your application code (ILogger, console.log, etc.) |
| **AppServiceAuditLogs** | Audit/login activity logs | Login activity via FTP and Kudu, authentication events |
| **AllMetrics** | Performance metrics | CPU percentage, memory usage, request count, data in/out (not logs, but metrics) |

**Key Points:**
- **AppServiceHTTPLogs** = Web server logs (IIS/nginx style logs)
- **AppServiceAppLogs** = Application logs (your code's log output)
- **AppServiceAuditLogs** = Security/audit logs (FTP/Kudu access)
- **AllMetrics** = Performance metrics, not logs

---

### Practice Question: App Service Log Types

**Question:**

What type of App Service log files store the web server logs?

**Options:**

A) AppServiceAppLogs

B) AppServiceAuditLogs

C) AllMetrics

D) AppServiceHTTPLogs ✅

---

**Correct Answer: D) AppServiceHTTPLogs**

---

**Explanation:**

| Option | Why Correct/Incorrect |
|--------|----------------------|
| **A) AppServiceAppLogs** | ❌ Incorrect - These are application logs containing messages from your application code |
| **B) AppServiceAuditLogs** | ❌ Incorrect - These contain login activity via FTP and Kudu, not web server logs |
| **C) AllMetrics** | ❌ Incorrect - These are not logs at all; they are performance metrics (CPU, memory, etc.) |
| **D) AppServiceHTTPLogs** | ✅ **Correct** - These are the web server logs containing HTTP request/response information |

**Reference:** [Enable diagnostics logging for apps in Azure App Service](https://docs.microsoft.com/en-us/azure/app-service/troubleshoot-diagnostic-logs)

### Enabling Application Logging

**Azure Portal:**
1. Navigate to your App Service
2. Go to **Monitoring** > **App Service logs**
3. Enable **Application Logging (Filesystem)** for temporary logging (12 hours)
   - Or enable **Application Logging (Blob)** for long-term storage
4. Set the log level: Error, Warning, Information, or Verbose
5. Save changes

**Azure CLI:**
```bash
# Enable application logging to file system
az webapp log config \
  --name MyWebApp \
  --resource-group MyResourceGroup \
  --application-logging filesystem \
  --level information

# Enable application logging to blob storage
az webapp log config \
  --name MyWebApp \
  --resource-group MyResourceGroup \
  --application-logging azureblogstorage \
  --level verbose \
  --azure-blob-storage-account-url "https://mystorageaccount.blob.core.windows.net/logs"
```

### Logging in Application Code

**ASP.NET Core (.NET):**
```csharp
public class HomeController : Controller
{
    private readonly ILogger<HomeController> _logger;

    public HomeController(ILogger<HomeController> logger)
    {
        _logger = logger;
    }

    public IActionResult Index()
    {
        _logger.LogInformation("Home page visited");
        _logger.LogWarning("This is a warning message");
        _logger.LogError("This is an error message");
        return View();
    }
}
```

**Node.js:**
```javascript
const express = require('express');
const app = express();

app.get('/', (req, res) => {
    console.log('Home page visited');
    console.warn('This is a warning message');
    console.error('This is an error message');
    res.send('Hello World');
});
```

**Python (Flask):**
```python
import logging
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    app.logger.info('Home page visited')
    app.logger.warning('This is a warning message')
    app.logger.error('This is an error message')
    return 'Hello World'
```

### Viewing Application Logs

**Stream logs in real-time (Azure CLI):**
```bash
az webapp log tail \
  --name MyWebApp \
  --resource-group MyResourceGroup
```

**Download logs (Azure CLI):**
```bash
az webapp log download \
  --name MyWebApp \
  --resource-group MyResourceGroup \
  --log-file logs.zip
```

**View logs in Azure Portal:**
1. Navigate to your App Service
2. Go to **Monitoring** > **Log stream**
3. Select **Application Logs** to see real-time logs

**Access log files via Kudu:**
- Navigate to `https://<app-name>.scm.azurewebsites.net`
- Go to **Debug console** > **CMD** or **PowerShell**
- Navigate to `LogFiles/Application/`

### Log Levels

| Level | Description | When to Use |
|-------|-------------|-------------|
| **Error** | Errors and exceptions | Production environments, critical issues only |
| **Warning** | Unexpected conditions that don't stop execution | Production, track potential issues |
| **Information** | General application flow | Development, testing, limited production use |
| **Verbose** | Detailed debugging information | Development and troubleshooting only (high volume) |

### File System vs Blob Storage

| Feature | File System | Blob Storage |
|---------|-------------|--------------|
| **Duration** | 12 hours (auto-disabled) | Long-term (persistent) |
| **Performance** | Faster access | Slightly slower |
| **Storage** | Limited to app's file system | Unlimited (based on storage account) |
| **Use Case** | Quick debugging, development | Production, compliance, audit trails |
| **Retention** | Automatic cleanup | Manual management required |

### Best Practices for Application Logging

1. **Use appropriate log levels**: Don't use Verbose in production; it generates too many logs
2. **Log meaningful information**: Include context like user IDs, request IDs, and timestamps
3. **Avoid logging sensitive data**: Never log passwords, tokens, or personal information
4. **Use structured logging**: Include structured data (JSON) for easier querying
5. **Enable blob storage for production**: Use blob storage for long-term retention and compliance
6. **Monitor log volume**: Excessive logging can impact performance and cost
7. **Set up alerts**: Configure Azure Monitor alerts for error patterns
8. **Use correlation IDs**: Track requests across distributed systems
9. **Implement log rotation**: Manage log file sizes and retention policies
10. **Centralize logs**: Use Azure Monitor, Application Insights, or Log Analytics for centralized analysis

### Application Insights vs App Service Logs

| Feature | App Service Logs | Application Insights |
|---------|------------------|---------------------|
| **Purpose** | Basic application logging | Full APM and monitoring |
| **Setup** | Built-in, minimal configuration | Requires SDK integration |
| **Data Retention** | Short-term or manual management | 90 days (configurable) |
| **Querying** | Limited (file-based or streaming) | Advanced (KQL queries) |
| **Cost** | Included with App Service | Pay per GB ingested |
| **Best For** | Quick debugging, simple apps | Production monitoring, complex apps |

## Application Request Routing (ARR) Affinity

### What is ARR Affinity?

Application Request Routing (ARR) Affinity is a feature that ensures client requests are routed to the same web app instance throughout a session. In multi-instance deployments, Azure uses a cookie called `ARRAffinity` to track which instance handled the initial request and routes all subsequent requests from that client to the same instance.

### When to Use ARR Affinity

**Enable ARR Affinity when:**
- Your application stores session state in local memory
- You use in-process session state
- Your application maintains instance-specific state that must persist across requests
- Legacy applications that were designed for single-server environments

**Disable ARR Affinity when:**
- Your application is stateless
- Session state is stored externally (Redis Cache, Azure SQL, Cosmos DB)
- You want to maximize load distribution across instances
- Building modern cloud-native applications

### Configuring ARR Affinity

**Azure Portal:**
1. Navigate to your App Service
2. Go to **Configuration** > **General settings**
3. Find the **ARR affinity** toggle
4. Set to **On** (default) or **Off**

**Azure CLI:**
```bash
# Enable ARR Affinity
az webapp update \
  --name MyWebApp \
  --resource-group MyResourceGroup \
  --client-affinity-enabled true

# Disable ARR Affinity
az webapp update \
  --name MyWebApp \
  --resource-group MyResourceGroup \
  --client-affinity-enabled false
```

**Azure PowerShell:**
```powershell
# Enable ARR Affinity
Set-AzWebApp -Name "MyWebApp" -ResourceGroupName "MyResourceGroup" -ClientAffinityEnabled $true

# Disable ARR Affinity
Set-AzWebApp -Name "MyWebApp" -ResourceGroupName "MyResourceGroup" -ClientAffinityEnabled $false
```

### How ARR Affinity Works

```
First Request:
Client → Azure Load Balancer → Instance 1
         ← ARRAffinity Cookie ← 

Subsequent Requests (with ARRAffinity cookie):
Client → Azure Load Balancer → Instance 1 (same instance)
```

### ARR Affinity vs Stateless Design

| Aspect | With ARR Affinity | Stateless (No Affinity) |
|--------|-------------------|-------------------------|
| **Session Storage** | Local instance memory | External (Redis, SQL, etc.) |
| **Scalability** | Limited by session distribution | Unlimited horizontal scaling |
| **Instance Failures** | Session data lost if instance fails | No session data loss |
| **Load Distribution** | Uneven across instances | Even distribution |
| **Best For** | Legacy apps, quick migrations | Cloud-native, scalable apps |

### Platform Settings Overview

In addition to ARR Affinity, Azure App Service provides several other platform settings:

**WebSocket:**
- Enables WebSocket protocol support
- Provides full-duplex communication over a single TCP connection
- Required for SignalR, Socket.IO, and other real-time communication frameworks

**Always On:**
- Keeps the app loaded even when there's no incoming traffic
- Prevents the app from being unloaded after 20 minutes of inactivity
- Improves response time for the first request
- Required for continuous WebJobs or timer-triggered functions

**HTTP Version:**
- Configures which HTTP protocol version to use
- **HTTP/1.1**: Traditional request-response model
- **HTTP/2**: Multiplexing, header compression, server push, persistent connections
- HTTP/2 improves performance but doesn't affect session affinity

## Cross-Origin Resource Sharing (CORS)

### What is CORS?

Cross-Origin Resource Sharing (CORS) is a security mechanism that allows or restricts web applications running in one domain from making requests to resources in a different domain. By default, web browsers block cross-origin requests for security reasons (Same-Origin Policy).

### When to Configure CORS

Configure CORS when:
- Your web app needs to accept API calls from a frontend hosted on a different domain
- Your single-page application (SPA) is hosted on a different domain than your backend API
- You're building microservices that need to communicate across different origins
- Third-party applications need to access your web app's resources

### Configuring CORS with Azure CLI

**Add an allowed origin:**
```bash
az webapp cors add \
  --resource-group MyResourceGroup \
  --name MyWebApp \
  --allowed-origins https://myapps.com
```

**Add multiple allowed origins:**
```bash
az webapp cors add \
  --resource-group MyResourceGroup \
  --name MyWebApp \
  --allowed-origins https://app1.com https://app2.com https://app3.com
```

**List current CORS settings:**
```bash
az webapp cors show \
  --resource-group MyResourceGroup \
  --name MyWebApp
```

**Remove a specific origin:**
```bash
az webapp cors remove \
  --resource-group MyResourceGroup \
  --name MyWebApp \
  --allowed-origins https://myapps.com
```

**Allow all origins (not recommended for production):**
```bash
az webapp cors add \
  --resource-group MyResourceGroup \
  --name MyWebApp \
  --allowed-origins '*'
```

### CORS vs Access Restrictions

It's important to understand the difference between CORS and access restrictions:

| Feature | CORS | Access Restrictions |
|---------|------|---------------------|
| **Level** | Application-level | Network-level |
| **Purpose** | Controls cross-origin HTTP requests in browsers | Controls which IP addresses/subnets can access the app |
| **Use Case** | Allow specific domains to call your API | Restrict access to specific networks or IPs |
| **Command** | `az webapp cors add` | `az webapp config access-restriction add` |

## Deployment Slot Settings (Sticky Settings)

### What Are Slot Settings?

Deployment slot settings, also known as "sticky settings," are configuration values that remain associated with a specific deployment slot during swap operations. By default, most settings are swapped between slots, but marking a setting as a slot setting prevents it from being swapped.

### When to Use Slot Settings

Use slot settings for configurations that are **environment-specific** and should not move between slots:

- **Connection strings**: Database connections that differ between staging and production
- **App settings**: API keys, feature flags, or environment-specific configurations
- **Storage account connections**: Different storage accounts for staging vs. production
- **External service endpoints**: URLs that point to different environments

### How to Configure Slot Settings

**Azure Portal:**
1. Navigate to your App Service
2. Go to **Configuration** > **Application settings** or **Connection strings**
3. Add or edit a setting
4. Check the **Deployment slot setting** checkbox
5. Save changes

**Azure CLI:**
```bash
# Set a slot-specific app setting
az webapp config appsettings set \
  --name app1 \
  --resource-group mygroup \
  --slot staging \
  --settings "MY_SETTING=value" \
  --slot-settings "MY_SETTING"

# Set a slot-specific connection string
az webapp config connection-string set \
  --name app1 \
  --resource-group mygroup \
  --slot staging \
  --connection-string-type SQLAzure \
  --settings "MyDbConnection=Server=..." \
  --slot-settings "MyDbConnection"
```

### Swap Behavior Example

**Before Swap:**
```
Production Slot:
  - ConnectionString (sticky): "Server=prod.database.windows.net"
  - ApiKey (not sticky): "prod-key-123"

Staging Slot:
  - ConnectionString (sticky): "Server=staging.database.windows.net"
  - ApiKey (not sticky): "staging-key-456"
```

**After Swap:**
```
Production Slot (was Staging):
  - ConnectionString (sticky): "Server=prod.database.windows.net" ← Stayed
  - ApiKey (not sticky): "staging-key-456" ← Swapped

Staging Slot (was Production):
  - ConnectionString (sticky): "Server=staging.database.windows.net" ← Stayed
  - ApiKey (not sticky): "prod-key-123" ← Swapped
```

## Key Concepts

### File Locking During Deployment

File locking occurs when:
- The application is running and has files open
- Files are being written while trying to overwrite them
- Multiple processes are accessing the same files

**Solutions to Eliminate File Lock Conflicts:**

1. **Run From Package (WEBSITE_RUN_FROM_PACKAGE=1)**: The ZIP package is mounted as a read-only wwwroot directory, completely eliminating file lock conflicts since no files are extracted or copied.

2. **Deployment Slots**: Deploy to a staging slot first, then swap to production. Files in production remain untouched during deployment.

### Why Staging Slots Solve File Locking

When deploying to a staging slot:
1. The ZIP package is deployed to the **staging slot**, not production
2. Production files remain untouched and unlocked
3. The staging app is warmed up and validated
4. The swap operation exchanges the slots (a routing change, not file operations)
5. No files are overwritten in production during deployment

### Deployment Slot Swap Process

```
[Staging Slot] ← Deploy ZIP here (no production impact)
     ↓
[Warm-up & Validation]
     ↓
[Auto Swap] ← Routing change (not file copy)
     ↓
[Production] ← Staging becomes production
```

## Best Practices

1. **Use deployment slots for production apps**: Always use at least one staging slot for production applications
2. **Enable auto swap**: Configure auto swap to automate the promotion process
3. **Validate in staging**: Test your application in the staging slot before swapping
4. **Monitor swap operations**: Watch for any issues during the swap process
5. **Use slot-specific settings**: Mark environment-specific configurations as deployment slot settings to keep them sticky:
   - Database connection strings
   - API keys and secrets specific to each environment
   - Feature flags that differ between environments
   - External service endpoints
6. **Test slot settings**: After configuring sticky settings, perform a test swap to verify they remain with the correct slot
7. **Document slot settings**: Maintain documentation of which settings are slot-specific and why
8. **Consider disabling ARR Affinity**: For new applications, design them to be stateless and store session data externally (Redis, Cosmos DB) to improve scalability
9. **Use Always On for production**: Enable Always On to ensure your app is always responsive and prevent cold starts
10. **Configure CORS properly**: Only add trusted origins to your CORS policy; avoid using wildcards (`*`) in production

## Common Azure CLI Commands for App Service

### Deployment Commands

| Command | Description |
|---------|-------------|
| `az webapp deploy` | Deploy a ZIP, WAR, JAR, or EAR package |
| `az webapp deployment slot create` | Create a deployment slot |
| `az webapp deployment slot swap` | Swap deployment slots |
| `az webapp deployment slot auto-swap` | Configure auto-swap for a slot |

### Configuration Commands

| Command | Description |
|---------|-------------|
| `az webapp cors add` | Add allowed origins for CORS |
| `az webapp cors show` | Display CORS settings |
| `az webapp cors remove` | Remove allowed origins |
| `az webapp config appsettings set` | Set application settings |
| `az webapp config connection-string set` | Set connection strings |
| `az webapp config access-restriction add` | Add IP/subnet access restrictions |

### Identity and Routing Commands

| Command | Description |
|---------|-------------|
| `az webapp identity assign` | Enable managed identity |
| `az webapp identity show` | Display managed identity details |
| `az webapp traffic-routing set` | Configure traffic routing between slots |

### Parameters for `az webapp deploy`

| Parameter | Description |
|-----------|-------------|
| `--src-path` | Path to the ZIP file to deploy |
| `--type` | Deployment type (zip, war, jar, ear, static) |
| `--slot` | Name of the deployment slot |
| `--clean` | Cleans the target folder before deployment |
| `--restart` | Restarts the app after deployment |
| `--timeout` | Timeout in seconds for the deployment operation |
| `--async` | Runs the deployment asynchronously |

## Example Deployment Workflow

```bash
# 1. Create a staging slot
az webapp deployment slot create \
  --name myapp \
  --resource-group mygroup \
  --slot staging

# 2. Configure auto swap
az webapp deployment slot auto-swap \
  --name myapp \
  --resource-group mygroup \
  --slot staging

# 3. Deploy to staging slot (auto swap will occur automatically)
az webapp deploy \
  --resource-group mygroup \
  --name myapp \
  --slot staging \
  --src-path ./myapp.zip \
  --type zip
```

## Kudu REST API

### What is Kudu?

Kudu is the engine behind Git deployments in Azure App Service. It provides a set of REST APIs for managing your App Service, including file operations, diagnostics, and deployments. The Kudu SCM (Source Control Management) endpoint is accessible at `https://<app-name>.scm.azurewebsites.net`.

### Common Kudu REST API Endpoints

| API Endpoint | Method | Description |
|--------------|--------|-------------|
| `/api/zip/{path}/` | **PUT** | Upload and expand a ZIP file to a folder |
| `/api/zip/{path}/` | **GET** | Download a folder as a ZIP file |
| `/api/vfs/{path}` | GET/PUT/DELETE | Virtual File System operations |
| `/api/deployments/{id}` | GET/PUT | Get or update deployment information |
| `/api/scm/info` | GET | Get SCM information |
| `/api/settings` | GET/POST | Get or update Kudu settings |
| `/api/diagnostics/runtime` | GET | Get runtime versions |
| `/api/processes` | GET | List running processes |

### ZIP API for Deployments

The Zip API (`/api/zip/{path}/`) is specifically designed for:
- **Uploading**: Expanding ZIP files into folders on the server
- **Downloading**: Downloading folders as ZIP files from the server

**Upload a ZIP file:**
```bash
# Upload and expand a ZIP file to wwwroot
curl -X PUT \
  -u "<deployment-user>:<password>" \
  --data-binary @myapp.zip \
  "https://<app-name>.scm.azurewebsites.net/api/zip/site/wwwroot/"
```

**Download a folder as ZIP:**
```bash
# Download the wwwroot folder as a ZIP file
curl -X GET \
  -u "<deployment-user>:<password>" \
  -o wwwroot.zip \
  "https://<app-name>.scm.azurewebsites.net/api/zip/site/wwwroot/"
```

### Practice Question: Kudu ZIP API

**Question:**

What is the REST API command for uploading a ZIP file into an Azure App Service using the Kudu SCM endpoint?

**Options:**

1. ❌ `POST /deploy`
   - **Incorrect**: There is no `/deploy` endpoint in the Kudu REST API for ZIP file uploads. The POST method is not used for ZIP deployments.

2. ❌ `POST /api/scm/{path}/`
   - **Incorrect**: The `/api/scm/` endpoint is used for SCM-related operations (like getting SCM info), not for uploading ZIP files.

3. ❌ `PUT /api/deployments/{id}`
   - **Incorrect**: The `/api/deployments/{id}` endpoint is used to get or update deployment metadata and status, not to upload ZIP files.

4. ✅ `PUT /api/zip/{path}/`
   - **Correct**: The Zip API uses `PUT /api/zip/{path}/` to upload and expand ZIP files into the specified folder. For example, `PUT /api/zip/site/wwwroot/` uploads and extracts a ZIP file to the wwwroot folder.

**Reference:** [Kudu REST API - GitHub](https://github.com/projectkudu/kudu/wiki/REST-API)

---

## WebJobs for Background Processing

### What are WebJobs?

WebJobs is a feature of Azure App Service that enables you to run programs or scripts in the same instance as a web app, API app, or mobile app. WebJobs can run alongside your main application without requiring additional Azure resources.

### Types of WebJobs

| Type | Description | Single Instance Support | Use Case |
|------|-------------|------------------------|----------|
| **Continuous** | Runs continuously in an endless loop. Automatically restarts if stopped. | ✅ Yes (with `is_singleton: true`) | Background processing, queue monitoring, real-time data processing |
| **Triggered** | Runs on a schedule (CRON) or on-demand | ❌ No | Scheduled tasks, batch processing, periodic cleanup jobs |

### WebJobs vs Other Background Processing Options

| Feature | WebJobs with AlwaysOn | IHostedService | Azure Functions (Timer) | Logic Apps |
|---------|----------------------|----------------|------------------------|------------|
| **Runs Within App Service** | ✅ Yes | ✅ Yes | ❌ Separate resource | ❌ Separate service |
| **Continuous Execution** | ✅ Yes | ✅ Yes | ❌ Schedule-based | ❌ Trigger-based |
| **Auto-Restart on Crash** | ✅ Yes | ❌ No guarantee | N/A | N/A |
| **Remote Debugging** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |
| **Idle Timeout Prevention** | ✅ With AlwaysOn | ❌ Requires AlwaysOn | N/A | N/A |
| **Additional Cost** | ❌ No extra cost | ❌ No extra cost | ✅ Separate billing | ✅ Separate billing |

### Key Requirements for Continuous WebJobs

1. **AlwaysOn Setting**: Must be enabled to prevent the app from being unloaded after 20 minutes of inactivity
2. **Basic Tier or Higher**: AlwaysOn is only available in Basic, Standard, Premium, and Isolated tiers
3. **Proper Configuration**: WebJob must be configured as "Continuous" type

### WebJobs Features

- **Automatic Restart**: Continuous WebJobs automatically restart if they stop or crash
- **Single Instance Execution**: Continuous WebJobs can be restricted to run on a single instance using `is_singleton: true` in `settings.job`
- **Remote Debugging**: Attach Visual Studio debugger to running WebJobs
- **Logging**: Built-in logging through Kudu dashboard
- **SDK Support**: WebJobs SDK provides triggers and bindings similar to Azure Functions
- **File Watching**: Can monitor files and directories for changes

### Creating a Continuous WebJob

```bash
# Deploy a WebJob using Azure CLI
az webapp webjob continuous create \
  --resource-group <group-name> \
  --name <app-name> \
  --webjob-name <webjob-name> \
  --webjob-type continuous \
  --file-path <path-to-zip>
```

### Practice Question: Background Processing for App Service

**Question:**

You need to implement background processing for an Azure App Service web app. The background tasks should run continuously, restart automatically if they stop, and support remote debugging. Which feature should you use?

**Options:**
- A) Background tasks using IHostedService
- B) Azure Functions with Timer trigger
- C) Azure Logic Apps with recurrence trigger
- D) WebJobs with AlwaysOn enabled

---

### Answer: D ✅

**Correct Answer: D) WebJobs with AlwaysOn enabled**

---

### Detailed Explanation

**Option A - Background tasks using IHostedService**
- **Incorrect**: IHostedService provides background task capabilities within ASP.NET Core applications
- However, it doesn't guarantee automatic restart after crashes
- Requires AlwaysOn to prevent idle timeout, otherwise the app (including hosted services) unloads after 20 minutes
- If the hosted service crashes, the application might need to be restarted manually
- WebJobs provides a more robust solution for continuous background processing

**Option B - Azure Functions with Timer trigger**
- **Incorrect**: Azure Functions with Timer triggers run on schedules (CRON expressions) rather than continuously
- Timer-triggered functions execute at specific intervals, not in an endless loop
- Would require a separate Azure resource (Function App) rather than running within the App Service web app
- Not suitable for continuous background processing requirements

**Option C - Azure Logic Apps with recurrence trigger**
- **Incorrect**: Logic Apps are designed for workflow orchestration, not continuous background processing
- Run as a completely separate Azure service
- Recurrence trigger runs workflows on a schedule, not continuously
- Not suitable for continuous background processing within an App Service web app
- Better suited for integrating multiple services and systems

**Option D - WebJobs with AlwaysOn enabled** ✅
- **Correct**: WebJobs with AlwaysOn enabled provide the complete solution:
  - **Continuous background processing**: Runs in an endless loop
  - **Automatic restart**: Automatically restarts if the WebJob stops or crashes
  - **Remote debugging**: Full support for attaching debuggers from Visual Studio
  - **Integrated with App Service**: Runs in the same instance, no additional Azure resources needed
  - **AlwaysOn**: Prevents the app from being unloaded due to inactivity

---

### Key Takeaways

1. **WebJobs are Ideal for App Service Background Processing**
   - Run in the same instance as your web app
   - No additional Azure resources or costs
   - Full integration with App Service features

2. **AlwaysOn is Critical for Continuous WebJobs**
   - Without AlwaysOn, the app unloads after 20 minutes of inactivity
   - AlwaysOn requires Basic tier or higher
   - Ensures continuous WebJobs never stop due to idle timeout

3. **IHostedService Limitations**
   - Part of the main application process
   - No built-in automatic restart on crash
   - Still requires AlwaysOn for idle timeout prevention

4. **Azure Functions and Logic Apps are Separate Services**
   - Require additional Azure resources
   - Not suitable for "within App Service" requirements
   - Timer triggers are schedule-based, not continuous

---

### Practice Question: Single-Instance WebJob Restriction

**Question:**

You are designing an Azure WebJob that will run on the same instances as a web app. You want to make use of a suitable WebJob type. The WebJob type should also allow for the option to restrict the WebJob to a single instance.

**Solution:** You configure the use of the Triggered WebJob type.

**Does the solution meet the goal?**

---

### Answer: No ❌

**Correct Answer: No**

---

### Explanation

**Why Triggered WebJob is NOT Correct:**

The **Triggered WebJob type** does not meet the requirement of restricting the WebJob to a single instance. Here's why:

- **Triggered WebJobs** run on a schedule (CRON expression) or on-demand
- They can run on multiple instances when the App Service is scaled out
- **No built-in option** to restrict execution to a single instance
- Each instance of the web app can execute the triggered WebJob independently

**Why Continuous WebJob is the Correct Solution:**

The **Continuous WebJob type** is the suitable option for this scenario:

- **Runs continuously** on the same instances as the web app
- **Single instance restriction available**: Can be configured to run on only one instance using the `is_singleton` setting in the `settings.job` file
- Ensures that only one instance of the WebJob is active at a time, even when the App Service scales to multiple instances

**Configuring Single-Instance Continuous WebJob:**

To restrict a Continuous WebJob to a single instance, create a `settings.job` file in the WebJob's directory:

```json
{
  "is_singleton": true
}
```

**Key Differences:**

| Feature | Continuous WebJob | Triggered WebJob |
|---------|------------------|------------------|
| **Execution Pattern** | Runs continuously | Runs on schedule or on-demand |
| **Single Instance Support** | ✅ Yes (with `is_singleton: true`) | ❌ No built-in support |
| **Use Case** | Background processing, queue monitoring | Scheduled tasks, batch jobs |
| **Scaling Behavior** | Can restrict to single instance | Runs on all instances by default |

---

### References

- [Run background tasks with WebJobs in Azure App Service](https://learn.microsoft.com/azure/app-service/webjobs-create)
- [WebJobs SDK](https://learn.microsoft.com/azure/app-service/webjobs-sdk-how-to)
- [Configure App Service apps](https://learn.microsoft.com/azure/app-service/configure-common)

---

## Additional Resources

- [Deploy to App Service - Microsoft Learn](https://learn.microsoft.com/en-us/azure/app-service/deploy-zip)
- [Set up staging environments in Azure App Service](https://learn.microsoft.com/en-us/azure/app-service/deploy-staging-slots)
- [Azure CLI: az webapp deploy](https://learn.microsoft.com/en-us/cli/azure/webapp)
- [Kudu REST API Documentation](https://github.com/projectkudu/kudu/wiki/REST-API)

## Azure Static Web Apps Deployment

Azure Static Web Apps is a service that automatically builds and deploys full stack web apps to Azure from a code repository. It provides streamlined deployment for static web applications with integrated serverless API backends.

### Key Features

| Feature | Description |
|---------|-------------|
| **Global CDN** | Content served from edge locations worldwide |
| **Serverless APIs** | Azure Functions integration for backend logic |
| **Authentication** | Built-in auth with providers (GitHub, Twitter, etc.) |
| **Custom Domains** | Free SSL certificates and custom domain support |
| **Deployment Slots** | Preview deployments and staging environments |
| **Git Integration** | Automatic builds on commits to configured branches |

### Deployment Methods

#### GitHub/GitLab Integration

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

#### Azure DevOps

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

#### CLI Deployment

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

### The .deployment File in Static Web Apps

The `.deployment` file is a configuration file that allows you to customize the deployment process for Azure Static Web Apps. It provides control over the build and deployment steps, enabling you to run custom scripts, set environment variables, and perform pre/post-deployment tasks.

#### Purpose and Usage

**When to Use:**
- Running custom build scripts
- Installing additional dependencies
- Performing database migrations
- Setting up environment-specific configurations
- Running tests before deployment

#### File Structure

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

#### Common Scenarios

| Scenario | Use Case | Example |
|----------|----------|---------|
| **Static Site Generation** | Generate content before deployment | Hugo, Jekyll, Gatsby builds |
| **Asset Optimization** | Minify CSS/JS, compress images | Webpack, Parcel builds |
| **API Deployment** | Deploy backend APIs alongside frontend | Azure Functions deployment |
| **Environment Setup** | Configure staging/production settings | Database connections, API keys |
| **Testing** | Run tests before deployment | Unit tests, integration tests |

#### Examples

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

### Build Configuration

#### build.json

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

#### Framework-Specific Configuration

| Framework | build.json Example |
|-----------|-------------------|
| **React** | `{"buildCommand": "npm run build", "outputLocation": "build"}` |
| **Vue.js** | `{"buildCommand": "npm run build", "outputLocation": "dist"}` |
| **Angular** | `{"buildCommand": "ng build --prod", "outputLocation": "dist"}` |
| **Hugo** | `{"buildCommand": "hugo --minify", "outputLocation": "public"}` |
| **Jekyll** | `{"buildCommand": "jekyll build", "outputLocation": "_site"}` |

### Custom Deployment Scripts

#### Pre-deployment Tasks

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

#### Post-deployment Tasks

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

### Static Content Generation

#### Supported Frameworks

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

#### Custom Build Commands

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

### Environment Variables

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

### Deployment Slots

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

### Best Practices

#### Deployment Configuration

1. **Use .deployment file** for complex build processes
2. **Leverage build.json** for standard configurations
3. **Test deployments locally** before pushing to repository
4. **Use environment variables** for configuration management
5. **Implement proper error handling** in deployment scripts

#### Security Considerations

1. **Store secrets securely** using Azure Key Vault
2. **Use managed identities** for Azure resource access
3. **Implement proper authentication** for API endpoints
4. **Regularly update dependencies** and frameworks
5. **Monitor deployment logs** for security issues

#### Performance Optimization

1. **Enable compression** for static assets
2. **Use CDN effectively** with proper cache headers
3. **Optimize images and assets** during build
4. **Implement lazy loading** for large resources
5. **Monitor performance metrics** post-deployment

### Troubleshooting

#### Common Issues

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

#### Debugging Tools

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

## Related Topics

- Deployment slots and slot settings
- Blue-green deployments
- Continuous deployment with Azure DevOps
- Application warm-up configuration
- Zero-downtime deployments

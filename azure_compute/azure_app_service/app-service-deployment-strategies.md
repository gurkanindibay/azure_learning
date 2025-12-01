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
  - [Question 3: Configuring CORS for External Requests](#question-3-configuring-cors-for-external-requests)
  - [Question 4: Session Affinity in Multi-Instance Deployments](#question-4-session-affinity-in-multi-instance-deployments)
  - [Question 5: Enabling Application Logging](#question-5-enabling-application-logging)
  - [Question 6: Docker Container Automatic Updates](#question-6-docker-container-automatic-updates)
  - [Question 7: Eliminating File Lock Conflicts](#question-7-eliminating-file-lock-conflicts)
  - [Question 8: Temporary Diagnostic Logging Configuration](#question-8-temporary-diagnostic-logging-configuration)
- [Application Logging in Azure App Service](#application-logging-in-azure-app-service)
  - [What is Application Logging?](#what-is-application-logging)
  - [Types of Logs in App Service](#types-of-logs-in-app-service)
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

### Question 3: Configuring CORS for External Requests

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

### Question 4: Session Affinity in Multi-Instance Deployments

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

### Question 5: Enabling Application Logging

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

### Question 6: Docker Container Automatic Updates

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

### Question 7: Eliminating File Lock Conflicts

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

### Question 8: Temporary Diagnostic Logging Configuration

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

| Type | Description | Use Case |
|------|-------------|----------|
| **Continuous** | Runs continuously in an endless loop. Automatically restarts if stopped. | Background processing, queue monitoring, real-time data processing |
| **Triggered** | Runs on a schedule (CRON) or on-demand | Scheduled tasks, batch processing, periodic cleanup jobs |

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

## Related Topics

- Deployment slots and slot settings
- Blue-green deployments
- Continuous deployment with Azure DevOps
- Application warm-up configuration
- Zero-downtime deployments

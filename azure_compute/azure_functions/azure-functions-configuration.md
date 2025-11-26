# Azure Functions - Configuration Files

## Overview

Azure Functions use configuration files to define function behavior, triggers, bindings, and application settings. Understanding these configuration files is essential for developing, deploying, and managing Azure Functions effectively.

## Key Configuration Files

| File | Purpose | Scope |
|------|---------|-------|
| **function.json** | Defines triggers, bindings, and function-level settings | Per function |
| **host.json** | Configures runtime behavior and global settings | Function app (all functions) |
| **local.settings.json** | Stores app settings and connection strings for local development | Local only (not deployed) |
| **proxies.json** | Defines HTTP proxies (deprecated in Functions v4) | Function app |

## function.json

### Overview

The `function.json` file is the **primary configuration file** for Azure Functions. It defines the function's trigger, bindings, and other configuration settings.

**Key Facts:**
- Every function has **one and only one** `function.json` file
- Located in the function's folder (e.g., `MyFunction/function.json`)
- Defines what triggers the function (HTTP, Timer, Queue, etc.)
- Specifies input and output bindings
- The runtime uses this file to determine events to monitor
- Controls how data is passed into and returned from function execution

### Structure

```json
{
  "disabled": false,
  "bindings": [
    {
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "authLevel": "function",
      "methods": ["get", "post"]
    },
    {
      "type": "http",
      "direction": "out",
      "name": "res"
    }
  ],
  "scriptFile": "../dist/MyFunction/index.js",
  "entryPoint": "main"
}
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `disabled` | boolean | Whether the function is disabled |
| `bindings` | array | Array of trigger and binding configurations |
| `scriptFile` | string | Path to the script file containing the function code |
| `entryPoint` | string | Name of the function to execute (for compiled languages) |

### Bindings Array

Each binding in the `bindings` array must include:

| Property | Required | Description |
|----------|----------|-------------|
| `type` | Yes | Type of binding (e.g., `httpTrigger`, `queueTrigger`, `cosmosDBTrigger`) |
| `direction` | Yes | Direction of data flow: `in`, `out`, or `inout` |
| `name` | Yes | Name used in function code to access the binding data |

### Common Trigger Examples

#### HTTP Trigger

```json
{
  "bindings": [
    {
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "authLevel": "anonymous",
      "methods": ["get", "post"],
      "route": "items/{id}"
    },
    {
      "type": "http",
      "direction": "out",
      "name": "res"
    }
  ]
}
```

#### Timer Trigger

```json
{
  "bindings": [
    {
      "type": "timerTrigger",
      "direction": "in",
      "name": "myTimer",
      "schedule": "0 */5 * * * *"
    }
  ]
}
```

#### Queue Trigger

```json
{
  "bindings": [
    {
      "type": "queueTrigger",
      "direction": "in",
      "name": "myQueueItem",
      "queueName": "myqueue",
      "connection": "AzureWebJobsStorage"
    }
  ]
}
```

#### Blob Trigger

```json
{
  "bindings": [
    {
      "type": "blobTrigger",
      "direction": "in",
      "name": "myBlob",
      "path": "samples-workitems/{name}",
      "connection": "AzureWebJobsStorage"
    }
  ]
}
```

#### Cosmos DB Trigger

```json
{
  "bindings": [
    {
      "type": "cosmosDBTrigger",
      "direction": "in",
      "name": "documents",
      "connectionStringSetting": "CosmosDBConnection",
      "databaseName": "MyDatabase",
      "collectionName": "MyContainer",
      "leaseCollectionName": "leases",
      "createLeaseCollectionIfNotExists": true
    }
  ]
}
```

### Input and Output Bindings

#### Cosmos DB Input Binding

```json
{
  "bindings": [
    {
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "authLevel": "function",
      "methods": ["get"]
    },
    {
      "type": "cosmosDB",
      "direction": "in",
      "name": "document",
      "connectionStringSetting": "CosmosDBConnection",
      "databaseName": "MyDatabase",
      "collectionName": "MyContainer",
      "id": "{Query.id}",
      "partitionKey": "{Query.partitionKey}"
    },
    {
      "type": "http",
      "direction": "out",
      "name": "res"
    }
  ]
}
```

#### Queue Output Binding

```json
{
  "bindings": [
    {
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "authLevel": "function",
      "methods": ["post"]
    },
    {
      "type": "queue",
      "direction": "out",
      "name": "outputQueueItem",
      "queueName": "outqueue",
      "connection": "AzureWebJobsStorage"
    },
    {
      "type": "http",
      "direction": "out",
      "name": "res"
    }
  ]
}
```

## host.json

### Overview

The `host.json` file contains **global configuration options** that affect all functions in a function app.

**Location:** Root of the function app project

### Basic Structure

```json
{
  "version": "2.0",
  "logging": {
    "logLevel": {
      "default": "Information",
      "Host.Results": "Error",
      "Function": "Error",
      "Host.Aggregator": "Trace"
    },
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "maxTelemetryItemsPerSecond": 20
      }
    }
  },
  "functionTimeout": "00:05:00",
  "extensions": {
    "http": {
      "routePrefix": "api",
      "maxOutstandingRequests": 200,
      "maxConcurrentRequests": 100
    },
    "queues": {
      "maxPollingInterval": "00:00:02",
      "visibilityTimeout": "00:00:30",
      "batchSize": 16,
      "maxDequeueCount": 5,
      "newBatchThreshold": 8
    },
    "cosmosDB": {
      "connectionMode": "Gateway",
      "protocol": "Https"
    }
  }
}
```

### Common Configuration Sections

#### Function Timeout

```json
{
  "version": "2.0",
  "functionTimeout": "00:10:00"
}
```

**Timeout Limits by Plan:**
| Plan | Default | Maximum |
|------|---------|---------|
| Consumption | 5 minutes | 10 minutes |
| Premium | 30 minutes | Unlimited |
| Dedicated | 30 minutes | Unlimited |

#### HTTP Settings

```json
{
  "version": "2.0",
  "extensions": {
    "http": {
      "routePrefix": "api",
      "maxOutstandingRequests": 200,
      "maxConcurrentRequests": 100,
      "dynamicThrottlesEnabled": true,
      "hsts": {
        "isEnabled": true,
        "maxAge": "10"
      }
    }
  }
}
```

#### Queue Settings

```json
{
  "version": "2.0",
  "extensions": {
    "queues": {
      "maxPollingInterval": "00:00:02",
      "visibilityTimeout": "00:00:30",
      "batchSize": 16,
      "maxDequeueCount": 5,
      "newBatchThreshold": 8
    }
  }
}
```

#### Logging Configuration

```json
{
  "version": "2.0",
  "logging": {
    "fileLoggingMode": "debugOnly",
    "logLevel": {
      "default": "Information",
      "Host": "Error",
      "Function": "Error",
      "Host.Aggregator": "Information"
    },
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "maxTelemetryItemsPerSecond": 20,
        "excludedTypes": "Request"
      }
    }
  }
}
```

## local.settings.json

### Overview

The `local.settings.json` file stores **app settings, connection strings, and settings** used by local development tools.

**Important:** This file is **not deployed** to Azure. It's used only for local development.

### Structure

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "node",
    "MyCustomSetting": "value",
    "CosmosDBConnection": "AccountEndpoint=https://...",
    "ServiceBusConnection": "Endpoint=sb://..."
  },
  "Host": {
    "LocalHttpPort": 7071,
    "CORS": "*",
    "CORSCredentials": false
  },
  "ConnectionStrings": {
    "SQLConnection": "Server=..."
  }
}
```

### Properties

| Property | Description |
|----------|-------------|
| `IsEncrypted` | Whether settings are encrypted |
| `Values` | Collection of application settings (key-value pairs) |
| `Host` | Settings for local Function host |
| `ConnectionStrings` | Connection strings (use `Values` for Azure) |

### Required Settings

```json
{
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "dotnet|node|python|java|powershell"
  }
}
```

**FUNCTIONS_WORKER_RUNTIME Options:**
- `dotnet` - .NET (C#, F#)
- `dotnet-isolated` - .NET isolated worker
- `node` - JavaScript/TypeScript
- `python` - Python
- `java` - Java
- `powershell` - PowerShell

## Practice Question

### Question: Azure Functions Configuration File

**Scenario:**
You are developing an Azure Functions application.

**Question:**
Azure Functions store their configuration settings in which file?

**Options:**

1. ✅ function.json
   - **Correct**: The `function.json` file defines the function's trigger, bindings, and other configuration settings. Every function has one and only one trigger. The runtime uses this config file to determine the events to monitor and how to pass data into and return data from a function execution.

2. ❌ default.js
   - **Incorrect**: There is no `default.js` configuration file in Azure Functions. This is not a standard Azure Functions file.

3. ❌ index.js
   - **Incorrect**: The `index.js` file typically contains the function code in JavaScript/Node.js functions, not the configuration. Configuration is stored in `function.json`.

4. ❌ web.config
   - **Incorrect**: `web.config` is used in traditional ASP.NET applications for IIS configuration. While it may exist in some Azure Functions deployments for specific IIS settings, it is not the primary configuration file for Azure Functions.

## function.json vs Attributes/Decorators

### Scripting Languages (JavaScript, Python, PowerShell)

For scripting languages, `function.json` is required and must be created manually:

**Folder Structure:**
```
MyFunctionApp/
├── host.json
├── local.settings.json
├── HttpTriggerFunction/
│   ├── function.json
│   └── index.js (or __init__.py)
└── TimerTriggerFunction/
    ├── function.json
    └── index.js (or __init__.py)
```

### Compiled Languages (C#, Java)

For compiled languages, you can use attributes/decorators instead of `function.json`:

**C# Example:**
```csharp
public static class MyFunction
{
    [FunctionName("HttpTriggerFunction")]
    public static async Task<IActionResult> Run(
        [HttpTrigger(AuthorizationLevel.Function, "get", "post")] HttpRequest req,
        ILogger log)
    {
        log.LogInformation("C# HTTP trigger function processed a request.");
        return new OkObjectResult("Hello!");
    }
}
```

The `function.json` is generated automatically during the build process for compiled languages.

**Java Example:**
```java
public class Function {
    @FunctionName("HttpTriggerFunction")
    public HttpResponseMessage run(
        @HttpTrigger(
            name = "req",
            methods = {HttpMethod.GET, HttpMethod.POST},
            authLevel = AuthorizationLevel.FUNCTION
        ) HttpRequestMessage<Optional<String>> request,
        final ExecutionContext context
    ) {
        context.getLogger().info("Java HTTP trigger processed a request.");
        return request.createResponseBuilder(HttpStatus.OK)
            .body("Hello!")
            .build();
    }
}
```

## Configuration Hierarchy

Azure Functions configuration follows this precedence (highest to lowest):

1. **Environment Variables** (Azure Portal app settings)
2. **local.settings.json** (local development only)
3. **host.json** (runtime configuration)
4. **function.json** (function-specific configuration)

## Common Configuration Scenarios

### Scenario 1: Disable a Function

**Using function.json:**
```json
{
  "disabled": true,
  "bindings": [...]
}
```

**Using App Settings:**
Set `AzureWebJobs.<FUNCTION_NAME>.Disabled` to `true`

### Scenario 2: Configure CORS for Local Development

**local.settings.json:**
```json
{
  "Host": {
    "CORS": "http://localhost:3000,http://localhost:4200",
    "CORSCredentials": true
  }
}
```

### Scenario 3: Set Custom Route Prefix

**host.json:**
```json
{
  "version": "2.0",
  "extensions": {
    "http": {
      "routePrefix": "myapi"
    }
  }
}
```

Result: Functions accessible at `/myapi/functionname` instead of `/api/functionname`

### Scenario 4: Remove API Route Prefix

**host.json:**
```json
{
  "version": "2.0",
  "extensions": {
    "http": {
      "routePrefix": ""
    }
  }
}
```

Result: Functions accessible at `/functionname` directly

## Securing Configuration

### Best Practices

1. **Never commit secrets to source control**
   - Add `local.settings.json` to `.gitignore`
   - Use Azure Key Vault for production secrets

2. **Use Azure Key Vault references**
   ```json
   {
     "Values": {
       "MySecret": "@Microsoft.KeyVault(SecretUri=https://myvault.vault.azure.net/secrets/MySecret/)"
     }
   }
   ```

3. **Use Managed Identity**
   - Enable system-assigned or user-assigned managed identity
   - Grant appropriate permissions to access resources

4. **Separate environments**
   - Use different app settings for dev/staging/production
   - Use deployment slots for testing configuration changes

## Deployment Considerations

### Files Deployed vs Not Deployed

| File | Deployed | Notes |
|------|----------|-------|
| `function.json` | ✅ Yes | Required for scripted functions |
| `host.json` | ✅ Yes | Global runtime configuration |
| `local.settings.json` | ❌ No | Local development only |
| `proxies.json` | ✅ Yes | If using proxies (deprecated in v4) |

### Deploying App Settings

App settings from `local.settings.json` must be configured separately in Azure:

**Azure CLI:**
```bash
# Set single setting
az functionapp config appsettings set \
  --name MyFunctionApp \
  --resource-group MyResourceGroup \
  --settings "MySetting=MyValue"

# Set multiple settings from JSON file
az functionapp config appsettings set \
  --name MyFunctionApp \
  --resource-group MyResourceGroup \
  --settings @settings.json
```

**Azure Portal:**
1. Navigate to Function App
2. Go to Configuration > Application settings
3. Add/edit settings

## Troubleshooting

### Common Issues

**Problem**: Function not triggering
- Check `function.json` for correct trigger configuration
- Verify connection strings in app settings
- Ensure function is not disabled (`"disabled": false`)

**Problem**: Settings not found in Azure
- Remember `local.settings.json` is not deployed
- Configure app settings in Azure Portal or via CLI

**Problem**: Build errors with attributes
- Ensure NuGet packages are installed
- Check attribute syntax matches the binding version

**Problem**: Host.json settings not applied
- Verify JSON syntax is valid
- Check `"version": "2.0"` is specified
- Restart function app after changes

## Additional Resources

- [Azure Functions triggers and bindings](https://docs.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings)
- [host.json reference](https://docs.microsoft.com/en-us/azure/azure-functions/functions-host-json)
- [Work with Azure Functions Core Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local)
- [Azure Functions app settings reference](https://docs.microsoft.com/en-us/azure/azure-functions/functions-app-settings)

## Custom Handlers

### Overview

**Custom handlers** are lightweight web servers that receive events from the Azure Functions host. They allow you to use **any language or runtime** that supports HTTP primitives to implement Azure Functions, even if that language is not natively supported by Azure Functions.

### Key Concepts

- **Purpose**: Enable Azure Functions with languages/runtimes not natively supported (e.g., Go, Rust, R, Deno)
- **Architecture**: A custom handler is a web server that receives HTTP requests from the Functions host
- **How it works**: The Functions host forwards trigger and binding data to your custom handler via HTTP requests

### How Custom Handlers Work

```
┌─────────────────────────────────────────────────────────────────┐
│                    Azure Functions Host                         │
├─────────────────────────────────────────────────────────────────┤
│  Trigger Event (HTTP, Queue, Timer, etc.)                       │
│           ↓                                                     │
│  Functions Host receives event                                  │
│           ↓                                                     │
│  HTTP Request sent to Custom Handler (localhost:port)           │
│           ↓                                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Custom Handler (Your Web Server)                        │   │
│  │  - Written in any language (Go, Rust, R, etc.)           │   │
│  │  - Receives HTTP POST with trigger/binding data          │   │
│  │  - Processes the request                                 │   │
│  │  - Returns HTTP response with output binding data        │   │
│  └─────────────────────────────────────────────────────────┘   │
│           ↓                                                     │
│  Functions Host receives response                               │
│           ↓                                                     │
│  Output bindings executed                                       │
└─────────────────────────────────────────────────────────────────┘
```

### Configuration

Custom handlers are configured in the `host.json` file:

```json
{
  "version": "2.0",
  "customHandler": {
    "description": {
      "defaultExecutablePath": "handler",
      "workingDirectory": "",
      "arguments": []
    },
    "enableForwardingHttpRequest": false
  }
}
```

**Configuration Properties:**

| Property | Description |
|----------|-------------|
| `defaultExecutablePath` | The executable to start as the custom handler process |
| `workingDirectory` | Working directory for the executable |
| `arguments` | Command-line arguments to pass to the executable |
| `enableForwardingHttpRequest` | For HTTP triggers only, forwards the original HTTP request instead of the custom handler payload |

### Example: Go Custom Handler

**handler.go:**
```go
package main

import (
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "os"
)

type InvokeRequest struct {
    Data     map[string]json.RawMessage
    Metadata map[string]interface{}
}

type InvokeResponse struct {
    Outputs     map[string]interface{}
    Logs        []string
    ReturnValue interface{}
}

func helloHandler(w http.ResponseWriter, r *http.Request) {
    var invokeRequest InvokeRequest
    json.NewDecoder(r.Body).Decode(&invokeRequest)

    returnValue := "Hello from Go custom handler!"
    
    invokeResponse := InvokeResponse{
        Outputs:     make(map[string]interface{}),
        Logs:        []string{"Function executed successfully"},
        ReturnValue: returnValue,
    }
    
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(invokeResponse)
}

func main() {
    customHandlerPort, exists := os.LookupEnv("FUNCTIONS_CUSTOMHANDLER_PORT")
    if !exists {
        customHandlerPort = "8080"
    }
    
    http.HandleFunc("/api/HttpTrigger", helloHandler)
    
    fmt.Println("Go custom handler listening on port", customHandlerPort)
    log.Fatal(http.ListenAndServe(":"+customHandlerPort, nil))
}
```

**host.json:**
```json
{
  "version": "2.0",
  "customHandler": {
    "description": {
      "defaultExecutablePath": "handler.exe",
      "workingDirectory": "",
      "arguments": []
    }
  },
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[3.*, 4.0.0)"
  }
}
```

**function.json (HttpTrigger folder):**
```json
{
  "bindings": [
    {
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "methods": ["get", "post"]
    },
    {
      "type": "http",
      "direction": "out",
      "name": "res"
    }
  ]
}
```

### Supported Languages via Custom Handlers

Custom handlers enable Azure Functions with virtually any language that can:
- Create an HTTP server
- Process JSON requests
- Return JSON responses

**Examples of languages you can use:**
- Go
- Rust
- R
- Deno
- PHP
- Ruby
- Swift
- Perl
- Any other language with HTTP capabilities

### Practice Question

**Question:**
Which feature of Azure Functions allows you to use a runtime not currently supported natively by Azure?

**Options:**

1. ✅ **Custom Handlers**
   - **Correct**: Custom handlers are lightweight web servers that receive events from the Azure Functions host. While Azure Functions features many language handlers by default (C#, JavaScript, Python, Java, PowerShell), there are cases where you may want to use other languages or runtimes. Any language that supports HTTP primitives can implement a custom handler.

2. ❌ Durable Functions
   - **Incorrect**: Durable Functions is an extension of Azure Functions that lets you write stateful functions in a serverless environment. It's used for orchestrating workflows and managing state, not for adding support for additional programming languages or runtimes.

3. ❌ Serverless Functions
   - **Incorrect**: Serverless Functions is not a specific feature name in Azure Functions. Azure Functions itself is a serverless compute service, but there is no feature called "Serverless Functions" that enables additional runtime support.

4. ❌ SignalR
   - **Incorrect**: SignalR is a library for adding real-time web functionality to applications. Azure Functions has SignalR Service bindings for building real-time applications, but SignalR does not provide support for additional programming languages or runtimes.

**Reference**: [Azure Functions Custom Handlers](https://docs.microsoft.com/en-us/azure/azure-functions/functions-custom-handlers)

### Custom Handlers vs Native Language Support

| Aspect | Native Language Support | Custom Handlers |
|--------|------------------------|-----------------|
| **Languages** | C#, JavaScript, Python, Java, PowerShell, TypeScript | Any language with HTTP support |
| **Performance** | Optimized for the runtime | Slightly more overhead due to HTTP communication |
| **Configuration** | Minimal setup | Requires host.json customHandler configuration |
| **Bindings** | Full support via attributes/decorators | Full support via function.json |
| **Cold Start** | Standard | Depends on executable startup time |
| **Debugging** | Native IDE support | Requires custom debugging setup |

### Best Practices for Custom Handlers

1. **Keep the handler lightweight**: Minimize startup time to reduce cold starts
2. **Handle errors gracefully**: Return appropriate HTTP status codes and error messages
3. **Log effectively**: Include logs in the response for debugging
4. **Use environment variables**: Read `FUNCTIONS_CUSTOMHANDLER_PORT` for the port to listen on
5. **Test locally**: Use Azure Functions Core Tools for local development and testing

## Related Topics

- Azure Functions hosting plans
- Azure Functions triggers and bindings
- Deployment and CI/CD
- Monitoring with Application Insights

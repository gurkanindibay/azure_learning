# Azure Functions - Configuration Files

## Overview

Azure Functions use configuration files to define function behavior, triggers, bindings, and application settings. Understanding these configuration files is essential for developing, deploying, and managing Azure Functions effectively.

## Table of Contents

- [Key Configuration Files](#key-configuration-files)
- [function.json](#functionjson)
  - [Overview](#overview-1)
  - [Structure](#structure)
  - [Properties](#properties)
  - [Bindings Array](#bindings-array)
  - [Common Trigger Examples](#common-trigger-examples)
  - [Input and Output Bindings](#input-and-output-bindings)
- [host.json](#hostjson)
  - [Overview](#overview-2)
  - [Basic Structure](#basic-structure)
  - [Common Configuration Sections](#common-configuration-sections)
  - [Practice Question: Reducing Telemetry Volume from Host.Aggregator](#practice-question-reducing-telemetry-volume-from-hostaggregator)
- [local.settings.json](#localsettingsjson)
  - [Overview](#overview-3)
  - [Structure](#structure-1)
  - [Properties](#properties-1)
  - [Required Settings](#required-settings)
- [Practice Question](#practice-question)
- [function.json vs Attributes/Decorators](#functionjson-vs-attributesdecorators)
- [Configuration Hierarchy](#configuration-hierarchy)
- [Common Configuration Scenarios](#common-configuration-scenarios)
- [Securing Configuration](#securing-configuration)
- [Deployment Considerations](#deployment-considerations)
  - [Practice Question: Deploying Functions with Custom Dependencies](#practice-question-deploying-functions-with-custom-dependencies)
- [Troubleshooting](#troubleshooting)
- [Additional Resources](#additional-resources)
- [Custom Handlers](#custom-handlers)
  - [Overview](#overview-4)
  - [Key Concepts](#key-concepts)
  - [How Custom Handlers Work](#how-custom-handlers-work)
  - [Configuration](#configuration)
  - [Custom Handler Requirements](#custom-handler-requirements)
  - [Example: Go Custom Handler](#example-go-custom-handler)
  - [Supported Languages via Custom Handlers](#supported-languages-via-custom-handlers)
  - [Practice Question](#practice-question-1)
  - [Custom Handlers vs Native Language Support](#custom-handlers-vs-native-language-support)
  - [Best Practices for Custom Handlers](#best-practices-for-custom-handlers)
- [Function App Lifecycle and Cleanup Operations](#function-app-lifecycle-and-cleanup-operations)
  - [Handling Shutdown and Cleanup](#handling-shutdown-and-cleanup)
  - [Practice Question: Cleanup Operations During Shutdown](#practice-question-cleanup-operations-during-shutdown)
- [Related Topics](#related-topics)

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

### Trigger Limit: Exactly One Per Function

**Key Concept**: A function must have **exactly one trigger**. Triggers are what cause a function to run - they define how a function is invoked. Triggers have associated data, which is often provided as the payload of the function.

**Important Rules:**
- A function **cannot** have zero triggers
- A function **cannot** have multiple triggers
- Each function has **exactly one** trigger

This is a fundamental design principle of Azure Functions that ensures clear, predictable function invocation.

### Practice Question: Number of Triggers Per Function

**Question:**

How many triggers can an Azure Function have?

**Options:**

A) Any number

B) 0 or 1

C) 32 maximum

D) Exactly one ✅

---

**Correct Answer: D) Exactly one**

---

**Explanation:**

Triggers are what cause a function to run. A trigger defines how a function is invoked and **a function must have exactly one trigger**. Triggers have associated data, which is often provided as the payload of the function.

| Option | Why Correct/Incorrect |
|--------|----------------------|
| **A) Any number** | ❌ Incorrect - Functions are limited to exactly one trigger |
| **B) 0 or 1** | ❌ Incorrect - A function cannot have zero triggers; it must have exactly one |
| **C) 32 maximum** | ❌ Incorrect - There is no such limit; the rule is exactly one trigger |
| **D) Exactly one** | ✅ **Correct** - Every function must have exactly one trigger that defines how it's invoked |

**Visual Example:**

```
✅ Valid Function Configuration:
┌─────────────────────────────────────┐
│ Function: ProcessOrder              │
├─────────────────────────────────────┤
│ Trigger: Queue Trigger (1)          │  ← Exactly one trigger
│ Input Binding: Cosmos DB            │  ← Multiple bindings OK
│ Output Binding: Blob Storage        │
│ Output Binding: SendGrid Email      │
└─────────────────────────────────────┘

❌ Invalid - No Trigger:
┌─────────────────────────────────────┐
│ Function: ProcessOrder              │
├─────────────────────────────────────┤
│ Input Binding: Cosmos DB            │  ← No trigger = Invalid!
│ Output Binding: Blob Storage        │
└─────────────────────────────────────┘

❌ Invalid - Multiple Triggers:
┌─────────────────────────────────────┐
│ Function: ProcessOrder              │
├─────────────────────────────────────┤
│ Trigger: HTTP Trigger               │  ← Two triggers = Invalid!
│ Trigger: Queue Trigger              │
│ Output Binding: Blob Storage        │
└─────────────────────────────────────┘
```

**Triggers vs Bindings:**

| Aspect | Trigger | Bindings |
|--------|---------|----------|
| **Purpose** | Causes function to run | Provides input/output data |
| **Count per function** | **Exactly 1** | 0 to many |
| **Direction** | Always `in` | `in`, `out`, or `inout` |
| **Examples** | HTTP, Queue, Timer, Blob, Cosmos DB | Blob, Cosmos DB, Table, SendGrid |

**Reference:** [Azure Functions triggers and bindings](https://docs.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings?tabs=csharp)

---

#### Direction Property Values

All triggers and bindings have a `direction` property in the `function.json` file. The possible values are:

| Value | Description |
|-------|-------------|
| `in` | **Input direction** - Data flows into the function. All triggers use this direction. Input bindings also use this direction to read data from external sources. |
| `out` | **Output direction** - Data flows out of the function. Output bindings use this direction to write data to external destinations. |
| `inout` | **Bidirectional** - Special direction that allows both reading and writing. When using `inout`, only the **Advanced editor** is available via the Integrate tab in the Azure portal. |

**Key Points:**
- For **triggers**, the direction is always `in`
- **Input bindings** use `in`
- **Output bindings** use `out`
- Some bindings support the special `inout` direction for bidirectional data flow

**Reference**: [Azure Functions triggers and bindings](https://docs.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings?tabs=csharp)

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

##### HTTP Trigger - Response Types in C#

When developing HTTP-triggered Azure Functions in C#, you have several options for returning responses. Understanding the appropriate response type is important for building correct and idiomatic functions.

**Common Response Types:**

| Response Type | Status Code | Use Case |
|---------------|-------------|----------|
| `OkObjectResult` | 200 | Successful request with JSON response body |
| `OkResult` | 200 | Successful request without response body |
| `BadRequestObjectResult` | 400 | Client error with error message |
| `NotFoundObjectResult` | 404 | Resource not found |
| `JsonResult` | Configurable | JSON response with custom status code |
| `ContentResult` | Configurable | Raw content with custom content type |

**Recommended Approach:**

For returning a JSON response with a 200 status code, use `OkObjectResult`:

```csharp
public static async Task<IActionResult> Run(HttpRequest req, ILogger log)
{
    return new OkObjectResult(new { message = "Success" });
}
```

The `OkObjectResult` automatically:
- Sets the status code to 200
- Serializes the object to JSON
- Sets the appropriate `Content-Type` header

---

##### Practice Question: HTTP Trigger JSON Response

**Question:**

You are developing an Azure Function that is triggered by an HTTP request. The function should return a JSON response with a status code of 200 when the request is successfully processed. Which of the following code snippets correctly implements this functionality in C#?

**Options:**

A) 
```csharp
public static async Task<IActionResult> Run(HttpRequest req, ILogger log)
{
    return new JsonResult(new { message = "Success" }) { StatusCode = 200 };
}
```

B) 
```csharp
public static async Task<IActionResult> Run(HttpRequest req, ILogger log)
{
    return new BadRequestObjectResult("An error occurred");
}
```

C) 
```csharp
public static async Task<IActionResult> Run(HttpRequest req, ILogger log)
{
    return new ContentResult { Content = "{\"message\":\"Success\"}", ContentType = "application/json" };
}
```

D) ✅
```csharp
public static async Task<IActionResult> Run(HttpRequest req, ILogger log)
{
    return new OkObjectResult(new { message = "Success" });
}
```

---

**Correct Answer: D) OkObjectResult**

---

**Explanation:**

| Option | Why Correct/Incorrect |
|--------|----------------------|
| **A) JsonResult** | ❌ Incorrect - While `JsonResult` returns a JSON response and can set the status code to 200, it may not be the most appropriate choice for returning a simple JSON response in this scenario. `OkObjectResult` is more idiomatic for Azure Functions HTTP triggers. |
| **B) BadRequestObjectResult** | ❌ Incorrect - `BadRequestObjectResult` returns a 400 status code, indicating a client error. This is not the correct response for successful request processing. It should return a 200 status code with a success message instead. |
| **C) ContentResult** | ❌ Incorrect - `ContentResult` can return a JSON response with the correct content type, but it lacks the explicit setting of the status code to 200. Without setting `StatusCode = 200`, the response may not correctly indicate successful processing. Additionally, manually constructing the JSON string is error-prone and less maintainable. |
| **D) OkObjectResult** | ✅ **Correct** - `OkObjectResult` is the recommended way to return a 200 response with a JSON body. It automatically sets the status code to 200, serializes the object to JSON, and sets the appropriate content type header. |

**Why OkObjectResult is Preferred:**

1. **Automatic Status Code**: Sets HTTP 200 OK automatically
2. **Content Negotiation**: Handles JSON serialization transparently
3. **Type Safety**: Works with strongly-typed objects
4. **Idiomatic**: Follows ASP.NET Core conventions used in Azure Functions
5. **Clean Code**: Requires minimal boilerplate

**Complete Example:**
```csharp
[FunctionName("HttpTriggerFunction")]
public static async Task<IActionResult> Run(
    [HttpTrigger(AuthorizationLevel.Function, "get", "post")] HttpRequest req,
    ILogger log)
{
    log.LogInformation("C# HTTP trigger function processed a request.");
    
    // Successfully processed - return 200 with JSON
    return new OkObjectResult(new { message = "Success", timestamp = DateTime.UtcNow });
}
```

**Reference:** [Azure Functions HTTP trigger](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-http-webhook-trigger)

---

##### HTTP Trigger Authorization Levels

Azure Functions HTTP triggers support different authorization levels to control access to the function. The `authLevel` property in `function.json` (or the `AuthorizationLevel` enum in C# attributes) determines what keys, if any, are required to invoke the function.

**Authorization Levels:**

| Level | Description | Key Required |
|-------|-------------|--------------|
| `anonymous` | No authentication required. Any request can trigger the function. | None |
| `function` | A function-specific API key is required. Each function has its own unique key. | Function key |
| `admin` | The master key (host key) is required. Provides access to all functions in the app. | Master/Host key |

**Key Characteristics:**

| Level | Security | Use Case |
|-------|----------|----------|
| **anonymous** | ❌ No protection | Public APIs, webhooks from external services, testing |
| **function** | ✅ Function-level protection | Most production HTTP endpoints, per-function access control |
| **admin** | ✅✅ App-level protection | Administrative endpoints, operations affecting the entire app |

**Configuration Examples:**

```json
// function.json - Anonymous access (no key required)
{
  "bindings": [
    {
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "authLevel": "anonymous",
      "methods": ["get"]
    }
  ]
}

// function.json - Function key required
{
  "bindings": [
    {
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "authLevel": "function",
      "methods": ["get", "post"]
    }
  ]
}

// function.json - Admin/Master key required
{
  "bindings": [
    {
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "authLevel": "admin",
      "methods": ["post"]
    }
  ]
}
```

**C# Attribute Examples:**

```csharp
// Anonymous access
[HttpTrigger(AuthorizationLevel.Anonymous, "get")]

// Function key required
[HttpTrigger(AuthorizationLevel.Function, "get", "post")]

// Admin key required
[HttpTrigger(AuthorizationLevel.Admin, "post")]
```

**How to Pass Keys:**

Keys can be passed to the function in two ways:
1. **Query string parameter**: `?code=<API_KEY>`
2. **HTTP header**: `x-functions-key: <API_KEY>`

**Example Requests:**

```bash
# Anonymous - no key needed
curl https://myapp.azurewebsites.net/api/publicfunction

# Function level - with function key
curl "https://myapp.azurewebsites.net/api/myfunction?code=<FUNCTION_KEY>"

# Or using header
curl -H "x-functions-key: <FUNCTION_KEY>" https://myapp.azurewebsites.net/api/myfunction

# Admin level - with master key
curl -H "x-functions-key: <MASTER_KEY>" https://myapp.azurewebsites.net/api/adminfunction
```

**Best Practices:**
- Use `function` level for most production HTTP endpoints
- Use `anonymous` only when the endpoint needs to be publicly accessible or when using alternative authentication (e.g., Azure AD, API Management)
- Reserve `admin` level for administrative or management operations only
- Consider using Azure API Management or Azure AD for more robust authentication scenarios

---

##### Practice Question: HTTP Trigger Authorization Level

**Question:**

You need to create an Azure Functions HTTP trigger that requires authentication. The function should only accept requests with a valid function key. Which authorization level should you configure?

**Options:**

A) user

B) admin

C) function ✅

D) anonymous

---

**Correct Answer: C) function**

---

**Explanation:**

| Option | Why Correct/Incorrect |
|--------|----------------------|
| **A) user** | ❌ Incorrect - The `user` authorization level is not a valid option for HTTP trigger authorization in Azure Functions. The valid levels are `anonymous`, `function`, and `admin` for controlling access to HTTP-triggered functions. |
| **B) admin** | ❌ Incorrect - The `admin` authorization level requires the master key (host key) which provides access to all functions in the app. This is more permissive than needed and should be reserved for administrative operations only. It doesn't provide function-specific authentication. |
| **C) function** | ✅ **Correct** - The `function` authorization level requires a function-specific API key to be provided in the request. This provides authentication at the function level, allowing different keys for different functions while maintaining security. |
| **D) anonymous** | ❌ Incorrect - The `anonymous` authorization level allows any request to trigger the function without requiring any authentication or API keys, which does not meet the requirement for authentication with a valid function key. |

**Visual Comparison:**

```
Authorization Level: anonymous
├── Key Required: None
├── Security: ❌ No protection
└── Use Case: Public endpoints

Authorization Level: function ✅
├── Key Required: Function-specific key
├── Security: ✅ Function-level protection
└── Use Case: Most production HTTP endpoints

Authorization Level: admin
├── Key Required: Master/Host key
├── Security: ✅✅ App-level protection
└── Use Case: Administrative operations only

Authorization Level: user
├── ❌ NOT A VALID OPTION
└── Does not exist in Azure Functions
```

**Reference:** [Azure Functions HTTP trigger - Authorization keys](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-http-webhook-trigger#authorization-keys)

---

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

##### CRON Expression Format

Azure Functions Timer Triggers use **NCRONTAB expressions** (6-field format) to define schedules. The format is:

```
{second} {minute} {hour} {day} {month} {day-of-week}
```

| Field | Allowed Values | Special Characters |
|-------|----------------|-------------------|
| Second | 0-59 | , - * / |
| Minute | 0-59 | , - * / |
| Hour | 0-23 | , - * / |
| Day | 1-31 | , - * / |
| Month | 1-12 | , - * / |
| Day of Week | 0-6 (0 = Sunday) | , - * / |

**Common CRON Expression Examples:**

| Expression | Description |
|------------|-------------|
| `0 */5 * * * *` | Every 5 minutes |
| `0 0 * * * *` | Every hour (at minute 0) |
| `0 5 * * * *` | At 5 minutes past every hour |
| `0 0 0 * * *` | Every day at midnight |
| `0 0 9 * * 1-5` | Every weekday at 9:00 AM |
| `0 30 9 * * *` | Every day at 9:30 AM |

---

##### Practice Question: Timer Trigger CRON Expression

**Question:**

You need to configure an Azure Function to run on a schedule using a CRON expression. Your requirement is to have the function execute at 5 minutes past every hour, every day of the week. Which of the following CRON expressions should you use?

**Options:**

A) `0 5 * * *`

B) `0/5 * * * *`

C) `5 * * * *` ✅

D) `5 * * * 1-5`

---

**Correct Answer: C) `5 * * * *`**

---

**Explanation:**

| Option | Expression | Why Correct/Incorrect |
|--------|------------|----------------------|
| **A) `0 5 * * *`** | 5-field format | ❌ Incorrect - This is a standard 5-field CRON expression (not Azure's 6-field NCRONTAB format). In 5-field format, this specifies execution at 5:00 AM (5 hours past midnight) every day, not 5 minutes past every hour. |
| **B) `0/5 * * * *`** | Every 5 minutes | ❌ Incorrect - The `0/5` in the first field means "starting at 0, every 5 units." This specifies the function should run every 5 minutes (at 0, 5, 10, 15, etc. minutes past each hour), not just at 5 minutes past each hour. |
| **C) `5 * * * *`** | 5 minutes past every hour | ✅ **Correct** - In Azure Functions' NCRONTAB format, the first field is seconds and the second is minutes. However, when only 5 fields are provided, Azure interprets this as `0 5 * * * *` (at second 0, minute 5, every hour, every day, every month, every day of week). The `*` wildcards in the subsequent fields ensure the function runs every hour, every day of the week. |
| **D) `5 * * * 1-5`** | 5 minutes past every hour, weekdays only | ❌ Incorrect - The `1-5` in the day-of-week field restricts execution to Monday through Friday only. This does not meet the requirement of running every day of the week (including weekends). |

**Visual Schedule Comparison:**

```
Expression A: 0 5 * * * (5-field CRON)
├── Runs at: 5:00 AM daily
└── ❌ Does not run hourly

Expression B: 0/5 * * * * (Azure 6-field)
├── Runs at: :00, :05, :10, :15, :20, :25, :30, :35, :40, :45, :50, :55
└── ❌ Runs every 5 minutes, not just at :05

Expression C: 5 * * * * (Correct)
├── Runs at: 00:05, 01:05, 02:05, ..., 23:05
└── ✅ Runs at 5 minutes past every hour, every day

Expression D: 5 * * * 1-5
├── Runs at: 00:05, 01:05, 02:05, ..., 23:05
├── But only Monday through Friday
└── ❌ Does not run on weekends
```

**Reference:** [Timer trigger for Azure Functions](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer?tabs=csharp#ncrontab-expressions)

---

##### Practice Question: Timer Trigger - Daily Execution at Specific Time

**Question:**

You have a timer-triggered Azure Functions app that must run exactly at 2:30 AM UTC every day. Which CRON expression should you use in the function.json binding?

**Options:**

A) `0 2 30 * * *`

B) `30 2 * * *`

C) `* 30 2 * * *`

D) `0 30 2 * * *` ✅

---

**Correct Answer: D) `0 30 2 * * *`**

---

**Explanation:**

Azure Functions uses a **six-field CRON format** (NCRONTAB) where the fields represent:
```
{second} {minute} {hour} {day} {month} {day-of-week}
```

| Option | Expression | Why Correct/Incorrect |
|--------|------------|----------------------|
| **A) `0 2 30 * * *`** | 0 seconds, 2 minutes, 30 hours | ❌ Incorrect - This expression would attempt to run at 2:00 AM on the 30th day of each month (interpreting 30 as day field due to invalid hour value), not at 2:30 AM daily. The hour and day fields are incorrectly positioned. |
| **B) `30 2 * * *`** | 5-field format | ❌ Incorrect - This is a five-field CRON expression missing the seconds field. Azure Functions requires a six-field CRON expression (NCRONTAB format), so this format would not be valid. |
| **C) `* 30 2 * * *`** | Every second at 2:30 | ❌ Incorrect - Using `*` for seconds means the function would trigger every second during the minute 2:30 AM, resulting in 60 executions instead of one single execution. |
| **D) `0 30 2 * * *`** | 0 seconds, 30 minutes, 2 hours | ✅ **Correct** - This CRON expression represents '0 seconds, 30 minutes, 2 hours' which translates to exactly 2:30:00 AM every day. The wildcards `*` for day, month, and day-of-week ensure it runs every day. |

**Visual Breakdown of the Correct Expression:**

```
0 30 2 * * *
│ │  │ │ │ │
│ │  │ │ │ └── Day of week: * (every day of the week)
│ │  │ │ └──── Month: * (every month)
│ │  │ └────── Day: * (every day of the month)
│ │  └──────── Hour: 2 (2 AM)
│ └─────────── Minute: 30 (30 minutes)
└───────────── Second: 0 (0 seconds)

Result: Runs at exactly 02:30:00 AM UTC every day
```

**Common CRON Mistakes:**

| Mistake | Problem |
|---------|---------|
| Using 5-field format | Azure Functions requires 6 fields (includes seconds) |
| Swapping hour and minute | Results in wrong execution time |
| Using `*` for seconds | Causes 60 executions per minute instead of 1 |

**Reference:** [Timer trigger for Azure Functions - NCRONTAB expressions](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer?tabs=csharp#ncrontab-expressions)

---

##### Timer Trigger - TimerInfo Object

When using a Timer Trigger, the function receives a `TimerInfo` object that provides information about the timer invocation. This object includes useful properties for handling late executions.

**TimerInfo Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `Schedule` | TimerSchedule | The timer schedule |
| `ScheduleStatus` | ScheduleStatus | Status information including last/next scheduled times |
| `IsPastDue` | bool | `true` if the function invocation is later than scheduled |

**C# Example - Checking for Late Execution:**
```csharp
[FunctionName("TimerTriggerCSharp")]
public static void Run(
    [TimerTrigger("0 */5 * * * *")] TimerInfo myTimer, 
    ILogger log)
{
    if (myTimer.IsPastDue)
    {
        log.LogInformation("Timer is running late!");
    }
    
    log.LogInformation($"C# Timer trigger function executed at: {DateTime.Now}");
}
```

**When is a Timer Past Due?**
- The function host was stopped or restarted during a scheduled execution
- The function was delayed due to resource constraints
- The app was scaled down and missed a scheduled trigger
- The function app was in a cold start state

---

##### Practice Question: Timer Trigger - IsPastDue

**Question:**

Your function uses the following code. You want to add a message to the log when the function starts late. What code belongs in the missing line?

```csharp
[FunctionName("TimerTriggerCSharp")]
public static void Run(
    [TimerTrigger("0 */5 * * * *")] TimerInfo myTimer, 
    ILogger log)
{
    // >>>>> LINE MISSING HERE <<<<<
    {
        log.LogInformation("Timer is running late!");
    }
    
    log.LogInformation($"C# Timer trigger function executed at: {DateTime.Now}");
}
```

**Options:**

A) `if (TimerTrigger.IsLate)`

B) `if (myTimer.IsPastDue)` ✅

C) `if (myTimer.TriggerTime < DateTime.Now)`

D) `if (myTimer.IsLate)`

---

**Correct Answer: B) `if (myTimer.IsPastDue)`**

---

**Explanation:**

| Option | Why Correct/Incorrect |
|--------|----------------------|
| **A) `if (TimerTrigger.IsLate)`** | ❌ Incorrect - `TimerTrigger` is the attribute class, not an instance with properties. You cannot access instance properties from the attribute type itself. |
| **B) `if (myTimer.IsPastDue)`** | ✅ **Correct** - The `TimerInfo` object (named `myTimer` in this function) has an `IsPastDue` property that returns `true` if the function execution is later than scheduled. |
| **C) `if (myTimer.TriggerTime < DateTime.Now)`** | ❌ Incorrect - There is no `TriggerTime` property on `TimerInfo`. While the logic seems reasonable, this property does not exist. |
| **D) `if (myTimer.IsLate)`** | ❌ Incorrect - There is no `IsLate` property on `TimerInfo`. The correct property name is `IsPastDue`. |

**Reference:** [Azure Functions Timer Trigger](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer?tabs=csharp#ncrontab-expressions)

---

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

#### Blob Trigger with Event Grid Source

For processing each blob only once (even if updated multiple times), use Event Grid as the source:

```json
{
  "bindings": [
    {
      "type": "blobTrigger",
      "direction": "in",
      "name": "myBlob",
      "path": "samples-workitems/{name}",
      "connection": "AzureWebJobsStorage",
      "source": "EventGrid"
    }
  ]
}
```

#### Practice Question: Blob Deletion Trigger

**Question:**

Is it possible to create a function in Azure that triggers only when a blob is deleted from a storage container?

**Options:**

A) Yes, using Azure Functions with Blob Storage trigger and setting it to listen for deletion events.

B) Yes, using Azure Event Grid to subscribe to blob deletion events and route them to an Azure Function. ✅

C) No, Azure Functions do not support triggers for blob deletion events.

D) Yes, but only if the blob is deleted via an HTTP request to an Azure Function.

---

**Correct Answer: B) Yes, using Azure Event Grid to subscribe to blob deletion events and route them to an Azure Function.**

---

**Explanation:**

| Option | Why Correct/Incorrect |
|--------|----------------------|
| **A) Blob Storage trigger for deletion events** | ❌ Incorrect - Blob Storage triggers only fire once for a **new or updated blob**. They cannot be configured to specifically fire when a blob is deleted, or more than once. The Blob Trigger monitors for blob additions and updates, not deletions. |
| **B) Azure Event Grid for blob deletion events** | ✅ **Correct** - Azure Event Grid can be used to subscribe to blob deletion events (`Microsoft.Storage.BlobDeleted`) in a storage account and route these events to an Azure Function for processing. This allows for the creation of a function that triggers only when a blob is deleted, making it a valid and recommended approach for handling such scenarios. |
| **C) Azure Functions do not support blob deletion triggers** | ❌ Incorrect - Azure Functions do support triggers for blob deletion events, but not through the Blob Storage trigger binding directly. Instead, you use Azure Event Grid subscriptions to capture blob deletion events and route them to an Azure Function. |
| **D) Only via HTTP request** | ❌ Incorrect - While it is possible to trigger a function in Azure when a blob is deleted via an HTTP request (by having your application call an HTTP-triggered function when it deletes a blob), this method is not the most efficient or direct way to achieve this functionality. Using Azure Event Grid to subscribe to blob deletion events and route them to an Azure Function is a more suitable and recommended approach for handling blob deletion triggers. |

---

**Key Difference: Blob Trigger vs Event Grid for Blob Events**

| Aspect | Blob Storage Trigger | Event Grid Integration |
|--------|---------------------|----------------------|
| **New Blob Created** | ✅ Supported | ✅ Supported |
| **Blob Updated** | ✅ Supported (may trigger multiple times) | ✅ Supported |
| **Blob Deleted** | ❌ **Not Supported** | ✅ **Supported** |
| **Event Types** | Limited to create/update | Full control over event types |
| **Delivery** | Polling-based or Event Grid source | Push-based notifications |

---

**Implementation: Triggering on Blob Deletion with Event Grid**

To create a function that triggers when a blob is deleted:

1. **Create an Event Grid System Topic** for your storage account
2. **Create an Event Subscription** filtering for `Microsoft.Storage.BlobDeleted` events
3. **Point the subscription** to an Event Grid-triggered Azure Function

**Example Event Grid Trigger Function (C#):**
```csharp
[FunctionName("BlobDeletedHandler")]
public static void Run(
    [EventGridTrigger] EventGridEvent eventGridEvent,
    ILogger log)
{
    log.LogInformation($"Blob deleted event received");
    log.LogInformation($"Event Type: {eventGridEvent.EventType}");
    log.LogInformation($"Subject: {eventGridEvent.Subject}");
    log.LogInformation($"Data: {eventGridEvent.Data}");
    
    // Process the blob deletion event
}
```

**function.json for Event Grid Trigger:**
```json
{
  "bindings": [
    {
      "type": "eventGridTrigger",
      "direction": "in",
      "name": "eventGridEvent"
    }
  ]
}
```

**Azure CLI - Create Event Subscription for Blob Deleted Events:**
```bash
az eventgrid event-subscription create \
  --name blob-deleted-subscription \
  --source-resource-id /subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{storage-account} \
  --endpoint-type azurefunction \
  --endpoint /subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.Web/sites/{function-app}/functions/BlobDeletedHandler \
  --included-event-types Microsoft.Storage.BlobDeleted
```

**Reference:** [Reacting to Blob storage events](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-blob-event-overview)

---

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

**Queue Settings Properties:**

| Property | Description | Default |
|----------|-------------|---------|
| `maxPollingInterval` | Maximum interval between queue polls | 00:01:00 |
| `visibilityTimeout` | Time a message is invisible after being dequeued | 00:00:00 (auto) |
| `batchSize` | Number of messages to retrieve per poll | 16 |
| `maxDequeueCount` | Number of times to try processing a message before moving to poison queue | 5 |
| `newBatchThreshold` | Threshold for fetching a new batch of messages | batchSize/2 |

#### Handling Poison Messages with Storage Queues

**Poison messages** are messages that cannot be processed successfully after multiple attempts. Azure Functions provides built-in support for handling poison messages with Azure Storage Queues.

**How it works:**
1. When a message is dequeued, the `dequeueCount` property is incremented
2. If processing fails, the message becomes visible again after `visibilityTimeout`
3. When `dequeueCount` exceeds `maxDequeueCount`, the message is automatically moved to a poison queue
4. The poison queue is named `<originalqueuename>-poison`

**Example Configuration:**
```json
{
  "version": "2.0",
  "extensions": {
    "queues": {
      "maxDequeueCount": 5,
      "visibilityTimeout": "00:00:30"
    }
  }
}
```

With this configuration:
- A message will be retried **5 times** before being moved to the poison queue
- After each failed attempt, the message is invisible for **30 seconds** before retry

**Important Notes:**
- `maxDequeueCount` must be set to a value greater than 1 for automatic poison queue handling
- Setting `visibilityTimeout` to a high value only delays message visibility; it does **not** handle poison messages
- The poison queue must be monitored separately for manual investigation

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

##### Practice Question: Reducing Telemetry Volume from Host.Aggregator

**Scenario:**
You are developing an Azure Functions app with Application Insights integration. Under load, you notice excessive telemetry volume from the Host.Aggregator category. You need to reduce this telemetry while maintaining function execution monitoring.

**Question:**
What should you configure in host.json?

**Options:**

1. ✅ Set the log level for Host.Aggregator to Warning and keep Host.Results at Information
   - **Correct**: This configuration reduces telemetry from Host.Aggregator by only logging warnings and errors, while Host.Results continues to provide detailed execution information for monitoring, effectively balancing volume and visibility.

2. ❌ Disable Host.Aggregator completely and rely only on Host.Results
   - **Incorrect**: Completely disabling a telemetry category might cause loss of important diagnostic information. It's better to adjust log levels than to disable categories entirely.

3. ❌ Set excludedTypes to ['Request'] in the sampling configuration
   - **Incorrect**: Excluding Request types from sampling would affect all request telemetry, not just Host.Aggregator, and could impact the ability to monitor function executions properly.

4. ❌ Configure maxTelemetryItemsPerSecond to 1 for all categories
   - **Incorrect**: This applies a global limit that affects all telemetry types equally and doesn't specifically address the Host.Aggregator volume issue. It may also be too restrictive for proper monitoring.

---

**Correct Configuration Example:**
```json
{
  "version": "2.0",
  "logging": {
    "logLevel": {
      "default": "Information",
      "Host.Aggregator": "Warning",
      "Host.Results": "Information"
    },
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "maxTelemetryItemsPerSecond": 20
      }
    }
  }
}
```

**Key Telemetry Categories in Azure Functions:**

| Category | Description | Recommended Level |
|----------|-------------|-------------------|
| **Host.Results** | Function execution results (success/failure, duration) | Information |
| **Host.Aggregator** | Aggregated metrics and statistics | Warning (to reduce volume) |
| **Function** | Function-specific logs | Information or Warning |
| **Host** | General host-level logs | Error or Warning |

**Best Practices for Managing Telemetry Volume:**
- Use category-specific log levels instead of global limits
- Keep `Host.Results` at Information level for execution monitoring
- Reduce `Host.Aggregator` to Warning when volume is excessive
- Use sampling settings to control overall telemetry rate
- Avoid completely disabling categories—adjust levels instead

---

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

### Question 1: Azure Functions Configuration File

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

---

### Question 2: Blob Trigger - Processing Each Blob Only Once

**Scenario:**
You are developing an Azure Function that processes data from an Azure Blob Storage container. The function should execute whenever a new blob is added to the container. You want to ensure that the function processes each blob only once, even if the blob is updated multiple times.

**Question:**
Which of the following configurations should you apply to the Blob Trigger binding?

**Options:**

1. ❌ Set `dataType` to `binary`
   - **Incorrect**: The `dataType` property specifies the type of data that the function expects to receive from the blob trigger (e.g., `binary`, `string`, `stream`). While this configuration is important for data processing, it does not ensure that the function processes each blob only once, regardless of updates.

2. ❌ Set `blobPath` to the container name
   - **Incorrect**: The `path` property (not `blobPath`) specifies the path within the Azure Blob Storage where the function should look for new blobs. While this configuration is crucial for defining the scope of the trigger, it does not address the requirement of processing each blob only once, even if updated multiple times.

3. ✅ Set `source` to `EventGrid`
   - **Correct**: Setting `source` to `EventGrid` configures the Blob Trigger binding to listen for events from Azure Event Grid instead of using the default polling mechanism. By using Event Grid:
     - The function receives notifications when a new blob is added
     - Event Grid provides **exactly-once delivery semantics** for blob creation events
     - The function processes each blob only once, even if the blob is updated multiple times after creation
     - This is more efficient and reliable than the default storage logs/polling approach

4. ❌ Set `connection` to the storage account connection string
   - **Incorrect**: The `connection` property specifies the app setting name that contains the storage account connection string. This configuration is essential for the function to access the Azure Blob Storage container but does not guarantee that each blob is processed only once.

---

#### Why Event Grid Source is Important

**Default Blob Trigger Behavior (Polling):**
- Uses storage logs or container polling to detect new/updated blobs
- May trigger multiple times for the same blob if it's updated
- Can have delays in detecting new blobs (especially in large containers)
- Less efficient for high-volume scenarios

**Event Grid Source Behavior:**
- Uses Azure Event Grid push-based notifications
- Triggers only on blob creation events (not updates, unless specifically configured)
- Near real-time notifications with low latency
- More reliable and scalable for high-volume scenarios
- **Exactly-once processing** for blob creation events

---

#### Configuration Example

**Default Blob Trigger (Polling - may process updates):**
```json
{
  "bindings": [
    {
      "type": "blobTrigger",
      "direction": "in",
      "name": "myBlob",
      "path": "my-container/{name}",
      "connection": "AzureWebJobsStorage"
    }
  ]
}
```

**Event Grid Source (Process each blob only once):**
```json
{
  "bindings": [
    {
      "type": "blobTrigger",
      "direction": "in",
      "name": "myBlob",
      "path": "my-container/{name}",
      "connection": "AzureWebJobsStorage",
      "source": "EventGrid"
    }
  ]
}
```

**C# Attribute Example:**
```csharp
[FunctionName("BlobTriggerEventGrid")]
public static void Run(
    [BlobTrigger("my-container/{name}", Source = BlobTriggerSource.EventGrid, 
                 Connection = "AzureWebJobsStorage")] Stream myBlob,
    string name,
    ILogger log)
{
    log.LogInformation($"Processing blob: {name}, Size: {myBlob.Length} bytes");
}
```

---

#### Key Differences: Default vs Event Grid Source

| Aspect | Default (Polling) | Event Grid Source |
|--------|-------------------|-------------------|
| **Detection Method** | Storage logs / polling | Push notifications |
| **Latency** | Can be delayed (seconds to minutes) | Near real-time |
| **Trigger on Updates** | Yes (may trigger multiple times) | No (only on creation by default) |
| **Scalability** | Limited by polling frequency | Highly scalable |
| **Reliability** | May miss events in high-volume scenarios | Reliable delivery guarantees |
| **Setup** | Simpler (default) | Requires Event Grid subscription |
| **Cost** | Storage transaction costs | Event Grid costs |

---

#### Setting Up Event Grid for Blob Trigger

To use Event Grid source, you need to:

1. **Create an Event Grid System Topic** for the storage account
2. **Create an Event Subscription** that points to your function app
3. **Configure the Blob Trigger** with `"source": "EventGrid"`

**Azure CLI Example:**
```bash
# Create Event Grid system topic for storage account
az eventgrid system-topic create \
  --name my-storage-topic \
  --resource-group MyResourceGroup \
  --source /subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{storage-account} \
  --topic-type Microsoft.Storage.StorageAccounts

# Create event subscription pointing to the function
az eventgrid system-topic event-subscription create \
  --name my-blob-subscription \
  --system-topic-name my-storage-topic \
  --resource-group MyResourceGroup \
  --endpoint-type azurefunction \
  --endpoint /subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.Web/sites/{function-app}/functions/{function-name} \
  --included-event-types Microsoft.Storage.BlobCreated
```

---

### Question 3: Handling Poison Messages with Storage Queues

**Scenario:**
You are developing an Azure Function that processes messages from an Azure Storage Queue. The function needs to handle poison messages (messages that cannot be processed successfully after multiple attempts).

**Question:**
Which of the following configurations should you implement to ensure poison messages are moved to a separate queue for further investigation?

**Options:**

1. ❌ Set `visibilityTimeout` to a high value in the queue trigger binding
   - **Incorrect**: Setting `visibilityTimeout` to a high value in the queue trigger binding will only delay the visibility of the message in the queue for processing. It does not handle the scenario of poison messages that cannot be processed successfully after multiple attempts.

2. ✅ Set `maxDequeueCount` to a value greater than 1 in the host.json file
   - **Correct**: Setting `maxDequeueCount` to a value greater than 1 in the `host.json` file allows you to specify the maximum number of times a message can be dequeued before it is considered a poison message. Once the message reaches this limit, it will be automatically moved to a separate queue named `<queuename>-poison` for further investigation.

3. ❌ Manually move poison messages to a dead-letter queue using custom code
   - **Incorrect**: Manually moving poison messages to a dead-letter queue using custom code is not an efficient solution as it requires additional development effort and monitoring. It is better to leverage built-in features of Azure Functions and Azure Storage Queues to handle poison messages automatically.

4. ❌ Enable Dead-lettering in the Storage Queue settings
   - **Incorrect**: Dead-lettering is a feature of **Service Bus Queues**, not Storage Queues, and is not applicable in this scenario. If you were using Service Bus Queues, enabling Dead-lettering would be a good approach as it allows you to automatically move messages that cannot be processed successfully to a separate dead-letter queue. However, for Storage Queues, use `maxDequeueCount` instead.

---

#### Key Differences: Storage Queues vs Service Bus Queues for Poison Messages

| Feature | Storage Queue | Service Bus Queue |
|---------|---------------|-------------------|
| **Poison Message Handling** | `maxDequeueCount` in host.json | Dead-letter queue (built-in) |
| **Poison Queue Name** | `<queuename>-poison` (auto-created) | Dead-letter sub-queue |
| **Configuration Location** | host.json | Service Bus settings |
| **Automatic Movement** | Yes (after maxDequeueCount) | Yes (with dead-lettering enabled) |

#### Configuration Example for Storage Queue Poison Messages

**host.json:**
```json
{
  "version": "2.0",
  "extensions": {
    "queues": {
      "maxDequeueCount": 5,
      "visibilityTimeout": "00:00:30",
      "batchSize": 16
    }
  }
}
```

**function.json (Queue Trigger):**
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

With this configuration, if a message from `myqueue` fails processing 5 times, it will automatically be moved to `myqueue-poison`.

**Reference**: [Azure Storage Queue trigger for Azure Functions](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-storage-queue-trigger)

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

### Practice Question: Deploying Functions with Custom Dependencies

**Scenario:**
You need to deploy an Azure Functions app with custom dependencies that are not available in the default runtime environment. The app requires a specific version of a system library.

**Question:**
Which deployment method should you use?

**Options:**

1. ❌ Deploy using Azure DevOps with the dependencies specified in the YAML pipeline configuration
   - **Incorrect**: Azure DevOps pipelines can automate deployment but cannot install system libraries into the Functions runtime environment. The pipeline runs in a separate build agent, not the target environment.

2. ❌ Use remote build with additional build steps specified in a custom deployment script
   - **Incorrect**: Remote build can handle application dependencies but cannot install system libraries or modify the underlying OS image. It's limited to what can be done within the build container's permissions.

3. ✅ Deploy the function app using a custom container image that includes all required dependencies
   - **Correct**: Using a custom container allows you to include any system libraries, dependencies, and specific versions required by your function app, providing full control over the runtime environment.

4. ❌ Deploy using ZIP deployment with the dependencies included in the package.json or requirements.txt file
   - **Incorrect**: ZIP deployment with package files only handles application-level dependencies that can be installed via package managers, not system libraries or specific versions of system components that need OS-level installation.

---

**Additional Context: Azure Functions Deployment Methods for Custom Dependencies**

| Deployment Method | Application Dependencies | System Libraries | Full Runtime Control |
|-------------------|--------------------------|------------------|----------------------|
| **Custom Container** | ✅ Yes | ✅ Yes | ✅ Yes |
| **ZIP Deployment** | ✅ Yes (via package managers) | ❌ No | ❌ No |
| **Remote Build** | ✅ Yes (via package managers) | ❌ No | ❌ No |
| **Azure DevOps** | ✅ Yes (via package managers) | ❌ No | ❌ No |

**When to Use Custom Containers:**
- You need specific versions of system libraries (e.g., libgdiplus, OpenCV)
- Your function requires native dependencies not available in the default runtime
- You need full control over the OS environment
- You want to ensure consistency between development and production environments
- You need to install tools or runtimes not supported by default

**Azure CLI Example - Deploy Function App with Custom Container:**
```bash
# Create a function app with a custom container
az functionapp create \
  --name MyFunctionApp \
  --resource-group MyResourceGroup \
  --storage-account mystorageaccount \
  --plan MyPremiumPlan \
  --deployment-container-image-name myacr.azurecr.io/myfunctionimage:v1

# Update the container image
az functionapp config container set \
  --name MyFunctionApp \
  --resource-group MyResourceGroup \
  --image myacr.azurecr.io/myfunctionimage:v2
```

**Note**: Custom container deployment requires a **Premium plan** or **Dedicated (App Service) plan**. The Consumption plan does not support custom containers.

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

## Azure Functions Core Tools (Local Development)

### Overview

**Azure Functions Core Tools** is a command-line tool that provides the core runtime and templates for creating Azure Functions, enabling local development and testing before deploying to Azure.

### Key Features

- **Cross-platform**: Works on Windows, macOS, and Linux
- **Local runtime**: Runs the same Functions runtime that's used in Azure
- **Function templates**: Provides templates to scaffold new functions
- **Local debugging**: Full debugging support in VS Code and Visual Studio
- **Deployment**: Deploy directly to Azure from the command line

### Version Information

| Version | Functions Runtime | Supported OS |
|---------|------------------|--------------|
| 4.x | Functions 4.x | Windows, macOS, Linux |
| 3.x | Functions 3.x | Windows, macOS, Linux |
| 2.x | Functions 2.x | Windows, macOS, Linux |
| 1.x | Functions 1.x | Windows only |

### Installation

**npm (all platforms):**
```bash
npm install -g azure-functions-core-tools@4 --unsafe-perm true
```

**Homebrew (macOS):**
```bash
brew tap azure/functions
brew install azure-functions-core-tools@4
```

**Windows (Chocolatey):**
```bash
choco install azure-functions-core-tools
```

### Common Commands

| Command | Description |
|---------|-------------|
| `func init` | Initialize a new Functions project |
| `func new` | Create a new function from a template |
| `func start` | Start the local Functions runtime |
| `func azure functionapp publish <name>` | Deploy to Azure |
| `func extensions install` | Install binding extensions |

### Local Development Workflow

1. **Initialize project**: `func init MyFunctionApp --worker-runtime dotnet`
2. **Create function**: `func new --name HttpTrigger --template "HTTP trigger"`
3. **Configure settings**: Edit `local.settings.json`
4. **Run locally**: `func start`
5. **Test**: Send requests to `http://localhost:7071/api/HttpTrigger`
6. **Deploy**: `func azure functionapp publish MyFunctionApp`

### Practice Question: Local Development Tools

**Question:**
Which library allows you to develop and test Azure Functions locally before deploying into Azure?

**Options:**

1. ✅ **Core Tools, cross-platform on Windows, macOS and Linux**
   - **Correct**: Azure Functions Core Tools provides the core runtime and templates for creating functions, which enable local development. Version 2.x and later supports development on Windows, Linux, and macOS. It includes the same runtime used in Azure, allowing you to test functions locally with full fidelity before deploying.

2. ❌ Azure Functions compile natively to an EXE and can be run from the command line
   - **Incorrect**: Azure Functions do not compile to standalone EXE files that can be run independently. While .NET-based functions compile to DLLs, they require the Functions runtime (provided by Core Tools locally or the Azure Functions host in the cloud) to execute.

3. ❌ Azure SDK library
   - **Incorrect**: The Azure SDK provides client libraries for interacting with Azure services from your code, but it is not a tool for running or testing Azure Functions locally. The SDK is used within your function code to connect to services like Storage, Cosmos DB, etc.

4. ❌ Azure Functions are cloud only, and cannot be tested locally
   - **Incorrect**: Azure Functions can absolutely be tested locally using Azure Functions Core Tools. Local development is a core feature of the Azure Functions development experience, and Microsoft strongly encourages testing locally before deploying to Azure.

**Reference**: [Azure Functions Core Tools - Develop Azure Functions locally](https://docs.microsoft.com/en-us/azure/azure-functions/functions-develop-local)

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

### Custom Handler Requirements

For a custom handler to be deployable and executable inside Azure Functions, it must meet the following requirements:

#### 1. Must be a Standalone Executable or Script

The custom handler must be something that can run on the Azure Functions host environment:

| Platform | Executable Format |
|----------|-------------------|
| **Windows** | `.exe`, `.bat`, `.cmd`, or script with interpreter |
| **Linux** | ELF binary, shell script, or script with interpreter |

#### 2. Must be HTTP-Capable

Your custom handler must:
- Start an HTTP server
- Listen on the port specified by `FUNCTIONS_CUSTOMHANDLER_PORT` environment variable
- Accept HTTP POST requests from the Functions host
- Return HTTP responses

#### 3. Request/Response Format

The Functions host sends requests and expects responses in a specific JSON format:

**Incoming Request (from Functions host to your handler):**
```json
{
  "Data": {
    "req": {
      "Url": "https://myfunc.azurewebsites.net/api/hello",
      "Method": "GET",
      "Query": { "name": "World" },
      "Headers": { "Content-Type": ["application/json"] },
      "Body": ""
    }
  },
  "Metadata": {
    "sys": {
      "MethodName": "HttpTrigger",
      "UtcNow": "2025-11-26T12:00:00Z"
    }
  }
}
```

**Expected Response (from your handler back to Functions host):**
```json
{
  "Outputs": {
    "res": {
      "statusCode": 200,
      "body": "Hello, World!",
      "headers": { "Content-Type": "application/json" }
    }
  },
  "Logs": ["Function executed successfully"],
  "ReturnValue": null
}
```

#### 4. Deployment Requirements

Your executable must be included in the deployment package:

```
MyFunctionApp/
├── host.json                 # Points to your executable
├── local.settings.json
├── handler.exe               # Your custom handler (Windows)
├── handler                   # Your custom handler (Linux)
└── HttpTrigger/
    └── function.json         # Function bindings
```

#### 5. Platform Considerations

| Consideration | Requirement |
|---------------|-------------|
| **Architecture** | Must match the Azure Functions host (typically x64) |
| **Dependencies** | All dependencies must be bundled or available on the host |
| **Startup time** | Should start quickly to avoid cold start delays |
| **Port binding** | Must read `FUNCTIONS_CUSTOMHANDLER_PORT` and bind to it |

#### 6. Simplified Mode for HTTP-Only Functions

If you only use HTTP triggers, you can enable `enableForwardingHttpRequest: true` to receive the raw HTTP request instead of the wrapper format:

```json
{
  "version": "2.0",
  "customHandler": {
    "description": {
      "defaultExecutablePath": "handler"
    },
    "enableForwardingHttpRequest": true
  }
}
```

This forwards the original HTTP request directly, making it easier to build standard web servers without needing to parse the custom handler payload format.

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

## Function App Lifecycle and Cleanup Operations

### Handling Shutdown and Cleanup

Azure Functions apps may need to perform cleanup operations during shutdown, such as releasing resources, closing connections, or flushing buffers. Understanding how to properly handle these scenarios is important for building robust serverless applications.

**Key Concepts:**

| Approach | Purpose | When It Runs |
|----------|---------|-------------|
| **IDisposable + DI** | Cleanup resources during graceful shutdown | When function app shuts down |
| **finally block** | Cleanup after individual function execution | After function method completes |
| **Timer-triggered function** | Scheduled cleanup tasks | On a schedule, not shutdown-aware |
| **CancellationToken** | Handle graceful cancellation | When function execution is cancelled |

**Recommended Pattern: IDisposable with Dependency Injection**

For cleanup operations that need to run when the function app is shutting down, implement the `IDisposable` interface and register the service through dependency injection.

```csharp
// Startup.cs - Register the service
using Microsoft.Azure.Functions.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection;

[assembly: FunctionsStartup(typeof(MyFunctionApp.Startup))]

namespace MyFunctionApp
{
    public class Startup : FunctionsStartup
    {
        public override void Configure(IFunctionsHostBuilder builder)
        {
            // Register as singleton to ensure single instance across function invocations
            builder.Services.AddSingleton<ICleanupService, CleanupService>();
        }
    }
}
```

```csharp
// CleanupService.cs - Implement IDisposable
public interface ICleanupService
{
    void DoWork();
}

public class CleanupService : ICleanupService, IDisposable
{
    private bool _disposed = false;
    
    public void DoWork()
    {
        // Service logic here
    }
    
    public void Dispose()
    {
        if (!_disposed)
        {
            // Cleanup operations when function app shuts down
            // - Close database connections
            // - Flush buffers
            // - Release unmanaged resources
            // - Send final telemetry
            
            _disposed = true;
        }
    }
}
```

```csharp
// MyFunction.cs - Use the service via constructor injection
public class MyFunction
{
    private readonly ICleanupService _cleanupService;
    
    public MyFunction(ICleanupService cleanupService)
    {
        _cleanupService = cleanupService;
    }
    
    [FunctionName("MyFunction")]
    public async Task<IActionResult> Run(
        [HttpTrigger(AuthorizationLevel.Function, "get", "post")] HttpRequest req)
    {
        _cleanupService.DoWork();
        return new OkResult();
    }
}
```

**Why IDisposable with DI Works:**
1. The DI container manages the service lifecycle
2. When the function app shuts down gracefully, the DI container disposes all registered `IDisposable` services
3. This provides a reliable hook for cleanup operations at the app level

**Alternative: IAsyncDisposable for Async Cleanup**

For cleanup operations that require async operations:

```csharp
public class AsyncCleanupService : IAsyncDisposable
{
    public async ValueTask DisposeAsync()
    {
        // Async cleanup operations
        await FlushBuffersAsync();
        await CloseConnectionsAsync();
    }
}
```

### Practice Question: Cleanup Operations During Shutdown

**Question:**
You have an Azure Functions app that needs to perform cleanup operations when the function app is shutting down. Which method should you implement in your function code?

**Options:**

1. ❌ Add a finally block in the main function method
   - **Incorrect**: A finally block only executes after the function method completes, not when the entire function app is shutting down. It doesn't handle app-level lifecycle events.

2. ✅ Implement IDisposable interface and use dependency injection to register the cleanup service
   - **Correct**: In Azure Functions, implementing IDisposable and registering services through dependency injection ensures that cleanup code runs when the function app shuts down. The Dispose method is called during graceful shutdown.

3. ❌ Create a separate timer-triggered function that runs cleanup tasks
   - **Incorrect**: A timer-triggered function runs on a schedule and cannot detect when the function app is shutting down. It's not suitable for shutdown cleanup operations.

4. ❌ Use the FunctionContext.OnShutdown event handler
   - **Incorrect**: There is no OnShutdown event handler on FunctionContext. Lifecycle management should be done through dependency injection and IDisposable pattern.

---

**Key Concepts Summary:**

| Approach | Handles App Shutdown? | Use Case |
|----------|----------------------|----------|
| **IDisposable + DI** | ✅ Yes | App-level cleanup (connections, resources) |
| **finally block** | ❌ No | Function-level cleanup (local resources) |
| **Timer trigger** | ❌ No | Scheduled maintenance tasks |
| **FunctionContext.OnShutdown** | ❌ Doesn't exist | N/A |

> 💡 **Exam Tip**: When asked about cleanup operations during function app shutdown, the correct approach is implementing `IDisposable` and registering the service via dependency injection. The DI container calls `Dispose()` during graceful shutdown. Don't confuse this with function-level cleanup (finally blocks) or scheduled tasks (timer triggers).

**Reference**: [Azure Functions Dependency Injection](https://docs.microsoft.com/en-us/azure/azure-functions/functions-dotnet-dependency-injection)

## Related Topics

- Azure Functions hosting plans
- Azure Functions triggers and bindings
- Deployment and CI/CD
- Monitoring with Application Insights

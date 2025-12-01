# Azure Durable Functions

## Overview

Durable Functions is an extension of Azure Functions that lets you write stateful functions in a serverless compute environment. The extension lets you define stateful workflows by writing **orchestrator functions** and stateful entities by writing **entity functions** using the Azure Functions programming model.

## Table of Contents

- [Key Concepts](#key-concepts)
- [Function Types](#function-types)
  - [Orchestrator Functions](#orchestrator-functions)
  - [Activity Functions](#activity-functions)
  - [Entity Functions](#entity-functions)
  - [Client Functions](#client-functions)
- [Application Patterns](#application-patterns)
- [Error Handling and Retry Policies](#error-handling-and-retry-policies)
  - [Overview](#overview-1)
  - [RetryOptions Configuration](#retryoptions-configuration)
  - [Using CallActivityWithRetryAsync](#using-callactivitywithretryasync)
  - [Practice Question: Implementing Retry Policies](#practice-question-implementing-retry-policies)
- [Orchestrator Constraints](#orchestrator-constraints)
- [Best Practices](#best-practices)
- [Related Topics](#related-topics)

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Orchestration** | A workflow defined by an orchestrator function that coordinates activities |
| **Activity** | A unit of work that can be called by an orchestrator |
| **Entity** | A small piece of state with operations for reading and updating |
| **Task Hub** | A logical container for all orchestration and entity state |
| **Replay** | The mechanism orchestrators use to rebuild their state |

## Function Types

### Orchestrator Functions

Orchestrator functions describe how actions are executed and the order in which they are executed. They coordinate activity functions and can wait for external events.

**Key Characteristics:**
- Must be deterministic (same input always produces same output)
- Cannot perform I/O operations directly
- Cannot use non-deterministic APIs (random numbers, current time, etc.)
- Use `context.CurrentUtcDateTime` instead of `DateTime.UtcNow`

```csharp
[FunctionName("OrchestratorFunction")]
public static async Task<List<string>> RunOrchestrator(
    [OrchestrationTrigger] IDurableOrchestrationContext context)
{
    var outputs = new List<string>();
    
    outputs.Add(await context.CallActivityAsync<string>("ActivityFunction", "Input1"));
    outputs.Add(await context.CallActivityAsync<string>("ActivityFunction", "Input2"));
    outputs.Add(await context.CallActivityAsync<string>("ActivityFunction", "Input3"));
    
    return outputs;
}
```

### Activity Functions

Activity functions are the units of work in a Durable Functions orchestration. They perform the actual work and can make external calls.

**Key Characteristics:**
- Can perform I/O operations
- Can be retried automatically on failure
- Have a single input and output
- Are scheduled and executed asynchronously

```csharp
[FunctionName("ActivityFunction")]
public static string RunActivity([ActivityTrigger] string input, ILogger log)
{
    log.LogInformation($"Processing: {input}");
    return $"Processed: {input}";
}
```

### Entity Functions

Entity functions define operations for reading and updating small pieces of state, known as durable entities.

### Client Functions

Client functions are regular Azure Functions that start orchestrations or send signals to entities.

```csharp
[FunctionName("HttpStart")]
public static async Task<HttpResponseMessage> HttpStart(
    [HttpTrigger(AuthorizationLevel.Anonymous, "post")] HttpRequestMessage req,
    [DurableClient] IDurableOrchestrationClient starter,
    ILogger log)
{
    string instanceId = await starter.StartNewAsync("OrchestratorFunction", null);
    return starter.CreateCheckStatusResponse(req, instanceId);
}
```

## Application Patterns

| Pattern | Description | Use Case |
|---------|-------------|----------|
| **Function Chaining** | Execute functions in sequence | Data processing pipelines |
| **Fan-out/Fan-in** | Execute functions in parallel, then aggregate | Batch processing |
| **Async HTTP APIs** | Long-running operations with polling | File processing |
| **Monitor** | Periodic polling until condition is met | Approval workflows |
| **Human Interaction** | Wait for external events | Manual approvals |
| **Aggregator** | Aggregate event data over time | IoT data collection |

## Error Handling and Retry Policies

### Overview

Durable Functions provides built-in support for error handling and automatic retries for activity functions. This is essential for building resilient workflows that can recover from transient failures.

### RetryOptions Configuration

The `RetryOptions` class configures the retry behavior for activity functions:

```csharp
var retryOptions = new RetryOptions(
    firstRetryInterval: TimeSpan.FromSeconds(30),
    maxNumberOfAttempts: 3
);
```

**RetryOptions Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `firstRetryInterval` | TimeSpan | Time to wait before the first retry |
| `maxNumberOfAttempts` | int | Maximum number of retry attempts |
| `backoffCoefficient` | double | Multiplier for exponential backoff (default: 1.0) |
| `maxRetryInterval` | TimeSpan | Maximum interval between retries |
| `retryTimeout` | TimeSpan | Maximum time to spend retrying |

**Exponential Backoff Example:**

```csharp
var retryOptions = new RetryOptions(
    firstRetryInterval: TimeSpan.FromSeconds(5),
    maxNumberOfAttempts: 5
)
{
    BackoffCoefficient = 2.0,           // Double the interval each retry
    MaxRetryInterval = TimeSpan.FromMinutes(5)  // Cap at 5 minutes
};
```

### Using CallActivityWithRetryAsync

To apply retry policies to activity function calls, use `CallActivityWithRetryAsync` instead of `CallActivityAsync`:

```csharp
[FunctionName("OrchestratorWithRetry")]
public static async Task<string> RunOrchestrator(
    [OrchestrationTrigger] IDurableOrchestrationContext context)
{
    var retryOptions = new RetryOptions(
        firstRetryInterval: TimeSpan.FromSeconds(30),
        maxNumberOfAttempts: 3
    );
    
    // Activity will be retried up to 3 times with 30-second intervals
    var result = await context.CallActivityWithRetryAsync<string>(
        "ProcessItem", 
        retryOptions, 
        "input-data"
    );
    
    return result;
}
```

### Practice Question: Implementing Retry Policies

**Question:**
You have a Durable Functions orchestrator that must handle errors from activity functions. If an activity function fails, it should retry up to 3 times with a 30-second delay between attempts. Which code should you use?

**Options:**

1. ❌ **Using incorrect RetryPolicy class:**
   ```csharp
   var retryOptions = new RetryPolicy() 
   { 
       RetryCount = 3, 
       RetryInterval = TimeSpan.FromSeconds(30) 
   }; 
   var result = await context.CallActivityAsync<string>("ProcessItem", input, retryOptions);
   ```
   - **Incorrect**: This code uses incorrect class name `RetryPolicy` instead of `RetryOptions`, and `CallActivityAsync` doesn't accept retry options as a parameter. Retry policies must be applied using `CallActivityWithRetryAsync`.

2. ❌ **Using Task.Delay (non-deterministic):**
   ```csharp
   var result = await context.CallActivityAsync<string>("ProcessItem", input); 
   if (result == null) 
   { 
       await Task.Delay(30000); 
       result = await context.CallActivityAsync<string>("ProcessItem", input); 
   }
   ```
   - **Incorrect**: This code uses `Task.Delay` which is non-deterministic and violates orchestrator constraints. It also only retries once based on a null check rather than handling actual failures with the required 3 attempts.

3. ❌ **Manual retry with try-catch:**
   ```csharp
   for (int i = 0; i < 3; i++) 
   { 
       try 
       { 
           return await context.CallActivityAsync<string>("ProcessItem", input); 
       } 
       catch 
       { 
           await context.CreateTimer(context.CurrentUtcDateTime.AddSeconds(30), CancellationToken.None); 
       } 
   }
   ```
   - **Incorrect**: While this implements retry logic, it violates orchestrator constraints by using try-catch for control flow. Orchestrators should use `CallActivityWithRetryAsync` for built-in retry handling rather than manual implementation.

4. ✅ **Correct approach using RetryOptions and CallActivityWithRetryAsync:**
   ```csharp
   var retryOptions = new RetryOptions(
       firstRetryInterval: TimeSpan.FromSeconds(30), 
       maxNumberOfAttempts: 3
   ); 
   var result = await context.CallActivityWithRetryAsync<string>("ProcessItem", retryOptions, input);
   ```
   - **Correct**: This code correctly configures `RetryOptions` with the required 30-second initial retry interval and 3 maximum attempts, then uses `CallActivityWithRetryAsync` to apply the retry policy to the activity function call.

**Key Takeaways:**
- Always use `RetryOptions` class (not `RetryPolicy`)
- Use `CallActivityWithRetryAsync` to apply retry policies (not `CallActivityAsync`)
- Never use `Task.Delay` in orchestrators - it's non-deterministic
- Use `context.CreateTimer` for deterministic delays if needed
- Prefer built-in retry handling over manual try-catch implementations

**Reference**: [Durable Functions Error Handling - Microsoft Learn](https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-error-handling)

## Orchestrator Constraints

Orchestrator functions must follow specific constraints to ensure deterministic execution:

| Constraint | Reason | Alternative |
|------------|--------|-------------|
| No I/O operations | Non-deterministic | Use activity functions |
| No `DateTime.Now` | Non-deterministic | Use `context.CurrentUtcDateTime` |
| No `Task.Delay` | Non-deterministic | Use `context.CreateTimer` |
| No `Guid.NewGuid()` | Non-deterministic | Use `context.NewGuid()` |
| No random numbers | Non-deterministic | Pass as input or use activity |
| No async calls outside SDK | Non-deterministic | Use SDK methods only |

## Best Practices

1. **Use Activity Functions for I/O**: Keep orchestrators lightweight and delegate I/O to activities
2. **Implement Retry Policies**: Use `CallActivityWithRetryAsync` for transient failure handling
3. **Use Sub-Orchestrations**: Break complex workflows into smaller orchestrations
4. **Handle Timeouts**: Use `context.CreateTimer` with cancellation for timeout scenarios
5. **Monitor Instance Status**: Use the client to query orchestration status and history
6. **Clean Up Completed Instances**: Purge old instances to manage storage costs

## Related Topics

- [Azure Functions Configuration](./azure-functions-configuration.md)
- [Azure Functions Hosting Plans](./azure-functions-hosting-plans.md)
- [Azure Functions CosmosDB Triggers](./azure-functions-cosmosdb-triggers.md)

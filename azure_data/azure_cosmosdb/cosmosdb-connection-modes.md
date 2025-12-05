# Azure Cosmos DB Connection Modes

## Overview

Azure Cosmos DB SDK supports two connection modes that determine how your application communicates with the Cosmos DB backend. Choosing the right connection mode is critical for optimizing latency and performance based on your application requirements.

---

## Table of Contents

1. [Connection Modes Overview](#connection-modes-overview)
2. [Direct Mode](#direct-mode)
3. [Gateway Mode](#gateway-mode)
4. [Gateway Mode Variants](#gateway-mode-variants)
5. [Connection Mode Comparison](#connection-mode-comparison)
6. [When to Use Each Mode](#when-to-use-each-mode)
7. [Configuration Examples](#configuration-examples)
8. [Exam Questions and Scenarios](#exam-questions-and-scenarios)
9. [References](#references)

---

## Connection Modes Overview

| Connection Mode | Description | Latency | Use Case |
|-----------------|-------------|---------|----------|
| **Direct Mode** | Application connects directly to Cosmos DB backend | Lowest | Production workloads requiring low latency |
| **Gateway Mode** | Connection through an intermediate gateway | Higher | Firewall-restricted environments |

---

## Direct Mode

### Description

When you connect to Azure Cosmos DB using **direct mode**, your application connects directly to the Azure Cosmos DB backend nodes. Even if you have many physical partitions, request routing is handled entirely client-side.

### Key Characteristics

- **Low Latency**: Direct mode offers the lowest latency because your application communicates directly with the Azure Cosmos DB backend
- **No Intermediate Hop**: Eliminates the need for an intermediate network hop
- **Client-Side Routing**: Request routing to the appropriate partition is handled entirely by the client SDK
- **TCP Protocol**: Uses TCP protocol for communication with backend nodes

### Benefits

- ✅ **Lowest latency** - No intermediate network hops
- ✅ **Better performance** for high-throughput workloads
- ✅ **Direct communication** with backend partitions
- ✅ **Recommended for production** scenarios

### Requirements

- Requires outbound connectivity on a range of TCP ports
- May require firewall configuration to allow direct connectivity

---

## Gateway Mode

### Description

Gateway mode involves connecting to Azure Cosmos DB through an intermediate gateway service. All requests are routed through this shared gateway before reaching the backend.

### Key Characteristics

- **Intermediate Hop**: Requests go through a shared gateway before reaching the Cosmos DB backend
- **HTTPS Protocol**: Uses HTTPS protocol for communication
- **Simpler Connectivity**: Only requires outbound HTTPS (port 443)

### Benefits

- ✅ **Simpler firewall configuration** - Only requires port 443
- ✅ **Works in restricted environments** where direct connectivity is not possible
- ✅ **Easier to configure** in corporate networks

### Drawbacks

- ❌ **Higher latency** due to the additional network hop
- ❌ **Lower throughput** compared to direct mode

---

## Gateway Mode Variants

### Standard Gateway Mode

The default gateway mode where requests are routed through a shared gateway service.

- Additional network hop adds latency
- Shared resources among multiple tenants

### Gateway Mode with Dedicated Gateway

A dedicated gateway provides isolated gateway resources for your Cosmos DB account.

- **Still involves an extra network hop** compared to direct mode
- Provides caching benefits (integrated cache)
- Better isolation than shared gateway
- **Does NOT eliminate the latency disadvantage** compared to direct mode

### Gateway Mode with Integrated Cache

Integrated cache can be used with dedicated gateway to cache frequently accessed data.

- **Can improve performance for repeated reads**
- Cache hits reduce backend calls
- **Gateway mode inherently has higher latency than direct mode** due to the additional network hop
- Not a replacement for direct mode when lowest latency is required

---

## Connection Mode Comparison

| Feature | Direct Mode | Gateway Mode | Gateway with Dedicated | Gateway with Cache |
|---------|-------------|--------------|----------------------|-------------------|
| **Latency** | Lowest | Higher | Higher | Higher (cache miss) / Lower (cache hit) |
| **Network Hop** | None (direct) | One extra hop | One extra hop | One extra hop |
| **Protocol** | TCP | HTTPS | HTTPS | HTTPS |
| **Firewall Config** | Complex (multiple ports) | Simple (port 443 only) | Simple (port 443 only) | Simple (port 443 only) |
| **Best For** | Low latency requirements | Firewall-restricted environments | Isolation needs | Read-heavy with repeated queries |

---

## When to Use Each Mode

### Use Direct Mode When:

- **Low latency is critical** for your application
- You need the **best possible performance**
- Your network allows **direct TCP connectivity** to Cosmos DB
- Running **production workloads** with high throughput requirements

### Use Gateway Mode When:

- Operating behind a **strict firewall** that only allows HTTPS
- Network restrictions prevent direct TCP connectivity
- **Simplicity of configuration** is more important than latency
- Development or testing environments where latency is less critical

---

## Configuration Examples

### .NET SDK - Direct Mode (Recommended for Low Latency)

```csharp
CosmosClientOptions options = new CosmosClientOptions
{
    ConnectionMode = ConnectionMode.Direct
};

CosmosClient client = new CosmosClient(
    connectionString,
    options
);
```

### .NET SDK - Gateway Mode

```csharp
CosmosClientOptions options = new CosmosClientOptions
{
    ConnectionMode = ConnectionMode.Gateway
};

CosmosClient client = new CosmosClient(
    connectionString,
    options
);
```

### Java SDK - Direct Mode

```java
CosmosClientBuilder clientBuilder = new CosmosClientBuilder()
    .endpoint(endpoint)
    .key(key)
    .directMode();

CosmosClient client = clientBuilder.buildClient();
```

### Java SDK - Gateway Mode

```java
CosmosClientBuilder clientBuilder = new CosmosClientBuilder()
    .endpoint(endpoint)
    .key(key)
    .gatewayMode();

CosmosClient client = clientBuilder.buildClient();
```

---

## Exam Questions and Scenarios

### Question 1: Optimizing for Low Latency

**Scenario:**

You are optimizing an Azure Cosmos DB application for low latency. The application currently uses gateway mode. What connection mode should you use instead?

**Options:**

- A) Gateway mode with integrated cache
- B) Direct mode ✅
- C) Standard gateway mode
- D) Gateway mode with dedicated gateway

---

**Correct Answer: B) Direct mode**

---

**Explanation:**

| Option | Why Incorrect/Correct |
|--------|----------------------|
| **A) Gateway mode with integrated cache** | ❌ While integrated cache can improve performance for repeated reads, gateway mode inherently has higher latency than direct mode due to the additional network hop. |
| **B) Direct mode** | ✅ **Correct** - Direct mode offers low latency because your application can communicate directly with the Azure Cosmos DB backend and doesn't need an intermediate network hop. Direct mode provides lower latency by eliminating the intermediate network hop. |
| **C) Standard gateway mode** | ❌ Standard gateway mode involves an intermediate hop through a shared gateway, which adds latency compared to direct connection to the backend. |
| **D) Gateway mode with dedicated gateway** | ❌ Gateway mode with dedicated gateway still involves an extra network hop compared to direct mode, which adds latency even though it provides caching benefits. |

### Key Takeaway

**When optimizing for lowest latency, always choose Direct Mode.** All gateway mode variants (standard, dedicated, with cache) involve an additional network hop that adds latency compared to direct mode.

---

## Best Practices

1. **Use Direct Mode for Production**: Default to direct mode for production workloads where latency matters
2. **Configure Firewall for Direct Mode**: Work with your network team to allow the necessary TCP ports for direct mode
3. **Use Gateway Mode Only When Necessary**: Only use gateway mode when network restrictions prevent direct connectivity
4. **Don't Confuse Caching with Latency**: Gateway mode with integrated cache improves repeated read performance but doesn't eliminate the latency penalty of the extra network hop
5. **Test Both Modes**: Benchmark your application with both modes to understand the latency impact in your specific environment

---

## References

- [Azure Cosmos DB SDK connectivity modes](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/sdk-connection-modes)
- [Configure direct mode in Azure Cosmos DB](https://learn.microsoft.com/en-us/azure/cosmos-db/nosql/how-to-configure-direct-mode)
- [Azure Cosmos DB integrated cache](https://learn.microsoft.com/en-us/azure/cosmos-db/integrated-cache)
- [Azure Cosmos DB dedicated gateway](https://learn.microsoft.com/en-us/azure/cosmos-db/dedicated-gateway)

# Azure Relay & Hybrid Connections Guide

See [README](./README.md) for overview.

## Quick Comparison

| Feature | Azure Relay | Hybrid Connections |
|---------|---|---|
| **Purpose** | WCF services + hybrid scenarios | App Service + on-prem resources |
| **Protocol** | SOAP/HTTP | HTTP/WebSocket |
| **Setup** | Relay endpoint | Hybrid Connection endpoint |
| **Use** | Legacy WCF, proxy scenarios | Bridging app service to on-prem |
| **Complexity** | Higher | Lower |
| **Cost** | Per message | Fixed monthly |

---

## Azure Relay Service

**What it is:**
- Hybrid connectivity service
- Allows on-premises services to be called from cloud
- No need to open firewall ports
- Secure tunnel through Azure

**Architecture:**

```
On-Premises          Firewall          Azure              Cloud App
WCF Service      (Remains Closed)    Relay Service      Makes Request
    │                                    │                    │
    ├─ (Outbound)                      │                    │
    │  Creates tunnel        ┌──────────┤                    │
    │  Registers endpoint    │          │                    │
    │                   ┌────┴────────┐ │                    │
    │                   │ Relay       │ │                    │
    │                   │ Namespace   │ │                    │
    │                   └────┬────────┘ │                    │
    │                        │◄─────────┘ (Cloud calls via)  │
    │                        │            Relay endpoint     │
    └────────────────────────┴─────────────────────────────►─┘
         (Responses flow back through relay)
```

**Key Advantages:**
- ✅ No firewall modifications needed
- ✅ No VPN required
- ✅ No public IP needed
- ✅ Secure end-to-end encryption
- ✅ Works across any network

---

## Relay Types

### 1. WCF Relay (Legacy)

**Use when:**
- You have existing WCF services
- You need SOAP-based services
- Running older enterprise applications

**Example Setup:**
```
On-Premises WCF Service
  │
  └─ Registers with: ServiceBusNamespace/MyWcfService
       │
       └─ Cloud clients call:
          https://namespace.servicebus.windows.net/MyWcfService
```

**Binding:**
```csharp
// Server side (on-premises)
var host = new ServiceHost(typeof(MyWcfService));
var binding = new NetTcpRelayBinding();
var address = ServiceBusEnvironment.CreateServiceUri(
    "sb", "mynamespace", "myservice");
host.AddServiceEndpoint(typeof(IMyWcfContract), binding, address);

// Client side (cloud)
var binding = new NetTcpRelayBinding();
var address = ServiceBusEnvironment.CreateServiceUri(
    "sb", "mynamespace", "myservice");
var factory = new ChannelFactory<IMyWcfContract>(binding, address);
IMyWcfContract proxy = factory.CreateChannel();
```

### 2. Hybrid Relay (HTTP)

**Use when:**
- You have HTTP-based services
- Simple REST APIs
- App Service integration

**Example:**
```
On-Premises REST API (port 8080)
  │
  └─ Listener: 127.0.0.1:8080
       │
       └─ Connected to: Relay Namespace/MyRestApi
            │
            └─ Cloud clients call:
               https://mynamespace.servicebus.windows.net/MyRestApi
```

---

## Hybrid Connections (App Service Integration)

**What it is:**
- Specialized version of Azure Relay for App Service
- Connect App Service to on-premises resources
- Easier than standalone Relay

**Common Uses:**

### Scenario 1: App Service → On-Premises Database
```
Azure App Service
    │
    ├─ Hybrid Connection
    │  ("mycompany-db")
    │
    └─ Connects to:
       On-Premises SQL Server
       (192.168.1.100:1433)
```

**Setup:**
1. Create Hybrid Connection in App Service
2. Install Hybrid Connection Manager on-premises
3. Manager listens for requests
4. App Service routes calls through tunnel

**Connection String:**
```
Server=mycompany-hybrid;Database=MyDB;...
```

### Scenario 2: App Service → On-Premises Service
```
Azure App Service
    │
    ├─ Makes HTTP call:
    │  http://myservice-hybrid:8080/api/data
    │
    └─ Hybrid Connection tunnels to:
       On-Premises Service
       (localhost:8080)
```

---

## Installation & Configuration

### Hybrid Connection Manager (On-Premises)

**Step 1: Download**
- Get from Azure Portal or GitHub
- Lightweight Windows/Linux service

**Step 2: Install & Register**
```
HybridConnectionManager.exe
  /SBNamespace <your-namespace>
  /SBName <hybrid-connection-name>
  /SBKey <primary-key>
```

**Step 3: Configure Local Forwarding**
```
Local Listener: 127.0.0.1:1433
Hybrid Connection: mycompany-db
```

**Step 4: Start Service**
- Automatically routes traffic
- Maintains persistent connection to relay
- Auto-reconnects on failure

### App Service Configuration

**In Portal:**
```
Networking → Hybrid Connections
  Add: mycompany-db → mycorp-server.local:1433
```

**In Code:**
```csharp
// Use the Hybrid Connection name as hostname
var connection = new SqlConnection(
    "Server=mycompany-db;Database=MyDB;Integrated Security=true"
);
connection.Open();
```

---

## When to Use Each Approach

| Scenario | Use |
|----------|-----|
| **Legacy WCF apps in cloud calling on-prem services** | Azure Relay (WCF) |
| **Cloud REST APIs calling on-prem REST services** | Hybrid Relay (HTTP) |
| **App Service needing on-prem database** | Hybrid Connections |
| **Simple HTTP tunnel to on-prem system** | Hybrid Connections |
| **SOAP/WCF services** | Azure Relay (WCF) |

---

## Key Differences from Other Solutions

| Feature | Relay | Hybrid Conn | VPN | ExpressRoute |
|---------|-------|---------|-----|-----|
| **Setup Time** | Hours | Hours | Hours | Weeks |
| **Firewall Changes** | None | None | YES | None |
| **Cost** | Pay/message | Pay/month | Pay/month | High |
| **Use** | WCF/HTTP tunnel | App Service | Large scale | Enterprise |
| **Complexity** | Medium | Low | High | High |

---

## Best Practices

1. **Use Hybrid Connections for App Service**
   - Simpler than standalone relay
   - Built-in integration
   - Better Azure ecosystem fit

2. **Use V2 Runtime**
   - App Service on windows/linux
   - Better performance
   - More reliable

3. **Monitor Connections**
   - Track relay health
   - Monitor connection drops
   - Set up alerts

4. **Security**
   - Use Shared Access Policies
   - Rotate keys regularly
   - Use RBAC for access control

5. **Network Topology**
   - Keep hybrid manager on same network as resources
   - Use DNS names when possible
   - Avoid hardcoded IPs

---

## Troubleshooting

**Connection fails:**
- Check Hybrid Connection Manager running
- Verify on-prem service is accessible from manager
- Check SAS key hasn't expired

**High latency:**
- Relay adds ~100ms overhead
- Not ideal for real-time scenarios
- Consider ExpressRoute for better latency

**Port conflicts:**
- Use different local ports for multiple connections
- Example: 127.0.0.1:1433, 127.0.0.1:3306

---

## References

- [Azure Relay Documentation](https://learn.microsoft.com/en-us/azure/service-bus-relay/)
- [Hybrid Connections Overview](https://learn.microsoft.com/en-us/azure/app-service/app-service-hybrid-connections)
- [Install Hybrid Connection Manager](https://learn.microsoft.com/en-us/azure/app-service/install-hybrid-connection-manager)
- [Service Bus Relay Samples](https://github.com/Azure/azure-service-bus)

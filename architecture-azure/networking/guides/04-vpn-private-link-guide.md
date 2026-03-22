# VPN vs Private Link Guide

See [Index](./01-index.md) for overview.

## Quick Summary

| Aspect | VPN | Private Link |
|--------|-----|--------------|
| **What** | Encrypted tunnel connection | Private IP connection to PaaS |
| **Who** | Networks & users | VNet to PaaS service |
| **Path** | Encrypted internet | Private Link (backbone) |
| **Cost** | Higher (gateway + data) | Medium (per endpoint) |
| **Failover** | Config-dependent | Automatic |

**Simple Rule:** *VPN connects **networks**, Private Link connects to **services***

---

## VPN Gateway

### Types
- **Site-to-Site (S2S)**: On-premises network ↔ Azure VNet
- **Point-to-Site (P2S)**: Remote users ↔ Azure VNet
- **VNet-to-VNet**: Azure VNet ↔ Azure VNet

### Architecture
```
On-Premises (192.168.0.0/16)
         │
    IPsec/IKE Tunnel
         │
Azure VNet (10.0.0.0/16)
         │
    VMs, databases, services
```

### P2S Authentication Methods
- **Azure Certificate**: Client certificates validated by the gateway
- **Azure Active Directory**: Azure AD credentials (OpenVPN only)
- **RADIUS Server**: Integrates with on-premises Active Directory domain credentials

> **Key Exam Point:** To authenticate P2S users with AD domain credentials, a **RADIUS server** is required. The VPN Gateway delegates authentication to the RADIUS server, which validates against the AD Domain Controller.

### Use Cases
- Remote workers accessing Azure VMs
- Migrating on-premises systems to Azure
- Branch office connectivity
- Hybrid Active Directory replication

---

## Private Link & Private Endpoints

### Architecture
```
Azure VNet
    │
    ├── VM/App Service
    │
    └── Private Endpoint (10.0.1.5)
            │
            ▼ (Private Link)
    
    Azure PaaS Service
    (Storage, SQL, etc.)
```

### Supported Services
- Storage (Blob, File, Queue, Table)
- SQL Database & Cosmos DB
- Key Vault
- App Service
- Container Registry
- Event Hubs & Service Bus

### Use Cases
- Securing PaaS services from public access
- Compliance: no public IP exposure
- On-premises access (via VPN + Private Link)
- Data exfiltration protection

---

## Decision Matrix

```
Connect On-Prem Network to Azure Network?
  └─ YES → VPN Gateway (S2S) or ExpressRoute

Connect Individual Users to Azure?
  └─ YES → VPN Gateway (P2S)

Connect Azure VM to Azure SQL Database Privately?
  └─ YES → Private Endpoint

Connect On-Prem App to Azure SQL Privately?
  └─ YES → VPN (network) + Private Endpoint (service)

Two Azure VNets?
  └─ YES → VNet Peering (NOT VPN)

Azure App Service to On-Prem Database?
  └─ YES → Hybrid Connections (simpler) or VPN + VNet Integration
```

---

## Can They Work Together?

**YES!** They're complementary, not competing:

```
Complete Hybrid Setup:
  VPN = Network connectivity (on-prem ↔ Azure VNet)
  Private Link = Service security (VNet → PaaS)
  
  Example:
  On-Prem → VPN Gateway → Azure VNet → Private Endpoint → SQL DB
  On-Prem → VPN Gateway → Azure VNet → VM/App Service
```

---

## Detailed Materials

For complete information including:
- VPN Gateway SKUs and throughput
- Architecture diagrams
- Implementation steps
- Exam scenarios

See the [original comprehensive documentation](https://learn.microsoft.com/en-us/azure/vpn-gateway/) or Azure Learning paths.

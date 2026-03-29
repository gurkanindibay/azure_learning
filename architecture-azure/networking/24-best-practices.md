# Azure Networking Best Practices Guide

See [README](./README.md) for overview.

## Design Principles

### 1. Zero Trust Network Access

**Principle:** Never trust, always verify.

**Implementation:**
```
Old Way (Perimeter):
  Corporate network = safe
  Internet = untrusted
  → One VPN gateway × all traffic

New Way (Zero Trust):
  Every connection verified
  Every device authenticated
  Every app authorized
  → Multiple checkpoints per connection
```

**In Azure:**
```
┌─────────────────────────────────────┐
│ Corporate Device (Intune-joined)    │
│ ├─ Device Compliance Check          │
│ ├─ MFA + Conditional Access         │
│ └─ Encryption Required              │
└──────────────┬──────────────────────┘
               │
         Azure Bastion
         (Just-in-time access)
               │
         ┌─────┴──────────┐
         ▼               ▼
     Azure VNet     Private Endpoints
     (NSG rules)    (No public IPs)
```

### 2. Defense in Depth

**Layers:**
```
Layer 1: Perimeter
  └─ Azure Firewall (any-to-any rules)
     DDoS Protection (standard/premium)

Layer 2: Network
  └─ NSG (subnet level)
     ASG (group level)

Layer 3: Workload
  └─ WAF (web application firewall)
     TLS/mTLS (encryption)

Layer 4: Data
  └─ Encryption at rest (Storage, SQL)
     Encryption in transit (TLS 1.2+)

Layer 5: Access
  └─ RBAC (who can change configs)
     Network policies (pod-level in AKS)
```

### 3. Simplicity Over Features

**Guideline:**
- Start simple, add complexity when needed
- Avoid feature creep
- Document all custom routing

**Example - Wrong Approach:**
```
Complexity: 
  ├─ 3 types of gateways
  ├─ 15 UDRs
  ├─ Custom DNS zones
  ├─ Multiple firewalls
  ├─ Peering + service endpoints + private endpoints
  └─ → Nobody understands the topology
```

**Correct Approach:**
```
Simplicity:
  ├─ One gateway type
  ├─ 3-5 strategic UDRs
  ├─ Single DNS solution
  ├─ One firewall
  └─ → Topology is clear and maintainable
```

---

## Network Architecture Patterns

### Hub-and-Spoke (Recommended for Most)

**Layout:**
```
         Gateway
            │
    ┌───────┼────────┐
    ▼       ▼        ▼
  Spoke1  Spoke2   Spoke3
```

**Why:** 
- Central control point
- Easy to add/remove spokes
- Cost-efficient
- Scales to 100+ spokes

**Firewall in Hub:**
```
1. All spoke traffic goes through hub firewall
2. Firewall inspects everything
3. Logs for compliance
4. Easy to block/allow patterns
```

**Configuration:**
```
Spoke UDR: 0.0.0.0/0 → Hub Firewall IP
Hub NSG: Allow spoke CIDR blocks only
Hub Route Table: Route to gateway/firewall
```

### Full Mesh (Small Teams Only)

**Layout:**
```
VNet1 ──── VNet2
  │   \  / │
  │    \/  │
  │    /\  │
  │   /  \ │
VNet4 ──── VNet3
```

**When to use:**
- Very small number of VNets (2-3)
- All-to-all communication needed
- High-bandwidth requirements

**Downsides:**
- Difficult to manage at scale
- Firewall/logging hard to implement
- High operational burden
- N² relationships (grows fast)

---

## Routing Best Practices

### 1. Use BGP for Multi-Site

**Instead of:** Static routes (manual updates needed on failures)

**Use:** BGP with ExpressRoute (automatic failover)

```
# CORRECT
On-Prem Router → BGP → Azure Gateway
  Routes: Dynamic, automatic failover
  
# WRONG
On-Prem Router → Static Routes → Azure Gateway
  Routes: Manual, zero downtime on changes
```

### 2. Effective Routes Priority

```
Priority (highest to lowest):
1. Longest prefix match (most specific first)
2. UDR (user-defined routes)
3. BGP routes (from ExpressRoute)
4. System routes (default Azure routing)
```

**Example:**
```
Request to 10.1.2.5:
┌─────────────────────────────────────┐
│ Check in order:                     │
│ 1. Any UDR matching 10.1.2.5? No    │
│ 2. Any UDR matching 10.1.0.0/16? No │
│ 3. BGP learned 10.1.0.0/8? Yes      │
│    → Use BGP next hop              │
└─────────────────────────────────────┘
```

### 3. Document Custom Routing

**Template:**
```markdown
## Custom Route: Finance Workload

**Purpose:** Route all finance traffic through DLP appliance

**Destination:** 10.20.0.0/16 (Finance App)
**Next Hop Type:** Virtual Appliance
**Next Hop IP:** 10.0.10.5 (DLP appliance)
**User Defined:** Yes

**Why:** Compliance requires DLP scanning
**Failure Mode:** If appliance down, traffic drops (fail-secure)
**Owner:** Finance Team
**Last Reviewed:** 2024-01-15
```

---

## Security Hardening

### NSG Rules - Least Privilege

**Wrong:**
```
NSG Rule 1: Allow 0.0.0.0/0 → Any
  (Allow everyone to everything)
```

**Correct:**
```
NSG Rules:
1. Allow 10.0.0.0/8 → 443 (HTTPS from corporate)
2. Allow 10.0.0.0/8 → 22 (SSH from bastion subnet only)
3. Deny everything else (implicit default)
```

### Application Security Groups (ASG)

**Use for:**
- Multi-tier applications
- Allow tier-to-tier communication

**Example:**
```
ASG:
  "web-tier": VMs 10.0.1.0-10
  "app-tier": VMs 10.0.2.0-10
  "db-tier": VMs 10.0.3.0-10

Rules:
  1. web-tier → app-tier:8080 ✓
  2. app-tier → db-tier:5432 ✓
  3. web-tier → db-tier ✗ (blocked)
  4. internet → web-tier:443 ✓
```

**Benefit:** Add VM to ASG, rules apply automatically

### Private Endpoints for PaaS

**Instead of:**
```
SQL: Publicly accessible (public endpoint)
  Access from: Anyone with credentials
  Attack surface: Internet-facing
```

**Use:**
```
SQL: Private endpoint only
  Access from: VNet only (via private IP)
  Firewalled: No public access
```

---

## Monitoring & Troubleshooting

### Network Watcher

**Enable for all VNets:**
```
Regions with VNets:
  ├─ East US → Network Watcher (checkpoints)
  ├─ West US → Network Watcher (checkpoints)
  └─ Europe → Network Watcher (checkpoints)
```

**Key Features:**
- **IP Flow Verify**: Debug NSG rules
- **Packet Capture**: Analyze packet traces
- **Connection Troubleshoot**: End-to-end connectivity
- **Next Hop**: See actual routing

### Application Insights for Hybrid

**Monitor:**
- App Service calling on-prem via Hybrid Connection
- Latency (baseline + alerts)
- Failed connections (auto-reconnect counts)
- Dependency tracking

**Alerts:**
```
Alert 1: Hybrid Connection latency > 200ms
           → Check on-prem link quality

Alert 2: Connection drop rate > 5%
           → Check on-prem service health

Alert 3: Failed requests > 10%
           → Check firewall rules
```

### Log Analytics

**Collect:**
```
NSG Flow Logs:
  ├─ Allowed traffic
  ├─ Denied traffic
  └─ Who? What? When?

Network Watcher Logs:
  ├─ Routing decisions
  ├─ BGP advertisements
  └─ Peering status

Azure Firewall Logs:
  ├─ All rule matches
  ├─ Blocked connections
  └─ Application data
```

**Query:**
```kusto
// Find all denied traffic from subnet
AzureNetworkAnalytics_CL
| where FlowStatus_s == "D"
| where SourceIP startswith "10.0.1."
| summarize count() by DestinationIP
```

---

## Cost Optimization

### 1. VNet Peering Costs

**Pricing:** $0.045/hour per Gbps (ingress/egress)

**Optimization:**
```
EXPENSIVE:
  ├─ VNet1 → VNet2 (full mesh, all vnets talk)
  ├─ VNet2 → VNet3
  └─ → High data transfer costs

OPTIMIZED:
  ├─ Spoke → Hub (only central point)
  ├─ Hub → Spoke (aggregated)
  └─ → Much lower data transfer
```

### 2. Gateway Bandwidth

**VPN Gateway Pricing:** $0.36/hour (Basic)

**Optimization:**
```
✓ Use passive setup if no continuous traffic
✓ Use smaller tier if bandwidth < 100 Mbps
✓ Consider ExpressRoute for sustained high traffic
```

### 3. Data Transfer Costs

**Intra-region:** Free
**Cross-region:** $0.02/GB out
**Internet egress:** $0.087/GB out

**Optimization:**
```
EXPENSIVE:
  East US → West US (continuous replication)
  → $0.02/GB × data size

OPTIMIZED:
  Two-region active: Read-local, Write-local
  → Only occasional sync traffic
```

---

## Compliance & Governance

### 1. Network Isolation for Workloads

```
Public Web Tier
  ├─ Perimeterless (Public IP OK)
  ├─ WAF in front
  └─ HTTPS/TLS required

Internal App Tier
  ├─ Private VNet only
  ├─ Access via Private Link
  └─ Encryption always on

Sensitive Data Tier
  ├─ Isolated VNet (no peering to others)
  ├─ Encryption at rest + in transit
  └─ Audit logging mandatory
```

### 2. Compliance Monitoring

**Azure Policy:**
```
Policy: Enforce NSG on all subnets
  → Auto-blocks creation without NSG

Policy: Enforce Private Endpoints for SQL
  → Only allow private, not public endpoints

Policy: Enforce TLS 1.2 minimum
  → Reject TLS 1.0/1.1 connections
```

### 3. Audit & Logging

**Enable:**
- Activity logs (who changed what)
- NSG flow logs (all traffic)
- Firewall logs (rule matches)
- Diagnostic logs (platform events)

**Retention:** 30-90 days minimum

---

## Common Pitfalls to Avoid

| Pitfall | Impact | Solution |
|---------|--------|----------|
| Unknown UDRs | Routing breaks unexpectedly | Document all custom routes |
| Overlapping CIDR blocks | IP conflict, services unreachable | Plan address space upfront |
| Forgot NSG on subnet | Unintended access allowed | Use Azure Policy to enforce |
| Private Link DNS not set up | Can't reach PaaS from on-prem | Configure hybrid DNS correctly |
| No monitoring | Outages unnoticed for hours | Enable Network Watcher on all vnets |
| Too many gateways | High cost and complexity | Use hub-and-spoke instead |
| Manual BGP tuning | Brittle failover logic | Use path prepending, not tweaks |

---

## References

- [Azure Networking Best Practices](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/azure-best-practices/network-segmentation)
- [Hub-Spoke Reference Architecture](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/hybrid-networking/hub-spoke)
- [Zero Trust with Azure](https://learn.microsoft.com/en-us/security/zero-trust/zero-trust-overview)
- [Network Watcher Documentation](https://learn.microsoft.com/en-us/azure/network-watcher/)
- [Azure Firewall Best Practices](https://learn.microsoft.com/en-us/azure/firewall/best-practices)

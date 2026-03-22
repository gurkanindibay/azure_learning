# Azure Virtual WAN

## Table of Contents

- [1. Overview](#1-overview)
- [2. Key Components](#2-key-components)
  - [📝 Exam Scenario: Available configurations for Basic Virtual WAN](#-exam-scenario-available-configurations-for-basic-virtual-wan)
- [3. Virtual WAN Hub Planning](#3-virtual-wan-hub-planning)
- [4. ExpressRoute and Global Reach](#4-expressroute-and-global-reach)
  - [4.1 What is ExpressRoute?](#41-what-is-expressroute)
  - [4.2 ExpressRoute Global Reach](#42-expressroute-global-reach)
- [5. Cost Optimization Considerations](#5-cost-optimization-considerations)
- [6. Virtual Hub Routing](#6-virtual-hub-routing)
  - [6.1 Route Tables and Connections](#61-route-tables-and-connections)
- [7. Network Virtual Appliances (NVA) in Virtual WAN Hub](#7-network-virtual-appliances-nva-in-virtual-wan-hub)
  - [7.1 NVA Resource Groups](#71-nva-resource-groups)

---

## 1. Overview

**Azure Virtual WAN** is a networking service that provides optimized and automated branch connectivity to, and through, Azure. It brings together many Azure networking services, such as VPN, ExpressRoute, and Azure Firewall, into a single operational interface.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           AZURE VIRTUAL WAN ARCHITECTURE                         │
│                                                                                  │
│                           ┌─────────────────────┐                               │
│                           │   Azure Virtual WAN  │                               │
│                           │    (Orchestration)   │                               │
│                           └──────────┬──────────┘                               │
│                                      │                                          │
│          ┌───────────────────────────┼───────────────────────────┐             │
│          │                           │                           │              │
│          ▼                           ▼                           ▼              │
│   ┌─────────────┐             ┌─────────────┐             ┌─────────────┐       │
│   │  Hub 1      │             │  Hub 2      │             │  Hub 3      │       │
│   │ (East US)   │◄───────────►│(North Europe)│◄───────────►│(Southeast  │       │
│   │             │             │             │             │   Asia)    │       │
│   └──────┬──────┘             └──────┬──────┘             └──────┬──────┘       │
│          │                           │                           │              │
│   ┌──────┴──────┐             ┌──────┴──────┐             ┌──────┴──────┐       │
│   │ ExpressRoute│             │ ExpressRoute│             │ ExpressRoute│       │
│   │ VPN Gateway │             │ VPN Gateway │             │ VPN Gateway │       │
│   │ VNet Conns  │             │ VNet Conns  │             │ VNet Conns  │       │
│   └──────┬──────┘             └──────┬──────┘             └──────┴──────┘       │
│          │                           │                           │              │
│          ▼                           ▼                           ▼              │
│   New York Office            Paris Office               Sydney Office           │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Key Benefits:**
- Unified management of VPN, ExpressRoute, and Azure Firewall
- Automated hub-to-hub full mesh connectivity
- Global transit network architecture
- Integration with Azure Monitor for network insights

---

## 2. Key Components

| Component | Description |
|-----------|-------------|
| **Virtual WAN** | Parent resource that contains all hubs and connections |
| **Hub** | Regional network hub with VPN, ExpressRoute, and VNet connections |
| **Hub VPN Gateway** | Provides Site-to-Site VPN connectivity within a hub |
| **ExpressRoute Gateway** | Enables ExpressRoute circuit connectivity |
| **VNet Connection** | Connects spoke VNets to the hub |
| **Hub-to-Hub Connection** | Automatic full mesh connectivity between hubs |

**Virtual WAN Types:**

| Type | Features | Use Case |
|------|----------|----------|
| **Basic** | Site-to-Site VPN only | Simple branch connectivity |
| **Standard** | ExpressRoute, User VPN, VNet connections, Hub-to-hub transit | Enterprise global transit network |

### 📝 Exam Scenario: Available configurations for Basic Virtual WAN

**Question:**
There are two types of virtual WANs: Basic and Standard. Basic virtual WAN supports different configurations. Choose the available configurations for Basic virtual WAN from the given options.

- A) User VPN (P2S)
- B) ExpressRoute
- C) Azure Firewall
- D) Site-to-site VPN
- E) All the Above

**Answer: D) Site-to-site VPN**

**Explanation:**

Basic Virtual WAN supports **only** Site-to-Site VPN configuration. All other features require Standard Virtual WAN.

| Option | Correct/Incorrect | Reason |
|--------|-------------------|--------|
| **A) User VPN (P2S)** | ❌ Incorrect | User VPN (Point-to-Site) is only available in Standard Virtual WAN |
| **B) ExpressRoute** | ❌ Incorrect | ExpressRoute is not available in Basic Virtual WAN |
| **C) Azure Firewall** | ❌ Incorrect | Azure Firewall integration is not available in Basic Virtual WAN |
| **D) Site-to-site VPN** | ✅ **Correct** | Basic Virtual WAN supports only Site-to-Site VPN configuration |
| **E) All the Above** | ❌ Incorrect | Only Site-to-Site VPN is supported in Basic Virtual WAN |

**Feature comparison by Virtual WAN type:**

| Feature | Basic | Standard |
|---------|:-----:|:--------:|
| Site-to-Site VPN | ✅ | ✅ |
| User VPN (P2S) | ❌ | ✅ |
| ExpressRoute | ❌ | ✅ |
| Azure Firewall | ❌ | ✅ |
| Hub-to-hub transit | ❌ | ✅ |
| VNet-to-VNet through hub | ❌ | ✅ |

**Key Takeaway:**
> **Basic Virtual WAN** supports only **Site-to-Site VPN**. For any other feature (ExpressRoute, User VPN, Azure Firewall, hub-to-hub transit), you must use **Standard Virtual WAN**.

**Reference:** [Azure Virtual WAN Overview | Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-wan/virtual-wan-about)

---

## 3. Virtual WAN Hub Planning

When planning Virtual WAN hubs, you need to consider:

1. **One Hub Per Region**: Each Azure region where you need connectivity requires its own hub
2. **ExpressRoute Circuits**: Each hub can connect to ExpressRoute circuits in that region
3. **Latency Requirements**: Place hubs close to your offices for optimal performance
4. **Cost Optimization**: Each hub incurs charges; minimize hubs while meeting requirements

### 📝 Exam Scenario: Global Office Connectivity

**Scenario:**
A company has offices in New York City, Sydney, Paris, and Johannesburg. They have an Azure subscription and plan to deploy a networking solution that:
- Connects to ExpressRoute circuits in East US, Southeast Asia, North Europe, and South Africa
- Minimizes latency by supporting connection in three regions
- Supports Site-to-Site VPN connections
- Minimizes costs

**Question:** What is the minimum number of Azure Virtual WAN hubs required?

**Answer: 3 hubs**

**Explanation:**

Azure Virtual WAN requires deploying at least one hub per region to support ExpressRoute connectivity while minimizing latency. Given the requirements:

| Requirement | Analysis |
|-------------|----------|
| Connect to 4 ExpressRoute regions | Need hubs strategically placed to connect circuits |
| Minimize latency in 3 regions | Need 3 hubs minimum |
| Support S2S VPN | Standard Virtual WAN with VPN capability |
| Minimize costs | Use only 3 hubs instead of 4 |

**Strategic Hub Placement (Example):**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    OPTIMAL 3-HUB DEPLOYMENT                                      │
│                                                                                  │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│   │   Hub 1         │    │   Hub 2         │    │   Hub 3         │            │
│   │   East US       │◄──►│   North Europe  │◄──►│   Southeast Asia│            │
│   │                 │    │   or            │    │                 │            │
│   │                 │    │   South Africa  │    │                 │            │
│   └────────┬────────┘    └────────┬────────┘    └────────┬────────┘            │
│            │                      │                      │                      │
│            ▼                      ▼                      ▼                      │
│    ┌───────────────┐     ┌───────────────┐      ┌───────────────┐              │
│    │ ExpressRoute  │     │ ExpressRoute  │      │ ExpressRoute  │              │
│    │ Circuit       │     │ Circuit       │      │ Circuit       │              │
│    │ (East US)     │     │ (N.Europe or  │      │ (SE Asia)     │              │
│    │               │     │  S.Africa)    │      │               │              │
│    └───────────────┘     └───────────────┘      └───────────────┘              │
│            │                      │                      │                      │
│            ▼                      ▼                      ▼                      │
│    New York Office        Paris or              Sydney Office                   │
│                          Johannesburg                                           │
│                          Office                                                 │
│                                                                                  │
│   Note: The 4th ExpressRoute circuit can connect via ExpressRoute Global       │
│         Reach or through an adjacent hub with some additional latency.          │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Why not 4 hubs?**
- The requirement explicitly states "minimize costs"
- The requirement asks for connectivity "in three regions" specifically
- Using only 3 hubs saves on hub charges while still providing connectivity to all 4 ExpressRoute circuits

**Why not 2 hubs?**
- Would not meet the requirement of "supporting connection in three regions"
- Would result in higher latency for offices further from hubs

### 📝 Exam Scenario: ExpressRoute Association with Basic Virtual WAN

**Scenario:**
You have an Azure subscription that contains:
- A **Basic** Azure Virtual WAN named VirtualWan1
- Two virtual hubs:

| Name | Location |
|------|----------|
| Hub1 | US East |
| Hub2 | US West |

- An ExpressRoute circuit in the US East Azure region

**Question:** You need to create an ExpressRoute association to VirtualWan1. What should you do first?

**Options:**
- A) Upgrade VirtualWan1 to Standard
- B) Create a gateway on Hub1
- C) Create a hub virtual network in US East
- D) Enable the ExpressRoute premium add-on

**Answer: A) Upgrade VirtualWan1 to Standard**

**Explanation:**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                VIRTUAL WAN TIERS AND EXPRESSROUTE SUPPORT                        │
│                                                                                  │
│   ┌─────────────────────────────────┐    ┌─────────────────────────────────┐    │
│   │        BASIC VIRTUAL WAN        │    │      STANDARD VIRTUAL WAN       │    │
│   │                                 │    │                                 │    │
│   │  ✓ Site-to-Site VPN only       │    │  ✓ Site-to-Site VPN            │    │
│   │  ✗ ExpressRoute NOT supported  │    │  ✓ ExpressRoute SUPPORTED      │    │
│   │  ✗ User VPN NOT supported      │    │  ✓ User VPN (Point-to-Site)    │    │
│   │  ✗ Hub-to-hub transit          │    │  ✓ Hub-to-hub transit          │    │
│   │  ✗ VNet-to-VNet through hub    │    │  ✓ VNet-to-VNet through hub    │    │
│   │                                 │    │                                 │    │
│   │  Use Case: Simple branch       │    │  Use Case: Enterprise global   │    │
│   │  connectivity                   │    │  transit network               │    │
│   └─────────────────────────────────┘    └─────────────────────────────────┘    │
│                                                                                  │
│   ⚠️ To use ExpressRoute with Virtual WAN, you MUST have Standard tier          │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Why each option is correct or incorrect:**

| Option | Correct/Incorrect | Reason |
|--------|-------------------|--------|
| **A) Upgrade VirtualWan1 to Standard** | ✅ **Correct** | ExpressRoute is not supported in Basic Virtual WAN. To associate an ExpressRoute circuit, the Virtual WAN must first be upgraded to Standard. Standard tier supports ExpressRoute, VPN, and inter-hub connectivity across regions. |
| **B) Create a gateway on Hub1** | ❌ Incorrect | Before creating an ExpressRoute gateway, Virtual WAN must be upgraded to Standard. Without this upgrade, you cannot create a gateway for ExpressRoute connectivity. |
| **C) Create a hub virtual network in US East** | ❌ Incorrect | Hub1 already exists in US East. Creating a new hub is unnecessary. The focus should be on upgrading the Virtual WAN to Standard tier to enable ExpressRoute support. |
| **D) Enable the ExpressRoute premium add-on** | ❌ Incorrect | The ExpressRoute premium add-on is only required for specific scenarios like connecting more than 10 VNet connections or enabling global reach between circuits. It does not enable ExpressRoute integration with a Basic Virtual WAN. |

**Key Takeaway:**
> **Basic Virtual WAN only supports Site-to-Site VPN.** For ExpressRoute, User VPN (P2S), or inter-hub transit, you must use **Standard Virtual WAN**.

**Complete Configuration Steps:**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│              EXPRESSROUTE ASSOCIATION - COMPLETE WORKFLOW                        │
│                                                                                  │
│   Step 1                Step 2                Step 3                Step 4      │
│   ┌──────────┐         ┌──────────┐         ┌──────────┐         ┌──────────┐  │
│   │ Upgrade  │         │ Create   │         │ Associate│         │ Verify   │  │
│   │ Virtual  │────────►│ Express  │────────►│ Express  │────────►│ Connec-  │  │
│   │ WAN to   │         │ Route    │         │ Route    │         │ tivity   │  │
│   │ Standard │         │ Gateway  │         │ Circuit  │         │          │  │
│   └──────────┘         └──────────┘         └──────────┘         └──────────┘  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

| Step | Action | Details |
|------|--------|---------|
| **1. Upgrade Virtual WAN** | Change type from Basic to Standard | Navigate to VirtualWan1 → Configuration → Change Type to **Standard** → Save |
| **2. Create ExpressRoute Gateway** | Add gateway to Hub1 (US East) | Navigate to Hub1 → ExpressRoute → Create gateway → Select scale units (e.g., 1 scale unit = 2 Gbps) |
| **3. Associate ExpressRoute Circuit** | Connect circuit to gateway | In Hub1 → ExpressRoute → Add connection → Select your ExpressRoute circuit → Provide authorization key if circuit is in different subscription |
| **4. Verify Connectivity** | Test the connection | Check effective routes, verify BGP peering status, test connectivity from on-premises |

**Detailed Step-by-Step:**

**Step 1: Upgrade VirtualWan1 to Standard**
1. Go to Azure Portal → Virtual WANs → VirtualWan1
2. Select **Configuration** from the left menu
3. Change **Type** from `Basic` to `Standard`
4. Click **Save**
5. Wait for the upgrade to complete (may take a few minutes)

**Step 2: Create ExpressRoute Gateway on Hub1**
1. Navigate to VirtualWan1 → Hubs → Hub1
2. Select **ExpressRoute** under Connectivity
3. Click **Create gateway**
4. Configure gateway settings:
   - **Gateway scale units**: Select based on throughput needs (1 unit = 2 Gbps)
   - Minimum: 1 scale unit, Maximum: 10 scale units
5. Click **Create**
6. Wait for gateway provisioning (can take 30+ minutes)

**Step 3: Associate ExpressRoute Circuit**
1. After gateway is provisioned, go to Hub1 → ExpressRoute
2. Click **+ Add connection**
3. Configure connection:
   - **Connection name**: Provide a descriptive name
   - **ExpressRoute circuit**: Select your circuit (if in same subscription)
   - **Authorization key**: Required if circuit is in a different subscription
   - **Routing weight**: Optional, for traffic engineering
4. Click **Create**

**Step 4: Verify Connectivity**
1. Check connection status shows **Connected**
2. Verify BGP routes are being exchanged:
   - Hub1 → Effective Routes → Check learned routes from ExpressRoute
3. Test connectivity from on-premises to Azure resources
4. Monitor using Azure Monitor and Network Watcher

**ExpressRoute Gateway Scale Units:**

| Scale Units | Aggregate Throughput | Use Case |
|-------------|---------------------|----------|
| 1 | 2 Gbps | Small workloads, dev/test |
| 2 | 4 Gbps | Medium workloads |
| 5 | 10 Gbps | Large enterprise |
| 10 | 20 Gbps | Maximum throughput needs |

> ⚠️ **Note:** Gateway provisioning can take 30-45 minutes. Plan accordingly during maintenance windows.

---

## 4. ExpressRoute and Global Reach

### 4.1 What is ExpressRoute?

**Azure ExpressRoute** is a service that provides a private, dedicated connection between your on-premises infrastructure and Azure datacenters. Unlike VPN connections that travel over the public internet, ExpressRoute connections do not go over the public internet, offering more reliability, faster speeds, consistent latencies, and higher security.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         EXPRESSROUTE CONNECTION                                  │
│                                                                                  │
│   On-Premises                                               Azure               │
│   Data Center                                               Data Center         │
│   ┌─────────────┐      ┌──────────────────┐      ┌─────────────────────────┐   │
│   │             │      │  Connectivity    │      │                         │   │
│   │  Corporate  │──────│  Provider        │──────│   Azure Virtual         │   │
│   │  Network    │      │  (Partner Edge)  │      │   Network / Services    │   │
│   │             │      │                  │      │                         │   │
│   └─────────────┘      └──────────────────┘      └─────────────────────────┘   │
│                                                                                  │
│   ────────────────── Private Connection (Not over Internet) ──────────────────  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Key ExpressRoute Features:**

| Feature | Description |
|---------|-------------|
| **Private Connectivity** | Traffic does not traverse the public internet |
| **Bandwidth Options** | 50 Mbps to 100 Gbps |
| **SLA-backed** | 99.95% availability SLA |
| **Global Reach** | Connect on-premises sites through Azure backbone |
| **Peering Types** | Azure Private, Microsoft, and Azure Public (deprecated) |

**ExpressRoute Peering Types:**

| Peering Type | Purpose | Services Accessed |
|--------------|---------|-------------------|
| **Azure Private Peering** | Connect to Azure IaaS (VMs, VNets) | Virtual Machines, Load Balancers, VNet resources |
| **Microsoft Peering** | Connect to Azure PaaS and Microsoft 365 | Azure Storage, SQL Database, Microsoft 365, Dynamics 365 |

**ExpressRoute vs VPN:**

| Aspect | ExpressRoute | Site-to-Site VPN |
|--------|--------------|------------------|
| **Connection** | Private (dedicated) | Public internet (encrypted) |
| **Bandwidth** | Up to 100 Gbps | Up to 10 Gbps |
| **Latency** | Predictable, low | Variable |
| **Cost** | Higher | Lower |
| **Setup Time** | Days to weeks | Minutes to hours |
| **Use Case** | Mission-critical, high-bandwidth | Dev/test, smaller workloads |

### 4.2 ExpressRoute Global Reach

**ExpressRoute Global Reach** can extend connectivity between ExpressRoute circuits without going through Virtual WAN hubs:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    EXPRESSROUTE GLOBAL REACH                                     │
│                                                                                  │
│   On-Premises Site 1                      On-Premises Site 2                    │
│   (New York)                              (Paris)                               │
│        │                                       │                                │
│        ▼                                       ▼                                │
│   ┌───────────────┐                      ┌───────────────┐                      │
│   │ ExpressRoute  │◄─────────────────────►│ ExpressRoute  │                      │
│   │ Circuit       │    Global Reach       │ Circuit       │                      │
│   │ (East US)     │  (Microsoft Backbone) │ (North Europe)│                      │
│   └───────────────┘                      └───────────────┘                      │
│                                                                                  │
│   Direct site-to-site connectivity without traversing Virtual WAN               │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**When to Use ExpressRoute Global Reach:**
- Direct branch-to-branch communication without hub traversal
- Reducing latency for site-to-site traffic
- Complementing Virtual WAN for specific traffic patterns

---

## 5. Cost Optimization Considerations

| Factor | Impact on Cost |
|--------|----------------|
| **Number of Hubs** | Each hub incurs hourly charges |
| **Hub Scale Units** | Higher scale = higher cost but more throughput |
| **VPN Connections** | Per connection charges for Site-to-Site |
| **ExpressRoute** | Separate ExpressRoute circuit and port charges |
| **Data Transfer** | Egress charges for data leaving Azure |

**Cost Optimization Tips:**
1. Deploy hubs only in regions where you need low-latency connectivity
2. Use ExpressRoute Global Reach for site-to-site traffic when possible
3. Right-size hub scale units based on actual throughput needs
4. Consider hub placement that can serve multiple nearby offices

---

## 6. Virtual Hub Routing

### 6.1 Route Tables and Connections

In Azure Virtual WAN, connections to a virtual hub (VNet connections, VPN connections, ExpressRoute connections) are associated with **route tables**. These connections with routing configuration are called **Connection Manager resources**. Each connection is associated with a specific route table that determines how traffic is forwarded.

**Key Concepts:**

| Concept | Description |
|---------|-------------|
| **Default Route Table** | Every hub has a default route table that contains system routes |
| **Custom Route Tables** | User-created route tables for traffic segmentation and isolation |
| **Association** | Links a connection to a route table — determines which route table the connection uses to forward traffic |
| **Propagation** | Determines which route tables learn routes from a connection |

**How It Works:**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    VIRTUAL HUB ROUTING - CONNECTION ASSOCIATION                   │
│                                                                                  │
│   ┌──────────────┐         ┌─────────────────┐         ┌──────────────────┐     │
│   │  VNet        │         │  Virtual Hub    │         │  VNet            │     │
│   │  Connection  │────────►│  Route Table    │────────►│  Destination     │     │
│   │  (Spoke A)   │  assoc  │  ┌───────────┐  │  route  │  (Spoke B)       │     │
│   └──────────────┘         │  │10.1.0.0/16│  │         └──────────────────┘     │
│                            │  │10.2.0.0/16│  │                                  │
│   ┌──────────────┐         │  │10.3.0.0/16│  │         ┌──────────────────┐     │
│   │  VPN         │────────►│  └───────────┘  │────────►│  On-Premises     │     │
│   │  Connection  │  assoc  │                 │  route  │  Network         │     │
│   └──────────────┘         └─────────────────┘         └──────────────────┘     │
│                                                                                  │
│   Association = "Use THIS route table to decide where to send traffic"          │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 📝 Exam Scenario: Connection Association with Route Tables

**Question:**
Connections with routing configuration are called Connection Manager resources. Each connection is associated with a specific route table. Why is it important to associate a connection with a route table?

- A. It allows traffic to be directed to specified destinations in the route table. ✅
- B. This feature allows the automatic dissemination of routes from one route table to another, ensuring seamless connectivity.
- C. It authenticates the users.
- D. It encrypts the traffic that is being sent to the intended destination.

**Correct Answer: A. It allows traffic to be directed to specified destinations in the route table.**

**Explanation:**
Associating a connection with a route table enables the traffic originating from that connection to be forwarded to the destinations specified in the routing table. The routing configuration of the connection will show the associated route table, and all traffic from that connection will use those routes for forwarding decisions.

**Why Other Options Are Incorrect:**

| Option | Why Incorrect |
|--------|---------------|
| **B. Automatic route dissemination between route tables** | Connections do not dynamically propagate routes from one route table to another. Route **propagation** is a separate concept — it determines which route tables *learn* routes from a connection, not automatic copying between tables. |
| **C. User authentication** | Neither connections nor routing tables authenticate users. Authentication is handled by separate identity and access management services (Azure AD, certificates, etc.). |
| **D. Traffic encryption** | Associating a connection with a route table has nothing to do with encryption. Encryption is handled at the connection level (e.g., IPsec for VPN, MACsec for ExpressRoute Direct). |

**Key Takeaway:**
> **Association** determines *which route table* a connection uses to make forwarding decisions. **Propagation** determines *which route tables* learn routes from that connection. These are two distinct concepts in Virtual Hub routing.

---

## 7. Network Virtual Appliances (NVA) in Virtual WAN Hub

A **Network Virtual Appliance (NVA)** can be deployed directly into a Virtual WAN hub, enabling integrated third-party network functions such as firewalls, SD-WAN, and WAN optimization within the hub infrastructure.

### 7.1 NVA Resource Groups

When an NVA is created in the Virtual WAN hub, **two resource groups** are automatically created in the customer's subscription:

| Resource Group | Description |
|----------------|-------------|
| **Customer Resource Group** | Contains the customer-facing resources associated with the NVA deployment |
| **Managed Resource Group** | Contains resources managed by Azure on behalf of the NVA partner, used for the internal operation of the appliance |

> ⚠️ **Note:** No "Partner Resource Group", "Virtual Resource Group", or "Controlled Resource Group" is created during this process.

### 📝 Exam Scenario: NVA Resource Groups in Virtual WAN Hub

**Question:**
When a Network Virtual Appliance (NVA) is created in the Virtual WAN hub, which resource groups will be created in the customer's subscription? (Select all that apply)

- A) Customer Resource Group
- B) Partner Resource Group
- C) Managed Resource Group
- D) Virtual Resource Group
- E) Controlled Resource Group

**Correct Answers: A and C**

| Option | Correct/Incorrect | Reason |
|--------|-------------------|--------|
| **A) Customer Resource Group** | ✅ **Correct** | One of the two resource groups created during NVA deployment in the Virtual WAN hub |
| **B) Partner Resource Group** | ❌ Incorrect | Not created during the NVA deployment process |
| **C) Managed Resource Group** | ✅ **Correct** | The second resource group created during NVA deployment, managed by Azure for the appliance's internal operations |
| **D) Virtual Resource Group** | ❌ Incorrect | Not created during the NVA deployment process |
| **E) Controlled Resource Group** | ❌ Incorrect | Not created during the NVA deployment process |

**Key Takeaway:**
> When deploying an NVA in a Virtual WAN hub, exactly **two resource groups** are created: the **Customer Resource Group** and the **Managed Resource Group**.

**Reference:** [About Network Virtual Appliances in a Virtual WAN hub](https://learn.microsoft.com/en-us/azure/virtual-wan/about-nva-hub)

---

## Related Resources

- [Azure Virtual WAN Overview](https://learn.microsoft.com/en-us/azure/virtual-wan/virtual-wan-about)
- [Virtual WAN FAQ](https://learn.microsoft.com/en-us/azure/virtual-wan/virtual-wan-faq)
- [ExpressRoute Global Reach](https://learn.microsoft.com/en-us/azure/expressroute/expressroute-global-reach)
- [Virtual WAN Global Transit Network Architecture](https://learn.microsoft.com/en-us/azure/virtual-wan/virtual-wan-global-transit-network-architecture)
- [About Virtual Hub Routing](https://learn.microsoft.com/en-us/azure/virtual-wan/about-virtual-hub-routing)
- [Connect Remote Resources by Using Azure Virtual WANs - Training](https://learn.microsoft.com/en-us/training/modules/connect-remote-resources-by-using-azure-virtual-wans/)
- [Azure Networking Fundamentals](./azure-networking-fundamentals.md)

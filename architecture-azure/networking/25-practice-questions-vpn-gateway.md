# Practice Questions: Azure VPN Gateway

> **Certification Domain**: Design, implement, and manage connectivity services (20–25%)
> **Certification**: Microsoft Certified: Azure Network Engineer Associate (AZ-700)
> **General Pattern**: [VPN Gateway](./05-azure-vpn-gateway.md)
> **Taxonomy**: [§5 Cloud & Infrastructure / Platform Architecture](../../architecture-general/10-practicality-taxonomy/architecture_taxonomy_reference.md)

---

## Question 1: P2S VPN client cannot reach peered VNet after topology change

### Scenario

You have an Azure subscription named "Subscription2" which includes two Azure virtual networks (VNets) named VNet2 and VNet3. VNet2 has a VPN gateway named "VGW1" and it uses static routing. There is a site-to-site (S2S) VPN connectivity established between VNet2 and your on-premises network. You have also configured a point-to-site (P2S) VPN connectivity to VNet2 on a computer system named "Client2" running Windows 11. Additionally, you have configured VNet peering between VNet2 and VNet3.

During verification, you noticed that you can connect to VNet3 from the on-premises network but not from Client2. You need to resolve this issue and make sure that Client2 can connect to VNet3.

**What steps would you take to address this problem?**

- A) Select the option "Allow gateway transit" on VNet3.
- B) Select the option "Allow gateway transit" for VNet2.
- C) On VGW1 enable BGP.
- D) On Client2, download and re-install the VPN client configuration package.

### Answer

**Correct Answer: D**

On Client2, download and re-install the VPN client configuration package.

### Explanation

The behavior of Point-to-Site (P2S) VPN routing depends on the client's operating system, the protocol used for VPN connectivity, and the connection/link between the VNets.

Azure currently supports two protocols for remote access: **SSTP** and **IKEv2**. While IKEv2 is supported by many client operating systems (Windows, macOS, Linux, iOS, Android), SSTP is only supported by Windows.

**The critical rule**: If you make any changes to your network's topology (such as adding VNet peering, adding/removing address spaces, or changing gateway configurations) and have Windows VPN clients, you **must** download and install the VPN client configuration package again for the changes to be applied to the client.

**Why the other options are incorrect:**

| Option | Why Incorrect |
|--------|---------------|
| **A) Allow gateway transit on VNet3** | Gateway transit settings are already correctly configured — the S2S VPN from on-premises can already reach VNet3. The issue is client-side, not peering-side. |
| **B) Allow gateway transit on VNet2** | Same as above — the S2S connection already traverses the peering successfully. |
| **C) Enable BGP on VGW1** | BGP would help with dynamic route propagation for S2S connections, but P2S clients on Windows using SSTP still require re-downloading the client configuration after topology changes. |

### Key concept

> **P2S VPN client routing update rule**: After any network topology change (VNet peering, address space modification, etc.), Windows P2S VPN clients must re-download and reinstall the VPN client configuration package. The routes embedded in the client configuration are static and do not update automatically.

### Reference

- [About P2S VPN routing — Azure VPN Gateway | Microsoft Learn](https://learn.microsoft.com/en-us/azure/vpn-gateway/vpn-gateway-about-point-to-site-routing)
- [Azure VPN Gateway - P2S VPN](./05-azure-vpn-gateway.md#42-point-to-site-p2s-vpn)

---

## Question 2: ExpressRoute primary + VPN failover for 500+ employees

### Scenario

A company wants to connect its on-premises data center to Azure and desires a dedicated and failover connection. They are not concerned about having a brief latency drop during the failover connection. Additionally, the company has more than 500 employees who will require access to this connection.

**Which type of connection would you recommend to the company?**

- A) A Site-to-Site for the primary and failover connection.
- B) A Site-to-Site for the primary, and a Point-to-Site for the failover connection.
- C) An ExpressRoute for the primary connection, and a Site-to-Site for the failover connection.
- D) A Site-to-Site for the primary, and an ExpressRoute for the failover connection.

### Answer

**Correct Answer: C**

An ExpressRoute for the primary connection, and a Site-to-Site for the failover connection.

### Explanation

The question has three key requirements that drive the answer:

1. **"Dedicated" connection** → ExpressRoute provides a private, dedicated link between on-premises and Azure (not over the public internet). S2S VPN uses the internet, so it is not "dedicated."
2. **"Acceptable brief latency drop during failover"** → S2S VPN runs over the internet with variable latency (higher than ExpressRoute). The company accepts this trade-off for the failover path.
3. **"500+ employees"** → This eliminates P2S VPN as a viable failover option.

**Why each option is correct or incorrect:**

| Option | Verdict | Reason |
|--------|---------|--------|
| **A) S2S primary + S2S failover** | ❌ | S2S VPN is internet-based, not a "dedicated" connection. Does not satisfy the primary connection requirement. |
| **B) S2S primary + P2S failover** | ❌ | S2S is not dedicated (same as A). P2S requires individual VPN client on every device — impractical for 500+ users. P2S max connections are 250–1000 depending on SKU. |
| **C) ExpressRoute primary + S2S failover** | ✅ | ExpressRoute = dedicated private circuit. S2S VPN = cost-effective failover with acceptable latency increase. All 500+ users route through S2S automatically (site-wide tunnel). |
| **D) S2S primary + ExpressRoute failover** | ❌ | Reversed priority — the dedicated (more expensive, higher quality) connection should be the primary, not the failover. ExpressRoute takes weeks to provision, making it impractical as a standby failover. |

**Coexisting configuration requirements:**
- VPN gateway must be **route-based** (policy-based does not support coexistence)
- GatewaySubnet must be `/27` or larger (recommended `/26`)
- Both gateways reside in the same VNet, sharing the GatewaySubnet
- BGP recommended for automatic failover (lower metric assigned to ExpressRoute routes)

### Key concept

> **ExpressRoute + S2S VPN coexistence** is a common pattern for enterprise hybrid connectivity. ExpressRoute serves as the high-bandwidth, low-latency primary path, while S2S VPN provides a cost-effective internet-based failover. BGP handles automatic route switching when the ExpressRoute circuit fails. This is distinct from P2S VPN, which is designed for individual remote users — not site-wide failover.

### Reference

- [Configure ExpressRoute and S2S VPN coexisting connections | Microsoft Learn](https://learn.microsoft.com/en-us/azure/expressroute/expressroute-howto-coexist-resource-manager)
- [ExpressRoute + VPN failover scenario](./23-networking-scenarios.md#hybrid-cloud-with-expressroute--vpn-failover)
- [VPN Gateway SKU comparison](./05-azure-vpn-gateway.md)

---

## Question 3: Valid VPN types for virtual network gateway

### Scenario

While creating the virtual network gateway for a VPN configuration, you need to specify a VPN type. Which of the following are valid VPN types that you can choose? (Select all applicable options)

- A) PolicyBased
- B) IntervalBased
- C) RouteBased
- D) LinkBased
- E) StatusBased

### Answer

**Correct Answers: A, C**

PolicyBased and RouteBased are the only two valid VPN types.

### Explanation

When creating a Virtual Network Gateway with gateway type **Vpn**, you must specify a **VPN type**. Azure supports exactly two VPN types:

- **PolicyBased** — Encrypts and directs packets through IPsec tunnels based on traffic selectors (combinations of source/destination address prefixes). Uses IKEv1 only. Limited to 1 S2S tunnel, Basic SKU only, and does not support P2S, VNet-to-VNet, BGP, or active-active configurations. Previously called "static routing."
- **RouteBased** — Uses IP forwarding/routing table to direct packets into tunnel interfaces. Supports IKEv1 and IKEv2, multiple S2S tunnels, P2S, VNet-to-VNet, BGP, active-active, and ExpressRoute coexistence. Previously called "dynamic routing." **Recommended for most scenarios.**

**Why the other options are incorrect:**

| Option | Why Incorrect |
|--------|---------------|
| **B) IntervalBased** | Not a valid VPN type. Does not exist in Azure. |
| **D) LinkBased** | Not a valid VPN type. Does not exist in Azure. |
| **E) StatusBased** | Not a valid VPN type. Does not exist in Azure. |

### Key concept

> **VPN type selection rule**: The only valid values for the `--vpn-type` parameter (or the "VPN type" portal setting) are **PolicyBased** and **RouteBased**. RouteBased is recommended unless a legacy on-premises VPN device requires PolicyBased. The choice impacts which features are available (P2S, multi-site, BGP, active-active, etc.).

### Reference

- [VPN Gateway configuration settings — VPN type | Microsoft Learn](https://learn.microsoft.com/en-us/azure/vpn-gateway/vpn-gateway-about-vpn-gateway-settings#vpntype)
- [Azure VPN Gateway — VPN Types](./05-azure-vpn-gateway.md#23-vpn-types-policybased-vs-routebased)

---

## Question 4: Correct sequence for IPsec/IKE policy configuration on S2S VPN

### Scenario

As the system administrator, you are responsible for creating and configuring the IPsec/IKE policy for a site-to-site VPN connection. You will need to follow the steps outlined below (not necessarily in the correct sequence) to develop and update the policy:

a. Create a local network gateway for the cross-premises connection.
b. Create a virtual network and a VPN gateway.
c. Create an IPsec/IKE policy by selecting appropriate algorithms and parameters.
d. Set up an IPsec connection using the IPsec/IKE policy.
e. Add, update, or remove an IPsec/IKE policy for an existing connection.

**Place the above steps in the correct sequence.**

- A) b-a-c-d-e
- B) a-b-c-d-e
- C) a-b-d-c-e
- D) a-c-d-e-b
- E) b-a-d-c-e

### Answer

**Correct Answer: A**

b-a-c-d-e

### Explanation

The correct sequence follows a logical dependency chain — each step requires the resources from previous steps to exist:

| Step | Action | Why This Order |
|------|--------|----------------|
| **1 (b)** | Create a virtual network and a VPN gateway | The VNet and VPN gateway must exist first. The VPN gateway is deployed in the GatewaySubnet and requires a public IP — it is the Azure-side anchor for any VPN connection. |
| **2 (a)** | Create a local network gateway | The local network gateway represents the on-premises VPN device in Azure. It stores the on-premises public IP and address ranges. It must exist before a connection can reference it. |
| **3 (c)** | Create an IPsec/IKE policy | The policy object (encryption algorithms, integrity algorithms, DH groups, PFS groups, SA lifetimes) must be defined before it can be attached to a connection. |
| **4 (d)** | Create the S2S VPN connection with the policy | The connection resource links the VPN gateway and local network gateway together. The pre-defined IPsec/IKE policy is attached at creation time. |
| **5 (e)** | Add, update, or remove an IPsec/IKE policy | Policy modifications happen on an already-existing connection. You can update the algorithms/parameters or remove the custom policy entirely (reverting to Azure defaults). |

**Why the other options are incorrect:**

| Option | Why Incorrect |
|--------|---------------|
| **B) a-b-c-d-e** | Creates the local network gateway before the VNet/VPN gateway. While technically possible, the standard workflow creates the VNet and VPN gateway first since they form the Azure-side foundation. |
| **C) a-b-d-c-e** | Creates the connection (d) before defining the IPsec/IKE policy (c). You cannot attach a policy to a connection if the policy hasn't been created yet. |
| **D) a-c-d-e-b** | Creates the VPN gateway last (b), which is impossible — you need the VPN gateway to create the connection (d). |
| **E) b-a-d-c-e** | Creates the connection (d) before the IPsec/IKE policy (c). The policy must exist before it can be referenced during connection creation. |

### Key concept

> **IPsec/IKE policy configuration workflow**: The dependency chain is VNet/VPN Gateway → Local Network Gateway → IPsec/IKE Policy → S2S Connection → Policy Updates. Each step depends on the output of the previous step. The VPN gateway and local network gateway are the two endpoints of a connection, the policy defines the encryption parameters, and policy updates are lifecycle operations on existing connections.

### Reference

- [Configure IPsec/IKE policy for S2S VPN or VNet-to-VNet connections | Microsoft Learn](https://learn.microsoft.com/en-us/azure/vpn-gateway/ipsec-ike-policy-howto)
- [Azure VPN Gateway — IPsec/IKE Protocols](./05-azure-vpn-gateway.md#81-ipsecike-protocols)

---

## Question 5: Azure resources required for BGP on Site-to-Site VPN

### Scenario

You plan to configure BGP for a Site-to-Site VPN connection between a datacenter and Azure.

**Which two Azure resources should you configure?** (Select two)

- A) A virtual network gateway
- B) Azure Application Gateway
- C) Azure Firewall
- D) A local network gateway
- E) Azure Front Door

### Answer

**Correct Answers: A, D**

A virtual network gateway and a local network gateway.

### Explanation

Configuring BGP for a Site-to-Site VPN requires BGP settings on **two** Azure resources that represent the two endpoints of the VPN tunnel:

| Resource | Role in BGP Configuration |
|----------|---------------------------|
| **A) Virtual network gateway** ✅ | The Azure-side VPN endpoint. You configure the Azure BGP ASN (default 65515) and it is auto-assigned a BGP peer IP from the GatewaySubnet. Must be RouteBased with a SKU of VpnGw1 or higher. |
| **D) Local network gateway** ✅ | Represents the on-premises VPN device in Azure. You configure the on-premises BGP peer IP address and Autonomous System Number (ASN) here so Azure knows how to establish the BGP session with the on-premises router. |

**Why the other options are incorrect:**

| Option | Why Incorrect |
|--------|---------------|
| **B) Azure Application Gateway** | A Layer 7 web traffic load balancer for managing HTTP/HTTPS traffic to web applications. It has no role in VPN connectivity or BGP routing. |
| **C) Azure Firewall** | A managed cloud-based network security service that protects Azure Virtual Network resources with stateful firewall rules. It is not involved in VPN tunnel establishment or BGP route exchange. |
| **E) Azure Front Door** | A global entry point for web applications providing CDN, SSL offloading, and WAF capabilities. It operates at the application layer and has no involvement in Site-to-Site VPN or BGP configuration. |

### Key concept

> **BGP for S2S VPN requires two gateway resources**: The **virtual network gateway** (Azure-side endpoint with Azure BGP ASN) and the **local network gateway** (on-premises representation with the on-premises BGP peer IP and ASN). BGP is then enabled on the **connection** resource that links these two gateways. This is distinct from ExpressRoute, where BGP is mandatory and configured at the circuit/peering level.

### Reference

- [Configure BGP for Azure VPN Gateway | Microsoft Learn](https://learn.microsoft.com/en-us/azure/vpn-gateway/bgp-howto)
- [Azure VPN Gateway — BGP Support](./05-azure-vpn-gateway.md#82-bgp-support)

---

## Question 6: Troubleshooting IPsec tunnel establishment failure

### Scenario

You fail to establish a Site-to-Site VPN connection between your company's main office and an Azure virtual network.

You need to troubleshoot what prevents you from establishing the IPsec tunnel.

**Which diagnostic log should you review?**

- A) IKEDiagnosticLog
- B) RouteDiagnosticLog
- C) GatewayDiagnosticLog
- D) TunnelDiagnosticLog

### Answer

**Correct Answer: A**

IKEDiagnosticLog

### Explanation

IPsec tunnel establishment is handled by the **IKE (Internet Key Exchange)** protocol. IKE negotiates the security associations (SAs) required before an IPsec tunnel can be created. The negotiation follows two phases:

1. **Phase 1 (IKE SA)**: Peers negotiate encryption, integrity, and DH group parameters, then authenticate each other (pre-shared key or certificate)
2. **Phase 2 (IPsec SA)**: Peers negotiate the IPsec parameters and establish the tunnel for data traffic

If the tunnel **fails to establish**, the failure is happening during one of these IKE phases. The **IKEDiagnosticLog** captures all IKE negotiation messages, proposal mismatches, authentication failures, timeouts, and error codes — making it the correct log to review.

**Why the other options are incorrect:**

| Option | Why Incorrect |
|--------|---------------|
| **B) RouteDiagnosticLog** | Logs route changes and BGP route updates. Useful for troubleshooting routing problems **after** a tunnel is already established, not for tunnel establishment failures. |
| **C) GatewayDiagnosticLog** | Logs gateway health events, configuration changes, and maintenance activities. Provides general gateway status but not the granular IKE negotiation details needed to diagnose IPsec tunnel failures. |
| **D) TunnelDiagnosticLog** | This log category **does not exist** in Azure VPN Gateway. The valid diagnostic log categories are: IKEDiagnosticLog, GatewayDiagnosticLog, RouteDiagnosticLog, and P2SDiagnosticLog. |

### Key concept

> **IKE is the gatekeeper of IPsec**: No IPsec tunnel can be established without a successful IKE negotiation. When troubleshooting tunnel establishment failures, always start with the **IKEDiagnosticLog**. Common issues found in IKE logs include mismatched encryption algorithms, incorrect pre-shared keys, DH group incompatibilities, and IKE version mismatches (IKEv1 vs IKEv2).

### Reference

- [VPN Gateway diagnostic log queries | Microsoft Learn](https://learn.microsoft.com/en-us/azure/vpn-gateway/vpn-gateway-diagnostic-log-query)
- [Troubleshoot Azure VPN Gateway using diagnostic logs | Microsoft Learn](https://learn.microsoft.com/en-us/azure/vpn-gateway/troubleshoot-vpn-with-azure-diagnostics)
- [Azure VPN Gateway — VPN Gateway Diagnostic Logs](./05-azure-vpn-gateway.md#vpn-gateway-diagnostic-logs)

---

## Related documentation

- [Azure VPN Gateway overview](./azure-vpn-gateway.md)
- [VPN vs Private Link Guide](./06-vpn-private-link-guide.md)
- [Azure Networking Scenarios](./23-networking-scenarios.md)

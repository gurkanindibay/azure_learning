# Practice Questions: Azure VPN Gateway

> **Certification Domain**: Design, implement, and manage connectivity services (20–25%)
> **Certification**: Microsoft Certified: Azure Network Engineer Associate (AZ-700)
> **General Pattern**: [VPN Gateway](./azure-vpn-gateway.md)
> **Taxonomy**: [§5 Cloud & Infrastructure / Platform Architecture](../../../architecture-general/10-practicality-taxonomy/architecture_taxonomy_reference.md)

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
- [Azure VPN Gateway - P2S VPN](./azure-vpn-gateway.md#42-point-to-site-p2s-vpn)

---

## Related documentation

- [Azure VPN Gateway overview](./azure-vpn-gateway.md)
- [VPN vs Private Link Guide](../guides/04-vpn-private-link-guide.md)
- [Azure Networking Scenarios](../guides/07-scenarios.md)

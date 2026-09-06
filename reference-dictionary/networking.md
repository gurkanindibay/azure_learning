---
type: Reference
title: "Networking"
description: "**Hub-and-Spoke** — a network topology where a central hub VNet hosts shared services and spoke VNets host workloads."
generated: { by: process:okf-migrate, at: 2026-07-04T00:00:00Z }
---

# Networking

> **Domain**: Network topology, traffic management, edge delivery, service mesh, load balancing, API gateway patterns, TCP/IP protocols, and network failure modes.
> **Parent**: [Reference Dictionary](index.md)

## Contents

| Term | Anchor |
|:---|:---|
| Anycast | [`#anycast`](#anycast) |
| BGP | [`#bgp`](#bgp) |
| PoP | [`#pop`](#pop) |
| Hub-and-Spoke | [`#hub-and-spoke`](#hub-and-spoke) |
| DMZ | [`#dmz`](#dmz) |
| CDN | [`#cdn`](#cdn) |
| Service Mesh | [`#service-mesh`](#service-mesh) |
| Smart Client | [`#smart-client`](#smart-client) |
| Load Balancer | [`#load-balancer`](#load-balancer) |
| Locality-Aware Routing | [`#locality-aware-routing`](#locality-aware-routing) |
| API Gateway | [`#api-gateway`](#api-gateway) |
| Consistent Hashing | [`#consistent-hashing`](#consistent-hashing) |
| Nagle's Algorithm / TCP_NODELAY | [`#nagles-algorithm-tcpnodelay`](#nagles-algorithm-tcpnodelay) |
| Zero-Copy Transfer | [`#zero-copy-transfer`](#zero-copy-transfer) |
| Network Partition | [`#network-partition`](#network-partition) |
| QUIC | [`#quic`](#quic) |
| HTTP/3 | [`#http3`](#http3) |
| Head-of-Line (HoL) Blocking | [`#head-of-line-hol-blocking`](#head-of-line-hol-blocking) |
| 0-RTT Connection Establishment | [`#0-rtt-connection-establishment`](#0-rtt-connection-establishment) |
| DNS Hierarchical Resolution | [`#dns-hierarchical-resolution`](#dns-hierarchical-resolution) |
| SMTP (Simple Mail Transfer Protocol) | [`#smtp-simple-mail-transfer-protocol`](#smtp-simple-mail-transfer-protocol) |
| IMAP (Internet Message Access Protocol) | [`#imap-internet-message-access-protocol`](#imap-internet-message-access-protocol) |
| POP3 (Post Office Protocol 3) | [`#pop3-post-office-protocol-3`](#pop3-post-office-protocol-3) |
| SPF (Sender Policy Framework) | [`#spf-sender-policy-framework`](#spf-sender-policy-framework) |
| DKIM (DomainKeys Identified Mail) | [`#dkim-domainkeys-identified-mail`](#dkim-domainkeys-identified-mail) |
| DMARC | [`#dmarc`](#dmarc) |
| Robots Exclusion Protocol | [`#robots-exclusion-protocol`](#robots-exclusion-protocol) |
| Politeness Policy | [`#politeness-policy`](#politeness-policy) |

---

## Anycast

A **network routing technique** where the same IP address is announced from multiple physical locations (edge points of presence, or PoPs). [Border Gateway Protocol (BGP)](#bgp) directs each user's traffic to the nearest/topologically closest announcement point, typically measured by AS-hop count or latency.

```text
Same anycast IP (203.0.113.10)
announced from multiple PoPs

        User in Sydney
              |
              v
   +----------------------+
   |  Edge PoP: Sydney    |
   |  AS-Path: short      |
   +----------------------+
              |
              |   User in Berlin
              |         |
              |         v
              |  +----------------------+
              |  |  Edge PoP: Amsterdam |
              |  |  AS-Path: short      |
              |  +----------------------+
              |         |
              v         v
        +--------------------+
        |  Origin backends   |
        +--------------------+
```

BGP routers on the internet pick the closest advertised path for that single IP, so the Sydney user lands in Sydney and the Berlin user lands in Amsterdam.

### Key Characteristics
- **Single IP, many locations**: One address is advertised from a distributed set of edge nodes.
- **BGP-driven routing**: Internet routers choose the closest announced path; no DNS or application-layer decision is required.
- **Automatic failover**: If a PoP withdraws its route, traffic shifts to the next-nearest healthy location using the same destination IP.
- **Edge termination**: The first TCP/SSL handshake happens close to the user, reducing round-trip latency and hiding the origin infrastructure.

### When to Use
- Global HTTP/HTTPS services where users must reach a low-latency entry point from anywhere in the world
- DDoS protection: attacks are absorbed at the distributed edge before reaching origin capacity
- Simplifying client configuration by offering one hostname/IP instead of region-specific endpoints

### When NOT to Use
- Private datacenter-only deployments where you cannot announce IPs from global locations (an anycast IP requires a distributed edge or CDN)
- Stateful TCP workloads that break when the same connection is rerouted to a different backend mid-session (use sticky sessions or application-layer affinity instead)
- Scenarios requiring deterministic routing to a specific region regardless of user location

**Also see**: [Azure Front Door](azure-services.md#azure-front-door) · [CDN](#cdn) · [Load Balancer](#load-balancer) · [BGP](#bgp)

---

## BGP

The **Border Gateway Protocol** is the routing protocol that powers the global internet. It exchanges reachability information between autonomous systems (AS) and allows each AS to choose the best path to a destination IP prefix based on policies, path attributes, and topology rather than simple hop count.

```text
BGP speakers exchange routes over TCP/179

       +-------------+                    +-------------+
       |   AS 64500  |<------------------>|   AS 64501  |
       |  Your Corp  |    advertise       |   ISP A     |
       |             |   203.0.113.0/24   |             |
       +-------------+                    +-------------+
              ^                                ^
              |                                |
       +-------------+                  +-------------+
       |   AS 64502  |<---------------->|   AS 64503  |
       |   ISP B     |   peer link      |   ISP C     |
       +-------------+                  +-------------+

Each AS picks the best path using attributes:
- Local Preference (internal policy)
- AS-Path length
- MED (suggested preference to neighbors)
- Next-hop reachability
```

### Key Characteristics
- **Path-vector protocol**: BGP routers advertise full AS-path information, so each router can avoid routing loops and apply policy preferences.
- **Policy-driven routing**: Network operators can prefer or reject paths based on AS path length, local preference, MED, community tags, and business relationships (transit vs peer vs customer).
- **Incremental updates**: Once a BGP session is established, only changed routes are advertised, not the full table.
- **Internet scale**: The public internet is composed of tens of thousands of autonomous systems connected via BGP; without it, there is no global end-to-end routing.
- **TCP-based**: BGP sessions run over TCP port 179, making them reliable and ordered.

### Common BGP Use Cases in Cloud/Hybrid Architectures
- **Internet-facing services**: Cloud providers announce anycast or regional IPs to the internet via BGP so users reach the closest PoP.
- **ExpressRoute**: Microsoft peers with your on-premises network provider using BGP to exchange routes between your network and Azure VNets.
- **VPN Gateway**: BGP can be enabled on Azure VPN Gateway to exchange routes dynamically over an IPsec tunnel instead of defining static routes.
- **Traffic engineering**: Route selection can influence which path inbound or outbound traffic takes, balancing cost and latency.

### When to Use
- Connecting an enterprise network to the public internet or to another organization's network
- Dynamic route exchange between on-premises and cloud networks (ExpressRoute, VPN with BGP)
- Multihoming to multiple ISPs for resilience and traffic engineering
- Building anycast or global load-balanced services that rely on distributed route announcements

### When NOT to Use
- Inside a single data center or small network where an IGP (OSPF, IS-IS, EIGRP) is simpler and converges faster
- When you need sub-second failover — BGP convergence is typically measured in seconds, not milliseconds
- For pure application-layer routing decisions (use a load balancer, API gateway, or service mesh instead)

**Also see**: [Anycast](#anycast) · [Azure ExpressRoute](../architecture-azure/networking/07-expressroute-bgp-guide.md) · [Azure VPN Gateway](../architecture-azure/networking/05-azure-vpn-gateway.md) · [Network Partition](#network-partition)

---

## PoP

A **Point of Presence (PoP)** is both a physical site and an architectural concept used to describe where a provider's network meets end users.

- **Physical meaning**: a real facility — a datacenter, colocation room, or edge location — containing routers, caches, load balancers, compute, and optical gear. For example, a Cloudflare edge datacenter in Frankfurt or an Azure Front Door location in Singapore.
- **Architectural / logical meaning**: an abstract edge node in diagrams and requirements. When architects say "traffic enters through the nearest PoP," they mean the closest logical termination point, regardless of which specific physical rack handles the request.

PoPs are operated by CDNs, DNS providers, global load balancers, and cloud edge services so that requests do not have to travel all the way back to a central origin datacenter.

```text
User in Tokyo          User in São Paulo
       |                       |
       v                       v
+-------------+           +-------------+
|  CDN PoP    |           |  CDN PoP    |
|   Tokyo     |           |   São Paulo |
+-------------+           +-------------+
       |                       |
       | cache miss            | cache hit
       |                       |
       +----------+   +--------+------------+
                  |   |
                  v   v
            +-----------------+
            |  Origin / Core  |
            |   Datacenter    |
            +-----------------+
```

A Tokyo user hits the Tokyo PoP. If the content is cached, it is served locally; otherwise the PoP fetches from the origin and caches it. A São Paulo user on a later request may get the same content entirely from the local PoP.

### Key Characteristics
- **Edge location**: Usually deployed in major metro areas or inside ISP networks to minimize last-mile latency.
- **Multi-function**: Can terminate TLS, cache content, run edge compute, apply WAF rules, or act as a BGP anycast router.
- **Shared across services**: A provider like Cloudflare or Azure Front Door reuses the same global PoP footprint for DNS, CDN, WAF, and load balancing.
- **Independent failover**: If one PoP becomes unreachable, routes or DNS can shift traffic to the next nearest PoP.

### When to Use
- Global services where latency to a single origin region is unacceptable
- Caching static assets close to users
- Absorbing DDoS and malicious traffic before it reaches origin capacity
- Running lightweight edge logic (validation, redirects, A/B tests) near the user

### When NOT to Use
- Applications with all users in one region (a single origin is simpler and cheaper)
- Stateful workloads that require all requests from a user to land in the same backend (PoPs distribute users; combine with session affinity or central state if needed)
- Scenarios where data-residency rules prohibit storing or processing data outside specific geographies

**Also see**: [Anycast](#anycast) · [CDN](#cdn) · [Azure Front Door](azure-services.md#azure-front-door)

---

## Hub-and-Spoke

A **network topology** where a central hub VNet hosts shared services (firewall, gateway, DNS) and spoke VNets host workloads. All spoke-to-spoke traffic routes through the hub for inspection and control.

**Also see**: [Azure Services: VNet](azure-services.md#vnet)

---

## DMZ

**Demilitarized Zone** — an isolated network segment between the untrusted internet and the trusted internal network. It hosts internet-facing services that must be reachable from outside, while preventing direct access to internal systems.

```text
Untrusted Internet
         |
         v
+-------------------+
|  External firewall|
|  (allow 80/443)   |
+-------------------+
         |
         v
+-------------------+        +-------------------+
|      DMZ          |        |   Internal        |
|  - Reverse proxy  |        |   network         |
|  - Public web API |        |  - App servers    |
|  - Bastion host   |        |  - Databases      |
|  - WAF edge       |        |  - Internal APIs  |
+-------------------+        +-------------------+
         |                            ^
         |                            |
         +----------+-----------------+
                    |
          +-------------------+
          |  Internal firewall|
          | (deny direct DMZ  |
          |  to DB; allow     |
          |  proxy → app)     |
          +-------------------+
```

The DMZ acts as a buffer. Public services live there, but the crown jewels (databases, internal APIs, sensitive data) remain behind a second firewall in the internal network. If a DMZ host is compromised, the attacker still does not have direct access to the internal network.

### Key Characteristics
- **Two security boundaries**: traffic must cross an external firewall to enter the DMZ, and an internal firewall to reach the trusted network.
- **Minimal privileges**: DMZ hosts run only the services required to face the internet; administrative access and sensitive data are kept internal.
- **Bastion/ jump host**: administrative access to internal systems often goes through a hardened host in the DMZ, not directly from the internet.
- **Not just on-premises**: the same concept applies in the cloud using public subnets, private subnets, NAT gateways, firewalls, and application gateways.

### Common Scenarios

| Scenario | DMZ role |
|---|---|
| **Public e-commerce site** | Web servers and reverse proxies sit in the DMZ; payment processing and order databases stay internal. |
| **Corporate VPN / RDP gateway** | The VPN concentrator or Remote Desktop Gateway is in the DMZ; internal file servers and domain controllers are not exposed. |
| **API gateway for partners** | The externally reachable API gateway lives in the DMZ; backend microservices and data stores remain behind the internal firewall. |
| **Email / DNS relay** | MX and DNS servers are placed in the DMZ to receive external mail and queries, while internal mail stores stay protected. |
| **Cloud hub-spoke with Azure Firewall** | Public-facing application gateway and Azure Firewall are in a hub DMZ-like subnet; spoke VNets containing workloads are private. |

### When to Use
- You have services that must be reachable from the internet
- You want to contain the blast radius if a public-facing host is compromised
- Compliance requires separation between public and private networks
- You need controlled entry points (reverse proxy, VPN gateway, bastion) into the internal network

### When NOT to Use
- All workloads are internal-only SaaS or intranet apps with no public entry points
- A single flat network is acceptable for the threat model (rare in production)
- You replace the DMZ with "public subnet + private subnet" cloud constructs but forget to enforce firewall rules between them

**Also see**: [Azure Services: Azure Firewall](azure-services.md#azure-firewall) · [Hub-and-Spoke](#hub-and-spoke) · [API Gateway](#api-gateway) · [Reverse Proxy](#reverse-proxy)

---

## CDN

A **Content Delivery Network** — a geographically distributed network of edge servers that cache static and dynamic content close to end users, reducing latency and offloading origin infrastructure.

### Key Characteristics
- **Edge caching**: Content replicated to points of presence (PoPs) worldwide; users fetch from the nearest edge
- **Origin offload**: 90%+ of requests served from edge cache, never reaching origin servers
- **DDoS absorption**: Distributed edge footprint absorbs volumetric attacks before they reach origin
- **Modern capabilities**: Edge compute (Cloudflare Workers, AWS Lambda@Edge), image optimization, A/B testing, SSL termination

### When to Use
- Global user base where latency to a single origin region is unacceptable
- Static assets (images, CSS, JS, videos) that benefit from caching at the edge
- DDoS protection at the network edge before traffic reaches application infrastructure

### When NOT to Use
- Intranet applications with all users in one geographic region
- Highly dynamic, personalized content that cannot be cached (though edge compute can help)
- When TLS private keys must never leave your infrastructure (some CDNs require key sharing)

**Also see**: [Caching](caching.md) · [Azure Front Door](azure-services.md#azure-front-door)

---

## Service Mesh

A **dedicated infrastructure layer** that handles service-to-service communication transparently, outside application code. Deployed as sidecar proxies alongside each service, providing observability, traffic management, and security without application changes.

### Key Characteristics
- **Sidecar proxy**: Each service instance gets a co-located proxy (Envoy, Linkerd-proxy) that intercepts all network traffic
- **Control plane + data plane**: Control plane (Istiod, Linkerd control plane) configures the data plane proxies
- **mTLS**: Automatic mutual TLS between services — encryption and identity without application code
- **Traffic management**: Retries, timeouts, circuit breaking, traffic splitting (canary), fault injection
- **Observability**: Automatic metrics (request rate, latency, error rate), distributed tracing, access logs

### When to Use
- Large microservice deployments (50+ services) where consistent observability and security are required
- Organizations with a dedicated platform team that can operate the mesh
- Compliance requirements mandating encryption-in-transit for all service-to-service traffic

### When NOT to Use
- Small deployments (under 10 services) — the operational overhead exceeds the benefit
- Teams without platform engineering capacity to operate the control plane
- When the extra latency hop per request (typically <1ms with Envoy) is unacceptable
- Monoliths or services communicating over message queues rather than synchronous HTTP/gRPC

**Also see**: [Sidecar Pattern](#sidecar-pattern) · [Microservices](#microservices) · [Circuit Breaker](resilience.md#circuit-breaker) · [Istio / Linkerd](https://istio.io/latest/about/service-mesh/)

---

## Load Balancer

A **traffic distribution component** that sits between clients and backend servers, distributing incoming requests across multiple server instances to maximize throughput, minimize response time, and avoid overloading any single resource.

### Key Characteristics
- **L4 (Transport Layer)**: Operates on TCP/UDP — fast, no payload inspection, distributes by IP:port
- **L7 (Application Layer)**: Operates on HTTP/HTTPS — can route by URL path, headers, cookies; supports TLS termination
- **Health checks**: Continuously verifies backend health; removes unhealthy instances from the pool
- **Algorithms**: Round-robin, least connections, IP hash, weighted, least response time
- **Consistent hashing**: Minimizes rebalancing when servers are added/removed — critical for stateful backends and caching

### When to Use
- Any multi-instance service behind a single endpoint
- SSL termination at the edge before traffic reaches application servers
- Gradual traffic shifting during deployments (canary, blue-green)

### When NOT to Use
- Single-instance deployments (the load balancer itself becomes a single point of failure without HA pairs)
- Peer-to-peer architectures where clients connect directly to any node
- When request affinity (sticky sessions) is required but the balancer doesn't support it

### Also see
- [API Gateway](networking.md#api-gateway) · [Reverse Proxy](#reverse-proxy) · [Consistent Hashing](networking.md#consistent-hashing) · [Azure Load Balancer / Application Gateway](azure-services.md)

---

## API Gateway

An infrastructure component that sits between clients and backend services, providing cross-cutting concerns such as **authentication, rate limiting, request routing, SSL termination, and protocol translation**.

### Key Characteristics

- Single entry point for external clients
- Centralizes auth validation, logging, and monitoring
- Hides internal service topology
- Often paired with load balancers and WAFs

### When to Use

- Multiple client types (mobile, web, third-party) access the same backend
- Need centralized authentication, rate limiting, or routing

### When NOT to Use

- As a single point of failure without redundancy
- For internal service-to-service communication (prefer service mesh or direct mTLS)

### Also see

- [Rate Limiting](api-design.md#rate-limiting)
- [Reverse Proxy, LB & API Gateway](../system-design-architecture/16-reverse-proxy-lb-api-gateway.md)

---

## Consistent Hashing

A distributed hashing technique that minimizes key redistribution when nodes are added or removed. Used for request affinity, distributed caching, and partition assignment.

| Property | Detail |
|:---|:---|
| **Ring structure** | Hash space organized as a circle |
| **Node addition** | Only ~1/N keys remapped |
| **Virtual nodes** | Multiple points per physical node for even distribution |

**Also see**: [Caching](caching.md) · [Messaging: Partition](messaging.md#partition)

---

## Nagle's Algorithm / TCP_NODELAY

**Nagle's Algorithm** — a TCP optimization (RFC 896) that buffers small outgoing packets to coalesce them into larger segments before transmission. Disabled by setting the socket option `TCP_NODELAY=true`.

### Key Characteristics
- **Enabled by default** (`TCP_NODELAY=false`) on most platforms, including JVM sockets
- Waits for ACK of previous packet OR until buffer fills to MSS (Maximum Segment Size) before sending
- Reduces TCP header overhead for workloads that produce many small writes (e.g., telnet, character-by-character)
- **Go's `net/http` disables Nagle by default** since Go 1.7 for HTTP servers
- The interaction with HTTP/1.1 persistent connections and multi-write responses can add 40+ ms of artificial latency

### When to Use (TCP_NODELAY=true)
- HTTP services writing complete responses (headers + body) — the response is one logical unit; buffering adds latency
- Latency-sensitive APIs where 40 ms is unacceptable
- Services using persistent HTTP/1.1 connections with multi-write response patterns

### When NOT to Use (TCP_NODELAY=false, Nagle enabled)
- Workloads that produce many tiny writes where TCP header overhead dominates (rare for HTTP services)
- Interactive terminal protocols (telnet, SSH) where the original optimization was designed

### Also see
- [Virtual Threads](java-jvm.md#virtual-threads) — concurrency model that interacts with socket I/O
- [Application Gateway](azure-services.md#application-gateway) — L7 proxy that terminates TCP connections

---

## Zero-Copy Transfer

An OS-level optimization that transfers data directly from **disk cache to the network socket** without copying it through application memory. In Kafka, the `sendfile()` system call eliminates CPU copies and context switches between kernel and user space, dramatically reducing CPU usage during high-throughput data serving.

### Key Characteristics
- Data path: disk → page cache → network socket (no application buffer involved)
- Eliminates redundant CPU copies and kernel/user context switches
- Available when data is served directly from the OS page cache (not from application-managed buffers)
- Used by Kafka for consumer fetch requests; also employed by Nginx and other high-performance servers

### When to Use
- High-throughput streaming systems where CPU is the bottleneck for data serving
- When consumers read data that is already in the OS page cache (recently produced or frequently read)

### When NOT to Use
- When messages require application-level transformation or encryption before sending
- When data is not in the page cache (misses still require disk reads into application memory first)

### Also see
- [Distributed Commit Log](messaging.md#distributed-commit-log) · [Message Batching](messaging.md#message-batching) · [Partition](messaging.md#partition)

---

## Network Partition

A **network partition** occurs when some nodes in a distributed system cannot communicate with others due to a network failure — messages are dropped, delayed, or entirely blocked between subsets of nodes. The system is split into two or more isolated groups that cannot coordinate.

```
Normal operation:                    Network partition:
┌───┐  ┌───┐  ┌───┐                 ┌───┐     ┌───┐  ┌───┐
│ A │──│ B │──│ C │                 │ A │  ✗  │ B │──│ C │
└───┘  └───┘  └───┘                 └───┘     └───┘  └───┘
  All nodes can talk                  A is isolated from B and C
```

### Key Characteristics
- **Inevitable**: In any distributed system, network partitions *will* happen — cables fail, switches reboot, DNS misbehaves, cloud regions become unreachable
- **CAP's hidden constant**: The P in CAP is not optional — you cannot choose to avoid partitions; you can only choose how the system behaves *during* one
- **Split-brain risk**: Each partition may believe it is the sole survivor and attempt to act independently — two partitions accepting writes creates irreconcilable divergence
- **Detection is fuzzy**: Nodes cannot reliably distinguish "the other node is dead" from "the network between us is dead" — this is why timeouts are always a tradeoff (too short = false positives; too long = real failures go undetected)

### What Happens During a Partition

| Architecture | Behavior During Partition | Example |
|:---|:---|:---|
| **Single-primary (CP)** | The partitioned side without the primary **rejects writes** — system prioritizes consistency over availability | MongoDB, PostgreSQL with synchronous replication |
| **Masterless (AP)** | Both sides **continue accepting writes** — system prioritizes availability over consistency; conflicts resolved later | Cassandra, DynamoDB (eventual consistency mode) |
| **Multi-primary with conflict resolution** | Both sides accept writes; conflicts detected and resolved on reconciliation | CouchDB, CRDT-based systems |

### When to Use
- Designing distributed systems — always assume partitions will occur and plan the failure mode explicitly
- Evaluating database tradeoffs — "what happens during a network partition?" is the most revealing question you can ask about a distributed database
- Planning multi-region deployments — cross-region links partition far more often than intra-region ones

### When NOT to Use
- Single-node systems — a network partition is meaningless when there's only one node (though it's still a single point of failure)
- As an excuse to avoid distribution — partitions are inevitable, not a reason to stay on a single machine forever

### Also see
- [CAP Theorem](data-architecture.md#cap-theorem) · [Masterless Architecture](databases.md#masterless-architecture) · [Eventual Consistency](cqrs-event-driven.md#eventual-consistency) · [Replication](data-architecture.md#replication)

---

## Locality-Aware Routing

A **request routing strategy** that directs traffic to the nearest healthy backend instance based on physical or network proximity (same pod → same node → same zone → same region → global). Minimizes network latency and cross-zone bandwidth by preferring local instances before falling back to remote ones.

### Key Characteristics
- **Tiered fallback**: Each locality tier is tried in order; if no healthy instance exists at one level, the algorithm proceeds to the next
- **Load-aware within tiers**: Among instances at the same locality, selection favors the least loaded (lowest outstanding requests, lowest queue depth, or lowest response time)
- **Topology key alignment**: Locality tiers map to Kubernetes topology keys — `kubernetes.io/hostname` (node), `topology.kubernetes.io/zone` (AZ), `topology.kubernetes.io/region`
- **Implemented via service mesh or smart client**: Istio Locality Load Balancing, Linkerd, or custom client-side discovery

### When to Use
- Communication-intensive microservices where east-west traffic dominates (gRPC, REST, caching, database proxies)
- Multi-zone clusters where cross-zone traffic incurs latency and cost penalties
- AI inference pipelines where same-node GPU-to-GPU latency matters

### When NOT to Use
- Single-zone deployments where all instances are effectively at the same locality tier
- Fan-out patterns where the client must reach all instances regardless of location
- When uneven load distribution causes hotspots — locality can concentrate traffic on a few local instances

### Also see
- [Service Mesh](#service-mesh) · [Load Balancer](#load-balancer) · [Smart Client](#smart-client) · [Pod Affinity](deployment-patterns.md#pod-affinity) · [Graceful Degradation](resilience.md#graceful-degradation)

---

## Smart Client

A **client-side service discovery and load balancing pattern** where the client maintains its own endpoint registry, groups backends by locality, and selects the optimal instance using custom logic (locality preference + load metrics) rather than relying solely on server-side load balancing.

### Key Characteristics
- **Client-owned endpoint discovery**: The client queries the service registry (DNS, Kubernetes API, Consul) and maintains its own backend list
- **Locality grouping**: Endpoints sorted into tiers — same node, same zone, same region — before applying load-based selection
- **Custom selection logic**: Beyond round-robin or least-connections — combines locality preference with queue depth, outstanding requests, or response latency
- **Tradeoff**: More client complexity in exchange for finer-grained routing control and elimination of the extra hop through a server-side load balancer

### When to Use
- gRPC clients that already use client-side load balancing via the gRPC resolver/balancer API
- Services where eliminating the load balancer hop measurably improves tail latency
- Environments where the client has richer health/load signals than a centralized load balancer can access

### When NOT to Use
- Simple HTTP services where Kubernetes Service + kube-proxy is sufficient
- When the client language or framework lacks mature service discovery libraries
- When centralized traffic management (TLS termination, rate limiting, auth) is needed at the edge

### Also see
- [Locality-Aware Routing](#locality-aware-routing) · [Service Mesh](#service-mesh) · [Load Balancer](#load-balancer) · [Pod Affinity](deployment-patterns.md#pod-affinity)

---

## QUIC

A **multiplexed, secure transport layer network protocol** developed by Google and standardized by the IETF (RFC 9000). QUIC runs over UDP rather than TCP, integrating TLS 1.3 encryption directly into the transport handshake to achieve reduced connection latency, seamless connection migration across network handoffs, and true independent stream multiplexing without TCP Head-of-Line blocking.

### Key Characteristics
- **UDP-based transport**: Operates in user-space over UDP port 443, enabling rapid protocol evolution without OS kernel upgrades
- **Encrypted by default**: Embeds TLS 1.3 cryptographic handshake directly into transport setup (1-RTT or 0-RTT initial connection)
- **Elimination of transport Head-of-Line blocking**: Independent byte streams; lost packets on Stream A stall only Stream A, while Streams B and C continue delivery unimpeded
- **Connection Migration**: Uses 64-bit Connection IDs (CIDs) rather than the 4-tuple (IP:Port), allowing seamless uninterrupted connections when a mobile device switches from Wi-Fi to cellular LTE/5G

### When to Use
- Modern web and mobile applications operating over lossy, high-latency, or mobile cellular networks
- Media streaming, video conferencing, and live cloud gaming
- Primary transport substrate for HTTP/3

### When NOT to Use
- Internal data center networks where ultra-stable fiber connections render UDP multiplexing gains negligible compared to hardware-offloaded TCP NIC acceleration
- Corporate firewalls or enterprise perimeter environments that aggressively drop or throttle non-DNS UDP traffic

### Also see
- [HTTP/3](#http3) · [Head-of-Line (HoL) Blocking](#head-of-line-hol-blocking) · [0-RTT Connection Establishment](#0-rtt-connection-establishment)

---

## HTTP/3

The **third major version of the Hypertext Transfer Protocol**, officially standardized in RFC 9114. Unlike HTTP/1.1 and HTTP/2 which run over TCP and TLS, HTTP/3 maps HTTP semantics directly onto the **QUIC** transport layer protocol.

### Key Characteristics
- **Native QUIC integration**: Replaces TCP + TLS with QUIC, inheriting 0-RTT handshakes and native UDP framing
- **QPACK Header Compression**: Upgraded from HTTP/2's HPACK to handle out-of-order header delivery without creating stream-level deadlocks
- **Unified connection establishment**: Combines transport and security handshakes into a single round-trip
- **Seamless network transitions**: Mobile clients do not disconnect or re-authenticate when changing IP addresses

### When to Use
- High-traffic public websites, APIs, and mobile backends aiming to minimize mobile user load times
- Global e-commerce and media streaming services with high proportions of mobile and roaming users
- Edge CDNs delivering static assets and dynamic API routes

### When NOT to Use
- Internal service-to-service microservice backbones where gRPC over HTTP/2 or plain TCP delivers lower CPU overhead
- Legacy server environments lacking UDP load-balancing infrastructure

### Also see
- [QUIC](#quic) · [Head-of-Line (HoL) Blocking](#head-of-line-hol-blocking) · [CDN](#cdn)

---

## Head-of-Line (HoL) Blocking

A **performance phenomenon and architectural bottleneck** where a single blocked, delayed, or lost packet or request at the front of a First-In, First-Out (FIFO) queue halts the transmission and processing of all subsequent independent items waiting behind it.

### Key Characteristics
- **HTTP/1.1 level**: Browsers could only issue one request per TCP connection at a time; slow responses blocked subsequent requests on that socket
- **HTTP/2 level**: Solved application-level blocking via multiplexed streams, but introduced **TCP-level HoL blocking** (a single lost TCP packet halts all multiplexed streams in the TCP receive buffer)
- **HTTP/3 / QUIC resolution**: Treats every stream as an independent transport sequence; dropped packets stall only the affected stream
- **Message queue analogy**: A poisonous or slow message at the head of a single partition consumer queue stalling all subsequent unrelated messages

### When to Use
- Diagnosing latency spikes and throughput plateaus in HTTP/2 streams over unstable mobile connections
- Designing message queues, streaming workers, and pipeline architectures with partitioned parallel processing

### When NOT to Use
- When strict, total sequential ordering across all entities is an absolute business requirement (e.g., single-account ledger transactions)

### Also see
- [QUIC](#quic) · [HTTP/3](#http3) · [Nagle's Algorithm / TCP_NODELAY](#nagles-algorithm-tcpnodelay)

---

## 0-RTT Connection Establishment

A **cryptographic protocol feature** (present in TLS 1.3 and QUIC) that allows a client reconnecting to a previously visited server to transmit encrypted application payload data (such as an HTTP GET request) on the very first packet of the handshake, achieving zero round-trip latency before application data transfer.

### Key Characteristics
- **Resumed session keys**: Leverages pre-shared keys (PSK) or session tickets negotiated during a previous TLS 1.3/QUIC handshake
- **Latency elimination**: Drops handshake delay from 2–3 RTTs (TLS 1.2 / TCP) and 1 RTT (TLS 1.3) down to 0 RTT for repeat visitors
- **Replay attack vulnerability**: Because the initial 0-RTT data packet cannot incorporate server-generated nonces, an attacker can intercept and replay 0-RTT packets across the network
- **Idempotency requirement**: Only strictly idempotent requests (like HTTP GET or safe queries) should ever be transmitted via 0-RTT data

### When to Use
- High-performance mobile applications and web APIs where repeat users demand instantaneous page loads
- Global edge networks connecting clients to geographically distant origin servers

### When NOT to Use
- Non-idempotent mutations (e.g., `POST /api/v1/payments`, order checkout, account withdrawals) without anti-replay protection tokens
- Unauthenticated or first-time client connections where 1-RTT is unavoidable

### Also see
- [QUIC](#quic) · [HTTP/3](#http3) · [Replay Attack](security-iam.md#replay-attack) · [Idempotency-Key](api-design.md#idempotency-key)

---

## DNS Hierarchical Resolution

The **globally distributed, tiered lookup mechanism** that translates human-readable domain names (e.g., `api.example.com`) into routable IP addresses (IPv4 `A` records, IPv6 `AAAA` records) through a multi-stage tree resolution hierarchy.

### Key Characteristics
- **Recursive Resolver**: The ISP or public resolver (e.g., 8.8.8.8, 1.1.1.1) that traverses the DNS hierarchy on behalf of the client
- **Root Nameservers**: 13 logical authoritative root server clusters (labeled A through M, deployed globally via Anycast) that direct queries to TLD servers
- **Top-Level Domain (TLD) Nameservers**: Servers managing specific domain extensions (`.com`, `.net`, `.io`) that delegate to Authoritative Nameservers
- **Authoritative Nameservers**: The final authority hosting the actual DNS record configurations for the specific registered domain
- **Hierarchical Caching & TTL**: Every response carries a Time-To-Live (TTL) integer determining how long intermediate resolvers can serve cached answers

### When to Use
- Designing global traffic routing, geo-DNS load balancing, and failover architectures
- Configuring record types: `A`/`AAAA` (host IPs), `CNAME` (canonical aliases), `MX` (mail routing), `NS` (name servers), `TXT` (domain verification, SPF/DKIM)

### When NOT to Use
- High-frequency dynamic load balancing (<5 seconds) where aggressive client/ISP DNS caching ignores low TTL values (use Anycast or L4/L7 Load Balancers instead)

### Also see
- [Anycast](#anycast) · [BGP](#bgp) · [CDN](#cdn)

---

## SMTP (Simple Mail Transfer Protocol)

The **de facto standard internet protocol** (RFC 5321) for transmitting electronic mail across IP networks. SMTP is a push-based protocol used by clients (MUAs) to submit outbound messages to Mail Submission Agents (MSAs) and by Mail Transfer Agents (MTAs) to relay messages between domains over TCP port 25 or 587.

### Key Characteristics
- **Push-only model**: Pushes messages from sender to destination; does not support pulling or mailbox synchronization
- **Text-based command protocol**: Communicates via ASCII commands (`HELO`/`EHLO`, `MAIL FROM`, `RCPT TO`, `DATA`, `QUIT`) with 3-digit numeric response codes
- **Relaying**: MTAs query destination DNS `MX` records to locate receiving mail servers and route messages across intermediary hops
- **Security extensions**: Upgraded with STARTTLS for opportunistic TLS encryption and SASL for authenticated submission

### When to Use
- Outbound transactional and marketing email delivery services (SendGrid, Mailgun, Amazon SES)
- Inter-server mail routing between public email domains (e.g., Gmail to Outlook)

### When NOT to Use
- Client mailbox reading, folder navigation, or message deletion (use IMAP or modern REST APIs like Microsoft Graph / Gmail API)
- Synchronous, high-throughput microservice event streaming

### Also see
- [IMAP (Internet Message Access Protocol)](#imap-internet-message-access-protocol) · [POP3 (Post Office Protocol 3)](#pop3-post-office-protocol-3) · [SPF (Sender Policy Framework)](#spf-sender-policy-framework)

---

## IMAP (Internet Message Access Protocol)

A **standard client-server email protocol** (RFC 9051 / RFC 3501) that allows email clients to access, organize, and manipulate messages stored remotely on a mail server while maintaining continuous state synchronization across multiple devices.

### Key Characteristics
- **Two-way server-side state**: Folders, read/unread flags, stars, and draft states are stored on the server; changes on one client synchronize to all other devices
- **On-demand header fetching**: Clients download only message headers and folder structures first, streaming heavy MIME body attachments only when explicitly opened
- **Offline caching**: Clients cache messages locally for offline viewing and sync pending changes upon reconnection
- **Port conventions**: TCP port 143 (plain/STARTTLS) and TCP port 993 (IMAPS over implicit TLS)

### When to Use
- Native desktop and mobile mail applications connecting to corporate or personal email servers
- Multi-device email access requiring synchronized inbox state and unified folders

### When NOT to Use
- Scenarios where storage is severely constrained on the mail server (POP3 or local archiving may be preferred)
- Sending outbound email (SMTP is required for delivery)

### Also see
- [SMTP (Simple Mail Transfer Protocol)](#smtp-simple-mail-transfer-protocol) · [POP3 (Post Office Protocol 3)](#pop3-post-office-protocol-3)

---

## POP3 (Post Office Protocol 3)

A **simple, legacy client-server email retrieval protocol** (RFC 1939) designed to download emails from a remote server to a single local client and delete them from the server once retrieved.

### Key Characteristics
- **Download-and-delete model**: By default, downloads new messages to local disk storage and purges server copies
- **One-way synchronization**: Folders created on the client do not exist on the server; read status does not replicate to other devices
- **Minimal server resource usage**: Reduces mail server storage footprint since messages reside locally on the user's computer
- **Port conventions**: TCP port 110 (plain/STARTTLS) and TCP port 995 (POP3S over implicit TLS)

### When to Use
- Low-bandwidth or resource-constrained environments where mail servers have minimal disk quotas
- Single-device legacy clients with dedicated local archiving requirements

### When NOT to Use
- Modern multi-device setups (smartphone, laptop, web browser) where synchronized read/sent status across devices is mandatory
- Shared mailbox or collaborative team workflows

### Also see
- [IMAP (Internet Message Access Protocol)](#imap-internet-message-access-protocol) · [SMTP (Simple Mail Transfer Protocol)](#smtp-simple-mail-transfer-protocol)

---

## SPF (Sender Policy Framework)

An **email authentication standard** (RFC 7208) that enables domain owners to publish a list of authorized IP addresses and mail servers permitted to send email on behalf of their domain using a special DNS `TXT` record.

### Key Characteristics
- **DNS TXT record structure**: e.g., `v=spf1 ip4:198.51.100.0/24 include:_spf.google.com ~all`
- **Envelope sender validation**: Receiving MTAs check the IP address of the connecting mail server against the domain found in the `Return-Path` (envelope `MAIL FROM`), not the visible header `From:`
- **Mechanisms and Qualifiers**: `+` (Pass), `-` (Fail / HardFail), `~` (SoftFail), `?` (Neutral)
- **10-lookup limit**: SPF checks must not exceed 10 recursive DNS lookups to protect resolvers from denial-of-service loops

### When to Use
- Mandatory configuration for all outgoing email domains to prevent domain spoofing and preserve inbox deliverability
- Defending against phishing and forged email headers claiming to originate from your organization

### When NOT to Use
- As a standalone defense: SPF breaks when emails are forwarded by third-party intermediaries (e.g., mailing lists); must be paired with DKIM and DMARC

### Also see
- [DKIM (DomainKeys Identified Mail)](#dkim-domainkeys-identified-mail) · [DMARC](#dmarc) · [SMTP (Simple Mail Transfer Protocol)](#smtp-simple-mail-transfer-protocol)

---

## DKIM (DomainKeys Identified Mail)

An **email authentication method** (RFC 6376) that uses public key cryptography to attach a digital signature to email messages, allowing the receiving mail server to verify that the email was sent by the domain owner and was not altered in transit.

### Key Characteristics
- **Cryptographic signature in headers**: Emits a `DKIM-Signature` header containing hashes of selected headers and message body
- **DNS public key publication**: Domain owners publish their public key in DNS under a selector subdomain (e.g., `selector1._domainkey.example.com`)
- **Forwarding resilient**: Unlike SPF, DKIM signatures survive email forwarding as long as the message body and signed headers are not modified
- **Tamper evidence**: Any modification to signed subject lines, recipient fields, or message contents invalidates the cryptographic signature

### When to Use
- All outbound transactional, marketing, and corporate email systems
- Ensuring message integrity and authenticating the sender domain cryptographically

### When NOT to Use
- Without SPF and DMARC: DKIM signs the domain in the signature header, but does not strictly enforce that the signature domain matches the user-visible `From:` address without DMARC Alignment

### Also see
- [SPF (Sender Policy Framework)](#spf-sender-policy-framework) · [DMARC](#dmarc) · [SMTP (Simple Mail Transfer Protocol)](#smtp-simple-mail-transfer-protocol)

---

## DMARC

**Domain-based Message Authentication, Reporting, and Conformance** (RFC 7489): an email security protocol that builds upon SPF and DKIM to provide domain owners with policy control and visibility over how unauthorized emails using their domain are handled by receiving mail providers.

### Key Characteristics
- **Identifier Alignment**: Requires that the domain in the visible `From:` header matches the authenticated SPF domain or the DKIM signing domain
- **Enforcement Policies (`p=`)**:
  - `p=none`: Monitor mode; generate failure reports without impacting delivery
  - `p=quarantine`: Direct failing messages to the recipient's spam/junk folder
  - `p=reject`: Block failing messages outright at the receiving MTA
- **Feedback & Reporting**: Receiving servers send aggregated XML reports (`rua`) and forensic failure alerts (`ruf`) to the domain owner detailing authentication passes and fails

### When to Use
- Complete enterprise protection against domain impersonation, CEO fraud, and phishing
- Meeting modern sender deliverability requirements enforced by major providers (Google, Yahoo, Microsoft)

### When NOT to Use
- Jumping directly to `p=reject` on day one without first monitoring via `p=none` to discover legitimate third-party senders (SaaS apps, CRM, ticketing tools)

### Also see
- [SPF (Sender Policy Framework)](#spf-sender-policy-framework) · [DKIM (DomainKeys Identified Mail)](#dkim-domainkeys-identified-mail) · [SMTP (Simple Mail Transfer Protocol)](#smtp-simple-mail-transfer-protocol)

---

## Robots Exclusion Protocol

A standard (formalized in RFC 9309) used by websites to instruct web crawlers and automated bots which URLs or path directories they are permitted or forbidden to access via a plaintext file hosted at `/robots.txt`.

### Key Characteristics
- **Standardized Directives**: Includes `User-agent` (target crawler identifier), `Disallow` (blocked URI prefixes), `Allow` (explicitly allowed subpaths), and `Sitemap` (location of XML sitemaps)
- **Voluntary Compliance**: Client-side enforcement mechanism; ethical crawlers (Googlebot, Bingbot) strictly parse and obey rules, but malicious scrapers can ignore them
- **Caching & Freshness**: Crawlers cache `robots.txt` files (typically for 24 hours) to avoid hammering the host server on every single page fetch

### When to Use
- Managing search engine indexing to prevent crawling of private admin consoles, internal APIs, or staging environments
- Reducing crawler server load by excluding high-volume faceted search combinations or duplicate content URLs

### When NOT to Use
- Enforcing confidential access security or authorization (sensitive endpoints require real authentication, IAM, and firewalls — `robots.txt` is publicly visible)

### Also see
- [Politeness Policy](#politeness-policy) · [API Gateway](#api-gateway)

---

## Politeness Policy

A **rate-limiting and scheduling architecture pattern implemented by web crawlers** to avoid overwhelming target web servers with excessive concurrent HTTP requests, preventing accidental Denial of Service (DoS) conditions during indexing.

### Key Characteristics
- **Per-Host Concurrency Limits**: Restricts the crawler to executing at most $N$ concurrent connections (often 1 or 2) against the same fully qualified domain name (FQDN)
- **Inter-Request Delay**: Enforces a minimum delay interval (e.g., 500ms–2000ms, or respecting `Crawl-delay` directives) between consecutive requests to the same origin server
- **Queue Partitioning**: Implements crawler URL Frontier architecture with separate FIFO queues per target host, managed by a Politeness Delay scheduler

### When to Use
- Distributed web scraping and search indexing pipelines (Apache Nutch, Scrapy)
- Data ingestion pipelines fetching external APIs or third-party RSS feeds without explicit rate-limit headers

### When NOT to Use
- Internal microservice-to-microservice RPC calls within high-bandwidth private VPC networks (use Service Meshes, Bulkheads, and Load Balancers)

### Also see
- [Robots Exclusion Protocol](#robots-exclusion-protocol) · [Backpressure](resilience.md#backpressure) · [Rate Limiting](api-design.md#rate-limiting)



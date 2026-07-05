---
type: Reference
title: "Networking"
description: "**Hub-and-Spoke** — a network topology where a central hub VNet hosts shared services and spoke VNets host workloads."
timestamp: 2026-07-04T00:00:00Z
---

# Networking

> **Domain**: Network topology, traffic management, edge delivery, service mesh, load balancing, API gateway patterns, TCP/IP protocols, and network failure modes.
> **Parent**: [Reference Dictionary](index.md)

## Contents

| Term | Anchor |
|:---|:---|
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
## Hub-and-Spoke

A **network topology** where a central hub VNet hosts shared services (firewall, gateway, DNS) and spoke VNets host workloads. All spoke-to-spoke traffic routes through the hub for inspection and control.

**Also see**: [Azure Services: VNet](azure-services.md#vnet)

---

## DMZ

**Demilitarized Zone** — an isolated network segment between the untrusted internet and trusted internal network. Hosts internet-facing services that should not have direct access to internal systems.

**Also see**: [Azure Services: Azure Firewall](azure-services.md#azure-firewall)

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
- [Service Mesh](#service-mesh) · [Load Balancer](#load-balancer) · [Smart Client](#smart-client) · [Pod Affinity](architecture-patterns.md#pod-affinity) · [Graceful Degradation](resilience.md#graceful-degradation)

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
- [Locality-Aware Routing](#locality-aware-routing) · [Service Mesh](#service-mesh) · [Load Balancer](#load-balancer) · [Pod Affinity](architecture-patterns.md#pod-affinity)


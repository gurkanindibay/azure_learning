# Choose the Right Consistency Level

**Completed**  
**100 XP**  
**3 minutes**

Each of the consistency models can be used for specific real-world scenarios. Each provides precise availability and performance tradeoffs backed by comprehensive SLAs. The following simple considerations help you make the right choice in many common scenarios.

## Consistency Levels Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│              Azure Cosmos DB Consistency Levels                     │
└─────────────────────────────────────────────────────────────────────┘

    Strong Consistency ◄────────────────────────────────────┐
         │                                                   │
         │  • Linearizability guarantee                     │
         │  • Most recent committed version                 │
         │  • Highest consistency                           │
         │  • Lowest availability & performance             │
         │                                                   │
         ▼                                                   │
    Bounded Staleness                                       │
         │                                                   │
         │  • Lag bounded by K versions or T time          │
         │  • Configurable staleness                        │
         │  • Predictable consistency                       │
    C    │                                                   │
    O    ▼                                                   │
    N    Session                                             │
    S    │                                                   │
    I    │  • Read-your-writes guarantee                    │
    S    │  • Write-follows-reads guarantee                 │
    T    │  • Monotonic reads & writes                      │
    E    │  • Default for most apps                         │
    N    │                                                   │
    C    ▼                                                   │
    Y    Consistent Prefix                                   │
         │                                                   │
    ↕    │  • No out-of-order writes                        │
         │  • Reads never see partial writes                │
    P    │  • Updates in order                              │
    E    │                                                   │
    R    ▼                                                   │
    F    Eventual Consistency                                │
    O    │                                                   │
    R    │  • No ordering guarantee                         │
    M    │  • Highest availability & performance            │
    A    │  • Lowest consistency                            │
    N    │  • Replicas eventually converge                  │
    C    │                                                   │
    E    └───────────────────────────────────────────────────┘

         ◄───────────── Trade-offs ─────────────►
         
         Consistency ←──────────────────────→ Performance
         Reliability ←──────────────────────→ Availability
         Latency     ←──────────────────────→ Throughput
```

### Use Cases by Consistency Level

| Consistency Level | Best For | Examples |
|------------------|----------|----------|
| **Strong** | Critical data requiring linearizability | Financial transactions, inventory management |
| **Bounded Staleness** | Predictable lag tolerance | Stock quotes, location tracking |
| **Session** | User-scoped consistency | Shopping carts, user preferences, social media |
| **Consistent Prefix** | Ordered updates without staleness bounds | Live sports scores, message feeds |
| **Eventual** | Maximum performance, order unimportant | Retweet counts, likes, non-threaded comments |

## Configure the Default Consistency Level

You can configure the default consistency level on your Azure Cosmos DB account at any time. The default consistency level configured on your account applies to all Azure Cosmos DB databases and containers under that account. All reads and queries issued against a container or a database use the specified consistency level by default.

Read consistency applies to a single read operation scoped within a logical partition. The read operation can be issued by a remote client or a stored procedure.

## Guarantees Associated with Consistency Levels

Azure Cosmos DB guarantees that 100 percent of read requests meet the consistency guarantee for the consistency level chosen. The precise definitions of the five consistency levels in Azure Cosmos DB using the TLA+ specification language are provided in the [azure-cosmos-tla GitHub repo](https://github.com/azure/azure-cosmos-tla).

## Strong Consistency

Strong consistency offers a linearizability guarantee. Linearizability refers to serving requests concurrently. The reads are guaranteed to return the most recent committed version of an item. A client never sees an uncommitted or partial write. Users are always guaranteed to read the latest committed write.

## Bounded Staleness Consistency

In bounded staleness consistency, the lag of data between any two regions is always less than a specified amount. The amount can be **K** versions (that is, updates) of an item or by **T** time intervals, whichever is reached first. In other words, when you choose bounded staleness, the maximum "staleness" of the data in any region can be configured in two ways:

- The number of versions (**K**) of the item
- The time interval (**T**) reads might lag behind the writes

Bounded Staleness is beneficial primarily to single-region write accounts with two or more regions. If the data lag in a region (determined per physical partition) exceeds the configured staleness value, writes for that partition are throttled until staleness is back within the configured upper bound.

For a single-region account, Bounded Staleness provides the same write consistency guarantees as Session and Eventual Consistency. With Bounded Staleness, data is replicated to a local majority (three replicas in a four replica set) in the single region.

## Session Consistency

In session consistency, within a single client session, reads are guaranteed to honor the read-your-writes, and write-follows-reads guarantees. This guarantee assumes a single "writer" session or sharing the session token for multiple writers.

Like all consistency levels weaker than Strong, writes are replicated to a minimum of three replicas (in a four replica set) in the local region, with asynchronous replication to all other regions.

## Consistent Prefix Consistency

In consistent prefix, updates made as single document writes see eventual consistency. Updates made as a batch within a transaction, are returned consistent to the transaction in which they were committed. Write operations within a transaction of multiple documents are always visible together.

Assume two write operations are performed on documents Doc 1 and Doc 2, within transactions T1 and T2. When client does a read in any replica, the user sees either "Doc 1 v1 and Doc 2 v1" or "Doc 1 v2 and Doc 2 v2," but never "Doc 1 v1 and Doc 2 v2" or "Doc 1 v2 and Doc 2 v1" for the same read or query operation.

---

## Session vs Consistent Prefix: Key Differences

### Session Consistency
**Scope:** Per client session  
**Guarantees:** Strong guarantees within YOUR session only

```
Your Session:
Write A → Write B → Write C
  ↓       ↓       ↓
Read:  You ALWAYS see A, B, C in order and your latest writes

Other Sessions:
Read:  May see older data (A, B) or no guarantees about seeing YOUR writes
```

**Example Scenario:**
```
You're shopping online:
1. You add item to cart (Write)
2. You refresh page (Read) → You SEE the item (read-your-writes)
3. You update quantity (Write)
4. You view cart (Read) → You SEE the updated quantity

But another user viewing your public wishlist may not see your latest changes yet.
```

**Key Point:** Guarantees apply ONLY within your session. Perfect for user-specific operations.

---

### Consistent Prefix Consistency
**Scope:** Global across all clients  
**Guarantees:** Write order is preserved for everyone, but no read-your-writes guarantee

```
Global Write Order:
Write A → Write B → Write C
  ↓       ↓       ↓
Any Client Reads:
  ✓ Can see: [] or [A] or [A,B] or [A,B,C]
  ✗ Never see: [B] or [C] or [A,C] or [B,C] (out of order)
```

**Example Scenario:**
```
Live sports scoring system:
1. Team scores: 10 points (Write A)
2. Team scores: 20 points (Write B)
3. Team scores: 30 points (Write C)

All viewers will see progression in order:
  - 10 → 20 → 30 ✓
  
Never out of order:
  - 10 → 30 (skipping 20) ✗
  - 20 → 10 (backwards) ✗

BUT: You might write 30 points and immediately read, still seeing 20 points
```

**Key Point:** Preserves global write order but NO guarantee you'll see your own writes immediately.

---

### Quick Comparison Table

| Feature | Session | Consistent Prefix |
|---------|---------|-------------------|
| **Read your writes** | ✓ YES (within session) | ✗ NO |
| **Write follows reads** | ✓ YES (within session) | ✗ NO |
| **Monotonic reads** | ✓ YES (within session) | ✗ NO |
| **Monotonic writes** | ✓ YES (within session) | ✓ YES (global) |
| **Consistent prefix** | ✓ YES | ✓ YES |
| **Scope** | Single session | Global |
| **Best for** | User-specific operations | Ordered event streams |

### When to Choose What?

**Choose Session when:**
- Users need to see their own changes immediately
- Shopping carts, user profiles, preferences
- Single user's workflow must be consistent
- Most common choice for web applications

**Choose Consistent Prefix when:**
- Order of updates matters globally
- No single session context
- Live feeds, activity streams, audit logs
- Multiple writers, order preservation critical
- Don't need immediate read-your-writes

## Eventual Consistency

In eventual consistency, there's no ordering guarantee for reads. In the absence of any further writes, the replicas eventually converge.

Eventual consistency is the weakest form of consistency because a client might read the values that are older than the ones it read before. Eventual consistency is ideal where the application doesn't require any ordering guarantees. Examples include count of Retweets, Likes, or nonthreaded comments.


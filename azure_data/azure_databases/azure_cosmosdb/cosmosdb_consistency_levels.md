# Choose the Right Consistency Level
## Table of Contents

- [Consistency Levels Overview](#consistency-levels-overview)
  - [Use Cases by Consistency Level](#use-cases-by-consistency-level)
- [Configure the Default Consistency Level](#configure-the-default-consistency-level)
  - [Default Consistency Level: Session](#default-consistency-level-session)
- [Guarantees Associated with Consistency Levels](#guarantees-associated-with-consistency-levels)
- [Strong Consistency](#strong-consistency)
- [Bounded Staleness Consistency](#bounded-staleness-consistency)
- [Session Consistency](#session-consistency)
- [Consistent Prefix Consistency](#consistent-prefix-consistency)
- [Session vs Consistent Prefix: Key Differences](#session-vs-consistent-prefix-key-differences)
  - [Session Consistency](#session-consistency-2)
  - [Consistent Prefix Consistency](#consistent-prefix-consistency-2)
  - [Quick Comparison Table](#quick-comparison-table)
  - [When to Choose What?](#when-to-choose-what)
- [Eventual Consistency](#eventual-consistency)
- [Cosmos DB Consistency Levels vs SQL Server Isolation Levels](#cosmos-db-consistency-levels-vs-sql-server-isolation-levels)
- [Practice Question: Consistency Level for Batch Transactions](#practice-question-consistency-level-for-batch-transactions)
  - [Scenario](#scenario)
  - [Question](#question)
  - [Answer: C - Consistent Prefix ✅](#answer-c-consistent-prefix)
  - [Detailed Explanation](#detailed-explanation)
    - [Why Option C (Consistent Prefix) is Correct](#why-option-c-consistent-prefix-is-correct)
    - [Why Option A (Bounded Staleness) is Incorrect](#why-option-a-bounded-staleness-is-incorrect)
    - [Why Option B (Session) is Incorrect](#why-option-b-session-is-incorrect)
    - [Why Option D (Eventual) is Incorrect](#why-option-d-eventual-is-incorrect)
  - [Summary: Why Consistent Prefix for Batch Transactions?](#summary-why-consistent-prefix-for-batch-transactions)
  - [The Critical Requirement](#the-critical-requirement)
  - [Code Example: Consistent Prefix for Batch Operations](#code-example-consistent-prefix-for-batch-operations)
  - [Key Takeaways](#key-takeaways)
- [Practice Question: Multi-Region High Availability with Low Latency](#practice-question-multi-region-high-availability-with-low-latency)
  - [Scenario](#scenario-2)
  - [Question](#question-2)
  - [Answer: B - Enable Multi-Region Writes and set the Consistency Level to Session ✅](#answer-b-enable-multi-region-writes-and-set-the-consistency-level-to-session)
  - [Detailed Explanation](#detailed-explanation-2)
    - [Requirements Analysis](#requirements-analysis)
    - [Why Option B (Multi-Region Writes + Session) is Correct](#why-option-b-multi-region-writes-session-is-correct)
    - [Why Option A (Multi-Region Writes + Strong) is Incorrect](#why-option-a-multi-region-writes-strong-is-incorrect)
    - [Why Option C (Single-Region Writes + Bounded Staleness) is Incorrect](#why-option-c-single-region-writes-bounded-staleness-is-incorrect)
    - [Why Option D (Single-Region Writes + Eventual) is Incorrect](#why-option-d-single-region-writes-eventual-is-incorrect)
  - [Summary Comparison Table](#summary-comparison-table)
  - [Key Takeaways](#key-takeaways-2)
- [Practice Question: Overriding Consistency Level at Request Level](#practice-question-overriding-consistency-level-at-request-level)
  - [Scenario](#scenario-3)
  - [Question](#question-3)
  - [Answer: B - Set the ConsistencyLevel property of QueryRequestOptions when making the query ✅](#answer-b-set-the-consistencylevel-property-of-queryrequestoptions-when-making-the-query)
  - [Detailed Explanation](#detailed-explanation-3)
    - [Why Option B is Correct](#why-option-b-is-correct)
    - [Why Option A is Incorrect](#why-option-a-is-incorrect)
    - [Why Option C is Incorrect](#why-option-c-is-incorrect)
    - [Why Option D is Incorrect](#why-option-d-is-incorrect)
  - [Summary Table](#summary-table)
  - [Code Example: Request-Level Consistency Override](#code-example-request-level-consistency-override)
  - [Key Takeaways](#key-takeaways-3)
  - [Additional Resources](#additional-resources)


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

### Default Consistency Level: Session

**Session** is the **predefined default consistency level** for Azure Cosmos DB accounts. When you create a new Cosmos DB account without specifying a consistency level, it automatically uses Session consistency.

**Why Session is the Default:**
- **Best balance** between consistency and performance for most applications
- **Read-your-writes guarantee** within a session - users always see their own updates
- **Good performance** - reads from single replica (100% throughput)
- **Low write latency** - writes only need to replicate locally before returning
- Works well with typical web application patterns

**Changing the Default Consistency Level:**

You can change the default consistency level through:

**Azure Portal:**
1. Navigate to your Azure Cosmos DB account
2. Open the **Default Consistency** pane
3. Select the desired consistency level
4. Click **Save**

**Azure CLI:**
```bash
# Create account with Session consistency (default)
az cosmosdb create --name $accountName --resource-group $rg --default-consistency-level Session

# Update existing account to Strong consistency
az cosmosdb update --name $accountName --resource-group $rg --default-consistency-level Strong
```

**PowerShell:**
```powershell
# Create account with Session consistency
New-AzCosmosDBAccount -ResourceGroupName $rg -Location $locations -Name $accountName -DefaultConsistencyLevel "Session"

# Update to Strong consistency
Update-AzCosmosDBAccount -ResourceGroupName $rg -Name $accountName -DefaultConsistencyLevel "Strong"
```

> **Note:** You can also override the default consistency level at the request level using `QueryRequestOptions.ConsistencyLevel` in your SDK code. You can request a **stronger** consistency level than the account default, but you cannot request a **weaker** level.

## Guarantees Associated with Consistency Levels

Azure Cosmos DB guarantees that 100 percent of read requests meet the consistency guarantee for the consistency level chosen. The precise definitions of the five consistency levels in Azure Cosmos DB using the TLA+ specification language are provided in the [azure-cosmos-tla GitHub repo](https://github.com/azure/azure-cosmos-tla).

## Strong Consistency

Strong consistency offers a linearizability guarantee. Linearizability refers to serving requests concurrently. The reads are guaranteed to return the most recent committed version of an item. A client never sees an uncommitted or partial write. Users are always guaranteed to read the latest committed write.

![alt text](images/strong-consistency.gif)

## Bounded Staleness Consistency

In bounded staleness consistency, the lag of data between any two regions is always less than a specified amount. The amount can be **K** versions (that is, updates) of an item or by **T** time intervals, whichever is reached first. In other words, when you choose bounded staleness, the maximum "staleness" of the data in any region can be configured in two ways:

- The number of versions (**K**) of the item
- The time interval (**T**) reads might lag behind the writes

Bounded Staleness is beneficial primarily to single-region write accounts with two or more regions. If the data lag in a region (determined per physical partition) exceeds the configured staleness value, writes for that partition are throttled until staleness is back within the configured upper bound.

For a single-region account, Bounded Staleness provides the same write consistency guarantees as Session and Eventual Consistency. With Bounded Staleness, data is replicated to a local majority (three replicas in a four replica set) in the single region.

![alt text](images/bounded-staleness-consistency.gif)

## Session Consistency

In session consistency, within a single client session, reads are guaranteed to honor the read-your-writes, and write-follows-reads guarantees. This guarantee assumes a single "writer" session or sharing the session token for multiple writers.

Like all consistency levels weaker than Strong, writes are replicated to a minimum of three replicas (in a four replica set) in the local region, with asynchronous replication to all other regions.

![alt text](images/session-consistency.gif)

## Consistent Prefix Consistency

In consistent prefix, updates made as single document writes see eventual consistency. Updates made as a batch within a transaction, are returned consistent to the transaction in which they were committed. Write operations within a transaction of multiple documents are always visible together.

Assume two write operations are performed on documents Doc 1 and Doc 2, within transactions T1 and T2. When client does a read in any replica, the user sees either "Doc 1 v1 and Doc 2 v1" or "Doc 1 v2 and Doc 2 v2," but never "Doc 1 v1 and Doc 2 v2" or "Doc 1 v2 and Doc 2 v1" for the same read or query operation.

![alt text](images/consistent-prefix.gif)

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

![alt text](images/eventual-consistency.gif)

---

## Cosmos DB Consistency Levels vs SQL Server Isolation Levels

For a detailed comparison between Cosmos DB consistency levels and SQL Server transaction isolation levels, including:
- Conceptual mapping between the two approaches
- Detailed comparisons (Strong vs Serializable, Session vs Read Committed, etc.)
- Best use case scenarios with code examples
- Performance comparisons
- Migration considerations

See the dedicated document: [Cosmos DB vs SQL Server Consistency Comparison](cosmosdb_vs_sql_server_consistency.md)

---

## Practice Question: Consistency Level for Batch Transactions

### Scenario

A company implements a multi-region Azure Cosmos DB account.

You need to configure the default consistency level for the account. The consistency level must ensure that update operations made as a batch within a transaction are always visible together.

### Question

Which consistency level should you use?

**Select only one answer:**

**A.** Bounded Staleness

**B.** Session

**C.** Consistent Prefix ✅

**D.** Eventual

---

### Answer: C - Consistent Prefix ✅

**Consistent Prefix** is the correct answer.

---

### Detailed Explanation

#### Why Option C (Consistent Prefix) is Correct

The **Consistent Prefix** consistency level is specifically designed to ensure that updates made as a batch within a transaction are always visible together. This is explicitly stated in the Consistent Prefix documentation:

**Key Guarantee:**
> "Updates made as a batch within a transaction are returned consistent to the transaction in which they were committed. Write operations within a transaction of multiple documents are always visible together."

**Example:**
```
Transaction T1: Write Doc1 v1, Doc2 v1 (committed together)
Transaction T2: Write Doc1 v2, Doc2 v2 (committed together)

Consistent Prefix Guarantees:
✓ Clients see: [] or [Doc1 v1, Doc2 v1] or [Doc1 v2, Doc2 v2]
✗ Never see: [Doc1 v1, Doc2 v2] or [Doc1 v2, Doc2 v1]
```

**Why This Matters for Batch Operations:**
- When you commit multiple documents in a single transaction, they form a logical unit
- Consistent Prefix ensures these documents are always read together in their transactional boundary
- No partial visibility of the transaction across any replicas

**Real-World Scenario:**
```csharp
// Order processing with multiple documents
var transaction = container.CreateTransactionalBatch(new PartitionKey(orderId))
    .CreateItem(new Order { Id = orderId, Status = "Confirmed" })
    .CreateItem(new OrderItem { OrderId = orderId, ProductId = "P1" })
    .CreateItem(new OrderItem { OrderId = orderId, ProductId = "P2" });

await transaction.ExecuteAsync();

// With Consistent Prefix:
// - All clients see either no documents OR all three documents together
// - Never see Order without OrderItems, or vice versa
```

---

#### Why Option A (Bounded Staleness) is Incorrect

**Bounded Staleness** is designed to manage the **lag of data between regions**, not specifically for ensuring batch transaction visibility.

**What Bounded Staleness Does:**
- Controls maximum staleness by **K versions** or **T time interval**
- Ensures replicas don't lag beyond configured bounds
- Provides predictable consistency with configurable delay

**Why It Doesn't Address the Requirement:**
- Primary focus: **data lag across regions**
- Does NOT specifically guarantee batch transaction visibility
- Overkill for this scenario (provides stronger guarantees than needed)

**Example:**
```
Bounded Staleness: Max lag = 10 versions or 5 seconds

Concern: How far behind can Region 2 be from Region 1?
NOT: Are batch writes visible together?
```

**When to Use Bounded Staleness:**
```csharp
// Use for scenarios where lag tolerance matters
// Example: Stock price ticker
var requestOptions = new ItemRequestOptions 
{ 
    ConsistencyLevel = ConsistencyLevel.BoundedStaleness 
};

// Guarantee: Data is never more than 5 seconds or 100 versions old
// But this is about staleness, not batch visibility
```

---

#### Why Option B (Session) is Incorrect

**Session** consistency focuses on **single-client session guarantees**, not global batch transaction visibility.

**What Session Does:**
- Read-your-writes guarantee **within your session**
- Write-follows-reads guarantee **within your session**
- Monotonic reads/writes **within your session**

**Why It Doesn't Meet the Requirement:**
- Session scope: **Individual client session only**
- Other clients/sessions: **No guarantees about seeing batch together**
- The requirement is for **all clients** to see batch operations together

**Limitation Example:**
```
Your Session:
Transaction T1: Write Doc1, Doc2 in batch
You read: ✓ See both Doc1 and Doc2 together (read-your-writes)

Other User's Session:
They read: ✗ May see Doc1 without Doc2 (no batch guarantee)
```

**Correct Session Usage:**
```csharp
// Session is perfect for user-specific operations
// Example: Shopping cart
var cart = await container.CreateItemAsync(
    new Cart { UserId = userId, Items = [...] }
);

// YOU always see your cart updates immediately
// But OTHER users don't need to see your cart at all
```

**Key Difference:**
- **Session**: Guarantees within YOUR session (single client)
- **Consistent Prefix**: Guarantees across ALL clients (global batch visibility)

---

#### Why Option D (Eventual) is Incorrect

**Eventual** consistency provides **no ordering or atomicity guarantees** for batch operations.

**What Eventual Does:**
- Replicas eventually converge (no time bound)
- No ordering guarantees
- Highest performance, weakest consistency

**Why It Fails the Requirement:**
- **No guarantee** that batch writes are visible together
- Updates can be seen **in any order**
- Partial transaction visibility is possible

**Problem Example:**
```
Transaction: Write Doc1, Doc2, Doc3 in batch

With Eventual Consistency:
Reader 1: Sees Doc1, Doc3 (missing Doc2) ✗
Reader 2: Sees Doc2 only (missing Doc1, Doc3) ✗
Reader 3: Sees Doc3, Doc1, Doc2 (wrong order) ✗

Eventually all readers see all docs, but no guarantees during convergence
```

**When Eventual is Appropriate:**
```csharp
// Use for non-critical aggregates
// Example: Like counter
await container.UpsertItemAsync(
    new Post { Id = postId, LikeCount = post.LikeCount + 1 }
);

// Eventual consistency fine - exact count not critical
// Order doesn't matter for simple counters
```

---

### Summary: Why Consistent Prefix for Batch Transactions?

| Consistency Level | Guarantees Batch Visibility Together? | Why? |
|-------------------|--------------------------------------|------|
| **Consistent Prefix** ✅ | **YES** | Explicitly designed for this - transactions always visible as a unit |
| **Bounded Staleness** ❌ | **NO** | Focuses on lag bounds, not batch atomicity |
| **Session** ❌ | **NO** | Only guarantees within single session, not globally |
| **Eventual** ❌ | **NO** | No ordering or atomicity guarantees at all |

### The Critical Requirement

**"Updates made as a batch within a transaction are always visible together"**

This specifically requires:
1. ✓ **Atomic visibility**: All documents in transaction visible as a unit
2. ✓ **Global guarantee**: Applies to all clients, not just one session
3. ✓ **Order preservation**: Updates appear in committed order
4. ✓ **No partial reads**: Never see some docs without others from same transaction

**Only Consistent Prefix provides all four guarantees.**

---

### Code Example: Consistent Prefix for Batch Operations

```csharp
// Configure account with Consistent Prefix
var clientOptions = new CosmosClientOptions
{
    ConsistencyLevel = ConsistencyLevel.ConsistentPrefix
};

var client = new CosmosClient(endpoint, key, clientOptions);
var container = client.GetContainer("database", "container");

// Perform batch operation
var batch = container.CreateTransactionalBatch(new PartitionKey(customerId))
    .CreateItem(new Customer { Id = customerId, Name = "John" })
    .CreateItem(new Order { CustomerId = customerId, OrderId = "O1" })
    .CreateItem(new Order { CustomerId = customerId, OrderId = "O2" });

var response = await batch.ExecuteAsync();

// With Consistent Prefix:
// - ALL clients globally will either see:
//   1. None of these documents (transaction not yet visible)
//   2. ALL three documents together (transaction fully visible)
// - NEVER partial: Customer without Orders, or Orders without Customer

// Any client reading:
var query = new QueryDefinition(
    "SELECT * FROM c WHERE c.CustomerId = @customerId")
    .WithParameter("@customerId", customerId);

var iterator = container.GetItemQueryIterator<dynamic>(query);
var results = await iterator.ReadNextAsync();

// Results are guaranteed to show complete transaction or nothing
// Never partial results from the batch
```

---

### Key Takeaways

1. **Consistent Prefix for Batch Transactions**
   - Explicitly guarantees batch write operations are visible together
   - Preserves global write order across all clients
   - Perfect for transactional scenarios requiring atomic visibility

2. **Not Bounded Staleness**
   - Bounded Staleness is about lag management, not batch atomicity
   - Use when you need predictable staleness bounds

3. **Not Session**
   - Session is scoped to individual client sessions
   - Use for user-specific operations (carts, profiles)

4. **Not Eventual**
   - No guarantees about order or atomicity
   - Use for non-critical aggregates (likes, views)

---

## Practice Question: Multi-Region High Availability with Low Latency

### Scenario

You are developing an application that uses Azure Cosmos DB as its database. The application requires low-latency reads and writes, and you need to ensure that the data is always available even in the event of a regional outage.

### Question

Which of the following configurations should you implement in Cosmos DB to meet these requirements?

**Select only one answer:**

**A.** Enable Multi-Region Writes and set the Consistency Level to Strong

**B.** Enable Multi-Region Writes and set the Consistency Level to Session ✅

**C.** Enable Single-Region Writes and set the Consistency Level to Bounded Staleness

**D.** Enable Single-Region Writes and set the Consistency Level to Eventual

---

### Answer: B - Enable Multi-Region Writes and set the Consistency Level to Session ✅

---

### Detailed Explanation

#### Requirements Analysis

The question specifies two key requirements:
1. **Low-latency reads and writes**
2. **High availability even during regional outages**

---

#### Why Option B (Multi-Region Writes + Session) is Correct

**Multi-Region Writes Benefits:**
- Enables writing to **any region**, not just a primary region
- During a regional outage, writes automatically continue in other regions
- Users write to their **nearest region** for lowest latency
- Provides true **active-active** configuration

**Session Consistency Benefits:**
- **Read-your-writes guarantee** within a session
- **Low latency**: Reads from single replica (100% throughput)
- **Write latency**: Local region only (fast)
- Perfect balance between consistency and performance

**Performance Characteristics:**
```
Session Consistency:
├── Read Throughput: 100% (single replica read)
├── Write Latency: Local region only
├── Read-Your-Writes: ✓ Guaranteed within session
└── Ideal for: User-facing applications
```

---

#### Why Option A (Multi-Region Writes + Strong) is Incorrect

While Multi-Region Writes provides high availability, **Strong consistency contradicts the low-latency requirement**.

**Strong Consistency Problems:**
- **Writes must synchronously replicate to ALL regions** before returning success
- This introduces significant latency, especially for geographically distant regions
- Read throughput is only **50%** (requires quorum from 2 replicas)

**Performance Impact:**
```
Strong Consistency:
├── Read Throughput: 50% (quorum read from 2 replicas)
├── Write Latency: Synchronous replication to ALL regions (HIGH)
├── Global Consistency: ✓ Yes, but at significant cost
└── Problem: Violates low-latency requirement
```

**Example Latency Comparison:**
```
Scenario: Write from East US, regions in East US, West Europe, Southeast Asia

Session Consistency:
- Write acknowledged after local East US replication (~5-10ms)

Strong Consistency:
- Write acknowledged after ALL regions confirm (~100-300ms)
- Must wait for Southeast Asia round-trip!
```

---

#### Why Option C (Single-Region Writes + Bounded Staleness) is Incorrect

**Single-Region Writes Limitation:**
- All writes go to **one primary region**
- During regional outage of the primary region, **writes fail**
- Does NOT meet the "always available" requirement

**Bounded Staleness:**
- Good for predictable lag tolerance
- But doesn't solve the availability problem

**Failure Scenario:**
```
Single-Region Write (Primary: East US):
├── East US outage occurs
├── Writes: ✗ FAIL (primary region unavailable)
├── Reads: ✓ Continue from other regions
└── Result: Does NOT meet high availability for writes
```

---

#### Why Option D (Single-Region Writes + Eventual) is Incorrect

**Same Single-Region Write Problem:**
- Primary region outage = write failures
- Does NOT provide high availability for writes

**Eventual Consistency Additional Issues:**
- No ordering guarantees
- Potential for reading stale data
- May not meet application requirements for data consistency

**Problems:**
```
Single-Region Write + Eventual:
├── Regional Outage: ✗ Writes fail
├── Consistency: Weakest level
├── Read-Your-Writes: ✗ Not guaranteed
└── Result: Fails both requirements
```

---

### Summary Comparison Table

| Configuration | Low Latency | High Availability | Meets Requirements |
|---------------|-------------|-------------------|-------------------|
| **Multi-Region + Session** ✅ | ✓ Yes | ✓ Yes | ✓ **YES** |
| **Multi-Region + Strong** | ✗ No (sync replication) | ✓ Yes | ✗ No |
| **Single-Region + Bounded Staleness** | ✓ Yes | ✗ No (write failures) | ✗ No |
| **Single-Region + Eventual** | ✓ Yes | ✗ No (write failures) | ✗ No |

---

### Key Takeaways

1. **Multi-Region Writes is essential for high availability**
   - Single-region writes create a single point of failure
   - Regional outages will cause write failures

2. **Session consistency provides the best balance**
   - Low latency (local region writes, single replica reads)
   - Sufficient consistency for most applications
   - Read-your-writes guarantee within user sessions

3. **Strong consistency sacrifices latency for global consistency**
   - Only use when absolutely required (financial transactions)
   - Not suitable when low latency is a requirement

4. **Default recommendation for most applications**
   - Multi-Region Writes + Session consistency
   - This is the most common production configuration

---

## Practice Question: Overriding Consistency Level at Request Level

### Scenario

When creating a Cosmos DB account, you indicate which consistency level you would like to follow: Strong, Bounded Staleness, Session, Consistent Prefix and Eventual.

### Question

How can a developer force Strong consistency on a query when the database itself is configured with Eventual consistency?

**Select only one answer:**

**A.** Set the MaxConcurrency property of QueryRequestOptions when making the query.

**B.** Set the ConsistencyLevel property of QueryRequestOptions when making the query. ✅

**C.** By specifying the exact partition key and row key in the query.

**D.** Modify the Consistency level of the database using settings before making the query.

---

### Answer: B - Set the ConsistencyLevel property of QueryRequestOptions when making the query ✅

---

### Detailed Explanation

#### Why Option B is Correct

The **QueryRequestOptions.ConsistencyLevel** property allows developers to override the default consistency level on a **per-request basis**. This is a powerful feature that enables:

- **Request-level control**: Different queries can use different consistency levels
- **No database modification required**: The account's default consistency remains unchanged
- **Flexibility**: Critical operations can use Strong consistency while others use Eventual

**Key Point from Microsoft Documentation:**
> "QueryRequestOptions.ConsistencyLevel Property gets or sets the consistency level required for the request in the Azure Cosmos DB service. This is a request level property, and doesn't affect the database settings."

**Code Example:**
```csharp
// Database is configured with Eventual consistency, but we need Strong for this query
var queryOptions = new QueryRequestOptions
{
    ConsistencyLevel = ConsistencyLevel.Strong
};

var query = new QueryDefinition("SELECT * FROM c WHERE c.accountId = @accountId")
    .WithParameter("@accountId", accountId);

var iterator = container.GetItemQueryIterator<Account>(query, requestOptions: queryOptions);
var results = await iterator.ReadNextAsync();

// This specific query uses Strong consistency
// Other queries without this option still use Eventual (account default)
```

**Important Constraint:**
You can only request a consistency level that is **equal to or weaker** than the account's default, **OR** you can request a **stronger** consistency level. However, requesting weaker consistency than the account default is the common use case.

**Wait - Clarification on Strengthening Consistency:**
Actually, you **CAN** strengthen consistency at the request level. The rule is:
- You can always request **stronger** consistency than the account default
- You **cannot** request **weaker** consistency than the account default

So for an account configured with Eventual (weakest), you can request any stronger level (Consistent Prefix, Session, Bounded Staleness, Strong).

---

#### Why Option A is Incorrect

**MaxConcurrency** property controls the **degree of parallelism** for query execution, not consistency.

**What MaxConcurrency Does:**
- Controls how many partitions are queried in parallel
- Affects query performance and resource consumption
- Has **nothing to do with consistency**

```csharp
var queryOptions = new QueryRequestOptions
{
    MaxConcurrency = 10  // Query up to 10 partitions in parallel
};

// This is about parallelism, not consistency!
```

---

#### Why Option C is Incorrect

**Specifying partition key and row key** affects query efficiency and scope, not consistency level.

**What Partition Key Does:**
- Routes the query to a specific logical partition
- Improves query performance (single partition query vs. cross-partition)
- **Does NOT change consistency level**

```csharp
// This is efficient (single partition) but doesn't affect consistency
var item = await container.ReadItemAsync<Account>(
    accountId,
    new PartitionKey(partitionKeyValue)
);

// Still uses account's default consistency (Eventual in this scenario)
```

---

#### Why Option D is Incorrect

**Modifying the database consistency level** is:
1. **Not necessary** - request-level override is available
2. **Affects all operations** - not just the specific query
3. **Requires administrative access** - may not be available to developers
4. **Overkill** - changes the entire account's behavior

```csharp
// This would change the account's DEFAULT consistency
// Affects ALL queries and operations from ALL clients
// NOT what you want for a single query override

// Instead, use per-request override:
var queryOptions = new QueryRequestOptions
{
    ConsistencyLevel = ConsistencyLevel.Strong  // Only this query
};
```

---

### Summary Table

| Option | What It Does | Affects Consistency? |
|--------|-------------|---------------------|
| **ConsistencyLevel property** ✅ | Sets consistency per request | ✓ Yes - request level |
| **MaxConcurrency property** | Controls query parallelism | ✗ No |
| **Partition key / row key** | Routes query to partition | ✗ No |
| **Modify database settings** | Changes account default | ✓ Yes - but too broad |

---

### Code Example: Request-Level Consistency Override

```csharp
public class CosmosDbService
{
    private readonly Container _container;

    // Critical financial query - use Strong consistency
    public async Task<Account> GetAccountBalanceStrong(string accountId)
    {
        var queryOptions = new QueryRequestOptions
        {
            ConsistencyLevel = ConsistencyLevel.Strong,
            PartitionKey = new PartitionKey(accountId)
        };

        var response = await _container.ReadItemAsync<Account>(
            accountId,
            new PartitionKey(accountId),
            new ItemRequestOptions { ConsistencyLevel = ConsistencyLevel.Strong }
        );

        return response.Resource;
    }

    // Non-critical read - use account default (Eventual)
    public async Task<IEnumerable<Product>> GetProductCatalog()
    {
        var query = new QueryDefinition("SELECT * FROM c WHERE c.type = 'product'");
        
        // No consistency override - uses account default (Eventual)
        var iterator = _container.GetItemQueryIterator<Product>(query);
        var results = new List<Product>();
        
        while (iterator.HasMoreResults)
        {
            var response = await iterator.ReadNextAsync();
            results.AddRange(response);
        }
        
        return results;
    }
}
```

---

### Key Takeaways

1. **Use QueryRequestOptions.ConsistencyLevel** for per-request consistency control
2. **Request-level property** - doesn't affect database settings
3. **Can strengthen consistency** from account default
4. **Ideal for mixed workloads** - critical operations get Strong, others use Eventual
5. **No administrative changes required** - developers can control at code level

---

### Additional Resources

- [Azure Cosmos DB Consistency Levels](https://learn.microsoft.com/en-us/azure/cosmos-db/consistency-levels)
- [QueryRequestOptions.ConsistencyLevel Property](https://docs.microsoft.com/en-us/dotnet/api/microsoft.azure.cosmos.queryrequestoptions.consistencylevel)
- [SQL Server Transaction Isolation Levels](https://learn.microsoft.com/en-us/sql/t-sql/statements/set-transaction-isolation-level-transact-sql)
- [Understanding Isolation Levels](https://learn.microsoft.com/en-us/sql/connect/jdbc/understanding-isolation-levels)
- [Snapshot Isolation in SQL Server](https://learn.microsoft.com/en-us/sql/connect/ado-net/sql/snapshot-isolation-sql-server)


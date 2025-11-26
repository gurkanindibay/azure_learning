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

## Cosmos DB Consistency Levels vs Relational Database Isolation Levels

### Overview

Azure Cosmos DB consistency levels and SQL Server transaction isolation levels solve similar problems but in fundamentally different contexts:

- **SQL Server Isolation Levels**: Control concurrency within a **single database instance** using locks and row versioning
- **Cosmos DB Consistency Levels**: Control consistency across **globally distributed databases** with multiple replicas

### SQL Server Isolation Levels Explained

SQL Server provides isolation levels that control how transactions interact with each other in a single database:

| Isolation Level | Dirty Read | Non-Repeatable Read | Phantom Read | Locking Mechanism |
|----------------|------------|---------------------|--------------|-------------------|
| **Read Uncommitted** | ✓ Allowed | ✓ Allowed | ✓ Allowed | No read locks |
| **Read Committed** (Default) | ❌ Prevented | ✓ Allowed | ✓ Allowed | Short-duration read locks |
| **Repeatable Read** | ❌ Prevented | ❌ Prevented | ✓ Allowed | Locks held until transaction ends |
| **Snapshot** | ❌ Prevented | ❌ Prevented | ❌ Prevented | Row versioning (no locks) |
| **Serializable** | ❌ Prevented | ❌ Prevented | ❌ Prevented | Range locks until transaction ends |

#### SQL Server Anomalies Explained

**Dirty Read**: Reading uncommitted changes from another transaction
```sql
-- Transaction 1
BEGIN TRANSACTION
UPDATE Accounts SET Balance = 500 WHERE Id = 1
-- Not committed yet

-- Transaction 2 (Read Uncommitted)
SELECT Balance FROM Accounts WHERE Id = 1  -- Reads 500

-- Transaction 1 rolls back
ROLLBACK  -- Balance is still 1000, Transaction 2 saw incorrect data
```

**Non-Repeatable Read**: Same query returns different results in the same transaction
```sql
-- Transaction 1
BEGIN TRANSACTION
SELECT Balance FROM Accounts WHERE Id = 1  -- Returns 1000

-- Transaction 2 updates and commits
UPDATE Accounts SET Balance = 500 WHERE Id = 1

-- Transaction 1 reads again
SELECT Balance FROM Accounts WHERE Id = 1  -- Returns 500 (different!)
COMMIT
```

**Phantom Read**: New rows appear in subsequent reads
```sql
-- Transaction 1
BEGIN TRANSACTION
SELECT COUNT(*) FROM Accounts WHERE Balance > 100  -- Returns 5

-- Transaction 2 inserts and commits
INSERT INTO Accounts (Balance) VALUES (200)

-- Transaction 1 reads again
SELECT COUNT(*) FROM Accounts WHERE Balance > 100  -- Returns 6 (phantom row!)
COMMIT
```

---

### Conceptual Mapping (Not Direct Equivalents)

While there's no direct 1-to-1 mapping due to different architectures, here's a conceptual comparison:

| Cosmos DB Consistency | Approximate SQL Equivalent | Key Similarity | Key Difference |
|----------------------|---------------------------|----------------|----------------|
| **Strong** | Serializable | Strongest guarantees, linearizability | Cosmos: Multi-region sync; SQL: Locking |
| **Bounded Staleness** | *(No direct equivalent)* | Configurable lag | Cosmos: Time/version lag; SQL: No equivalent |
| **Session** | Read Committed + Session Token | Read your writes | Cosmos: Session-scoped; SQL: Transaction-scoped |
| **Consistent Prefix** | *(No direct equivalent)* | Ordered reads | Cosmos: Global order; SQL: No equivalent |
| **Eventual** | Read Uncommitted | Highest performance, weakest consistency | Cosmos: Eventual convergence; SQL: Dirty reads |

⚠️ **Important**: This mapping is **conceptual only**. The underlying mechanisms and guarantees are fundamentally different.

---

### Detailed Comparison

#### Strong Consistency vs Serializable Isolation

**Cosmos DB Strong:**
```
Client 1: Write X=1 → Write X=2 → Commit
Client 2: Read X → Always gets 2 (most recent committed)

Multi-region guarantee:
- Writes synchronously replicated to ALL regions
- All regions see same value at same time
- Lower write availability, higher latency
```

**SQL Server Serializable:**
```sql
-- Transaction 1
BEGIN TRANSACTION
SELECT * FROM Orders WHERE Status = 'Pending'
-- Holds range lock on 'Pending' orders
-- Other transactions CANNOT insert/update/delete Pending orders
COMMIT
```

**Comparison:**

| Aspect | Cosmos DB Strong | SQL Serializable |
|--------|-----------------|------------------|
| **Mechanism** | Synchronous multi-region replication | Range locks on affected data |
| **Scope** | Global across all regions | Single database instance |
| **Blocking** | No blocking, but higher write latency | Blocks conflicting transactions |
| **Use Case** | Critical data requiring global consistency | Prevent concurrent modifications in DB |
| **Performance** | Lower write performance globally | Lower concurrency locally |

---

#### Session Consistency vs Read Committed

**Cosmos DB Session:**
```
Your Session:
Write Cart Item A → Read Cart → See Item A ✓
Write Cart Item B → Read Cart → See A,B ✓

Other User's Session:
Read Your Cart → May not see Item B yet (eventual)
```

**SQL Server Read Committed:**
```sql
-- Transaction 1
BEGIN TRANSACTION
UPDATE Accounts SET Balance = 500 WHERE Id = 1
-- Not committed - other transactions CANNOT see this

-- Transaction 2
SELECT Balance FROM Accounts WHERE Id = 1  -- Still sees 1000 (old value)

-- Transaction 1 commits
COMMIT

-- Transaction 2 now can see
SELECT Balance FROM Accounts WHERE Id = 1  -- Sees 500
```

**Comparison:**

| Aspect | Cosmos DB Session | SQL Read Committed |
|--------|-------------------|-------------------|
| **Read Your Writes** | ✓ YES (within session) | ✓ YES (within transaction) |
| **Scope** | Client session across requests | Single transaction |
| **Duration** | Entire application session | Transaction lifetime only |
| **Dirty Reads** | ❌ Prevented | ❌ Prevented |
| **Non-Repeatable Reads** | ✓ Possible (outside session) | ✓ Possible |
| **Mechanism** | Session tokens | Shared/Exclusive locks |

---

#### Eventual Consistency vs Read Uncommitted

**Cosmos DB Eventual:**
```
Region 1: Write X=1 → Region 2 may still see old value
Time passes...
Region 2: Eventually sees X=1
No guarantees on WHEN convergence happens
```

**SQL Server Read Uncommitted:**
```sql
-- Transaction 1
BEGIN TRANSACTION
UPDATE Accounts SET Balance = 500 WHERE Id = 1
-- Not committed yet

-- Transaction 2 (Read Uncommitted)
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED
SELECT Balance FROM Accounts WHERE Id = 1  -- Reads 500 (uncommitted)

-- Transaction 1 rolls back
ROLLBACK  -- Balance reverts to 1000
-- Transaction 2 saw data that never existed!
```

**Comparison:**

| Aspect | Cosmos DB Eventual | SQL Read Uncommitted |
|--------|-------------------|---------------------|
| **Dirty Reads** | ❌ No (reads committed data) | ✓ YES (reads uncommitted) |
| **Ordering** | No guarantees | No guarantees |
| **Risk** | Stale data | Reading data that may be rolled back |
| **Performance** | Highest | Highest |
| **Use Case** | Counters, likes, views | Quick aggregates, approximate counts |

---

### Best Use Case Scenarios

#### Financial Transaction System

**Requirement**: Account balance must always be accurate, no inconsistencies allowed

**SQL Server Approach:**
```sql
-- Use Serializable to prevent lost updates
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE
BEGIN TRANSACTION

-- Read current balance
SELECT @balance = Balance FROM Accounts WHERE Id = @accountId

-- Validate sufficient funds
IF @balance >= @withdrawalAmount
BEGIN
    UPDATE Accounts 
    SET Balance = Balance - @withdrawalAmount 
    WHERE Id = @accountId
    
    INSERT INTO Transactions (AccountId, Amount, Type)
    VALUES (@accountId, @withdrawalAmount, 'Withdrawal')
    
    COMMIT
END
ELSE
    ROLLBACK
```

**Cosmos DB Approach:**
```csharp
// Use Strong consistency for financial operations
var requestOptions = new ItemRequestOptions 
{ 
    ConsistencyLevel = ConsistencyLevel.Strong 
};

// Read balance (guaranteed most recent)
var account = await container.ReadItemAsync<Account>(
    accountId, 
    new PartitionKey(accountId),
    requestOptions
);

if (account.Resource.Balance >= withdrawalAmount)
{
    account.Resource.Balance -= withdrawalAmount;
    account.Resource.TransactionHistory.Add(new Transaction(...));
    
    // Write must be replicated to all regions before success
    await container.ReplaceItemAsync(
        account.Resource, 
        accountId, 
        new PartitionKey(accountId),
        requestOptions
    );
}
```

**Comparison:**
- SQL: Uses locks to prevent concurrent modifications
- Cosmos: Synchronously replicates to ensure global consistency
- Both: Guarantee no lost updates or dirty reads

---

#### Shopping Cart Application

**Requirement**: User should always see their own cart updates, but other users don't need immediate consistency

**SQL Server Approach:**
```sql
-- Use Read Committed (default) with proper transaction handling
SET TRANSACTION ISOLATION LEVEL READ COMMITTED
BEGIN TRANSACTION

-- Add item to cart
INSERT INTO CartItems (UserId, CartId, ProductId, Quantity)
VALUES (@userId, @cartId, @productId, @quantity)

-- User immediately sees their cart
SELECT * FROM CartItems WHERE CartId = @cartId

COMMIT
```

**Cosmos DB Approach:**
```csharp
// Use Session consistency (default) - perfect for this scenario
// No need to explicitly set it, but showing for clarity
var requestOptions = new ItemRequestOptions 
{ 
    ConsistencyLevel = ConsistencyLevel.Session 
};

// Add item to cart
var cartItem = new CartItem 
{ 
    UserId = userId, 
    CartId = cartId, 
    ProductId = productId 
};

await container.CreateItemAsync(cartItem, new PartitionKey(userId));

// User ALWAYS sees their own writes (read-your-writes guarantee)
var userCart = await container.ReadItemAsync<Cart>(
    cartId, 
    new PartitionKey(userId),
    requestOptions  // Session token automatically included
);
```

**Comparison:**
- SQL: Transaction ensures user sees their changes
- Cosmos: Session token ensures read-your-writes across API calls
- Both: Prevent dirty reads, allow non-repeatable reads from other users

---

#### Social Media Like Counter

**Requirement**: Display approximate like counts, exact accuracy not critical

**SQL Server Approach:**
```sql
-- Use Read Uncommitted for maximum performance
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED

-- Fast, non-blocking read of approximate count
SELECT LikeCount FROM Posts WHERE PostId = @postId

-- Update counter (many concurrent updates)
UPDATE Posts 
SET LikeCount = LikeCount + 1 
WHERE PostId = @postId
```

**Cosmos DB Approach:**
```csharp
// Use Eventual consistency for maximum throughput
var requestOptions = new ItemRequestOptions 
{ 
    ConsistencyLevel = ConsistencyLevel.Eventual 
};

// Read like count (may be slightly stale)
var post = await container.ReadItemAsync<Post>(
    postId, 
    new PartitionKey(postId),
    requestOptions
);

// Increment counter (many concurrent updates across regions)
post.Resource.LikeCount++;
await container.ReplaceItemAsync(
    post.Resource, 
    postId, 
    new PartitionKey(postId)
);
```

**Comparison:**
- SQL: Reads uncommitted data for speed, may see inconsistent counts
- Cosmos: Reads from nearest replica, eventual convergence
- Both: Optimize for performance over accuracy

---

#### Live Sports Score System

**Requirement**: Scores must be displayed in order (10→20→30), but slight delay acceptable

**SQL Server Approach:**
```sql
-- Use Repeatable Read to maintain order within transaction
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ
BEGIN TRANSACTION

-- Insert score updates in order
INSERT INTO ScoreUpdates (GameId, Score, Timestamp)
VALUES (@gameId, 10, GETDATE())

-- Within this transaction, order is maintained
SELECT * FROM ScoreUpdates WHERE GameId = @gameId ORDER BY Timestamp

COMMIT
```

**Cosmos DB Approach:**
```csharp
// Use Consistent Prefix - guarantees ordered updates
var requestOptions = new ItemRequestOptions 
{ 
    ConsistencyLevel = ConsistencyLevel.ConsistentPrefix 
};

// Write score updates
await container.CreateItemAsync(
    new ScoreUpdate { GameId = gameId, Score = 10, Timestamp = DateTime.UtcNow },
    new PartitionKey(gameId)
);

await container.CreateItemAsync(
    new ScoreUpdate { GameId = gameId, Score = 20, Timestamp = DateTime.UtcNow },
    new PartitionKey(gameId)
);

// All clients see scores in order: 10→20, never 20→10
// But may have delay seeing the latest score
var scores = container.GetItemQueryIterator<ScoreUpdate>(
    new QueryDefinition("SELECT * FROM c WHERE c.GameId = @gameId ORDER BY c.Timestamp")
        .WithParameter("@gameId", gameId),
    requestOptions: requestOptions
);
```

**Comparison:**
- SQL: Repeatable Read maintains order within a transaction
- Cosmos: Consistent Prefix maintains global write order
- Key Difference: Cosmos guarantees order across all replicas globally

---

#### Inventory Management System

**Requirement**: Prevent overselling - stock levels must be accurate

**SQL Server Approach:**
```sql
-- Use Repeatable Read to prevent lost updates
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ
BEGIN TRANSACTION

-- Read current stock (lock held until transaction ends)
SELECT @currentStock = StockLevel 
FROM Inventory 
WHERE ProductId = @productId

-- Check availability
IF @currentStock >= @orderQuantity
BEGIN
    -- Decrement stock
    UPDATE Inventory 
    SET StockLevel = StockLevel - @orderQuantity 
    WHERE ProductId = @productId
    
    -- Create order
    INSERT INTO Orders (ProductId, Quantity) 
    VALUES (@productId, @orderQuantity)
    
    COMMIT
END
ELSE
    ROLLBACK
```

**Cosmos DB Approach:**
```csharp
// Use Bounded Staleness for near-strong consistency with better performance
var requestOptions = new ItemRequestOptions 
{ 
    ConsistencyLevel = ConsistencyLevel.BoundedStaleness 
};

// Configure bounded staleness at account level:
// Max lag: 100 versions or 5 seconds

// Read stock with maximum 5-second staleness guarantee
var inventory = await container.ReadItemAsync<Inventory>(
    productId, 
    new PartitionKey(productId),
    requestOptions
);

if (inventory.Resource.StockLevel >= orderQuantity)
{
    // Use optimistic concurrency with ETag
    inventory.Resource.StockLevel -= orderQuantity;
    
    try 
    {
        await container.ReplaceItemAsync(
            inventory.Resource,
            productId,
            new PartitionKey(productId),
            new ItemRequestOptions { IfMatchEtag = inventory.ETag }
        );
    }
    catch (CosmosException ex) when (ex.StatusCode == HttpStatusCode.PreconditionFailed)
    {
        // Retry logic - another transaction modified the item
    }
}
```

**Comparison:**
- SQL: Uses locks to prevent concurrent modifications
- Cosmos: Uses bounded staleness (near-strong) + optimistic concurrency (ETags)
- Both: Prevent overselling through different mechanisms

---

### Key Architectural Differences

| Aspect | SQL Server Isolation Levels | Cosmos DB Consistency Levels |
|--------|----------------------------|------------------------------|
| **Architecture** | Single database instance | Globally distributed, multi-region |
| **Primary Concern** | Concurrent transactions in same DB | Data consistency across replicas |
| **Mechanism** | Locks and row versioning | Quorum reads/writes, replication |
| **Scope** | Transaction-level | Request-level (can override per request) |
| **Performance Impact** | Lock contention, blocking | Network latency, replication overhead |
| **Consistency Point** | Within database | Across geographies |
| **Default** | Read Committed | Session |
| **Configuration** | Per transaction/connection | Per account (with per-request override) |

---

### When to Use What?

#### Use SQL Server Isolation Levels When:

✅ **Single-Region Application**
- All users access same database instance
- No need for geographic distribution
- Strong ACID guarantees required within one DB

✅ **Complex Transactions**
- Multi-step transactions with rollback
- Need for referential integrity
- Joins across multiple tables

✅ **Locking is Acceptable**
- Can tolerate blocked transactions
- Lower concurrency workloads
- Batch processing with exclusive access

#### Use Cosmos DB Consistency Levels When:

✅ **Global Distribution Required**
- Users across multiple regions
- Low latency reads from nearest region
- Geo-redundancy and disaster recovery

✅ **High Concurrency**
- Millions of operations per second
- No blocking allowed
- Optimistic concurrency model preferred

✅ **Flexible Consistency Tradeoffs**
- Different consistency for different operations
- Balance performance vs consistency per request
- Session-based consistency for user operations

---

### Performance Comparison

#### SQL Server Isolation Level Performance

**From Highest to Lowest Performance:**
```
Read Uncommitted (Fastest, Least Safe)
    ↓
Read Committed (Default, Balanced)
    ↓
Repeatable Read (Slower, More Locks)
    ↓
Snapshot (No Locks, But TempDB Overhead)
    ↓
Serializable (Slowest, Most Locks)
```

**Concurrency Impact:**
- Higher isolation = More locks = More blocking = Lower concurrency

#### Cosmos DB Consistency Level Performance

**Read Throughput (Same RUs):**
```
Eventual (1 replica read)      → 100% throughput
Consistent Prefix (1 replica)  → 100% throughput
Session (1 replica)            → 100% throughput
Bounded Staleness (2 replicas) → 50% throughput
Strong (2 replicas)            → 50% throughput
```

**Write Latency:**
```
Eventual → Local region only (Fast)
Session → Local region only (Fast)
Consistent Prefix → Local region only (Fast)
Bounded Staleness → Local region + replication lag check
Strong → ALL regions synchronously (Slowest)
```

---

### Migration Considerations

#### Migrating from SQL Server to Cosmos DB

**Mapping Your Isolation Needs:**

| If Your SQL App Uses | Consider Cosmos DB | Reason |
|---------------------|-------------------|---------|
| **Serializable** | Strong | Strongest guarantees, but check multi-region impact |
| **Repeatable Read** | Bounded Staleness | Near-strong with configurable lag |
| **Read Committed** | Session | Read-your-writes, similar semantics |
| **Read Uncommitted** | Eventual | Maximum performance |
| **Snapshot** | Session or Bounded Staleness | No-lock semantics, consistent reads |

⚠️ **Important Migration Notes:**

1. **No Exact Equivalents**: Cosmos DB consistency levels operate at a different layer (distributed systems vs. single DB)

2. **Rethink Transactions**: 
   - SQL: Multi-statement transactions with locks
   - Cosmos: Optimistic concurrency with ETags, stored procedures for atomicity

3. **Partition Key Critical**:
   - Cosmos DB consistency guarantees are per partition
   - Cross-partition consistency has additional considerations

4. **Test Thoroughly**:
   - Behavior differences may surprise you
   - Performance characteristics very different

---

### Summary Table: Practical Scenarios

| Scenario | SQL Server | Cosmos DB | Rationale |
|----------|-----------|-----------|-----------|
| **Financial Transactions** | Serializable | Strong | Need absolute consistency |
| **User Shopping Cart** | Read Committed | Session | Read-your-writes sufficient |
| **Product Catalog Reads** | Read Committed | Session/Bounded Staleness | Slight staleness acceptable |
| **Like/View Counters** | Read Uncommitted | Eventual | Approximate counts fine |
| **Inventory Decrement** | Repeatable Read | Bounded Staleness + ETag | Prevent overselling |
| **Audit Logs** | Read Committed | Consistent Prefix | Order preservation important |
| **Live Scoreboards** | Repeatable Read | Consistent Prefix | Ordered updates required |
| **User Profile Updates** | Read Committed | Session | Users need immediate feedback |
| **Analytics Queries** | Read Uncommitted/Snapshot | Eventual | Aggregates, approximate ok |
| **Order Processing** | Serializable | Strong (single-region write) | No order conflicts allowed |

---

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

### Additional Resources

- [Azure Cosmos DB Consistency Levels](https://learn.microsoft.com/en-us/azure/cosmos-db/consistency-levels)
- [SQL Server Transaction Isolation Levels](https://learn.microsoft.com/en-us/sql/t-sql/statements/set-transaction-isolation-level-transact-sql)
- [Understanding Isolation Levels](https://learn.microsoft.com/en-us/sql/connect/jdbc/understanding-isolation-levels)
- [Snapshot Isolation in SQL Server](https://learn.microsoft.com/en-us/sql/connect/ado-net/sql/snapshot-isolation-sql-server)


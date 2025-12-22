# Cosmos DB Consistency Levels vs Relational Database Isolation Levels

This document compares Azure Cosmos DB consistency levels with SQL Server transaction isolation levels to help developers understand the conceptual mappings and differences between these two approaches to data consistency.

## Table of Contents

- [Overview](#overview)
- [SQL Server Isolation Levels Explained](#sql-server-isolation-levels-explained)
  - [SQL Server Anomalies Explained](#sql-server-anomalies-explained)
- [Conceptual Mapping (Not Direct Equivalents)](#conceptual-mapping-not-direct-equivalents)
- [Detailed Comparison](#detailed-comparison)
  - [Strong Consistency vs Serializable Isolation](#strong-consistency-vs-serializable-isolation)
  - [Session Consistency vs Read Committed](#session-consistency-vs-read-committed)
  - [Eventual Consistency vs Read Uncommitted](#eventual-consistency-vs-read-uncommitted)
- [Best Use Case Scenarios](#best-use-case-scenarios)
  - [Financial Transaction System](#financial-transaction-system)
  - [Shopping Cart Application](#shopping-cart-application)
  - [Social Media Like Counter](#social-media-like-counter)
  - [Live Sports Score System](#live-sports-score-system)
  - [Inventory Management System](#inventory-management-system)
- [Key Architectural Differences](#key-architectural-differences)
- [When to Use What?](#when-to-use-what)
  - [Use SQL Server Isolation Levels When](#use-sql-server-isolation-levels-when)
  - [Use Cosmos DB Consistency Levels When](#use-cosmos-db-consistency-levels-when)
- [Performance Comparison](#performance-comparison)
  - [SQL Server Isolation Level Performance](#sql-server-isolation-level-performance)
  - [Cosmos DB Consistency Level Performance](#cosmos-db-consistency-level-performance)
- [Migration Considerations](#migration-considerations)
  - [Migrating from SQL Server to Cosmos DB](#migrating-from-sql-server-to-cosmos-db)
- [Summary Table: Practical Scenarios](#summary-table-practical-scenarios)
- [Additional Resources](#additional-resources)

---

## Overview

Azure Cosmos DB consistency levels and SQL Server transaction isolation levels solve similar problems but in fundamentally different contexts:

- **SQL Server Isolation Levels**: Control concurrency within a **single database instance** using locks and row versioning
- **Cosmos DB Consistency Levels**: Control consistency across **globally distributed databases** with multiple replicas

---

## SQL Server Isolation Levels Explained

SQL Server provides isolation levels that control how transactions interact with each other in a single database:

| Isolation Level | Dirty Read | Non-Repeatable Read | Phantom Read | Locking Mechanism |
|----------------|------------|---------------------|--------------|-------------------|
| **Read Uncommitted** | ✓ Allowed | ✓ Allowed | ✓ Allowed | No read locks |
| **Read Committed** (Default) | ❌ Prevented | ✓ Allowed | ✓ Allowed | Short-duration read locks |
| **Repeatable Read** | ❌ Prevented | ❌ Prevented | ✓ Allowed | Locks held until transaction ends |
| **Snapshot** | ❌ Prevented | ❌ Prevented | ❌ Prevented | Row versioning (no locks) |
| **Serializable** | ❌ Prevented | ❌ Prevented | ❌ Prevented | Range locks until transaction ends |

### SQL Server Anomalies Explained

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

## Conceptual Mapping (Not Direct Equivalents)

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

## Detailed Comparison

### Strong Consistency vs Serializable Isolation

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

### Session Consistency vs Read Committed

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

### Eventual Consistency vs Read Uncommitted

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

## Best Use Case Scenarios

### Financial Transaction System

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

### Shopping Cart Application

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

### Social Media Like Counter

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

### Live Sports Score System

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

### Inventory Management System

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

## Key Architectural Differences

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

## When to Use What?

### Use SQL Server Isolation Levels When:

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

### Use Cosmos DB Consistency Levels When:

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

## Performance Comparison

### SQL Server Isolation Level Performance

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

### Cosmos DB Consistency Level Performance

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

## Migration Considerations

### Migrating from SQL Server to Cosmos DB

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

## Summary Table: Practical Scenarios

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

## Additional Resources

- [Azure Cosmos DB Consistency Levels](https://learn.microsoft.com/en-us/azure/cosmos-db/consistency-levels)
- [SQL Server Transaction Isolation Levels](https://learn.microsoft.com/en-us/sql/t-sql/statements/set-transaction-isolation-level-transact-sql)
- [Understanding Isolation Levels](https://learn.microsoft.com/en-us/sql/connect/jdbc/understanding-isolation-levels)
- [Snapshot Isolation in SQL Server](https://learn.microsoft.com/en-us/sql/connect/ado-net/sql/snapshot-isolation-sql-server)
- [Cosmos DB Consistency Levels Overview](cosmosdb_consistency_levels.md)

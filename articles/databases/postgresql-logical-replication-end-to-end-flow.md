---
type: Article
title: "Understanding PostgreSQL Logical Replication: The Complete End-to-End Flow"
description: "Complete guide to PostgreSQL logical replication architecture, including WAL durability, LSN tracking, slot management, and apply worker internals."
timestamp: 2026-08-01T00:00:00Z
---

> **Source**: [Understanding PostgreSQL Logical Replication](https://blog.devgenius.io/understanding-postgresql-logical-replication-the-complete-end-to-end-flow-8081ced8f765) by Nadeem Khan (NK), published 2026-02-14

# Understanding PostgreSQL Logical Replication: The Complete End-to-End Flow

In 2022, I was tasked with building a real-time streaming pipeline between PostgreSQL and Salesforce. My search for a robust Change Data Capture (CDC) solution led me deep into the world of **Logical Replication**.

While many developers treat replication as a “black box” configuration, I quickly learned that operating at scale requires a precise understanding of the underlying internals. Without knowing how the state machine moves, debugging production lag or WAL bloat becomes guesswork.

This post deconstructs the journey of a transaction: from the moment a COMMIT hits the Write-Ahead Log (WAL) to the final acknowledgement from a subscriber. Understanding these mechanics is the prerequisite for our next discussion: how CDC platforms leverage these internals to build highly scalable, fault-tolerant systems.

## WAL Generation and Durability in PostgreSQL

![](https://miro.medium.com/v2/resize:fit:4096/format:webp/0*-ytAnphCPTitF2lO)

How transaction are written to WAL files and Data Files

To understand WAL generation, we need to uncover the database transaction.

### When a Transaction Is Running

- For every data modification (INSERT, UPDATE, DELETE), a corresponding WAL record is generated.
- These WAL records are written into **WAL buffers** in shared memory.
- Modified data pages are stored in **shared buffers** and marked as **dirty pages**.

> *WAL records may be written to disk before commit due to WAL writer activity or buffer pressure, but the durability of a transaction is not guaranteed until the WAL is flushed to at least the LSN of its COMMIT record.*

At this stage:

- Changes are visible in the transaction.
- Neither the WAL nor the data pages are guaranteed durable yet. i.e if the server crashed, the transaction is lost.

### When the Transaction Is Committed

- A COMMIT record is appended to WAL.
- PostgreSQL flushes WAL to disk up to the LSN of the commit record.
- Only after this flush completes is the transaction considered durable.

At this stage:

- Data pages are still only in shared buffers.
- They are not written to disk at commit.
- WAL is the authoritative, durable record of the transaction.

This enforces the **Write-Ahead Logging rule**:

> *WAL must be flushed to disk before any corresponding dirty data page is written.*

### Data Page Flush (Checkpointing)

Dirty pages are written to disk later by:

- Background writer
- Checkpointer
- Or occasionally backend processes

This happens independently of transaction commit. During crash recovery, PostgreSQL replays WAL to bring data files to a consistent state.

### Log Sequence Number (LSN)

Every WAL record is written at a specific **Log Sequence Number (LSN)**.

The LSN:

- Represents a byte offset within the WAL stream.
- Uniquely identifies the position of a change.
- Is used to coordinate durability, replication, and recovery.

## Logical Decoding

![](https://miro.medium.com/v2/resize:fit:4096/format:webp/0*UJghrlRnkb80DKR0)

Logical Decoding flow

Logical Decoding is triggered when a subscriber issues the

```sql
START_REPLICATION SLOT <slot> LOGICAL <lsn>
```

This command causes PostgreSQL to:

1. Spawn a **WALSender** process.
2. Attach it to a **logical replication slot**.
3. Initialise a **Logical Decoding Context**, which includes:
- An XLogReader (WAL reader)
- A ReorderBuffer
- A SnapBuild (snapshot builder)
- An **Output Plugin** (e.g., pgoutput)

Before explaining the execution flow, we need to understand these core components.

### Replication Slot

A logical replication slot is a persistent state stored within a Postgres Cluster. It ensures:

- WAL required for decoding is not recycled.
- Logical decoding resumes from the correct LSN after restart.

It tracks 3 important values:

- **confirmed\_flush\_lsn:** The highest LSN the subscriber has acknowledged as durable.
- **restart\_lsn:** The earliest WAL position still required to safely decode in-progress transactions.
- **catelog\_xmin:** The oldest catelog transaction ID that must be retained to preserve schema visibility for decoding.

Decoding starts from **confirmed\_flush\_lsn**. WAL retention is governed by **restart\_lsn**.

> Every time a consumer starts reading from a logical replication slot, PostgreSQL will begin streaming changes from the LSN requested by the consumer, as long as it is greater than or equal to `restart_lsn`. The slot’s `confirmed_flush_lsn` represents the highest LSN that the consumer has acknowledged as durably processed. PostgreSQL will not remove WAL segments that are required by the slot, and WAL older than `restart_lsn` can be safely recycled.
> 
> In case the primary crashes and restarts, the slot retains its persisted state, including both `restart_lsn` and `confirmed_flush_lsn`. The consumer should resume streaming from its last durable checkpoint, typically aligned with `confirmed_flush_lsn`. The slot’s `confirmed_flush_lsn` only advances when the consumer sends feedback confirming it has flushed or applied changes up to a specific LSN.
> 
> The goal is to build the consumer architecture in a way that minimizes the gap between `restart_lsn` and `confirmed_flush_lsn`. The difference between them represents WAL that must be retained for the slot, and a large gap increases WAL retention pressure on PostgreSQL.

### WALSender Process

The WALSender is a dedicated backend process that drives logical decoding. It:

- Reads WAL records from disk (pg\_wal/) using XLogReader.
- Passes WAL records into the logical decoding machinery.
- Streams decoded transactions to the subscriber.
- Processes subscriber feedback to advance slot state.

The WALSender reads **all WAL records sequentially,** starting from the slot’s confirmed\_flush\_lsn.

### Reorder Buffer

WAL records are physically ordered by LSN, but because many transactions can execute concurrently, records can become interleaved. Below is an example of how WAL records will look across all transactions.

```text
LSN 0/1000  XID 10  INSERT
LSN 0/1010  XID 11  UPDATE
LSN 0/1020  XID 10  UPDATE
LSN 0/1030  XID 10  COMMIT
LSN 0/1040  XID 11  COMMIT
```

A subscriber must receive:

**Transaction 10 → BEGIN, INSERT, UPDATE, COMMIT  
Transaction 11 → BEGIN, UPDATE, COMMIT**

The ReorderBuffer:

- Maintains a hash table keyed by transaction\_id (XID).
- Buffers row-level changes per transaction.
- Stores the transaction’s final\_lsn (the LSN of the COMMIT record).
- Spills large transactions to disk if memory exceeds logical\_decoding\_work\_mem.

Only when the COMMIT record is encountered does the ReorderBuffer release the complete transaction to the output plugin.

### Output Plugin (pgoutput)

The output plugin defines how decoded changes are serialised. For built-in logical replication, the plugin is pgoutput. During transaction replay, the ReorderBuffer invokes the output plugin’s registered callbacks (such as begin\_cb, change\_cb, and commit\_cb). These callbacks allow the plugin to serialise decoded changes into a format suitable for transmission to the subscriber.

Below are the available callbacks that can be registered.

```c
typedef struct OutputPluginCallbacks
{
    LogicalDecodeStartupCB startup_cb;
    LogicalDecodeBeginCB begin_cb;
    LogicalDecodeChangeCB change_cb;
    LogicalDecodeTruncateCB truncate_cb;
    LogicalDecodeCommitCB commit_cb;
    LogicalDecodeMessageCB message_cb;
    LogicalDecodeFilterByOriginCB filter_by_origin_cb;
    LogicalDecodeShutdownCB shutdown_cb;
    LogicalDecodeFilterPrepareCB filter_prepare_cb;
    LogicalDecodeBeginPrepareCB begin_prepare_cb;
    LogicalDecodePrepareCB prepare_cb;
    LogicalDecodeCommitPreparedCB commit_prepared_cb;
    LogicalDecodeRollbackPreparedCB rollback_prepared_cb;
    LogicalDecodeStreamStartCB stream_start_cb;
    LogicalDecodeStreamStopCB stream_stop_cb;
    LogicalDecodeStreamAbortCB stream_abort_cb;
    LogicalDecodeStreamPrepareCB stream_prepare_cb;
    LogicalDecodeStreamCommitCB stream_commit_cb;
    LogicalDecodeStreamChangeCB stream_change_cb;
    LogicalDecodeStreamMessageCB stream_message_cb;
    LogicalDecodeStreamTruncateCB stream_truncate_cb;
} OutputPluginCallbacks;

typedef void (*LogicalOutputPluginInit) (struct OutputPluginCallbacks *cb);
```

## Logical Decoding Execution Flow

Now that we understand the components, the execution flow becomes precise:

1. The WALSender reads WAL records sequentially from the WAL segment files under pg\_wal/ using XLogReader, starting at the slot’s confirmed\_flush\_lsn. It reads durable WAL records in strict LSN order.
2. Each WAL record is passed to LogicalDecodingProcessRecord()
3. If the record represents a row-level change, *it is decoded into a ReorderBufferChange and added to the corresponding ReorderBufferTXN entry keyed by its XID.*
4. If the record is a COMMIT:
- *The ReorderBuffer marks the transaction as committed.*
- *The transaction’s final\_lsn (commit LSN) is recorded.*
- *All buffered changes for that transaction are replayed in WAL order.*
- *The output plugin callbacks (begin\_cb, change\_cb, commit\_cb) are invoked.*
- *The serialised logical transaction is written to the replication stream and sent to the subscriber.*

Logical decoding, therefore, operates at two distinct granularities:

- **Record-by-record** while reading and parsing WAL.
- **Transaction-by-transaction,** when emitting logical changes to the subscriber.

## Publication

Until now, we have seen that logical decoding reconstructs all committed row-level changes and prepares them for transmission via the logical replication protocol.

However, logical replication does not stream everything. It streams only what is defined by the publication.

A publication is a database object whose definition is stored in PostgreSQL system catelog tables, just like tables, indexes, and functions. Its metadata resides in:

- pg\_publication
- pg\_publication\_rel
- pg\_publication\_namespace

Publication defines:

- Which tables are eligible for replication
- Which operations (INSERT, UPDATE, DELETE, TRUNCATE) are replicated
- Optional row-level filters
- Optional column lists

A database node that has a publication is called a Publisher Node.

During the initialisation of a logical replication session, the output plugin (pgoutput) loads the publication metadata into memory. As each committed transaction is decoded, the plugin applies these rules to determine which changes should be serialised and sent to the subscriber.

Replica Identity must be configured for the tables added to the publication for UPDATE and DELETE operations to work properly. Replica Identity is like a rule that defines what makes a row unique; without it, we won’t know what to update or delete. The default value of Replica Identity is the Primary Key. Also, the entire row can be defined as the Replica Identity.

Check out this [official link](https://www.postgresql.org/docs/current/sql-createpublication.html) to see how Publications are created.

## Subscription

A subscription is a database object on the subscriber (receiver) node. Its definition is stored in PostgreSQL system catelog tables and persists across restarts.

A subscription defines:

- The connection details to the primary server
- Which publication(s) to subscribe to
- The replication slot to use
- Apply and synchronization behavior

The core system catelog tables involved are:

- pg\_subscription
- pg\_subscription\_rel

pg\_subscription stores the subscription definition, including connection information and publication list.

pg\_subscription\_rel tracks per-table synchronisation and applies state, including progress during initial data copy and streaming.

Check out [this official link](https://www.postgresql.org/docs/current/sql-createsubscription.html) to learn how to create a subscription.

## Logical Replication for Database Table Replication

![](https://miro.medium.com/v2/resize:fit:4800/format:webp/1*Yw7NjlDLbxIu2tB3FAgL2A.png)

Logical Replication Process

Logical replication is most commonly used to replicate selected tables from one PostgreSQL instance (the **Publisher**) to another (the **Subscriber**). At this point, we have explored WAL durability, decoding, slots, publications, and subscriptions. Now, we connect these components into the full end-to-end flow.

### Step 1: Initial Synchronisation (The Baseline Copy)

When you create a subscription with the default options, PostgreSQL performs an initial table synchronisation to ensure the subscriber starts with data.

```sql
CREATE SUBSCRIPTION mysub CONNECTION 'host=publisher_host dbname=mydb user=repuser' PUBLICATION mypub;
```

During this phase, the subscriber connects to the publisher, and a **consistent snapshot** is taken. Table data is copied using COPY, and a replication slot is created. Because the snapshot is tied to a specific LSN, PostgreSQL guarantees that rows copied during sync are consistent, while any changes committed *after* the snapshot are captured in the WAL for streaming. No rows are missed, and no rows are duplicated.

### Step 2: Streaming Phase

After the snapshot phase completes (or immediately if copy\_data = false), the streaming phase begins. The replication worker on the subscriber opens a connection and issues:

```sql
START_REPLICATION SLOT <slot> LOGICAL <lsn>
```

On the publisher, the **WALSender** starts reading WAL from the slot’s position (confirmed\_flushed\_lsn ), the **ReorderBuffer** reconstructs the transactions, and **pgoutput** serialises the changes filtered by your publication rules.

### Step 3: Apply Worker on the Subscriber

On the subscriber, a dedicated **logical replication apply worker** takes over. It:

- Receives and deserialises logical replication messages.
- Executes equivalent INSERT, UPDATE, and DELETE operations locally.
- Writes changes to the subscriber’s own heap and generates local WAL.

**T** he apply worker uses a **replication origin** to mark these writes. This metadata prevents infinite replication loops in bidirectional setups where the subscriber might also be a publisher.

### Step 4: Feedback Loop

Logical replication is asynchronous by default. To maintain the state machine, the subscriber must inform the publisher of its actions. After applying changes and flushing its local WAL, the subscriber periodically sends a feedback message that includes the highest LSN it has safely flushed.

On the publisher, the replication slot’s confirmed\_flush\_lsn is updated, and the restart\_lsn is recalculated. This closes the durability loop; the primary now knows exactly which changes the subscriber has persisted.

### Step 5: WAL Retention and Recycling

WAL files on the publisher cannot be removed while a replication slot still needs them. This retention is governed by the restart\_lsn.

If the subscriber stops, crashes, or falls significantly behind:

1. The confirmed\_flush\_lsn stops advancing.
2. The restart\_lsn freezes.
3. **WAL accumulates** in the pg\_wal directory.

In production, unmanaged replication lag can lead to disk exhaustion on the primary. Monitoring slot lag is not just a best practice; it is a requirement for system stability.

## End-to-End Flow Summary

Putting it all together, the journey of a single row change looks like this:

1. **User** commits a transaction.
2. **WAL** is flushed to the publisher’s disk.
3. **WALSender** reads the WAL, and **ReorderBuffer** reconstructs the transaction.
4. **Publication** filters the change; **pgoutput** serialises it.
5. **Subscriber Apply Worker** executes the change and flushes its local WAL.
6. **The subscriber** sends a feedback LSN to the publisher.
7. **Publisher** advances the confirmed\_flush\_lsn.
8. **Old WAL segments** finally become recyclable.

## Closing Thoughts

While we have focused on database-to-database replication, the true power of the logical decoding state machine lies in its flexibility. Because we are streaming row-level changes rather than disk blocks, PostgreSQL becomes a first-class citizen in a modern event-driven architecture.

Common production use cases include:

- **Zero-Downtime Upgrades:** Replicating data from an older major version (e.g., PG 12) to a newer one (e.g., PG 17).
- **Data Aggregation:** Consolidating specific tables from multiple regional shards into a single reporting warehouse.
- **Change Data Capture (CDC):** Streaming database events into message brokers like Kafka or RabbitMQ to trigger downstream microservices.

In our next post, we will dive deep into the **CDC pattern**, exploring how tools like Debezium leverage the logical replication slot to turn your database into a real-time event source.

Happy Learning.

Follow me on [LinkedIn](https://www.linkedin.com/in/nadeem-khan-75135210a/) and [Medium](https://codewithnk.com/) for more such content.
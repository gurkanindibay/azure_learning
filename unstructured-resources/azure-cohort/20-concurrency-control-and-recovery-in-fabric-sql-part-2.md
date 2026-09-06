---
type: Unstructured Note
title: "Concurrency Control And Recovery In Fabric Sql Part 2"
description: "Summary"
tags: [notes, azure]
generated: { by: process:okf-migrate, at: 2026-08-22T00:00:00Z }
---

Summary

**Key Topics:**

- **Fabric Transactions Lecture:** The meeting continued with Part 2 of the fabric transactions lecture, focusing on write-write conflict detection and snapshot isolation. The discussion included an example of how transactions are managed and validated in a distributed system. **3:08**

- **Conflict Detection Mechanism:** The participants reviewed the conflict detection mechanism, explaining how SQL Server detects conflicts during transaction commits by using a versioned table in tempdb. They discussed the process of handling parallel transactions and the role of the write-write conflicts table. **3:57**

- **Live Demo of Conflict Detection:** A live demo was conducted to illustrate the concepts discussed. The demo involved creating and manipulating tables, demonstrating how schema modification locks and transaction commits work in practice. The demo also highlighted the importance of handling write-write conflicts and the impact of parallel transactions. **16:58**

- **Compaction and Checkpointing:** The meeting covered the concepts of data compaction and checkpointing, explaining how these processes help maintain storage quality and efficiency. The participants discussed the creation of new manifest files and the role of checkpoints in optimizing the log sequence. **37:39**

- **Garbage Collection:** The participants discussed the need for garbage collection in the system, highlighting the various reasons why garbage is generated and the importance of cleaning up old versions of files. They explained the process of garbage collection and its impact on system performance. **1:03:50**

- **Table and Database Cloning:** The meeting included a discussion on table and database cloning, explaining how logical metadata is copied to create new tables with independent futures. The participants also talked about the challenges of garbage collection in the context of cloned tables. **1:07:16**

- **Time Travel Queries:** The concept of time travel queries was introduced, allowing users to query the state of a table at a specific moment in the past. The participants discussed the implementation of time travel queries and their use cases, such as comparing current data with historical data. **1:32:56**

- **System Upgrades and Recovery:** The participants addressed the process of system upgrades and recovery, emphasizing the importance of maintaining data integrity during upgrades. They explained how SQL Server's recovery mechanism ensures that transactions are correctly rolled back or committed during system restarts. **1:49:18**


## Fabric Transactions Lecture

### Fabric Transactions Lecture Details:

- **Write-Write Conflict Detection:** The lecture focused on how SQL Server detects write-write conflicts during transaction commits. The mechanism involves using a versioned table in tempdb to track updates and deletes. When a transaction attempts to commit, SQL Server checks if another transaction has already modified the same row. If a conflict is detected, an error is thrown, and the transaction is rolled back. **3:57**

- **Snapshot Isolation:** The concept of snapshot isolation was discussed, where transactions operate on a consistent snapshot of the database. This approach allows transactions to run in parallel without locking, but conflicts are detected at commit time. The lecture explained how snapshot isolation helps in maintaining data consistency while improving performance. **3:26**

- **Example of Conflict Detection:** An example was provided to illustrate the conflict detection process. Two transactions, X2 and X3, were shown to be running in parallel, both attempting to delete the same row. The lecture explained how SQL Server detects the conflict and ensures that only one transaction can commit, while the other is rolled back. **5:41**

- **Live Demo:** A live demo was conducted to demonstrate the concepts discussed. The demo involved creating a new table, cloning an existing table, and performing updates and deletes. The demo highlighted how schema modification locks work and how transactions are validated and committed. The demo also showed the impact of write-write conflicts and how they are handled in practice. **16:58**

- **Handling Parallel Transactions:** The lecture emphasized the importance of allowing transactions to run in parallel to improve performance. It explained how SQL Server uses optimistic concurrency control to let transactions proceed without locking, but detects conflicts at commit time to ensure data consistency. **3:42**

- **Validation and Commit Process:** The process of validating and committing transactions was detailed. When a transaction attempts to commit, SQL Server checks the write-write conflicts table to see if any other transaction has modified the same row. If no conflict is detected, the transaction is committed; otherwise, it is rolled back. **6:00**

These points provide a comprehensive overview of the key aspects of the Fabric Transactions Lecture discussed during the meeting.

</RESPONSE>


## Conflict Detection Mechanism

### Conflict Detection Mechanism Details:

- **Overview:** The conflict detection mechanism in SQL Server is designed to handle write-write conflicts during transaction commits. This mechanism ensures data consistency by detecting when two transactions attempt to modify the same row simultaneously.

- **Versioned Table in tempdb:** SQL Server uses a versioned table in tempdb to track updates and deletes. When a transaction performs an update or delete, it records this action in the versioned table. **3:57**

- **Commit Time Check:** At commit time, SQL Server checks the versioned table to determine if another transaction has already modified the same row. This check is crucial for detecting conflicts. **4:06**

- **Write-Write Conflicts Table:** The write-write conflicts table plays a central role in conflict detection. When a transaction attempts to commit, SQL Server tries to insert or update a row in this table. If the write succeeds, no conflict has occurred. If the write fails, it indicates that another transaction has already committed changes to the same row, resulting in a conflict. **4:19**

- **Error Handling:** When a conflict is detected, SQL Server throws an appropriate error, and the transaction is rolled back. This ensures that only one transaction can commit changes to a particular row, maintaining data consistency. **4:26**

- **Example Scenario:** An example was provided where two transactions, X2 and X3, run in parallel and attempt to delete the same row. SQL Server detects the conflict at commit time by checking the write-write conflicts table. Since X2 commits first, X3 encounters a conflict and is rolled back. **5:41**

- **Optimistic Concurrency Control:** The mechanism relies on optimistic concurrency control, allowing transactions to proceed without locking. Conflicts are detected at commit time, which helps improve performance by reducing the need for locks during transaction execution. **3:42**

These details provide a comprehensive understanding of the conflict detection mechanism discussed during the meeting.


## Live Demo of Conflict Detection: 

### Live Demo of Conflict Detection Details:

- **Setup:** The live demo involved creating a new table by cloning an existing customer table from the tpch schema. The cloned table was named "furniture customers," and the demo focused on manipulating rows related to the "furniture" market segment. **20:00**

- **Transaction Creation:** The demo started with a transaction that cloned the customer table and then deleted all rows from the cloned table where the market segment was not "furniture." This operation was performed within a single transaction to demonstrate the impact of schema modification locks. **20:16**

- **Parallel Session:** A parallel session was initiated to query the cloned table while the first transaction was still in progress. This session was expected to hang because the schema modification lock held by the first transaction prevented the second session from acquiring a schema stability lock. **23:54**

- **Commit and Rollback:** The first transaction was committed, allowing the parallel session to proceed and verify the changes. The demo also included a scenario where the first transaction was rolled back, demonstrating how the parallel session would then encounter an "invalid object name" error due to the table not existing. **24:36**

- **Update Operations:** The demo further included updating the market segment of the "furniture customers" table to "wood furniture" within a transaction. This was followed by a parallel update to "metal furniture" outside of a transaction. The demo showcased how the in-doubt transaction still saw "wood furniture," while the committed transaction saw "metal furniture." **27:52**

- **Conflict Detection:** The key part of the demo was when the in-doubt transaction attempted to commit its changes to "wood furniture" after the parallel update to "metal furniture" had already committed. This resulted in a write-write conflict, and SQL Server threw an error indicating a snapshot isolation transaction aborted due to an update conflict. **28:56**

- **Retry Mechanism:** The demo concluded by retrying the transaction, which succeeded this time as there were no parallel updates causing conflicts. This highlighted the importance of handling write-write conflicts and the need for retry mechanisms in applications. **30:45**

These points provide a detailed overview of the live demo conducted during the meeting, illustrating the conflict detection mechanism in action.


## Compaction and Checkpointing

### Compaction and Checkpointing Details:

- **Compaction:**

- **Purpose:** Compaction is used to improve storage quality by reading poorly laid out data and rewriting it in a better form. This process helps manage trickle inserts and large deletions that can degrade storage quality over time. **37:39**

- **Process:** During compaction, the system reads a set of files, marks them as removed in the log, and writes new files that represent the same data in a more optimized layout. The net data change is zero, but the storage layout is improved. **38:13**

- **Conflict Detection:** Compaction participates in write-write conflict detection. If a compaction process and a user update run in parallel and affect the same data, a conflict is detected, and the compaction may be rolled back. **43:12**

- **Commit:** Once compaction is validated and no conflicts are detected, it commits the new files and marks the old files for removal. **43:23**

- **Checkpointing:**

- **Purpose:** Checkpointing is used to create a more efficient representation of the log sequence by summarizing the net effect of a series of manifests. This reduces the number of small JSON files that need to be read, improving performance. **39:09**

- **Process:** A checkpoint file is created by reading the entire sequence of manifests, compressing out any add and remove pairs, and writing the resulting state into a single file. This file represents the current state of the table as of the last manifest in the sequence. **39:58**

- **Efficiency:** Checkpoints are more efficient to read than a long sequence of individual manifests. They contain the net effect of all changes up to a certain point, making it faster to reconstruct the current state of the table. **44:37**

- **Garbage Collection:** Checkpoints also aid in garbage collection by allowing the system to truncate the log sequence and remove old manifests and data files that are no longer needed. This is done once the retention period has elapsed, ensuring that files are only deleted when it is safe to do so. **49:20**

- **Example Scenario:**

- **Compaction:** In the example provided, a compaction process reads a file (e.g., 1.parquet) and its associated delete bitmap, rewrites the data into a new file (e.g., 4.parquet), and marks the old files as removed. This new file contains only the valid rows, improving storage efficiency. **42:05**

- **Checkpointing:** A checkpoint file (e.g., S0.parquet) is created to represent the state of the table after a series of manifests. This file includes only the active data files and excludes any files that have been removed, making it a more efficient way to read the table's state. **43:50**

These details provide a comprehensive understanding of the compaction and checkpointing processes discussed during the meeting.


## Garbage Collection: 

### Garbage Collection Details:

- **Purpose:** Garbage collection is essential for cleaning up files and storage that are no longer needed due to various operations such as aborted transactions, retries, storage optimizations, and table or database drops. **1:03:54**

- **Triggers for Garbage Collection:**

- **Aborted Transactions:** Files generated by transactions that were aborted need to be cleaned up. **1:04:03**

- **Retries:** When a back-end DML task is retried, the previous version's files must be removed. **1:04:09**

- **Storage Optimizations:** Operations like compaction create new versions of files and mark old versions as removed, necessitating cleanup. **1:04:23**

- **Drop and Truncate Operations:** Dropping or truncating tables and databases generates files that need to be deleted. **1:04:35**

- **Process:**

- **System Task:** Garbage collection runs as a system task, which is aware of both successful and failed operations, retention policies, and clone references. **1:05:12**

- **Retention Awareness:** The system must consider retention periods to ensure that files are not deleted prematurely. For example, files are kept for 30 days by default to support time travel queries and backups. **46:43**

- **Clone Awareness:** The system tracks references to files created by table and database clones to ensure that shared files are not deleted while still in use. **1:06:09**

- **Complexity:**

- **Reference Counting:** The system uses reference counting to track how many tables or clones reference a particular file. Only when all references are removed, and the retention period has elapsed, can the file be safely deleted. **1:06:28**

- **Clone Islands:** The concept of Clone Islands is used to group tables that are related by cloning. Garbage collection processes these groups to ensure that shared files are managed correctly. **1:31:44**

- **Example Scenario:**

- **Table Drop:** When a table is dropped, the logical metadata is removed, but the manifest sequence is retained for the retention period. This ensures that if the database is restored to a point before the drop, the files are still available. **1:27:39**

- **Checkpointing:** Checkpoints help in garbage collection by summarizing the log sequence, allowing the system to truncate old manifests and data files that are no longer needed. **49:20**

These points provide a detailed overview of the garbage collection process discussed during the meeting, highlighting its importance, triggers, and complexity.


## Table and Database Cloning

### Table and Database Cloning Details:

- **Table Cloning:**

- **Purpose:** Table cloning creates a new table that starts with the same data as the original table but can evolve independently. This is useful for scenarios like testing, data analysis, or creating backups. **1:08:12**

- **Process:**

- **Logical Metadata Copy:** The logical metadata of the original table is copied to the new table. **1:07:25**

- **Manifest Sequence:** The names of the manifest files and their sequence are copied to the new table. The actual data files and deletion vectors are shared between the original and cloned tables. **1:07:32**

- **Independent Evolution:** After cloning, any changes to the original or cloned table do not affect the other. Each table can have its own schema changes, compactions, and data modifications. **1:08:45**

- **Example:** If a table T1 is cloned to T2, T2 starts with the same data as T1. Any subsequent inserts, updates, or schema changes to T2 do not affect T1. **1:22:55**

- **Database Cloning:**

- **Purpose:** Database cloning creates a new database that starts with the same state as the original database. This is useful for scenarios like testing, development, or creating backups. **1:09:14**

- **Process:**

- **Backup and Restore:** The cloning process is similar to a backup and restore operation. The metadata of the original database is backed up and restored with a new name. **1:09:24**

- **File References:** The new database references the same data files as the original database. Any new files created in the cloned database are stored in the context of the new database. **1:09:41**

- **Cross-Workspace Cloning:** This mechanism works both within the same workspace and across different workspaces. **1:09:56**

- **Example:** If a database DB1 is cloned to DB2, DB2 starts with the same state as DB1. Any subsequent changes to DB2 do not affect DB1.

- **Garbage Collection Considerations:**

- **Reference Tracking:** The system tracks references to files created by clones to ensure that shared files are not deleted while still in use. **1:06:09**

- **Clone Islands:** Clone Islands group tables related by cloning, and garbage collection processes these groups to manage shared files correctly. **1:31:44**

These details provide a comprehensive understanding of the table and database cloning processes discussed during the meeting, highlighting their purpose, process, and implications for storage and garbage collection.


## Time Travel Queries: 

### Time Travel Queries Details:

- **Purpose:** Time travel queries allow users to query the state of a table as it existed at a specific point in the past. This is useful for auditing, historical analysis, and recovering previous data states. **1:32:56**

- **Mechanism:**

- **Snapshot Isolation:** Time travel queries leverage the snapshot isolation mechanism, which maintains a read-only snapshot of the manifest sequence at the specified timestamp. **1:33:03**

- **Prefix Calculation:** The system calculates the prefix of the manifest sequence based on the provided timestamp, ensuring that the query reads the correct historical state of the table. **1:33:10**

- **Per-Table Consistency:** Each table's state is transactionally consistent at the specified timestamp. However, there is no guarantee of multi-table transactional consistency for the same timestamp. **1:34:28**

- **Usage:**

- **Query Syntax:** Users can specify a timestamp in their queries to retrieve the state of the table at that time. For example, `SELECT * FROM table AS OF TIMESTAMP 'YYYY-MM-DD HH:MM:SS'`. **1:33:10**

- **Clone and Backup:** Time travel can also be used in conjunction with table cloning and backup/restore operations. Users can create a clone of a table as it existed at a specific timestamp or restore a database to a previous state. **1:35:36**

- **Limitations:**

- **Schema Changes:** If an `ALTER TABLE` operation has occurred, time travel through that DDL change requires versioned logical metadata, which is not currently supported. **1:35:02**

- **Retention Policy:** The ability to time travel is subject to the retention policy, which typically keeps data for 30 days. After this period, the data may no longer be available for time travel queries. **46:43**

- **Example Scenarios:**

- **New Customers:** A user can create a clone of the customer table as of yesterday and compare it with the current state to identify new customers added in the last day. **1:36:04**

- **Historical Analysis:** Users can run queries to analyze the state of the data at various points in time, helping with trend analysis and historical reporting. **1:32:56**

These points provide a detailed overview of the time travel query functionality discussed during the meeting, highlighting its purpose, mechanism, usage, limitations, and example scenarios.


## System Upgrades and Recovery

### System Upgrades and Recovery Details:

- **System Upgrades:**

- **Frequency:** System upgrades, including code changes, are rolled out at least once a week. **1:50:02**

- **Handling Active Transactions:**

- **Graceful Shutdown:** Ideally, the system would stop accepting new requests and wait for active transactions to complete before shutting down. However, the platform often controls the shutdown process, which may not always be graceful. **1:49:38**

- **Recovery Mechanism:** Regardless of how the shutdown occurs (graceful or abrupt), SQL Server's recovery mechanism ensures that the system can recover to a consistent state. Active transactions are either rolled back during shutdown or during the subsequent startup and recovery process. **1:51:00**

- **Recovery:**

- **Standard SQL Recovery:**

- **Process:** The recovery process involves analyzing the log, redoing committed transactions, and undoing uncommitted transactions. This ensures the database is in a consistent state after a crash or shutdown. **1:10:54**

- **Strength:** SQL Server's recovery mechanism is robust and ensures data integrity and consistency without requiring backend involvement. **1:11:30**

- **File Integrity:**

- **Azure Storage:** The system relies on Azure Storage to maintain the integrity and availability of data files. These files are immutable once written, and Azure Storage handles replication and disaster recovery. **1:13:55**

- **Soft Delete:** Azure Storage's soft delete feature provides an additional safeguard, allowing files to be undeleted within a seven-day window if mistakenly deleted. **1:15:27**

- **Backup and Restore:**

- **Database Backups:** Regular backups of the database's MDF and LDF files are taken, typically every four to eight hours. These backups are stored as immutable files in OneLake. **1:18:24**

- **Restoration:** In the event of corruption or data loss, the system can restore the database from these backups, minimizing data loss to a few hours at most. **1:19:02**

These details provide a comprehensive understanding of the system upgrades and recovery processes discussed during the meeting, highlighting their frequency, handling of active transactions, recovery mechanisms, file integrity measures, and backup and restore procedures.


## Questions

### Questions and Answers Covering All Topics in the Session:

1. **Q:** What is the primary purpose of snapshot isolation in database transactions?

**A:** Snapshot isolation allows transactions to work in parallel by maintaining a consistent view of the data as it existed at the start of the transaction, detecting conflicts at commit time. **3:26**

2. **Q:** How does the system detect write-write conflicts in snapshot isolation?

**A:** The system detects write-write conflicts by attempting to insert or update a row in a versioned table in tempdb at commit time. If the write fails, it indicates a conflict. **4:26**

3. **Q:** What happens to the data files when a transaction is rolled back?

**A:** When a transaction is rolled back, any new files created during the transaction are marked for garbage collection, and the system tables are rolled back to their previous state. **9:07**

4. **Q:** How does the system handle concurrent updates to the same row in snapshot isolation?

**A:** Concurrent updates to the same row result in a write-write conflict, causing one of the transactions to fail and roll back. **7:58**

5. **Q:** What is the purpose of the compaction process in the system?

**A:** Compaction improves storage quality by reading poorly laid out data and rewriting it in a better form, creating new files and marking old ones as removed. **37:39**

6. **Q:** How does the system create a checkpoint file, and what is its purpose?

**A:** A checkpoint file is created by computing the net effect of a sequence of manifests, resulting in a single file that represents the current state of the table, making it more efficient to read. **39:58**

7. **Q:** What is the retention policy for data files in the system?

**A:** The retention policy typically keeps data files for 30 days, allowing time travel queries and backups to access historical data within this period. **46:43**

8. **Q:** How does the system handle garbage collection for dropped tables?

**A:** The system retains the manifest sequence for dropped tables until the retention period elapses, ensuring that files are not prematurely deleted and can be restored if needed. **1:28:29**

9. **Q:** What is the purpose of table cloning in the system?

**A:** Table cloning creates a new table with the same metadata and data as the original table, allowing independent evolution of the tables while sharing the same initial data files. **1:08:12**

10. **Q:** How does the system ensure data consistency during a database restore?

**A:** During a database restore, the system uses the backup of the MDF and LDF files to restore the database to a consistent state, ensuring that all transactions are correctly applied or rolled back. **1:18:24**

11. **Q:** What is the role of Azure Storage in the system's data management?

**A:** Azure Storage provides high availability, disaster recovery, and data integrity for the system's data files, leveraging replication and soft delete features. **1:13:55**

12. **Q:** How does the system handle schema changes in time travel queries?

**A:** Time travel through schema changes requires versioned logical metadata, which is not currently supported, limiting the ability to query past states if the schema has changed. **1:35:02**

13. **Q:** What is the impact of compaction on concurrent user transactions?

**A:** Compaction can cause write-write conflicts with concurrent user transactions, requiring users to retry their transactions if a conflict occurs. **52:27**

14. **Q:** How does the system publish metadata to make tables available to other fabric applications?

**A:** The system publishes metadata by copying manifests to a delta log folder in a publicly visible tables folder, allowing other fabric applications to read the data without copying it. **54:41**

15. **Q:** What is the significance of the checkpoint file in garbage collection?

**A:** The checkpoint file helps in garbage collection by providing a compact representation of the manifest sequence, allowing the system to safely delete old manifests and data files. **1:29:59**

16. **Q:** How does the system handle upgrades and active transactions?

**A:** During upgrades, the system may shut down gracefully or abruptly. Active transactions are either rolled back during shutdown or during the subsequent startup and recovery process. **1:51:00**

17. **Q:** What is the role of the manifest table in the system?

**A:** The manifest table tracks the sequence of manifests for each table, ensuring that the system can correctly manage data files and handle operations like compaction and garbage collection. **1:21:33**

18. **Q:** How does the system ensure data integrity during a violent shutdown?

**A:** The system relies on SQL Server's recovery mechanism to ensure data integrity. During startup, the system analyzes the log, redoes committed transactions, and undoes uncommitted transactions to restore a consistent state. **1:51:00**

19. **Q:** What is the purpose of the logical metadata in the system?

**A:** Logical metadata tracks the schema and structure of tables, allowing the system to manage operations like cloning, compaction, and garbage collection while ensuring data consistency and integrity. **1:21:33**

20. **Q:** How does the system handle file corruption in Azure Storage?

**A:** The system relies on Azure Storage's standard mechanisms for recovering from file corruption, including replication and soft delete features, to ensure data availability and integrity. **1:16:06**

These questions and answers cover the key topics discussed in the session, providing a comprehensive overview of the system's functionality, processes, and mechanisms.


## Scenario based questions

### Scenario-Based Questions and Answers:

1. **Q:** A user attempts to update a row in a table while another transaction is concurrently trying to delete the same row. What will happen, and how will the system handle this?

**A:** The system will detect a write-write conflict at commit time. The transaction that attempts to commit second will fail, and an error will be thrown, indicating the conflict. The failed transaction will then roll back. **7:58**

2. **Q:** During a database restore, you need to ensure that all data files are intact and consistent. How does the system achieve this?

**A:** The system uses backups of the MDF and LDF files to restore the database to a consistent state. SQL Server's recovery mechanism redoes committed transactions and undoes uncommitted transactions to ensure data integrity. **1:18:24**

3. **Q:** A user wants to create a new table that starts with the same data as an existing table but evolves independently. How can this be achieved?

**A:** The user can use the table cloning feature, which copies the logical metadata and the names of the manifest files to a new table. The new table will share the initial data files but can evolve independently. **1:08:12**

4. **Q:** You need to improve the storage quality of a table that has undergone many small updates and deletions. What process will you use, and what does it involve?

**A:** The compaction process should be used. It reads the poorly laid out data and rewrites it in a better form, creating new files and marking the old ones as removed. This improves storage quality and efficiency. **37:39**

5. **Q:** A user wants to query the state of a table as it existed a week ago. How can this be done, and what are the limitations?

**A:** The user can perform a time travel query by specifying a timestamp from a week ago. The system will read the prefix of the manifest sequence up to that timestamp. However, if there have been schema changes, time travel through DDL is not supported without versioned logical metadata. **1:35:02**

6. **Q:** A table has been dropped, but you need to ensure that its data files are not prematurely deleted. How does the system handle this?

**A:** The system retains the manifest sequence for the dropped table until the retention period elapses. This ensures that files are not prematurely deleted and can be restored if needed. **1:28:29**

7. **Q:** You need to make a table's data available to other fabric applications without copying the data. How is this achieved?

**A:** The system publishes metadata by copying manifests to a delta log folder in a publicly visible tables folder. Other fabric applications can read the data directly from this location using the delta log format. **54:41**

8. **Q:** A user transaction is running concurrently with a system compaction task. What potential issue might arise, and how should it be handled?

**A:** A write-write conflict might arise if the user transaction and the compaction task try to modify the same data. The user transaction will need to be retried if it fails due to this conflict. **52:27**

9. **Q:** You need to ensure that old manifest files are deleted after a checkpoint is created. What is the current system behavior, and what improvements are planned?

**A:** Currently, old manifest files are not automatically deleted after a checkpoint is created. However, there is a planned feature to delete these files once they are no longer needed for retention or time travel purposes. **1:48:44**

10. **Q:** A user wants to update a table's data, but the system is about to undergo an upgrade. How will the system handle active transactions during the upgrade?

**A:** The system will either roll back active transactions during a graceful shutdown or handle them during the subsequent startup and recovery process. SQL Server's recovery mechanism ensures data integrity regardless of the shutdown method. **1:51:00**

These scenario-based questions and answers cover various aspects of the system's functionality, providing practical insights into how different processes and features are handled.


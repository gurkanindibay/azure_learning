---
type: Unstructured Note
title: "Concurrency Control And Recovery In Fabric Sql Part 1"
description: "Summary"
tags: [notes, azure]
generated: { by: process:okf-migrate, at: 2026-08-22T00:00:00Z }
---

Summary

**Key Topics:**

- **Introduction to Polaris and Fabric Data Warehouse:** MPR introduced the session by discussing Polaris and the Fabric Data Warehouse, focusing on how transactions are handled using modern concepts like log-structured tables and lake tables. They emphasized the goal of creating a cloud-native production warehouse. **5:16**

- **Design Principles for Fabric DW:** MPR outlined the design principles for Fabric DW, emphasizing that backends have no state, state changes must be communicated through new files in storage, and backends cannot directly communicate with the front end. These principles ensure scalability and reliability. **12:58**

- **Types of Data Managed in Fabric DW:** MPR explained the types of data managed in Fabric DW, including logical metadata, physical metadata, and data files. They highlighted the use of Parquet files for data storage and deletion vectors for managing row validity. **17:48**

- **Architecture of Fabric DW:** MPR provided an architecture diagram showing how different components of Fabric DW fit together, including the SQL Server front end, distributed cloud processor (DCP), backends, and storage. They explained the flow of information and the role of manifest files in maintaining transactional consistency. **24:22**

- **Concurrency Control in Fabric DW:** MPR discussed the mixed concurrency control model used in Fabric DW, with optimistic concurrency for data and physical metadata access and pessimistic concurrency for logical metadata. They explained the importance of immutability of data files and the use of schema-related locks for logical metadata. **36:08**

- **Write-Write Conflict Detection:** MPR addressed the mechanism for detecting write-write conflicts in Fabric DW, explaining that table-level conflict detection is currently used. They described the process of writing transaction IDs to a conflict table in tempdb during commit to detect conflicts and ensure transactional consistency. **1:46:35**

- **System Tasks and Storage Optimization:** MPR highlighted the importance of system tasks for storage optimization in Fabric DW, including garbage collection and data compaction. They emphasized that these tasks are the responsibility of the solution provider to ensure efficient and clean storage over time. **1:27:27**

- **Comparison with Row-Oriented Systems:** MPR compared the process of handling transactions in Fabric DW with traditional row-oriented systems, illustrating the differences in data organization, metadata management, and the use of manifest files and Parquet files. **1:31:57**

- **Future Work and Next Steps:** MPR concluded the session by mentioning future work and next steps, including a continuation of the discussion in the next session. They indicated that more details about background tasks, a demo, and future plans would be covered. **2:02:01**


## Introduction to Polaris and Fabric Data Warehouse

**Introduction to Polaris and Fabric Data Warehouse:**

- **Overview:** MPR began by discussing the integration of Polaris with the Fabric Data Warehouse, focusing on how transactions are managed using modern concepts like log-structured tables and lake tables. The goal is to create a cloud-native production warehouse that leverages these advanced data management techniques. **5:16**

- **Polaris Architecture:** MPR explained that Polaris is designed to provide a shared storage architecture where all state management pieces within the back end are removed. This architecture allows for dynamic allocation of backends based on resource demand, with all state managed centrally at the front end. **10:41**

- **Transaction Management:** The session covered how transactions are handled in this architecture, emphasizing the use of log-structured tables or lake tables. These tables are adapted in combination with Polaris to create a scalable and efficient data warehouse solution. **5:16**

- **Design Principles:** MPR outlined key design principles, such as ensuring that backends have no state, communicating state changes through new files in storage, and preventing direct communication between backends and the front end. These principles are crucial for achieving scalability and reliability in the system. **12:58**

- **SIGMOD Paper:** MPR mentioned that the work on Polaris and the Fabric Data Warehouse has been published in a SIGMOD paper, highlighting the academic and practical significance of their approach. **6:05**

- **Historical Context:** The lecture has evolved since the first year of Azure Data University, reflecting the continuous development and refinement of the Polaris and Fabric Data Warehouse integration. **6:12**

This introduction set the stage for a detailed discussion on the architecture, design principles, and transaction management strategies employed in the Fabric Data Warehouse.

</RESPONSE>


## Design Principles for Fabric DW

**Design Principles for Fabric DW:**

- **No State in Backends:** One of the fundamental principles is that backends do not manage any state. This means that any state changes cannot be made directly by the backends, ensuring that the system remains scalable and resilient. **12:58**

- **State Communication Through Storage:** Any state changes must be communicated through new files in storage. This principle ensures that all changes are durable and can be managed centrally, avoiding the need for backends to maintain state information. **13:13**

- **Execution Task Definition:** Backends only receive the information they need as part of the execution task definition. If a backend does not receive specific state information, it cannot assume its existence. This ensures that backends operate with the most current and relevant data. **13:13**

- **Durability of State Changes:** For any state change to be recognized in the future, it must be communicated through new files that are flushed and made durable in storage. This principle ensures that all changes are persistent and can be reliably managed. **14:20**

- **Communication Path Through DCP:** Backends cannot directly communicate with the front end. All communication must go through the Distributed Cloud Processor (DCP), which coordinates the topology, scheduling, and execution of tasks. This design supports scalability and ensures that the system can handle large-scale data processing efficiently. **16:01**

- **Scalability:** By adhering to these principles, the system can scale to handle any size of data problem. The architecture is designed to support large-scale data processing and ensure that the system remains efficient and reliable. **16:38**

These design principles are critical for ensuring that the Fabric Data Warehouse is scalable, resilient, and capable of handling large-scale data processing tasks efficiently.

</RESPONSE>


## Types of Data Managed in Fabric DW

**Types of Data Managed in Fabric DW:**

- **Logical Metadata:** This includes the definition of tables, such as their names, columns, column types, and statistics. Logical metadata provides a high-level description of the data structure without containing the data itself. **17:11**

- **Physical Metadata:** This describes the state of the data stored in the tables at any given moment. It includes information on how to locate the data but does not contain the data itself. **17:37**

- **Data Files:** The actual data is stored in Parquet files, a columnar storage format that is widely used for its efficiency in handling large-scale data analytics. **18:07**

- **Deletion Vectors:** These are used to manage deletions within Parquet files. A deletion vector is essentially a bitmap that indicates which rows in a Parquet file are still valid. This allows the system to maintain immutability of Parquet files while managing deletions separately. **20:00**

- **Metadata-Only Table Clones:** This feature allows for the creation of new tables that share the same schema and data as an existing table without physically copying the data files. This is useful for scenarios where multiple references to the same data are needed, and it helps in managing storage efficiently. **21:01**

- **Storage Locations:** Physical metadata, data files, and deletion vectors are stored in Azure Storage, abstracted by One Lake. Logical metadata and clone information are stored in a SQL Server database file (MDF and LDF). This separation ensures that each type of data is managed in the most appropriate storage medium for its characteristics. **22:17**

These types of data are managed to ensure efficient storage, retrieval, and processing within the Fabric Data Warehouse, leveraging both cloud storage and traditional database systems.

</RESPONSE>


## Architecture of Fabric 

**Architecture of Fabric DW:**

- **Front End:** The front end consists of a SQL Server instance that manages logical metadata and user transactions. It is responsible for creating and managing manifest files, which track changes to the data. **24:27**

- **Distributed Cloud Processor (DCP):** The DCP coordinates the execution of tasks across multiple backends. It schedules tasks, distributes execution plans, and collects results from the backends. The DCP ensures that the system can scale dynamically based on resource demands. **24:40**

- **Backends:** Backends are responsible for executing tasks assigned by the DCP. They handle data processing, create new data files, and update manifest files. Backends do not manage any state, ensuring that they can be dynamically allocated and deallocated as needed. **25:03**

- **Storage:** Data files, physical metadata, and deletion vectors are stored in Azure Storage, abstracted by One Lake. This provides a scalable and durable storage solution. Logical metadata and clone information are stored in a SQL Server database file (MDF and LDF). **25:24**

- **Manifest Files:** Manifest files are used to track changes to the data. Each transaction that modifies a table creates a new manifest file, which records the changes made. These files are stored in a log sequence and can be checkpointed for efficiency. **25:52**

- **Transaction Management:** Transactions are managed centrally at the front end. The front end creates and manages manifest files, and commits are recorded by updating the manifest sequence in the SQL Server database. This approach simplifies transaction management and ensures consistency. **27:55**

- **Concurrency Control:** The system uses a mixed concurrency control model. Logical metadata changes are managed pessimistically using locks, while data and physical metadata changes are managed optimistically. This allows for efficient parallel processing while ensuring consistency. **36:40**

- **Communication Path:** All communication between the front end and backends goes through the DCP. This ensures that the system can scale efficiently and that backends do not need to manage state or communicate directly with the front end. **16:01**

This architecture ensures that Fabric DW is scalable, resilient, and capable of handling large-scale data processing tasks efficiently.

</RESPONSE>


## Concurrency Control in Fabric DW

**Concurrency Control in Fabric DW:**

- **Mixed Concurrency Control Model:** Fabric DW uses a mixed concurrency control model, which combines optimistic concurrency control for data and physical metadata access with pessimistic concurrency control for logical metadata. **36:40**

- **Optimistic Concurrency Control:** For data and physical metadata, the system allows multiple transactions to proceed in parallel without locking resources. Changes are made by creating new files rather than modifying existing ones, ensuring that reads can occur without coordination. Conflicts are detected at commit time, and transactions that conflict are aborted. **36:58**

- **Pessimistic Concurrency Control:** For logical metadata, which includes table definitions and schema changes, the system uses locks to ensure consistency. Schema stability locks are taken for read operations, and schema modification locks are taken for write operations. This ensures that only one transaction can modify the schema at a time, preventing conflicts. **36:51**

- **Snapshot Isolation:** User transactions are automatically converted to snapshot isolation level, which provides a consistent view of the data as it was at the start of the transaction. This isolation level allows for repeatable reads within a transaction and helps manage concurrency without locking data resources. **1:16:32**

- **Write-Write Conflict Detection:** The system detects write-write conflicts at the table level. When a transaction attempts to commit, it checks for conflicts by writing to a special table in tempdb. If another transaction has already modified the same table, the commit will fail, and the transaction will be aborted. This ensures that only one transaction can modify a table at a time. **1:46:50**

- **Logical Metadata Versioning:** Currently, logical metadata is not versioned, so schema changes require locks to ensure consistency. However, SQL Server is building versioning for logical metadata, which will allow for non-blocking reads and writes in the future. **41:05**

- **Garbage Collection:** The system includes tasks for garbage collection to clean up unused files and deletion vectors. This ensures that storage remains efficient and that old versions of data do not accumulate unnecessarily. **1:42:37**

This concurrency control model ensures that Fabric DW can handle high levels of parallelism and large-scale data processing while maintaining consistency and efficiency.

</RESPONSE>


## Write-Write Conflict Detection

**Write-Write Conflict Detection in Fabric DW:**

- **Optimistic Approach:** Fabric DW uses an optimistic concurrency control approach for data and physical metadata. This means that multiple transactions can proceed in parallel without locking resources. Conflicts are detected at commit time rather than during transaction execution. **36:58**

- **Table-Level Conflict Detection:** Currently, write-write conflicts are detected at the table level. If two transactions attempt to modify the same table, the first transaction to commit will succeed, and the second transaction will be aborted if a conflict is detected. **1:46:50**

- **Conflict Detection Mechanism:** The system uses a special table in tempdb to track write-write conflicts. When a transaction attempts to commit, it writes its transaction ID to this table. If another transaction has already written to the same table, a conflict is detected, and the commit will fail. **1:47:35**

- **Serialized Commits:** Although transactions can execute in parallel, their commits are serialized. This means that only one transaction can commit at a time, ensuring that conflicts are detected and resolved correctly. **1:50:21**

- **Transaction ID Tracking:** The system tracks transaction IDs to detect conflicts. Each transaction is assigned a unique ID, and these IDs are used to determine if a conflict has occurred. **1:48:35**

- **Handling Conflicts:** If a conflict is detected, the transaction that attempted to commit second will be aborted. This ensures that only one transaction can modify a table at a time, maintaining consistency. **1:50:40**

- **Future Improvements:** While the current implementation detects conflicts at the table level, there are plans to implement finer-grained conflict detection, such as at the file level. This would allow for more precise conflict detection and potentially reduce the number of aborted transactions. **1:47:23**

This write-write conflict detection mechanism ensures that Fabric DW can handle concurrent transactions efficiently while maintaining data consistency.

</RESPONSE>


## System Tasks and Storage Optimization

**System Tasks and Storage Optimization in Fabric DW:**

- **Garbage Collection:** One of the primary system tasks is garbage collection. This involves cleaning up files that are no longer needed, such as those created by aborted transactions or old versions of data files that have been logically removed. This ensures that storage remains efficient and that unnecessary files do not accumulate. **1:42:37**

- **Data Compaction:** Data compaction is another critical system task. Over time, as rows are deleted and new rows are added, deletion vectors can grow, and data files can become fragmented. Data compaction involves reading the current state of data files and deletion vectors, and then creating new, optimized data files that do not have deletion vectors. This improves read performance and storage efficiency. **1:42:15**

- **Manifest Management:** The system manages manifest files, which track changes to data files. Over time, the sequence of manifest files can grow, so the system periodically creates checkpoint files that summarize the state of multiple manifest files. This reduces the number of files that need to be read to determine the current state of a table. **26:24**

- **Publishing Manifests:** Manifests are initially stored in a private location and are not directly readable by other systems. A system task asynchronously publishes copies of these manifest files to a publicly readable location, following the Delta log protocol. This allows other systems, such as Spark, to read the state of the tables. **1:12:03**

- **Storage Optimization Principles:** The design principles for storage optimization include ensuring that backends have no state, communicating state changes through new files in storage, and using the distributed cloud processor (DCP) for all communication between backends and the front end. This ensures that the system can scale efficiently and handle large volumes of data. **12:58**

- **Handling Logical Metadata:** Logical metadata, such as table definitions, is stored in SQL Server database files. This metadata is not versioned, so schema changes require locks to ensure consistency. However, SQL Server is building versioning for logical metadata, which will allow for non-blocking reads and writes in the future. **41:05**

These system tasks and storage optimization strategies ensure that Fabric DW can handle large-scale data processing efficiently while maintaining data consistency and optimizing storage usage.

</RESPONSE>


## Comparison with Row-Oriented Systems

**Comparison with Row-Oriented Systems:**

- **Data Storage Format:**

- **Row-Oriented Systems:** Data is stored in pages, with each page containing multiple rows. Each row is stored contiguously, making it efficient for transactional workloads where entire rows are frequently accessed or modified. **1:28:59**

- **Fabric DW (Columnar Storage):** Data is stored in Parquet files, which are columnar. Each column's data is stored separately, making it efficient for analytical workloads where operations are performed on specific columns rather than entire rows. **1:32:07**

- **Data Modification:**

- **Row-Oriented Systems:** Modifications (inserts, updates, deletes) are performed in place. For example, if a row is deleted, the space is immediately available for new data. **1:31:00**

- **Fabric DW:** Data files are immutable. Modifications result in new files being created. For example, a delete operation adds a deletion vector to indicate which rows are no longer valid, rather than modifying the original file. **1:34:18**

- **Concurrency Control:**

- **Row-Oriented Systems:** Typically use pessimistic concurrency control with two-phase locking. Transactions acquire locks on data they access, which can lead to contention and blocking. **1:31:42**

- **Fabric DW:** Uses a mixed concurrency control model. Data and physical metadata access are managed optimistically, allowing multiple transactions to proceed in parallel. Logical metadata changes are managed pessimistically with locks. **36:40**

- **Transaction Management:**

- **Row-Oriented Systems:** Use write-ahead logging for recovery and maintain distributed transaction contexts, requiring all participants to stick around for the transaction's lifetime. **1:31:42**

- **Fabric DW:** Transactions are managed through manifest files. Each transaction creates a new manifest file, and changes are recorded in these files. The system uses a two-phase commit approach, but the first phase happens much earlier, reducing the need for distributed transaction management. **47:26**

- **Read Performance:**

- **Row-Oriented Systems:** Efficient for transactional queries that access entire rows. However, analytical queries that need specific columns can be slower due to the need to read entire rows. **1:28:59**

- **Fabric DW:** Optimized for analytical queries. Columnar storage allows for efficient reading of specific columns, reducing the amount of data that needs to be read and processed. **1:32:07**

- **Storage Optimization:**

- **Row-Oriented Systems:** Typically do not require extensive storage optimization tasks, as data is modified in place.

- **Fabric DW:** Requires system tasks for garbage collection and data compaction to manage storage efficiently and maintain performance. **1:42:20**

This comparison highlights the differences in data storage, modification, concurrency control, transaction management, read performance, and storage optimization between row-oriented systems and Fabric DW.

</RESPONSE>


## Future Work and Next Steps

**Future Work and Next Steps in Fabric DW:**

- **Logical Metadata Versioning:** SQL Server is working on building versioning for logical metadata. Once available, this will allow for non-blocking reads and writes, eliminating the need for schema stability locks and improving concurrency. **41:05**

- **Finer-Grained Conflict Detection:** Currently, write-write conflict detection is performed at the table level. Future work includes implementing finer-grained conflict detection, potentially at the file level, to reduce unnecessary transaction aborts and improve system efficiency. **1:47:12**

- **Enhanced Storage Optimization:** Ongoing efforts to improve storage optimization tasks, such as more efficient garbage collection and data compaction processes, will ensure that the system remains performant and storage-efficient as data volumes grow. **1:42:20**

- **Improved Data Compaction:** Developing more sophisticated data compaction algorithms to handle large-scale data transformations and optimize read performance by reducing the need for deletion vectors. **1:42:15**

- **Interoperability Enhancements:** Ensuring seamless interoperability with other systems, such as Spark and Kusto, by adhering to the Delta log protocol and coordinating protocol changes across different applications within the Fabric ecosystem. **58:44**

- **Scalability Improvements:** Continuously enhancing the system's ability to scale efficiently, handling larger volumes of data and more concurrent transactions without compromising performance or consistency. **16:38**

These future work items and next steps aim to enhance the functionality, performance, and scalability of Fabric DW, ensuring it meets the evolving needs of large-scale data processing and analytics.

</RESPONSE>


## Questions

**1. What is the primary focus of the meeting?**

- The meeting focuses on discussing the architecture, design principles, and implementation details of the Fabric Data Warehouse (DW) and its comparison with traditional row-oriented systems. **5:09**

**2. What are the key design principles for Fabric DW?**

- The key design principles include: backends have no state, execution tasks must receive all necessary information, state changes must be communicated through new files in storage, and backends cannot directly communicate with the front end. **12:58**

**3. How does Fabric DW handle transactions?**

- Transactions are managed through manifest files, with each transaction creating a new manifest file. Changes are recorded in these files, and the system uses a two-phase commit approach. **47:26**

**4. What is the role of the Distributed Cloud Processor (DCP) in Fabric DW?**

- The DCP coordinates the topology, scheduling, and execution of tasks. It acts as a conduit for information between the front end and backends but does not directly manage state or commit transactions. **15:48**

**5. How does Fabric DW ensure data consistency?**

- Data consistency is ensured through a combination of optimistic concurrency control for data and physical metadata access, and pessimistic concurrency control for logical metadata. **36:40**

**6. What is the purpose of deletion vectors in Fabric DW?**

- Deletion vectors are used to indicate which rows in a Parquet file are no longer valid, allowing the system to maintain immutability of data files while managing deletions. **20:44**

**7. How does Fabric DW handle garbage collection?**

- Garbage collection is handled through asynchronous system tasks that clean up files and storage optimizations, ensuring efficient use of storage and maintaining performance. **1:42:20**

**8. What is the difference between row-oriented systems and Fabric DW in terms of data storage?**

- Row-oriented systems store data in pages with rows stored contiguously, while Fabric DW uses columnar storage with data stored in Parquet files, optimizing for analytical workloads. **1:32:07**

**9. How does Fabric DW manage logical metadata?**

- Logical metadata is stored in a SQL Server database, and changes to logical metadata are managed through schema stability locks to ensure consistency. **41:05**

**10. What is the role of manifest files in Fabric DW?**

- Manifest files store physical metadata and record changes to data. Each transaction creates a new manifest file, and the sequence of manifest files represents the state of the table. **47:26**

**11. How does Fabric DW handle write-write conflict detection?**

- Write-write conflict detection is performed at the table level using a special table in tempdb. Conflicts are detected during the commit phase, ensuring that only one transaction can commit changes to a table at a time. **1:47:28**

**12. What are the benefits of using Parquet files in Fabric DW?**

- Parquet files provide efficient columnar storage, allowing for optimized read performance for analytical queries and reducing the amount of data that needs to be read and processed. **1:32:07**

**13. How does Fabric DW handle data compaction?**

- Data compaction is performed through system tasks that transform the state of Parquet files and deletion vectors into new, optimized data files without deletion vectors, improving read performance. **1:42:15**

**14. What is the significance of the Delta log protocol in Fabric DW?**

- The Delta log protocol is used for manifest file format, ensuring interoperability with other systems like Spark and Kusto. It allows for efficient management of table state and data changes. **58:44**

**15. How does Fabric DW ensure scalability?**

- Fabric DW ensures scalability by dynamically allocating backends based on resource demand, using shared storage, and optimizing for bulk data operations. **16:38**

**16. What are the future work items for Fabric DW?**

- Future work includes logical metadata versioning, finer-grained conflict detection, enhanced storage optimization, improved data compaction, interoperability enhancements, and scalability improvements. **41:05**

**17. How does Fabric DW handle read performance?**

- Read performance is optimized through columnar storage, allowing for efficient reading of specific columns and reducing the amount of data that needs to be processed for analytical queries. **1:32:07**

**18. What is the role of the front end in Fabric DW?**

- The front end manages logical metadata, coordinates transaction commits, and interacts with the DCP to distribute execution tasks to backends. **11:15**

**19. How does Fabric DW handle data modifications?**

- Data modifications result in new files being created, with changes recorded in manifest files. Deletions are managed through deletion vectors, ensuring that data files remain immutable. **1:34:18**

**20. How does Fabric DW manage transaction commits?**

- Transaction commits are managed by recording the name of the manifest file in a system table in the front end database. This approach simplifies the commit process and reduces the need for distributed transaction management. **46:03**

</RESPONSE>


## Scenario based questions

**1. Scenario: A user wants to insert a large dataset into Fabric DW. How is this handled?**

- The dataset is divided into smaller tasks distributed to multiple backends. Each backend creates new Parquet files and records their names in a manifest file. The front end then flushes the manifest file, and the transaction is committed by recording the manifest file name in the system table. **48:53**

**2. Scenario: Two users are updating the same table simultaneously. How does Fabric DW handle potential conflicts?**

- Fabric DW uses optimistic concurrency control, allowing both updates to proceed. During the commit phase, a write-write conflict detection mechanism checks for conflicts. If a conflict is detected, one transaction is aborted. **1:47:28**

**3. Scenario: A user deletes several rows from a table. How is this managed in Fabric DW?**

- Deletions are managed using deletion vectors, which mark the deleted rows in the Parquet file. The deletion vector is recorded in the manifest file, ensuring the data file remains immutable. **20:44**

**4. Scenario: A user queries a table with frequent updates and deletions. How does Fabric DW ensure efficient read performance?**

- Fabric DW uses data compaction tasks to merge Parquet files and deletion vectors into new, optimized files without deletion vectors, improving read performance. **1:42:15**

**5. Scenario: A user wants to clone a table without copying the data. How is this achieved in Fabric DW?**

- Fabric DW supports metadata-only table clones, where the new table references the same data files as the original table. This is managed by copying the logical metadata and updating the system table. **21:17**

**6. Scenario: A user needs to access the latest state of a table from Spark. How is this facilitated?**

- Fabric DW publishes the state of tables to a publicly readable Delta log folder in One Lake. Spark reads the Delta log sequence to access the latest state of the table. **51:05**

**7. Scenario: A backend node fails during a transaction. How does Fabric DW handle this?**

- Since backends have no state, the failure of a backend node does not impact the transaction. The front end and DCP manage the transaction state, and the task can be rescheduled on another backend. **12:50**

**8. Scenario: A user wants to ensure data consistency during concurrent schema changes. How is this managed?**

- Fabric DW uses pessimistic concurrency control for logical metadata, taking schema stability locks to ensure consistent access to schema information during concurrent changes. **36:40**

**9. Scenario: A user queries a table while a data compaction task is running. How does Fabric DW ensure query accuracy?**

- Data compaction tasks run asynchronously, and the system ensures that queries access the latest committed state of the table, maintaining accuracy and consistency. **1:42:20**

**10. Scenario: A user wants to understand the storage optimization tasks in Fabric DW. What tasks are included?**

- Storage optimization tasks in Fabric DW include garbage collection, data compaction, and publishing Delta logs. These tasks ensure efficient storage use and maintain performance. **1:42:20**

</RESPONSE>


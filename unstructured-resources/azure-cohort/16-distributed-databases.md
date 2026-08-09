Summary

**Key Topics:**

- **Introduction and Roles:** Hari Sudan introduced themselves as the Director of Engineering for Azure Cosmos DB at Microsoft, with 16 years of experience, primarily in databases. Nemanja, who has been with Azure SQL since 2019, also introduced themselves and mentioned their current focus on networking for the PG team in Serbia. **4:59**

- **Distributed Databases Overview:** Hari Sudan discussed the importance of distributed databases, highlighting the need for scalability, fault tolerance, and availability. They explained that vertical scaling becomes expensive and limited, making distributed databases a more cost-effective solution for handling large amounts of data and ensuring data redundancy. **7:36**

- **Shared Disk Architecture:** Hari Sudan explained the shared disk architecture, where CPU and memory are local to the nodes, but the primary storage is shared. This allows for independent scaling of storage and compute, but also introduces challenges in query optimization and cache invalidation. **16:46**

- **Shared Nothing Architecture:** Hari Sudan described the shared nothing architecture, where each node has its own local storage and does not share resources with other nodes. This architecture provides better performance and resiliency, but requires careful data partitioning and handling of data movement when adding new nodes. **29:42**

- **Consistent Hashing:** Hari Sudan introduced the concept of consistent hashing, a technique used to minimize data movement when adding new nodes to a distributed system. This technique involves hashing both data keys and node IDs to determine data placement, ensuring that only a small portion of data needs to be moved when a new node is added. **44:00**

- **Two-Phase Commit Protocol:** Hari Sudan explained the two-phase commit protocol, which ensures atomicity in distributed transactions. The protocol involves a prepare phase, where nodes check if they can commit the transaction, and a commit phase, where the coordinator instructs nodes to commit the transaction. This protocol handles various failure scenarios to ensure data consistency. **1:08:14**

- **Replication and Fault Tolerance:** Hari Sudan discussed the importance of replication for fault tolerance, explaining that data is replicated across multiple nodes to ensure availability in case of node failures. They also described different replication models, including leader-based, multi-leader, and leaderless replication, each with its own advantages and challenges. **1:26:09**

- **Vector Clocks for Event Ordering:** Hari Sudan introduced the concept of vector clocks, which are used to maintain a partial ordering of events in distributed systems. Vector clocks help track the causal relationships between events, ensuring that nodes can determine the order of events even in the presence of clock skew and network delays. **1:57:13**


## Distributed Databases Overview

- **Scalability and Cost:** Hari Sudan emphasized the need for distributed databases due to the limitations and high costs associated with vertical scaling. As data volume and transaction throughput increase, scaling a single node becomes impractical and expensive. Distributed databases allow workloads to be spread across multiple servers, achieving scalability at a lower cost. **7:36**

- **Availability:** Distributed databases provide higher availability by replicating data across multiple nodes. This ensures that data is not lost even if individual nodes fail. In a cloud environment, where hardware failures are common, having redundant copies of data in different locations is crucial for maintaining data integrity and availability. **8:47**

- **Global Accessibility:** For applications with a global user base, distributed databases enable data to be accessible from multiple geographic locations. This reduces latency and improves user experience by allowing users to access data from a local replica rather than a distant one. **10:11**

- **Flexibility:** Distributed databases offer flexibility in handling varying workloads. By adding or removing nodes, the system can dynamically scale to meet changing demands. This architectural pattern allows for sustainable growth and efficient resource utilization. **10:50**

- **Challenges:** Hari Sudan also highlighted the challenges associated with distributed databases, such as handling network failures, ensuring data consistency, and managing the complexity of distributed systems. These challenges require sophisticated mechanisms for fault tolerance, data replication, and event ordering. **13:51**

</RESPONSE>


## Shared Disk Architecture

- **Architecture Overview:** In a shared disk architecture, the CPU and memory are local to each compute node, but the primary storage (disk) is shared among all nodes. This allows multiple compute nodes to access the same storage, enabling independent scaling of storage and compute resources. **16:46**

- **Advantages:**

- **Independent Scaling:** Storage and compute can be scaled independently. If more storage is needed, it can be added without affecting the compute nodes, and vice versa. **17:54**

- **Shared Access:** Any compute node can access any part of the data stored on the shared disk, which simplifies data management and ensures consistency. **22:16**

- **Disadvantages:**

- **Predicate Pushdown Limitations:** Compute nodes may need to load entire data pages from the shared storage, even if only a subset of the data is required. This can lead to inefficiencies, as unnecessary data is transferred over the network. **24:34**

- **Cache Invalidation:** When a write operation occurs, cached copies of the data in other compute nodes need to be invalidated to prevent stale reads. This adds complexity to the system. **29:09**

- **Example Systems:** Shared disk architecture is used in systems like Amazon Aurora and SQL Server Hyperscale, where the storage is decoupled from the compute nodes, allowing for flexible scaling and high availability. **17:14**

</RESPONSE>


## Two-Phase Commit Protocol

- **Purpose:** The Two-Phase Commit (2PC) protocol is used to ensure atomicity in distributed transactions, where a transaction spans multiple nodes or partitions. It guarantees that either all nodes commit the transaction or none do, maintaining consistency across the distributed system. **1:08:02**

- **Phases:**

- **Prepare Phase:**

- The coordinator node sends a "prepare" request to all participant nodes involved in the transaction, asking if they can commit the transaction.

- Each participant node checks if it can commit the transaction (e.g., no conflicting transactions, constraints are satisfied) and responds with "OK" if it can, or "Abort" if it cannot. **1:09:16**

- If a participant responds with "OK," it must be able to commit the transaction later, even if it crashes and recovers. This involves writing the transaction data to a non-volatile storage. **1:11:35**

- **Commit Phase:**

- If all participants respond with "OK," the coordinator decides to commit the transaction and sends a "commit" request to all participants.

- Each participant then commits the transaction and sends an acknowledgment back to the coordinator. **1:13:48**

- If any participant responds with "Abort" or if the coordinator does not receive responses from all participants within a timeout period, the coordinator decides to abort the transaction and sends an "abort" request to all participants. **1:15:12**

- **Failure Handling:**

- **Participant Failure:** If a participant fails after sending "OK" but before committing, it must recover and check with the coordinator to determine the transaction's final outcome (commit or abort). **1:18:23**

- **Coordinator Failure:** If the coordinator fails after deciding to commit but before notifying participants, it must recover and resend the "commit" request to ensure all participants commit the transaction. **1:19:40**

- **Challenges:**

- **Blocking:** If the coordinator fails after participants have sent "OK" but before sending the "commit" or "abort" request, participants are blocked and cannot proceed with other transactions involving the same data until the coordinator recovers. **1:18:29**

- **Timeouts:** Distributed systems rely on timeouts to detect failures, as nodes may not explicitly notify others of their failure. This can lead to delays in transaction resolution. **1:20:32**

- **Use Cases:** The 2PC protocol is commonly used in distributed databases and systems requiring strong consistency and atomicity across multiple nodes or partitions. **1:08:02**

</RESPONSE>


## Shared Nothing Architecture

- **Architecture Overview:** In a shared nothing architecture, each node has its own local CPU, memory, and disk. There is no shared storage or memory between nodes, and all communication between nodes happens over the network using protocols like TCP/IP. **16:46**

- **Advantages:**

- **Performance:** Since the compute engine and storage are local to each node, there is no need to load unnecessary data from a shared disk. This allows for efficient query execution and better performance. **30:52**

- **Failure Isolation:** Failures are isolated to individual nodes, minimizing the impact on the overall system. If one node fails, only the data and workload on that node are affected, while the rest of the system continues to operate. **31:49**

- **Scalability:** The system can easily scale by adding more nodes, each with its own independent resources. This allows for horizontal scaling without the limitations of shared resources. **36:38**

- **Challenges:**

- **Data Distribution:** Data must be partitioned and distributed across nodes in a way that ensures balanced load and minimizes data movement when nodes are added or removed. Techniques like consistent hashing are used to achieve this. **38:05**

- **Data Movement:** When a new node is added, data must be moved from existing nodes to the new node to balance the load. This requires careful planning to minimize the amount of data movement and ensure efficient rebalancing. **38:26**

- **Cross-Node Communication:** Some operations may require communication between nodes, which can introduce latency and complexity. Systems must be designed to minimize the need for cross-node communication. **32:37**

- **Example Systems:** Shared nothing architecture is used in systems like Cosmos DB and DynamoDB, where each node operates independently, and data is distributed across nodes to achieve scalability and fault tolerance. **19:05**

</RESPONSE>


## Consistent Hashing

- **Concept:** Consistent hashing is a technique used to distribute data across a set of nodes in a way that minimizes data movement when nodes are added or removed. It maps both data and nodes to a circular hash space, ensuring that each node is responsible for a contiguous segment of the hash space. **43:37**

- **Mechanism:**

- **Hash Space:** The hash space is represented as a ring, with values ranging from 0 to 1. Both data keys and node identifiers are hashed to positions on this ring. **45:52**

- **Node Placement:** Nodes are placed on the ring based on their hashed identifiers. Each node is responsible for the segment of the ring between its position and the position of the previous node. **47:57**

- **Data Placement:** Data keys are hashed to positions on the ring. A data key is stored on the node that is responsible for the segment of the ring containing the key's hash value. **48:28**

- **Adding Nodes:**

- When a new node is added, it is hashed to a position on the ring. The new node takes over responsibility for the segment of the ring between its position and the position of the next node. **50:01**

- Only the data in this segment needs to be moved to the new node, minimizing the amount of data movement required. **50:40**

- **Advantages:**

- **Minimal Data Movement:** Consistent hashing ensures that only a small portion of the data needs to be moved when nodes are added or removed, reducing the overhead of rebalancing. **51:04**

- **Scalability:** The system can easily scale by adding or removing nodes, with minimal impact on the overall data distribution. **45:31**

- **Example Systems:** Consistent hashing is used in distributed systems like Cosmos DB and DynamoDB to achieve efficient data distribution and scalability. **52:10**

</RESPONSE>


## Replication and Fault Tolerance

- **Replication:**

- **Purpose:** Replication involves creating multiple copies of data across different nodes to ensure data availability and fault tolerance. It helps in maintaining data consistency and availability even if some nodes fail. **1:26:09**

- **Leader-Based Replication:**

- **Primary and Secondary Replicas:** In this model, one node acts as the leader (primary) and others as followers (secondaries). All write operations go to the primary, which then replicates the data to the secondaries. **1:30:00**

- **Quorum Commit:** The primary waits for acknowledgments from a majority (quorum) of the replicas before confirming a write operation to the client. This ensures data durability and consistency. **1:30:11**

- **Failover:** If the primary fails, one of the secondaries is promoted to primary to ensure continued availability. **1:34:19**

- **Multi-Leader Replication:**

- **Multiple Primaries:** Each region or data center can have its own primary replica, allowing write operations to be processed locally, reducing latency and improving availability. **1:38:15**

- **Conflict Resolution:** Since multiple primaries can lead to concurrent writes to the same data, conflict resolution mechanisms (e.g., last writer wins, custom conflict resolution logic) are used to resolve inconsistencies. **1:38:59**

- **Leaderless Replication:**

- **No Designated Leader:** In this model, there is no single leader. Clients write to multiple replicas directly, and quorum-based mechanisms are used to ensure consistency. **1:46:06**

- **Client Responsibility:** The client is responsible for coordinating writes and reads to ensure data consistency and handling failures. **1:46:34**

- **Fault Tolerance:**

- **Handling Failures:** Distributed systems must handle various types of failures, including node crashes, network partitions, and data corruption. **1:24:05**

- **Replication for Fault Tolerance:**

- **Redundancy:** By maintaining multiple replicas of data, the system can tolerate the failure of one or more nodes without losing data or availability. **1:26:34**

- **Recovery:** When a node fails, the system can recover by promoting a secondary replica to primary or by creating a new replica from existing ones. **1:32:07**

- **Consensus Algorithms:**

- **Paxos:** A consensus algorithm used to achieve agreement among distributed nodes. It ensures that a majority of nodes agree on the same value, providing fault tolerance and consistency. **1:48:05**

- **Multi-Paxos:** An extension of Paxos that elects a leader to handle multiple rounds of consensus, improving performance by reducing the number of required message exchanges. **1:49:35**

- **Consistency Models:**

- **Strong Consistency:** Ensures that all replicas have the same data at all times, providing a single, consistent view of the data. This often requires sacrificing availability during network partitions. **1:51:16**

- **Eventual Consistency:** Guarantees that all replicas will eventually converge to the same state, allowing for temporary inconsistencies. This model prioritizes availability and partition tolerance. **1:52:06**

These mechanisms and models are crucial for building robust distributed systems that can handle failures gracefully while maintaining data consistency and availability.


## Vector Clocks for Event Ordering

- **Purpose:** Vector clocks are used in distributed systems to provide a mechanism for capturing causality and ordering of events across multiple nodes. They help in determining the partial ordering of events and identifying concurrent events. **1:57:07**

- **Structure:**

- **Vector Clock:** A vector clock is an array of logical clocks, where each element in the array corresponds to a node in the distributed system. Each node maintains its own logical clock and updates it based on events it processes. **1:57:17**

- **Array Elements:** The array has as many elements as there are nodes in the system. Each element represents the logical clock value for a specific node. **1:57:40**

- **Operation:**

- **Event Generation:** When a node generates an event, it increments its own logical clock in the vector clock. **1:57:34**

- **Message Sending:** When a node sends a message to another node, it includes its current vector clock with the message. **1:58:00**

- **Message Receiving:** When a node receives a message, it updates its vector clock by taking the element-wise maximum of its own vector clock and the received vector clock. It then increments its own logical clock. **1:58:12**

- **Example:**

- **Initial State:** Assume three nodes P1, P2, and P3 with initial vector clocks [0,0,0].

- **Event at P1:** P1 generates an event, updates its vector clock to [1,0,0], and sends a message to P2.

- **P2 Receives Message:** P2 receives the message with vector clock [1,0,0], updates its vector clock to [1,1,0], and increments its own clock to [1,2,0]. **1:58:16**

- **Event at P3:** P3 generates an event, updates its vector clock to [0,0,1].

- **P2 Sends Message to P3:** P2 sends a message to P3 with vector clock [1,2,0]. P3 updates its vector clock to [1,2,1] and increments its own clock to [1,2,2]. **1:58:23**

- **Concurrency and Causality:**

- **Concurrent Events:** Two events are concurrent if their vector clocks are not comparable, meaning neither vector clock is element-wise greater than the other. **1:59:35**

- **Causal Relationship:** An event at node A causally precedes an event at node B if the vector clock of the event at A is element-wise less than the vector clock of the event at B. **1:58:41**

- **Advantages:**

- **Capturing Causality:** Vector clocks effectively capture the causal relationships between events in a distributed system.

- **Conflict Detection:** They help in detecting conflicts and concurrent updates, which is crucial for conflict resolution in distributed databases. **2:00:31**

- **Challenges:**

- **Scalability:** The size of the vector clock grows with the number of nodes in the system, which can be a scalability concern in large distributed systems. **2:00:47**

Vector clocks are a powerful tool for maintaining the partial ordering of events and ensuring consistency in distributed systems. They are particularly useful in scenarios where understanding the causality of events is critical. **2:00:31**


## Questions

Sure, here are 20 questions with answers covering the key issues discussed in the lecture:

1. **Q: What are the primary reasons for using distributed databases?**

- **A:** Distributed databases are used for scalability, fault tolerance, and availability. They allow for spreading the workload across multiple servers, reducing costs, and ensuring data redundancy to survive node failures. **8:22**

2. **Q: What is the difference between shared disk and shared nothing architectures?**

- **A:** In shared disk architecture, the storage is shared among multiple compute nodes, allowing independent scaling of storage and compute. In shared nothing architecture, each node has its own local storage, and nodes communicate over the network, providing better performance and fault tolerance. **16:46**

3. **Q: How does consistent hashing help in distributed databases?**

- **A:** Consistent hashing minimizes the amount of data movement when adding or removing nodes by distributing data across a ring of hash values. This ensures that only a small portion of data needs to be moved, reducing the impact on the system. **45:19**

4. **Q: What is the role of a coordinator in a two-phase commit protocol?**

- **A:** The coordinator orchestrates the transaction by sending prepare requests to all participants, collecting their responses, and then sending commit or abort messages based on the responses. It ensures atomicity across distributed nodes. **1:08:40**

5. **Q: What are the main challenges in distributed systems?**

- **A:** The main challenges include handling unreliable networks, clock skews, and various types of failures such as node crashes, network partitions, and data corruption. **1:24:05**

6. **Q: How does leader-based replication work?**

- **A:** In leader-based replication, one node acts as the leader (primary) and handles all write operations. The leader replicates the data to follower (secondary) nodes, ensuring data consistency and durability through quorum commits. **1:30:00**

7. **Q: What is the advantage of multi-leader replication?**

- **A:** Multi-leader replication allows multiple regions or data centers to have their own primary replicas, reducing latency for local writes and improving fault tolerance by eliminating a single point of failure for writes. **1:38:15**

8. **Q: How do vector clocks help in event ordering?**

- **A:** Vector clocks capture the causal relationships between events by maintaining an array of logical clocks for each node. They help in determining the partial ordering of events and identifying concurrent events. **1:57:07**

9. **Q: What is the purpose of replication in distributed databases?**

- **A:** Replication ensures data availability and fault tolerance by creating multiple copies of data across different nodes. It helps maintain data consistency and availability even if some nodes fail. **1:26:09**

10. **Q: What is the difference between strong consistency and eventual consistency?**

- **A:** Strong consistency ensures that all replicas have the same data at all times, providing a single, consistent view of the data. Eventual consistency guarantees that all replicas will eventually converge to the same state, allowing for temporary inconsistencies. **1:52:06**

11. **Q: How does the two-phase commit protocol ensure atomicity?**

- **A:** The two-phase commit protocol ensures atomicity by having a prepare phase where participants agree to commit, followed by a commit phase where the coordinator instructs participants to commit or abort based on their responses. **1:08:40**

12. **Q: What is the role of a logical clock in distributed systems?**

- **A:** Logical clocks provide a mechanism for ordering events within a single node, ensuring a serial order of transactions without relying on physical timestamps. **1:54:26**

13. **Q: How does leaderless replication differ from leader-based replication?**

- **A:** In leaderless replication, there is no designated leader. Clients write to multiple replicas directly, and quorum-based mechanisms are used to ensure consistency. The client is responsible for coordinating writes and reads. **1:46:06**

14. **Q: What is the purpose of quorum commits in replication?**

- **A:** Quorum commits ensure data durability and consistency by requiring a majority of replicas to acknowledge a write operation before confirming it to the client. **1:30:11**

15. **Q: How do distributed systems handle clock skews?**

- **A:** Distributed systems handle clock skews by using logical clocks or vector clocks instead of relying on physical timestamps, ensuring consistent ordering of events across nodes. **1:53:20**

16. **Q: What is the significance of the CAP theorem in distributed databases?**

- **A:** The CAP theorem states that a distributed system can only achieve two out of three properties: consistency, availability, and partition tolerance. This means that trade-offs must be made based on the system's requirements. **1:51:29**

17. **Q: How does the system handle failures during the two-phase commit protocol?**

- **A:** The system handles failures by using timeouts and retries. If a participant fails to respond, the coordinator may decide to abort the transaction. If the coordinator fails, participants will contact the coordinator upon recovery to determine the transaction's status. **1:19:18**

18. **Q: What are the advantages of using vector clocks over logical clocks?**

- **A:** Vector clocks provide a more comprehensive mechanism for capturing causality and ordering events across multiple nodes, whereas logical clocks only provide partial ordering within a single node. **1:57:17**

19. **Q: How does the system ensure data consistency in leader-based replication?**

- **A:** Data consistency is ensured by having the leader handle all write operations and replicate the data to follower nodes. Quorum commits are used to ensure that a majority of replicas acknowledge the write before confirming it to the client. **1:30:00**

20. **Q: What is the role of conflict resolution in multi-leader replication?**

- **A:** Conflict resolution is crucial in multi-leader replication to handle concurrent writes to the same data from different leaders. Techniques such as last writer wins or custom conflict resolution logic provided by the application are used to resolve conflicts. **1:38:59**


## Scenario based Questions

Sure, here are 10 scenario-based questions with answers covering the key issues discussed in the lecture:

1. **Q: A company wants to scale its database to handle a large volume of transactions without incurring high costs. What architecture should they consider and why?**

- **A:** They should consider a shared nothing architecture because it allows for horizontal scaling by adding more nodes, which can handle increased transaction volumes at a lower cost compared to vertical scaling. **8:22**

2. **Q: During a database upgrade, one of the primary nodes fails. How does the system ensure data availability and consistency?**

- **A:** The system performs a failover to one of the secondary replicas, which then becomes the new primary. This ensures data availability and consistency by maintaining a quorum of replicas that have the latest data. **1:34:19**

3. **Q: An application needs to perform a transaction that updates records across multiple partitions. How does the system ensure atomicity of this transaction?**

- **A:** The system uses a two-phase commit protocol, where a coordinator sends prepare requests to all involved partitions. If all partitions agree, the coordinator sends a commit message, ensuring atomicity across the distributed nodes. **1:08:40**

4. **Q: A distributed database experiences high latency when writing data from a remote region. What replication strategy can help reduce this latency?**

- **A:** Multi-leader replication can help reduce latency by allowing each region to have its own primary replica, enabling local writes and reducing the dependency on a single primary replica in a distant region. **1:38:15**

5. **Q: A node in a distributed database fails to respond to a write request. How does the system handle this failure to ensure data consistency?**

- **A:** The system uses at least once delivery, where the write request is retried until a response is received. This ensures that the data is eventually written to the node, maintaining consistency. **1:21:54**

6. **Q: A company wants to ensure that their database can handle regional outages without data loss. What replication strategy should they implement?**

- **A:** They should implement a multi-region replication strategy with multiple replicas in each region. This ensures that even if an entire region goes down, other regions can still provide data availability and consistency. **1:35:54**

7. **Q: An application requires low-latency reads and writes but can tolerate temporary inconsistencies. What consistency model should they use?**

- **A:** They should use eventual consistency, which allows for low-latency reads and writes by not requiring immediate consistency across all replicas. The system will eventually converge to a consistent state. **1:52:06**

8. **Q: A distributed database needs to handle concurrent updates to the same record from different regions. How does the system resolve conflicts?**

- **A:** The system uses conflict resolution techniques such as last writer wins or custom conflict resolution logic provided by the application to determine which update to keep. **1:38:59**

9. **Q: A company wants to minimize data movement when adding new nodes to their distributed database. What partitioning strategy should they use?**

- **A:** They should use consistent hashing, which minimizes data movement by distributing data across a ring of hash values. When a new node is added, only a small portion of data needs to be moved. **45:19**

10. **Q: An application needs to ensure that all replicas have the same data at all times. What consistency model should they use?**

- **A:** They should use strong consistency, which ensures that all replicas have the same data at all times, providing a single, consistent view of the data. **1:52:06**


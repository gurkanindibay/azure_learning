---
type: System Design Case
title: "Back-of-the-envelope estimation"
description: "Recently, a few engineers asked me whether we really need back-of-the-envelope estimation in a system design interview. I think it would be helpful to clarify. Estimations are important because we ..."
tags: [system-design]
timestamp: 2026-08-22T00:00:00Z
---

# Back-of-the-envelope estimation

> **Source**: ByteByteGo — System Design compilation PDF

Recently, a few engineers asked me whether we really need back-of-the-envelope estimation in a system design interview. I think it would be helpful to clarify. Estimations are important because we need them to understand the scale of the system and justify the design. It helps answer questions like: - Do we really need a distributed solution? - Is a cache layer necessary? - Shall we choose data replication or sharding? Here is an example of how the estimations shape the design decision. One interview question is to design proximity service and how to scale geospatial index is a key part of it. Here are a few paragraphs we wrote to show why jumping to a sharding design without estimations is a bad idea: “One common mistake about scaling the geospatial index is to quickly jump to a sharding scheme without considering the actual data size of the table. In our case, the full dataset for the geospatial index table is not large (quadtree index only takes 1.71G memory and storage requirement for geohash index is similar). The whole geospatial index can easily fit in the working set of a modern database server. However, depending on the read volume, a single database server might not have enough CPU or network bandwidth to service all read requests. If that is the case, it will be necessary to spread the read load among multiple database servers. There are two general approaches to spread the load of a relational database server. We can add read replicas or shard the database. Many engineers like to talk about sharding during interviews. However, it might not be a good fit for the geohash table. Sharding is complicated. The sharding logic has to be added to the application layer. Sometimes, sharding is the only option. In this case though, since everything can fit in the working set of a database server, there is no strong technical reason to shard the data among multiple servers.

A better approach, in this case, is to have a series of read replicas to help with the read load. This method is much simpler to develop and maintain. Thus, we recommend scaling the geospatial index table through replicas.”
—
Check out our bestselling system design books. Paperback: Amazon Digital: ByteByteGo.

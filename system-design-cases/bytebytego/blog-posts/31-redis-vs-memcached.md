---
okf_version: "0.1"
type: concept
---

# Redis vs Memcached

> **Source**: ByteByteGo — System Design compilation PDF

![Redis vs Memcached](images/img-030.jpeg)

The diagram below illustrates the key differences. The advantages on data structures make Redis a good choice for: - Recording the number of clicks and comments for each post (hash) - Sorting the commented user list and deduping the users (zset) - Caching user behavior history and filtering malicious behaviors (zset, hash) - Storing boolean information of extremely large data into small space. For example, login status, membership status. (bitmap)

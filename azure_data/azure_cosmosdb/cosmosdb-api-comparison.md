# Azure Cosmos DB API Comparison Guide

## Overview

Azure Cosmos DB is a fully managed, globally distributed, multi-model database service that supports multiple APIs. Each API is optimized for specific data models and use cases. This document provides a comprehensive comparison of all available APIs to help you choose the right one for your application.

---

## Table of Contents

1. [API Determines Account Type](#api-determines-account-type)
2. [Quick Reference: Which API for Which Data?](#quick-reference-which-api-for-which-data)
3. [Core (SQL) API](#core-sql-api)
4. [MongoDB API](#mongodb-api)
5. [Apache Cassandra API](#apache-cassandra-api)
6. [Apache Gremlin API](#apache-gremlin-api)
7. [Table API](#table-api)
8. [PostgreSQL API](#postgresql-api)
9. [Data Format Comparison](#data-format-comparison)
10. [API Selection Decision Guide](#api-selection-decision-guide)
11. [Exam Scenarios](#exam-scenarios)

---

## API Determines Account Type

### One API Per Account Rule

**Important**: The API you choose determines the type of Cosmos DB account to create. Currently, you **must create a separate account for each API**. You cannot mix different APIs within the same account.

| Scenario | Possible? | Explanation |
|----------|-----------|-------------|
| Create SQL API database and Gremlin API database in same account | ❌ No | Each account supports only one API type |
| Create multiple SQL API databases in same account | ✅ Yes | Multiple databases of the same API type are allowed |
| Create multiple containers in same database | ✅ Yes | Multiple containers within a database are allowed |

### Practice Question: Multiple APIs in One Account

**Scenario:**

You've created a Cosmos DB account named **Account1**. Inside, you create one database named **Db1**, and one container named **Container1**. The data you are storing is document data using the **Core (SQL) API**. You have a new requirement to add a **graph database using the Gremlin API**.

**Question:**

Can you create another database named Db2 inside Account1 for the graph data?

**Options:**

- A) Yes, each database can use a different API in one account
- B) No, each account can only contain one type of data ✅
- C) Yes, you can use any API to call a Cosmos DB database of any type

---

**Correct Answer: B) No, each account can only contain one type of data**

---

**Explanation:**

The API determines the type of account to create. Azure Cosmos DB provides five APIs:

| API | Data Type | Description |
|-----|-----------|-------------|
| **Core (SQL)** | Document | Native JSON document storage |
| **MongoDB** | Document | MongoDB-compatible document storage |
| **Gremlin** | Graph | Graph data with vertices and edges |
| **Azure Table** | Key-Value | Simple key-value storage |
| **Cassandra** | Column-Family | Wide-column storage |

**Key Point:** Currently, you must create a **separate account for each API**. This means:

- **Account1** (Core SQL API) → Can only have SQL databases and containers
- To use Gremlin API, you must create a **new account** (e.g., Account2) with Gremlin API selected

**Why the other options are incorrect:**

| Option | Why Incorrect |
|--------|---------------|
| **A) Yes, each database can use a different API** | Incorrect - APIs are set at the account level, not database level |
| **C) Yes, you can use any API to call any database** | Incorrect - Each API has its own wire protocol and data model; you cannot use SQL queries on a Gremlin database |

**Reference:** [Azure Cosmos DB resource model](https://docs.microsoft.com/en-us/azure/cosmos-db/account-databases-containers-items)

---

## Quick Reference: Which API for Which Data?

| Data Type | Best API | Data Format | Use Case |
|-----------|----------|-------------|----------|
| **Document (JSON)** | ✅ **Core (SQL)** | JSON (text-based) | Native JSON documents, flexible schema |
| **Document (binary)** | MongoDB API | BSON (binary JSON) | MongoDB migration, binary-encoded documents |
| **Column-oriented** | Cassandra API | Wide-column | Time-series, IoT, high-write scenarios |
| **Graph relationships** | Gremlin API | Vertices & Edges | Social networks, recommendations, fraud detection |
| **Key-value** | Table API | Rows with columns | Simple key-value, Azure Table Storage migration |
| **Relational** | PostgreSQL API | Relational tables | PostgreSQL migration, relational workloads |

---

## Core (SQL) API

### ✅ Best Choice for JSON Document Data

The **Core (SQL) API** (also known as **NoSQL API**) is Cosmos DB's native API and the **recommended choice for working with JSON document data**.

### Data Format

- **Format**: Native JSON (JavaScript Object Notation)
- **Type**: Text-based, human-readable
- **Schema**: Schema-free (flexible)

### Key Characteristics

| Feature | Description |
|---------|-------------|
| **Native Cosmos DB API** | Purpose-built for Cosmos DB |
| **Query Language** | SQL-like syntax for querying JSON |
| **Data Storage** | Native JSON documents |
| **Schema** | Schema-free, flexible structure |
| **Indexing** | Automatic indexing of all properties |
| **SDK Support** | .NET, Java, Python, Node.js, etc. |

### Example Document

```json
{
    "id": "product-001",
    "name": "Wireless Mouse",
    "categoryId": "electronics",
    "price": 29.99,
    "specifications": {
        "color": "black",
        "weight": "85g",
        "connectivity": "2.4GHz wireless"
    },
    "tags": ["wireless", "ergonomic", "office"],
    "inStock": true,
    "lastUpdated": "2025-11-26T10:30:00Z"
}
```

### Query Example

```sql
SELECT p.name, p.price, p.specifications.color
FROM products p
WHERE p.categoryId = 'electronics' 
  AND p.price < 50
ORDER BY p.price DESC
```

### When to Use Core (SQL) API

✅ **Use Core (SQL) API when:**
- Building new applications on Cosmos DB
- Working with native JSON documents
- Need flexible, schema-free data model
- Want SQL-like query syntax
- Require automatic indexing
- Don't have existing MongoDB/Cassandra/Gremlin applications
- Need the best Cosmos DB feature support

### Advantages

- ✅ Native Cosmos DB experience
- ✅ Full feature support (all Cosmos DB features first available here)
- ✅ Human-readable JSON format
- ✅ Familiar SQL-like query syntax
- ✅ Automatic indexing of all JSON properties
- ✅ Rich SDK support across languages
- ✅ Best performance optimization options

---

## MongoDB API

### For MongoDB Compatibility and BSON Documents

The **MongoDB API** allows you to use Azure Cosmos DB with existing MongoDB drivers, tools, and applications.

### Data Format

- **Format**: BSON (Binary JSON)
- **Type**: Binary-encoded, not human-readable directly
- **Schema**: Schema-free (flexible)

### Key Difference: JSON vs BSON

| Aspect | JSON (Core SQL API) | BSON (MongoDB API) |
|--------|--------------------|--------------------|
| **Format** | Text-based | Binary-encoded |
| **Readability** | Human-readable | Not directly readable |
| **Data Types** | Limited (string, number, boolean, array, object, null) | Extended (Date, Binary, ObjectId, Decimal128, etc.) |
| **Size** | Larger for some data | More compact for binary data |
| **Performance** | Text parsing required | Faster parsing (binary) |
| **Use Case** | General JSON documents | MongoDB compatibility |

### BSON Extended Types

BSON supports additional data types not available in standard JSON:

```javascript
// BSON-specific types
{
    "_id": ObjectId("507f1f77bcf86cd799439011"),  // 12-byte unique identifier
    "name": "Product",
    "createdAt": ISODate("2025-11-26T10:30:00Z"), // Native date type
    "price": NumberDecimal("29.99"),              // 128-bit decimal
    "data": BinData(0, "base64encodeddata"),      // Binary data
    "regularExpression": /pattern/i               // Regex
}
```

### When to Use MongoDB API

✅ **Use MongoDB API when:**
- Migrating existing MongoDB applications to Azure
- Using MongoDB drivers, tools, or libraries
- Have developers experienced with MongoDB
- Need BSON-specific data types (ObjectId, Decimal128, etc.)
- Want wire protocol compatibility with MongoDB

❌ **Don't use MongoDB API when:**
- Building new applications from scratch (use Core SQL API)
- Need native JSON document storage
- Want SQL-like query syntax
- Don't have MongoDB dependencies

### MongoDB Migration to Azure Cosmos DB

When migrating an on-premises MongoDB deployment to Azure Cosmos DB (using MongoDB API), you need to use the appropriate migration tools.

#### Correct Migration Tool: `mongorestore`

✅ **`mongorestore`** is the recommended tool for migrating MongoDB data to Azure Cosmos DB.

**Why use mongorestore:**
- Restores MongoDB backups directly to Azure Cosmos DB
- Works seamlessly with Cosmos DB's MongoDB API
- Maintains data integrity and structure during migration
- Supports the MongoDB wire protocol

**Migration Process:**
1. Export data from on-premises MongoDB using `mongodump`
2. Use `mongorestore` to restore the data to Azure Cosmos DB MongoDB API account
3. Verify data migration and update connection strings in applications

#### Incorrect Migration Tools

❌ **Data Management Gateway**
- Not suitable for MongoDB to Cosmos DB migration
- Designed for hybrid data integration scenarios
- Does not provide MongoDB-specific migration capabilities

❌ **Azure Storage Explorer**
- Used for managing Azure Storage resources (blobs, files, queues, tables)
- Not designed for database migrations
- Cannot migrate MongoDB data to Cosmos DB

❌ **AzCopy**
- Command-line tool for copying data to/from Azure Storage services
- Works with Azure Storage (blobs, files), not databases
- Not the recommended tool for MongoDB to Cosmos DB migration

**Exam Tip**: When migrating MongoDB to Azure Cosmos DB with MongoDB API, always use MongoDB-native tools like `mongorestore` rather than generic Azure tools.

### Important Exam Note

⚠️ **For the exam question "Which API works best with document (JSON) data?"**

**Answer: Core (SQL) API** ✅

**Why not MongoDB API?**
- MongoDB uses **BSON** (Binary JSON), not plain JSON
- BSON is a **binary format**, not text-based
- While BSON can represent JSON, it's encoded differently
- Core (SQL) API stores native, text-based JSON documents

---

## Apache Cassandra API

### For Column-Oriented Data

The **Cassandra API** provides wire protocol compatibility with Apache Cassandra, using a wide-column data model.

### Data Format

- **Format**: Wide-column (column families)
- **Type**: Column-oriented schema
- **Schema**: Defined schema required

### Data Model

```
┌───────────────────────────────────────────────────────┐
│  Row Key     │  Column 1  │  Column 2  │  Column N   │
├──────────────┼────────────┼────────────┼─────────────┤
│  user:001    │  name:John │  email:... │  age:30     │
│  user:002    │  name:Jane │  email:... │  (missing)  │
│  user:003    │  name:Bob  │  (missing) │  age:25     │
└───────────────────────────────────────────────────────┘

Note: Each row can have different columns (sparse)
```

### Example Schema and Query (CQL)

```cql
-- Create a table with column-oriented design
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    name TEXT,
    email TEXT,
    created_at TIMESTAMP
);

-- Insert data
INSERT INTO users (user_id, name, email, created_at)
VALUES (uuid(), 'John Doe', 'john@example.com', toTimestamp(now()));

-- Query data
SELECT name, email FROM users WHERE user_id = <uuid>;
```

### When to Use Cassandra API

✅ **Use Cassandra API when:**
- Migrating Apache Cassandra workloads to Azure
- Need column-oriented data model
- Working with time-series data
- High-volume write scenarios (IoT, logging)
- Using CQL (Cassandra Query Language)
- Have existing Cassandra drivers and tools

---

## Apache Gremlin API

### For Graph Data

The **Gremlin API** is designed for graph databases, storing data as vertices (nodes) and edges (relationships).

### Data Format

- **Format**: Graph (Vertices and Edges)
- **Type**: Property graph model
- **Schema**: Schema-free vertices and edges

### Data Model

```
┌─────────────┐          ┌─────────────┐
│   VERTEX    │          │   VERTEX    │
│  (Person)   │          │  (Product)  │
│  id: "1"    │          │  id: "101"  │
│  name: John │──BOUGHT──│  name: Laptop│
│  age: 30    │          │  price: 999 │
└─────────────┘          └─────────────┘
       │
       │ KNOWS
       ▼
┌─────────────┐
│   VERTEX    │
│  (Person)   │
│  id: "2"    │
│  name: Jane │
└─────────────┘
```

### Example Gremlin Queries

```groovy
// Add a vertex (node)
g.addV('person')
 .property('id', '1')
 .property('name', 'John')
 .property('age', 30)

// Add an edge (relationship)
g.V('1').addE('knows').to(g.V('2'))

// Query: Find all friends of John
g.V().has('name', 'John').out('knows').values('name')

// Query: Find products bought by John
g.V().has('name', 'John').out('bought').values('name')

// Query: Find friends of friends
g.V().has('name', 'John').out('knows').out('knows').values('name')
```

### When to Use Gremlin API

✅ **Use Gremlin API when:**
- Modeling complex relationships between entities
- Building social networks
- Recommendation engines
- Fraud detection systems
- Knowledge graphs
- Network and IT operations analysis

---

## Table API

### For Key-Value and Azure Table Storage Migration

The **Table API** provides compatibility with Azure Table Storage, offering a simple key-value data model.

### Data Format

- **Format**: Key-value (entity with properties)
- **Type**: Structured rows with partition key and row key
- **Schema**: Semi-structured (defined properties per entity)

### Data Model

```
┌────────────────┬───────────────┬──────────────┬──────────────┐
│ PartitionKey   │ RowKey        │ Property1    │ Property2    │
├────────────────┼───────────────┼──────────────┼──────────────┤
│ "Electronics"  │ "Product001"  │ "Laptop"     │ 999.99       │
│ "Electronics"  │ "Product002"  │ "Mouse"      │ 29.99        │
│ "Furniture"    │ "Product003"  │ "Desk"       │ 299.99       │
└────────────────┴───────────────┴──────────────┴──────────────┘
```

### When to Use Table API

✅ **Use Table API when:**
- Migrating from Azure Table Storage
- Simple key-value storage needs
- Using existing Table Storage SDKs
- Need global distribution for Table Storage data

---

## PostgreSQL API

### For Relational/PostgreSQL Workloads

The **PostgreSQL API** (Azure Cosmos DB for PostgreSQL) enables distributed PostgreSQL with relational data model.

### Data Format

- **Format**: Relational tables
- **Type**: Structured, schema-defined
- **Schema**: Traditional relational schema

### When to Use PostgreSQL API

✅ **Use PostgreSQL API when:**
- Need relational database capabilities
- Migrating PostgreSQL workloads
- Require ACID transactions across tables
- Using SQL for complex relational queries
- Need horizontal scaling for PostgreSQL

---

## Data Format Comparison

### Complete Format Comparison Table

| API | Data Format | Storage Type | Human Readable | Schema | Query Language |
|-----|-------------|--------------|----------------|--------|----------------|
| **Core (SQL)** | JSON | Document | ✅ Yes (text) | Schema-free | SQL-like |
| **MongoDB** | BSON | Document | ❌ No (binary) | Schema-free | MongoDB Query |
| **Cassandra** | Column-family | Wide-column | ❌ Structured | Schema required | CQL |
| **Gremlin** | Vertices/Edges | Graph | N/A | Schema-free | Gremlin |
| **Table** | Key-value rows | Key-value | ❌ Structured | Semi-structured | OData |
| **PostgreSQL** | Relational | Tables | ❌ Structured | Schema required | SQL |

### Visual Comparison

```
┌──────────────────────────────────────────────────────────────────┐
│                     DATA FORMAT SPECTRUM                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Document-Based                    Structured/Relational          │
│  ◄─────────────────────────────────────────────────────────────► │
│                                                                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐│
│  │Core SQL │  │MongoDB  │  │Cassandra│  │ Table   │  │PostgreSQL│
│  │  (JSON) │  │ (BSON)  │  │(Columns)│  │(Key-Val)│  │(Relation)│
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘│
│      ↓            ↓            ↓            ↓            ↓       │
│   Native       Binary       Column-       Key-        Tables     │
│    JSON       Encoded      Oriented      Value        Rows       │
│                                                                   │
│  Schema-free ◄────────────────────────────────────► Schema-req'd │
└──────────────────────────────────────────────────────────────────┘
```

### JSON vs BSON Deep Dive

Since the exam question focuses on JSON vs BSON, here's a detailed comparison:

```
JSON (Core SQL API)                    BSON (MongoDB API)
───────────────────                    ──────────────────

Text-based format:                     Binary-encoded format:
{                                      \x16\x00\x00\x00\x02name\x00
  "name": "John",                      \x05\x00\x00\x00John\x00
  "age": 30                            \x10age\x00\x1e\x00\x00\x00
}                                      \x00

✅ Human readable                      ❌ Not human readable
✅ Easy to debug                       ✅ More data types
✅ Universal format                    ✅ Faster parsing
✅ Native web format                   ✅ Smaller for binary data
❌ Limited data types                  ❌ MongoDB-specific
❌ Larger for numbers                  ❌ Needs conversion
```

---

## API Selection Decision Guide

### Decision Tree

```
                    What type of data do you have?
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
   Documents?            Graph/Network?        Tabular?
        │                     │                     │
        │                     ▼                     │
        │              ┌──────────────┐             │
        │              │ Gremlin API  │             │
        │              │ (Vertices &  │             │
        │              │   Edges)     │             │
        │              └──────────────┘             │
        │                                           │
        ▼                                           ▼
  ┌──────────────┐                           ┌──────────────┐
  │ New app or   │                           │ Key-value or │
  │ native JSON? │                           │ Relational?  │
  └──────┬───────┘                           └──────┬───────┘
         │                                          │
    ┌────┴────┐                              ┌──────┴──────┐
    │         │                              │             │
    ▼         ▼                              ▼             ▼
  ┌────┐    ┌────────┐                 ┌─────────┐   ┌──────────┐
  │Yes │    │MongoDB │                 │Table API│   │PostgreSQL│
  │    │    │migrate?│                 │Key-Value│   │Relational│
  └──┬─┘    └───┬────┘                 └─────────┘   └──────────┘
     │          │
     │     ┌────┴────┐
     │     │         │
     ▼     ▼         ▼
┌─────────────┐  ┌─────────────┐
│ Core (SQL)  │  │ MongoDB API │
│ API         │  │ (BSON)      │
│ (Native     │  │             │
│  JSON)      │  │             │
└─────────────┘  └─────────────┘
```

### Quick Selection Guide

| Requirement | Recommended API |
|------------|-----------------|
| New application with JSON data | **Core (SQL) API** ✅ |
| Migrate from MongoDB | MongoDB API |
| Migrate from Cassandra | Cassandra API |
| Graph relationships | Gremlin API |
| Migrate from Azure Table Storage | Table API |
| Relational PostgreSQL workloads | PostgreSQL API |
| Time-series / High-write | Cassandra API |
| Social network / Recommendations | Gremlin API |

---

## Exam Scenarios

### Scenario 1: JSON Document Data

**Question:** Which CosmosDB API format works best with document (JSON) data?

**Options:**
- A) Core SQL ✅
- B) Cassandra API
- C) Graph API
- D) MongoDB API

**Correct Answer: A) Core SQL**

**Explanation:**

| API | Why Correct/Incorrect |
|-----|----------------------|
| **Core (SQL)** ✅ | Stores data in **native JSON document format** (text-based, human-readable) |
| **Cassandra API** ❌ | Stores data in **column-oriented schema**, not documents |
| **Gremlin (Graph) API** ❌ | Stores data as **vertices (nodes) and edges (relationships)**, not documents |
| **MongoDB API** ❌ | Uses **BSON (Binary JSON)** format, which is **binary-encoded**, not text-based JSON |

**Key Distinction:**
- **JSON** = JavaScript Object Notation (text-based, human-readable)
- **BSON** = Binary JSON (binary-encoded, not directly human-readable)

The question specifically asks about **JSON** data, making **Core (SQL) API** the correct answer because it uses native, text-based JSON format.

---

### Scenario 2: Graph Data

**Question:** Which CosmosDB API format works best with graph data?

**Options:**
- A) Table API
- B) Cassandra API
- C) Gremlin API ✅
- D) Core (SQL) API

**Correct Answer: C) Gremlin API**

**Explanation:**

| API | Data Format | Why Correct/Incorrect |
|-----|-------------|----------------------|
| **Gremlin API** ✅ | Vertices & Edges | Allows users to make **graph queries** and store data as **edges and vertices** - perfect for graph data |
| **Table API** ❌ | Key/Value | Stores data in **key/value format**, not suited for graph relationships |
| **Cassandra API** ❌ | Column-oriented | Stores data in a **column-oriented schema**, optimized for wide-column workloads |
| **Core (SQL) API** ❌ | Document (JSON) | Stores data in **document format**, not optimized for graph traversals |

**Why Gremlin API is the best for Graph Data:**

1. **Native Graph Model**: Data is stored as vertices (nodes) and edges (relationships)
2. **Graph Traversal Queries**: Gremlin query language is specifically designed for traversing relationships
3. **Relationship-First Design**: Optimized for queries like "find friends of friends" or "shortest path between nodes"
4. **Property Graph Model**: Both vertices and edges can have properties

**Graph Data Example:**
```
    ┌─────────┐         ┌─────────┐
    │ Person  │─KNOWS──▶│ Person  │
    │ "John"  │         │ "Jane"  │
    └─────────┘         └─────────┘
         │
         │ BOUGHT
         ▼
    ┌─────────┐
    │ Product │
    │ "Laptop"│
    └─────────┘
```

**Gremlin Query Examples:**
```groovy
// Find all people John knows
g.V().has('name', 'John').out('knows').values('name')

// Find products bought by John's friends
g.V().has('name', 'John').out('knows').out('bought').values('name')

// Find the shortest path between two people
g.V().has('name', 'John').repeat(out('knows')).until(has('name', 'Jane')).path()
```

**Use Cases for Gremlin API:**
- Social networks (friend connections)
- Recommendation engines (product relationships)
- Fraud detection (transaction patterns)
- Knowledge graphs (entity relationships)
- Network topology (IT infrastructure)

**Reference:** [Introduction to Azure Cosmos DB](https://docs.microsoft.com/en-us/azure/cosmos-db/introduction)

---

### Scenario 3: Key-Value Data

**Question:** Which CosmosDB API format works best with key-value data?

**Options:**
- A) Table API ✅
- B) MongoDB API
- C) Gremlin API
- D) Cassandra API

**Correct Answer: A) Table API**

**Explanation:**

| API | Data Format | Why Correct/Incorrect |
|-----|-------------|----------------------|
| **Table API** ✅ | Key/Value | Stores data in **key/value format** - specifically designed for simple key-value storage patterns |
| **MongoDB API** ❌ | BSON (Binary JSON) | Stores data in a **document structure via BSON format**, not key-value |
| **Gremlin API** ❌ | Vertices & Edges | Allows users to make **graph queries** and stores data as **edges and vertices**, not key-value |
| **Cassandra API** ❌ | Column-oriented | Stores data in a **column-oriented schema**, optimized for wide-column workloads |

**Why Table API is the best for Key-Value Data:**

1. **Native Key-Value Model**: Data is stored with PartitionKey and RowKey as the primary identifiers
2. **Simple Access Pattern**: Optimized for point reads and writes using keys
3. **Azure Table Storage Compatible**: Provides an upgrade path from Azure Table Storage with global distribution
4. **Efficient Lookups**: Fast retrieval by key without complex query requirements

**Key-Value Data Example:**
```
┌────────────────┬───────────────┬──────────────┬──────────────┐
│ PartitionKey   │ RowKey        │ Value1       │ Value2       │
├────────────────┼───────────────┼──────────────┼──────────────┤
│ "config"       │ "timeout"     │ "30"         │ "seconds"    │
│ "config"       │ "retries"     │ "3"          │ null         │
│ "session"      │ "user123"     │ "{...}"      │ "active"     │
└────────────────┴───────────────┴──────────────┴──────────────┘
```

**Use Cases for Table API:**
- Configuration storage (key-value settings)
- Session management
- User preference storage
- Simple caching scenarios
- Migration from Azure Table Storage

**Reference:** [Introduction to Azure Cosmos DB](https://docs.microsoft.com/en-us/azure/cosmos-db/introduction)

---

### Scenario 4: MongoDB Migration

**Question:** Your company has an existing MongoDB application that needs to be migrated to Azure Cosmos DB with minimal code changes. Which API should you use?

**Answer:** MongoDB API

**Reasoning:** 
- MongoDB API provides wire protocol compatibility
- Existing MongoDB drivers and tools work unchanged
- BSON format compatibility maintained

---

### Scenario 5: MongoDB RBAC Roles and Users Storage

**Question:** You need to create a custom RBAC role for Azure Cosmos DB for MongoDB. Where are roles and users stored?

**Options:**
- A) In the Azure Resource Manager
- B) Within a specific database in the Azure Cosmos DB account ✅
- C) In Azure Active Directory
- D) In the master database at account level

**Correct Answer: B) Within a specific database in the Azure Cosmos DB account**

**Explanation:**

| Option | Why Correct/Incorrect |
|--------|----------------------|
| **Azure Resource Manager** ❌ | ARM is used to manage roles and users but doesn't store them; the actual storage is within the MongoDB database |
| **Within a specific database** ✅ | In Azure Cosmos DB for MongoDB, RBAC roles and users are stored within a database and managed using Azure CLI, PowerShell, or ARM templates |
| **Azure Active Directory** ❌ | Azure Cosmos DB for MongoDB uses its own RBAC system separate from Azure AD, with users and roles stored within the database itself |
| **Master database at account level** ❌ | There is no master database at account level for MongoDB API; roles and users are stored within individual databases |

**Key Points:**
- Azure Cosmos DB for MongoDB has its own RBAC implementation
- Roles and users are database-scoped, not account-scoped
- Management can be done via Azure CLI, PowerShell, or ARM templates
- This is different from Azure AD RBAC which controls Azure resource access

**Reference:** [Azure Cosmos DB for MongoDB RBAC](https://docs.microsoft.com/en-us/azure/cosmos-db/mongodb/how-to-setup-rbac)

---

### Scenario 6: Social Network Application

**Question:** You're building a social network application that needs to efficiently query friend relationships and friend-of-friend connections. Which API should you use?

**Answer:** Gremlin API

**Reasoning:**
- Graph databases excel at relationship queries
- Traversing connections is natural in graph model
- Gremlin query language designed for graph traversals

---

### Scenario 7: IoT Time-Series Data

**Question:** You're collecting high-volume sensor data from IoT devices that needs to be written quickly and queried by time ranges. Which API should you use?

**Answer:** Cassandra API

**Reasoning:**
- Cassandra excels at high-write throughput
- Wide-column model optimal for time-series
- Efficient time-range queries with partition design

---

### Scenario 8: Flexible JSON Documents

**Question:** You're building a new e-commerce application that needs to store product catalogs with varying attributes depending on product category. You want SQL-like query capabilities. Which API should you use?

**Answer:** Core (SQL) API

**Reasoning:**
- Schema-free JSON documents handle varying attributes
- SQL-like query syntax for familiar querying
- Native Cosmos DB API with full feature support
- Best choice for new applications without migration requirements

---

## Summary

### Key Takeaways

1. **For JSON document data** → Use **Core (SQL) API** (native JSON, text-based)

2. **BSON ≠ JSON**: MongoDB uses BSON (binary), not plain JSON

3. **Cassandra**: Column-oriented, not document-based

4. **Gremlin**: Graph (vertices/edges), not document-based

5. **Choose based on data model**:
   - Documents (JSON) → Core SQL
   - Documents (BSON/MongoDB compatible) → MongoDB
   - Columns → Cassandra
   - Graphs → Gremlin
   - Key-value → Table
   - Relational → PostgreSQL

### Memory Aid

```
C - Core SQL    → JSON (J is for JSON!)
M - MongoDB     → BSON (B is for Binary!)
C - Cassandra   → Columns
G - Gremlin     → Graph
T - Table       → Tabular key-value
P - PostgreSQL  → PostgreSQL relational
```

---

## References

- [Introduction to Azure Cosmos DB](https://docs.microsoft.com/en-us/azure/cosmos-db/introduction)
- [Choose an API in Azure Cosmos DB](https://docs.microsoft.com/en-us/azure/cosmos-db/choose-api)
- [Core (SQL) API Documentation](https://docs.microsoft.com/en-us/azure/cosmos-db/sql/sql-api-introduction)
- [MongoDB API Documentation](https://docs.microsoft.com/en-us/azure/cosmos-db/mongodb/mongodb-introduction)
- [Cassandra API Documentation](https://docs.microsoft.com/en-us/azure/cosmos-db/cassandra/cassandra-introduction)
- [Gremlin API Documentation](https://docs.microsoft.com/en-us/azure/cosmos-db/gremlin/gremlin-support)

---

**Document Version:** 1.0  
**Last Updated:** November 26, 2025  
**Domain:** Non-relational DB

---

End of Document

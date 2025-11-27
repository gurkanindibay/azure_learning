# Explore Microsoft .NET SDK v3 for Azure Cosmos DB

**Completed**  
**100 XP**  
**3 minutes**

This unit focuses on Azure Cosmos DB .NET SDK v3 for API for NoSQL (`Microsoft.Azure.Cosmos` NuGet package). If you're familiar with the previous version of the .NET SDK, you might be familiar with the terms collection and document.

The [azure-cosmos-dotnet-v3 GitHub repository](https://github.com/Azure/azure-cosmos-dotnet-v3) includes the latest .NET sample solutions. You use these solutions to perform CRUD (create, read, update, and delete) and other common operations on Azure Cosmos DB resources.

Because Azure Cosmos DB supports multiple API models, version 3 of the .NET SDK uses the generic terms **container** and **item**. A container can be a collection, graph, or table. An item can be a document, edge/vertex, or row, and is the content inside a container.

## Table of Contents

1. [Hierarchy Overview](#hierarchy-overview)
2. [Step 1: Initialize CosmosClient](#step-1-initialize-cosmosclient)
3. [Step 2: Database Operations](#step-2-database-operations)
   - [Create a Database](#create-a-database)
   - [Read a Database](#read-a-database)
   - [Delete a Database](#delete-a-database)
4. [Step 3: Container Operations](#step-3-container-operations)
   - [Create a Container](#create-a-container)
   - [Get a Container](#get-a-container)
   - [Delete a Container](#delete-a-container)
5. [Step 4: Item Operations](#step-4-item-operations)
   - [Create an Item](#create-an-item)
   - [Read an Item](#read-an-item)
   - [Query Items](#query-items)
   - [Update an Item](#update-an-item)
   - [Delete an Item](#delete-an-item)

---

## Hierarchy Overview

The Azure Cosmos DB object model follows this hierarchy:

```
CosmosClient (Account Level)
    ↓
Database (Database Level)
    ↓
Container (Container/Collection Level)
    ↓
Item (Document/Record Level)
```

**Important Notes:**
- `CosmosClient` is thread-safe and should be maintained as a singleton per application lifetime
- All operations use async methods for better performance
- Each level provides methods to work with the level below it

---

## Step 1: Initialize CosmosClient

**First**, create a `CosmosClient` instance to connect to your Azure Cosmos DB account. This is the entry point for all operations.

```csharp
// Initialize the client with endpoint and key
CosmosClient client = new CosmosClient(endpoint, key);
```

**Best Practice:** Maintain a single instance of `CosmosClient` per lifetime of the application for efficient connection management and performance.

---

## Step 2: Database Operations

Once you have a `CosmosClient`, you can perform database-level operations.

### Create a Database

**Option 1:** Create a database (throws exception if it already exists)

```csharp
// Creates a new database - throws exception if database already exists
Database database = await client.CreateDatabaseAsync(
    id: "adventureworks"
);
```

**Option 2:** Create a database only if it doesn't exist (recommended)

```csharp
// Creates a new database only if it doesn't exist
Database database = await client.CreateDatabaseIfNotExistsAsync(
    id: "adventureworks"
);
```

### Read a Database

Get a reference to an existing database and read its properties.

```csharp
// Get a reference to the database
Database database = client.GetDatabase("adventureworks");

// Read the database properties
DatabaseResponse response = await database.ReadAsync();
```

### Delete a Database

Remove a database and all its containers.

```csharp
// Delete the database
await database.DeleteAsync();
```

---

## Step 3: Container Operations

After obtaining a `Database` object, you can perform container-level operations.

### Create a Container

Create a container with a partition key and throughput settings.

```csharp
// Create a container with specified partition key and throughput
ContainerResponse containerResponse = await database.CreateContainerIfNotExistsAsync(
    id: "products",
    partitionKeyPath: "/categoryId",
    throughput: 400  // Minimum value of 400 RU/s
);

// Get the container reference
Container container = containerResponse.Container;
```

**Key Parameters:**
- `id`: Unique name for the container
- `partitionKeyPath`: Property path for partitioning (e.g., `/categoryId`)
- `throughput`: Request Units per second (minimum 400 RU/s)

### Get a Container

Get a reference to an existing container.

```csharp
// Get a reference to the container
Container container = database.GetContainer("products");

// Read the container properties
ContainerProperties containerProperties = await container.ReadContainerAsync();
```

### Delete a Container

Remove a container and all its items.

```csharp
// Delete the container
await database.GetContainer("products").DeleteContainerAsync();
```

---

## Step 4: Item Operations

After obtaining a `Container` object, you can perform CRUD operations on items (documents/records).

### Create an Item

Insert a new item into the container.

```csharp
// Define your data model
public class Product
{
    public string id { get; set; }
    public string name { get; set; }
    public string categoryId { get; set; }  // Partition key
    public decimal price { get; set; }
}

// Create a new item
var newProduct = new Product
{
    id = "product-1",
    name = "Widget",
    categoryId = "electronics",
    price = 99.99m
};

// Insert the item into the container
ItemResponse<Product> response = await container.CreateItemAsync(
    newProduct, 
    new PartitionKey(newProduct.categoryId)
);
```

**Key Points:**
- Object must have an `id` property
- Must provide the partition key value
- Returns `ItemResponse<T>` with metadata

### Read an Item

Retrieve a specific item by its ID and partition key.

```csharp
string itemId = "product-1";
string partitionKeyValue = "electronics";

// Read the item
ItemResponse<Product> response = await container.ReadItemAsync<Product>(
    itemId, 
    new PartitionKey(partitionKeyValue)
);

// Access the item
Product product = response.Resource;
```

**Key Points:**
- Both `id` and partition key are required
- This is a point-read operation (most efficient)

### Query Items

Query multiple items using SQL-like syntax.

```csharp
// Define a parameterized query
QueryDefinition query = new QueryDefinition(
    "SELECT * FROM products p WHERE p.categoryId = @categoryId AND p.price < @maxPrice")
    .WithParameter("@categoryId", "electronics")
    .WithParameter("@maxPrice", 100);

// Execute the query
FeedIterator<Product> resultSet = container.GetItemQueryIterator<Product>(
    query,
    requestOptions: new QueryRequestOptions()
    {
        PartitionKey = new PartitionKey("electronics"),  // Optional: improves performance
        MaxItemCount = 10  // Page size
    });

// Iterate through results
while (resultSet.HasMoreResults)
{
    FeedResponse<Product> response = await resultSet.ReadNextAsync();
    
    foreach (Product product in response)
    {
        Console.WriteLine($"Found: {product.name} - ${product.price}");
    }
}
```

**Key Points:**
- Use parameterized queries to prevent injection
- Results are paginated via `FeedIterator`
- Specifying partition key improves performance

### Query Items with LINQ

You can also use LINQ to query items, which provides compile-time type checking and IntelliSense support.

```csharp
// Using LINQ with ToFeedIterator
var query = container.GetItemLinqQueryable<Product>()
                     .Where(item => item.categoryId == "electronics");
var resultSet = query.ToFeedIterator();

// Iterate through results
while (resultSet.HasMoreResults)
{
    FeedResponse<Product> response = await resultSet.ReadNextAsync();
    foreach (Product product in response)
    {
        Console.WriteLine($"Found: {product.name}");
    }
}
```

**Important:** When querying with a filter condition, use the correct comparison operator:

| Approach | Correct Syntax | Notes |
|----------|---------------|-------|
| SQL Query | `SELECT * FROM c WHERE c.type = 'car'` | Use single `=` for equality |
| LINQ | `.Where(item => item.type == "car")` | Use `==` for equality |

**Common Mistake:** Using `==` in SQL queries (e.g., `c.type == 'car'`) is incorrect SQL syntax. Similarly, using `.Equals()` method in LINQ queries may not translate properly to Cosmos DB queries.

```csharp
// ✅ Correct: SQL query with single equals
var query = new QueryDefinition("SELECT * FROM c WHERE c.type = 'car'");
var resultSet = container.GetItemQueryIterator<Item>(query);

// ✅ Correct: LINQ with == operator
var query = container.GetItemLinqQueryable<Item>()
                     .Where(item => item.type == "car");
var resultSet = query.ToFeedIterator();

// ❌ Incorrect: SQL query with double equals (invalid SQL)
var resultSet = container.GetItemQueryIterator<Item>("SELECT * FROM c WHERE c.type == 'car'");

// ❌ Incorrect: LINQ with .Equals() method (may not translate properly)
var query = container.GetItemLinqQueryable<Item>()
                     .Where(item => item.type.Equals("car"));
var resultSet = query.ToFeedIterator();
```

### Update an Item

Modify an existing item.

```csharp
// Read the item first
ItemResponse<Product> readResponse = await container.ReadItemAsync<Product>(
    "product-1", 
    new PartitionKey("electronics")
);

Product product = readResponse.Resource;

// Modify the item
product.price = 89.99m;

// Replace the item in the database
ItemResponse<Product> updateResponse = await container.ReplaceItemAsync(
    product,
    product.id,
    new PartitionKey(product.categoryId)
);
```

**Alternative - Upsert:** Insert or update if exists

```csharp
// Upsert: Creates if doesn't exist, updates if it does
ItemResponse<Product> upsertResponse = await container.UpsertItemAsync(
    product,
    new PartitionKey(product.categoryId)
);
```

### Delete an Item

Remove an item from the container.

```csharp
string itemId = "product-1";
string partitionKeyValue = "electronics";

// Delete the item
ItemResponse<Product> deleteResponse = await container.DeleteItemAsync<Product>(
    itemId,
    new PartitionKey(partitionKeyValue)
);
```

---

## Complete Workflow Example

Here's a complete example showing the top-to-bottom flow:

```csharp
// Step 1: Initialize Client
CosmosClient client = new CosmosClient(endpoint, key);

// Step 2: Create/Get Database
Database database = await client.CreateDatabaseIfNotExistsAsync("adventureworks");

// Step 3: Create/Get Container
Container container = await database.CreateContainerIfNotExistsAsync(
    id: "products",
    partitionKeyPath: "/categoryId",
    throughput: 400
);

// Step 4: Create an Item
var product = new Product
{
    id = "product-1",
    name = "Laptop",
    categoryId = "electronics",
    price = 999.99m
};

await container.CreateItemAsync(product, new PartitionKey(product.categoryId));

// Step 5: Read the Item
ItemResponse<Product> response = await container.ReadItemAsync<Product>(
    "product-1",
    new PartitionKey("electronics")
);

// Step 6: Update the Item
product.price = 899.99m;
await container.ReplaceItemAsync(product, product.id, new PartitionKey(product.categoryId));

// Step 7: Query Items
QueryDefinition query = new QueryDefinition(
    "SELECT * FROM products p WHERE p.categoryId = @categoryId")
    .WithParameter("@categoryId", "electronics");

FeedIterator<Product> results = container.GetItemQueryIterator<Product>(query);

// Step 8: Delete the Item
await container.DeleteItemAsync<Product>("product-1", new PartitionKey("electronics"));
```

---

## Summary

Follow this hierarchy for all operations:

1. **CosmosClient** → Entry point (singleton)
2. **Database** → Logical grouping of containers
3. **Container** → Stores items with a partition key
4. **Items** → Your actual data (documents/records)

Each level provides methods to access and manipulate the level below it, creating a clear and intuitive API structure.
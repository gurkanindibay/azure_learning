# Effective SQL Queries: 5 Query Optimization Patterns

> **Source**: [Medium — HabibWahid](https://medium.com) · May 27, 2026 · 8 min read  
> **Domain**: SQL, Query Optimization, Database Performance  
> **Related**: [Databases & Query Performance](../../system-design-architecture/01-databases-query-performance.md)

---

## Table of Contents

1. [The Problem with Writing SQL Like a Junior](#the-problem-with-writing-sql-like-a-junior)
2. [Pattern 1: Index-Aware Query Design](#pattern-1-index-aware-query-design)
3. [Pattern 2: SELECT Only What You Need](#pattern-2-select-only-what-you-need)
4. [Pattern 3: Eliminate N+1 Queries at the SQL Level](#pattern-3-eliminate-n1-queries-at-the-sql-level)
5. [Pattern 4: CTEs Over Nested Subqueries](#pattern-4-ctes-over-nested-subqueries)
6. [Pattern 5: EXPLAIN Before You Ship — Always](#pattern-5-explain-before-you-ship--always)
7. [From Queries That Work to Queries That Scale](#from-queries-that-work-to-queries-that-scale)

---

## Introduction

Writing SQL that returns results isn't hard. Writing SQL that doesn't destroy your database at scale — that's what separates juniors from seniors.

```sql
SELECT * FROM orders WHERE customer_id = 1042 ORDER BY created_at DESC;
```

The above query ran in 4ms in development. In production with 1.1 million rows and no index on `customer_id`, it was doing a full table scan on every page load. Forty concurrent users meant forty full table scans, simultaneously, every few seconds.

The database wasn't slow. **The query was wrong.** There's a difference.

Most developers treat SQL as plumbing — write it once, see results, move on. Senior developers treat it as code that has to survive production traffic and growing data. They don't just write queries that return the right data. They write queries that stay fast when your table grows from ten thousand rows to ten million.

---

## The Problem with Writing SQL Like a Junior

Most developers write queries the natural way: describe what you want, let the database figure out how to get it. That works until it doesn't.

```sql
-- ❌ The typical junior query
SELECT * FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE c.email LIKE '%gmail.com'
AND o.status = 'PENDING'
ORDER BY o.created_at DESC;
```

Three quiet catastrophes in one query:

| Issue | Explanation |
|:---|:---|
| `SELECT *` | Fetches every column whether you need it or not |
| `LIKE '%gmail.com'` | Leading wildcard makes index use on `email` impossible |
| No `LIMIT` | Result set grows unboundedly with your data |

It works fine on a test database. On production, it's a ticking clock.

---

## The 5 Patterns Senior Devs Use Instead

### Pattern 1: Index-Aware Query Design

| | |
|:---|:---|
| **Problem** | Writing queries without knowing — or caring — whether the database can use an index to answer them |
| **Root cause** | Functions on indexed columns, leading wildcards, and wrong column order silently disable indexes |

**❌ BAD — Three index killers disguised as normal queries:**

```sql
-- Leading wildcard - no index on email can help
SELECT * FROM customers WHERE email LIKE '%gmail.com';

-- Function on column - disables the index on created_at entirely
SELECT * FROM orders WHERE YEAR(created_at) = 2025;

-- Wrong column order - index is on (status, created_at), query skips status
SELECT * FROM orders WHERE created_at > '2025-01-01';
```

**✅ CORRECT — Index-friendly rewrites:**

```sql
-- Trailing wildcard - index works
SELECT id, name FROM customers WHERE email LIKE 'john%';

-- Range on the column directly - index works
SELECT id, total FROM orders WHERE created_at >= '2025-01-01';

-- Leading column first - composite index (status, created_at) now works
SELECT id, total FROM orders WHERE status = 'PENDING' AND created_at > '2025-01-01';
```

**✅ CORRECT — Declare the composite indexes your queries need:**

```java
@Entity
@Table(name = "orders", indexes = {
    @Index(columnList = "customer_id, status"),
    @Index(columnList = "status, created_at")
})
public class Order { ... }
```

**Why This Matters:**

- An indexed query on 10 million rows runs in under 5ms. An unindexed one runs in 8+ seconds
- Functions applied to indexed columns — `YEAR()`, `LOWER()`, `DATE()` — silently disable the index
- Composite indexes must be ordered correctly — the leading column must appear in your `WHERE` clause
- Run `EXPLAIN ANALYZE` on every significant query before shipping. If you see `Seq Scan`, you're not done

---

### Pattern 2: SELECT Only What You Need

| | |
|:---|:---|
| **Problem** | `SELECT *` feels harmless in development. In production, it fetches every column across every joined table — most of which your application never touches — then ships all of it over the network |
| **Root cause** | Developers don't name columns explicitly, so the database has no choice but to return everything |

**❌ BAD — 50-column products table. You need 3 columns. You get all 50:**

```sql
SELECT * FROM products
JOIN categories c ON products.category_id = c.id
WHERE products.active = true;
```

**✅ CORRECT — Explicit columns only:**

```sql
SELECT p.id, p.name, p.price
FROM products p
WHERE p.active = true
ORDER BY p.created_at DESC
LIMIT 20;
```

**✅ CORRECT — Interface projection enforces this at the ORM layer:**

```java
public interface ProductSummary {
    Long getId();
    String getName();
    BigDecimal getPrice();
}

// JPA fetches only these three columns - not the full entity
Page<ProductSummary> findByActiveTrue(Pageable pageable);
```

**Why This Matters:**

- Explicit columns allow covering indexes — the database answers the query entirely from the index, never touching the table
- Projections eliminate Hibernate's entity tracking overhead on read-only data
- `SELECT *` breaks silently when table schemas change — named columns fail loudly, which is better

---

### Pattern 3: Eliminate N+1 Queries at the SQL Level

| | |
|:---|:---|
| **Problem** | Loading a list, then querying for related data one row at a time. JPA's lazy loading makes this invisible — it looks like a loop in your code, but it's hundreds of database round-trips |
| **Root cause** | ORM lazy-loading hides the cost of repeated child-entity fetches inside loops |

**❌ BAD — Classic N+1: 500 orders = 1,001 queries:**

```java
List<Order> orders = orderRepository.findAll(); // 1 query

orders.forEach(order -> {
    order.getCustomer().getName(); // +1 query per order
    order.getItems().size();       // +1 query per order
});
```

**✅ CORRECT — One query replaces 1,001:**

```sql
SELECT
    o.id, o.total, o.status,
    c.name           AS customer_name,
    COUNT(oi.id)     AS item_count
FROM orders o
JOIN customers c   ON o.customer_id = c.id
LEFT JOIN order_items oi ON oi.order_id = o.id
WHERE o.status = 'PENDING'
GROUP BY o.id, c.name
ORDER BY o.created_at DESC
LIMIT 50;
```

**✅ CORRECT — EntityGraph forces a single JOIN query instead of lazy loading:**

```java
@EntityGraph(attributePaths = {"customer", "items"})
Page<Order> findByStatus(String status, Pageable pageable);
```

**Why This Matters:**

- Every database round trip has fixed overhead — connection, parsing, network — regardless of how small the query is
- 1,001 queries vs 1 query isn't a performance concern — it's a correctness concern at scale
- Use `LEFT JOIN` when related records might not exist — `INNER JOIN` silently drops parent rows that have no children

---

### Pattern 4: CTEs Over Nested Subqueries

| | |
|:---|:---|
| **Problem** | Complex business queries written as deeply nested subqueries become impossible to read, impossible to debug, and give the query planner no room to optimize each step |
| **Root cause** | Nesting obscures the logical flow — each subquery is anonymous and can't be tested independently |

**❌ BAD — Three levels deep. What does this even do at a glance?**

```sql
SELECT customer_id, total_spent FROM (
    SELECT customer_id, SUM(total) AS total_spent
    FROM orders
    WHERE customer_id IN (
        SELECT id FROM customers WHERE country = 'US'
    )
    AND status = 'COMPLETED'
    GROUP BY customer_id
) AS summary
WHERE total_spent > 1000;
```

**✅ CORRECT — Same result, each step is named and debuggable in isolation:**

```sql
WITH us_customers AS (
    SELECT id, name FROM customers WHERE country = 'US'
),
completed_orders AS (
    SELECT o.customer_id, SUM(o.total) AS total_spent
    FROM orders o
    JOIN us_customers uc ON o.customer_id = uc.id
    WHERE o.status = 'COMPLETED'
    GROUP BY o.customer_id
    HAVING SUM(o.total) > 1000
)
SELECT uc.name, co.total_spent
FROM completed_orders co
JOIN us_customers uc ON co.customer_id = uc.id
ORDER BY co.total_spent DESC;
```

**✅ CORRECT — CTE lives in a custom repository implementation:**

```java
@Override
public List<CustomerSpendDTO> findHighValueCustomers(String country) {
    String sql = """
        WITH target AS (
            SELECT id, name FROM customers WHERE country = :country
        ),
        spend AS (
            SELECT customer_id, SUM(total) AS total_spent
            FROM orders WHERE status = 'COMPLETED'
            GROUP BY customer_id HAVING SUM(total) > 1000
        )
        SELECT t.name, s.total_spent FROM spend s JOIN target t ON s.customer_id = t.id
    """;
    return em.createNativeQuery(sql, "CustomerSpendMapping")
        .setParameter("country", country)
        .getResultList();
}
```

**Why This Matters:**

- You can run any individual CTE as a standalone query to debug it — impossible with nested subqueries
- Readable queries get reviewed properly. Unreadable ones get rubber-stamped and shipped
- PostgreSQL and MySQL 8+ optimize CTEs as well as nested subqueries — no performance penalty for clarity

---

### Pattern 5: EXPLAIN Before You Ship — Always

| | |
|:---|:---|
| **Problem** | Shipping queries without ever looking at how the database actually executes them. The query looks correct, the results look right, and the execution plan is scanning 4 million rows every time |
| **Root cause** | Developers test for correctness, not for execution plan — the two are unrelated |

**❌ BAD — Written, tested, shipped — query plan never checked:**

```java
@Query("SELECT o FROM Order o WHERE o.status = :status AND o.createdAt > :since")
List<Order> findForReport(String status, LocalDateTime since);
// Does this use an index? Unknown. You'll find out from a production incident.
```

**✅ CORRECT — Read the plan before users see the latency:**

```sql
EXPLAIN ANALYZE
SELECT o.id, o.total, c.name
FROM orders o JOIN customers c ON o.customer_id = c.id
WHERE o.status = 'PENDING' AND o.created_at > '2025-01-01'
ORDER BY o.created_at DESC LIMIT 50;
```

**Reading the output:**

```text
-- ✅ Good signs:
--   "Index Scan using idx_orders_status_created" → index is being used
--   "rows=50" near a LIMIT node → database stops early

-- ❌ Bad signs — fix before shipping:
--   "Seq Scan on orders  rows=1200000" → full table scan, add an index
--   "Sort  rows=800000" → sorting before LIMIT, add index on ORDER BY column
```

**✅ CORRECT — Enable Hibernate statistics in dev to surface slow queries automatically:**

```properties
# application-dev.properties
spring.jpa.properties.hibernate.generate_statistics=true
logging.level.org.hibernate.stat=DEBUG
```

**Why This Matters:**

- `EXPLAIN` is free. Diagnosing a production slowdown at 2 AM is not
- Query plans change as data grows — a plan that uses an index today may switch to a seq scan at 10× volume
- Hibernate statistics surface N+1 problems and slow query counts without touching the database logs at all

---

## From Queries That Work to Queries That Scale

The difference between junior and senior SQL isn't syntax. It's understanding that the database treats every query as a contract — and a poorly written contract gets expensive exactly when you can least afford it.

**Before:**

```java
// Full entity, no limit, no index guarantee, plan never checked
List<Order> findByStatus(String status);
```

**After:**

```java
@Transactional(readOnly = true)
@EntityGraph(attributePaths = {"customer"})
@Query("SELECT new com.example.dto.OrderSummary(o.id, o.total, c.name) " +
       "FROM Order o JOIN o.customer c " +
       "WHERE o.status = :status AND o.createdAt > :since " +
       "ORDER BY o.createdAt DESC")
Page<OrderSummary> findByStatus(String status, LocalDateTime since, Pageable pageable);
```

---

## Summary: The 5 Patterns

| # | Pattern | Key Principle |
|:---|:---|:---|
| 1 | **Index-Aware Design** | Write queries the index can answer — not queries the database has to brute-force |
| 2 | **SELECT Explicitly** | Fetch only the columns your caller needs, nothing more |
| 3 | **Eliminate N+1** | One JOIN replaces a thousand lazy-loaded round trips |
| 4 | **CTEs over Subqueries** | Name your logic, debug each step independently |
| 5 | **EXPLAIN Before You Ship** | See the execution plan before your users do |

---

## The Truth About SQL at Scale

Junior developers write queries that return the right data. Senior developers write queries that return the right data — and stay fast when the table grows from 10,000 rows to 10,000,000.

The database doesn't care that your query was readable. It doesn't care that the results were correct. **It cares about how many rows it had to examine to find your answer.** That number is the only one that matters at 2 AM on a Wednesday when production is on fire, and your query log is full of full table scans.

> **Learn to think like the query planner. Everything else follows.**

---
type: Article
title: "Most Developers Think HashMap Is Always O(1). That’s Not True."
description: "Why Java HashMap’s O(1) guarantee is conditional: hash collisions, linked-list degradation, Java 8 treeification rules, and production implications."
source: "https://medium.com/@kanishks772/most-developers-think-hashmap-is-always-o-1-thats-not-true-a8b12dac3705"
author:
  - "[[The Latency Gambler]]"
published: 2026-03-14
created: 2026-06-23
tags:
  - "clippings"
  - "java"
  - "data-structures"
  - "performance"
---

# Most Developers Think HashMap Is Always O(1). That’s Not True.

*The hidden mechanics inside your buckets and why they matter more than you think.*

Every developer has typed `map.get(key)` and assumed it runs in constant time. That assumption is mostly right — but "mostly" is doing a lot of heavy lifting.

![HashMap buckets visualized](https://miro.medium.com/v2/resize:fit:1400/format:webp/0*I8G7-4b56g_w3uK8)

*AI-generated image*

HashMap’s O(1) guarantee is **conditional**. When conditions break down, so does your performance. And in production systems under load, that breakdown can be quietly catastrophic.

## The Bucket Model (Quick Refresher)

A HashMap stores entries by hashing the key to an index in an internal array. Ideally, keys spread evenly across buckets:

```text
Key ──► hashCode() ──► index ──► Bucket

  [ 0 ] → [ "apple" ]
  [ 1 ] → [ "mango" ]
  [ 2 ] → [ "grape" ]
  [ 3 ] → (empty)
```

One key per bucket? Lookup is O(1). Clean and fast.

But hash functions aren’t magic. Two different keys can produce the same index — a **hash collision**. When that happens, entries stack up inside a single bucket as a linked list:

```text
[ 2 ] → ["grape"] → ["guava"] → ["grapefruit"] → null
```

Now a lookup at index 2 has to walk that list. With *n* entries in the same bucket, you’re back to **O(n)**. In adversarial conditions — like carefully crafted input keys — this can be exploited to degrade a service intentionally.

## What Java 8 Quietly Changed

Before Java 8, HashMap always used linked lists for collision chains. After Java 8, it got smarter.

When a single bucket grows beyond **8 entries**, the structure inside that bucket automatically converts from a linked list to a **Red-Black Tree**:

```text
BEFORE (Linked List):          AFTER (Red-Black Tree):

[head]                              [D]
    │                               /     \
   [A]→[B]→[C]→[D]→[E]→...       [B]     [F]
                                  / \     / \
                                [A] [C] [E] [G]
```

A Red-Black Tree is a self-balancing binary search tree. What does that mean for lookup?

| Structure | Worst-case Lookup |
|:---|:---|
| Linked List | O(n) |
| Red-Black Tree | O(log n) |

That’s not just a theoretical win. In a bucket with 1,000 colliding entries, a linked list requires up to 1,000 comparisons. A Red-Black Tree caps it at ~10.

## The Treeification Rule Has a Catch

Here’s the part most engineers never encounter in a tutorial.

**Treeification** — the conversion from list to tree — only triggers when **two conditions are met simultaneously**:

1. A bucket holds more than **8 entries**.
2. The HashMap’s total capacity is at least **64**.

```java
// From OpenJDK source (simplified)
static final int TREEIFY_THRESHOLD = 8;
static final int MIN_TREEIFY_CAPACITY = 64;

// Inside HashMap:
if (binCount >= TREEIFY_THRESHOLD - 1)
    treeifyBin(tab, hash);

// Inside treeifyBin():
if (tab == null || (n = tab.length) < MIN_TREEIFY_CAPACITY)
    resize(); // resize instead of treeify
```

If the backing array is smaller than 64, the JVM chooses to **resize the map** rather than convert the structure. Why? Because resizing rehashes all keys and typically redistributes them across more buckets — eliminating the collision without needing a tree at all.

This is sensible default behavior. But it means you can’t assume treeification is always protecting you.

## A Demonstrable Example

```java
import java.util.HashMap;

public class CollisionDemo {
    // These keys are crafted to collide in a default HashMap
    static final String[] COLLIDING_KEYS = {
        "Aa", "BB", "Ca", "DB", "Ea", "FB", "Ga", "HB",
        "Ia", "JB" // 10 keys - enough to trigger treeification
    };

    public static void main(String[] args) {
        HashMap<String, Integer> map = new HashMap<>(128); // capacity > 64
        for (int i = 0; i < COLLIDING_KEYS.length; i++) {
            map.put(COLLIDING_KEYS[i], i);
        }
        // Internally, one bucket now holds a Red-Black Tree
        // Lookups here are O(log n), not O(n)
        System.out.println(map.get("HB")); // Still works - and faster than a list
    }
}
```

Note: `"Aa"` and `"BB"` share the same `hashCode()` in Java (`'A'*31 + 'a'` == `'B'*31 + 'B'`). This is real behavior, not contrived.

## The Architecture at a Glance

```text
HashMap Internal Structure
  ──────────────────────────

Bucket Array
  ┌───┬───┬───┬───┬───┬───┐
  │ 0 │ 1 │ 2 │ 3 │ 4 │...│
  └───┴───┴┬──┴───┴───┴───┘
           │
           ▼
     ┌─────────────────────────────────────┐
     │  entries ≤ 8  →  Linked List        │
     │  entries > 8  →  Red-Black Tree     │
     │  (only if total capacity ≥ 64)      │
     └─────────────────────────────────────┘
```

## What This Means in Practice

HashMap isn’t a simple key-value store sitting on an array. It’s a **hybrid adaptive structure** that shifts its internal representation based on runtime conditions.

A few practical implications:

- **Poor hash functions hurt more than you think.** If your custom `hashCode()` creates collisions, you're building linked lists, not trees.
- **Small maps don’t treeify.** If your HashMap is used with limited capacity (common in config maps or caches), you might never get tree protection.
- **Concurrent maps have different rules.** `ConcurrentHashMap` also treeifies, but its segment locking interacts with this in ways worth reading separately.

The real takeaway isn’t to distrust HashMap — it remains one of the most well-engineered data structures in the JDK. The takeaway is that **performance guarantees have preconditions**, and understanding those preconditions is what separates good engineers from great ones.

---

*HashMap documentation:* [*OpenJDK source*](https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/util/HashMap.java)

---
type: Architecture Pattern
title: "Event Storming"
description: "**Event Storming** is a collaborative workshop technique for discovering and modeling complex business domains. Created by **Alberto Brandolini**, it brings together domain experts and developers t..."
tags: [application-software-architecture, domain-driven-design]
timestamp: 2026-06-14T00:00:00Z
---

# Event Storming

## Table of Contents

- [Overview](#overview)
- [What is Event Storming?](#what-is-event-storming)
- [Why Event Storming?](#why-event-storming)
- [Key Participants](#key-participants)
- [Core Building Blocks](#core-building-blocks)
- [The Sticky Note Color Code](#the-sticky-note-color-code)
- [Event Storming Formats](#event-storming-formats)
- [Step-by-Step Process](#step-by-step-process)
- [Visual Example: E-Commerce Order Flow](#visual-example-e-commerce-order-flow)
- [Identifying Bounded Contexts](#identifying-bounded-contexts)
- [Common Patterns Discovered](#common-patterns-discovered)
- [Tips for Facilitation](#tips-for-facilitation)
- [Remote Event Storming](#remote-event-storming)
- [Outcomes and Artifacts](#outcomes-and-artifacts)
- [Common Pitfalls](#common-pitfalls)
- [Event Storming vs Other Techniques](#event-storming-vs-other-techniques)
- [References](#references)

## Overview

**Event Storming** is a collaborative workshop technique for discovering and modeling complex business domains. Created by **Alberto Brandolini**, it brings together domain experts and developers to explore business processes through **domain events**—things that happen in the system that are relevant to the business.

> "Event Storming is a flexible workshop format for collaborative exploration of complex business domains."  
> — Alberto Brandolini

## What is Event Storming?

Event Storming is a **visual, collaborative** workshop where participants:

1. **Explore** a business domain by identifying events
2. **Discover** the commands, actors, and policies that trigger events
3. **Visualize** the entire process on a large modeling surface
4. **Identify** boundaries, problems, and opportunities

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Event Storming Session                       │
│                                                                      │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│   │ Domain  │  │  Dev    │  │  Dev    │  │ Product │  │   UX    │  │
│   │ Expert  │  │  Team   │  │  Lead   │  │ Owner   │  │Designer │  │
│   └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘  │
│        │            │            │            │            │        │
│        └────────────┴────────────┴────────────┴────────────┘        │
│                              │                                       │
│                              ▼                                       │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    Large Modeling Surface                    │   │
│   │                       (Wall / Miro)                          │   │
│   │                                                              │   │
│   │   🟧 🟧 🟧 🟦 🟧 🟨 🟧 🟪 🟧 🟧 🟩 🟧 🟥 🟧 🟧            │   │
│   │                                                              │   │
│   │         ──────────────────────────────────────►              │   │
│   │                      Timeline                                │   │
│   └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Why Event Storming?

| Benefit | Description |
|---------|-------------|
| **Shared Understanding** | Developers and domain experts speak the same language |
| **Fast Discovery** | Explore complex domains in hours, not weeks |
| **Uncover Hidden Knowledge** | Surface tacit knowledge from experts |
| **Identify Problems** | Find bottlenecks, pain points, and inconsistencies |
| **Define Boundaries** | Discover natural bounded contexts for microservices |
| **Alignment** | Everyone sees the big picture together |
| **No Technical Prerequisites** | Non-technical stakeholders can participate fully |

### Traditional vs Event Storming

```
Traditional Approach:
─────────────────────
Weeks of meetings → Requirements document → Review → Misunderstandings → Rework

Event Storming:
───────────────
2-4 hour workshop → Shared visual model → Immediate feedback → Aligned team
```

## Key Participants

| Role | Contribution |
|------|--------------|
| **Domain Experts** | Know how the business actually works |
| **Developers** | Ask clarifying questions, identify technical concerns |
| **Product Owner** | Prioritize and scope |
| **UX Designer** | User journey perspective |
| **Facilitator** | Guide the process, keep energy high |
| **Architect** | Identify system boundaries |

**Ideal group size:** 6-10 people (small enough to collaborate, large enough for diverse perspectives)

## Core Building Blocks

### The Elements

```
┌────────────────────────────────────────────────────────────────────┐
│                    Event Storming Building Blocks                   │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   🟧 DOMAIN EVENT          🟦 COMMAND             🟨 ACTOR          │
│   ┌─────────────────┐      ┌─────────────────┐   ┌─────────────┐   │
│   │                 │      │                 │   │   👤        │   │
│   │ Order Placed    │      │ Place Order     │   │   Customer  │   │
│   │                 │      │                 │   │             │   │
│   └─────────────────┘      └─────────────────┘   └─────────────┘   │
│   Something that           Action that causes    Person/system     │
│   happened (past tense)    an event              that triggers     │
│                                                                     │
│   🟪 POLICY/RULE           🟩 READ MODEL          🟥 HOT SPOT      │
│   ┌─────────────────┐      ┌─────────────────┐   ┌─────────────┐   │
│   │                 │      │                 │   │     ⚠️      │   │
│   │ When order >$100│      │ Order Summary   │   │  Unclear    │   │
│   │ apply discount  │      │ View            │   │  process!   │   │
│   └─────────────────┘      └─────────────────┘   └─────────────┘   │
│   Business rule that       Information needed    Problem, question │
│   triggers events          to make decisions     or conflict       │
│                                                                     │
│   🟫 AGGREGATE             ⬜ EXTERNAL SYSTEM                       │
│   ┌─────────────────┐      ┌─────────────────┐                     │
│   │                 │      │                 │                     │
│   │     Order       │      │ Payment Gateway │                     │
│   │                 │      │                 │                     │
│   └─────────────────┘      └─────────────────┘                     │
│   Entity that handles      Third-party system                      │
│   commands & events                                                 │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

## The Sticky Note Color Code

| Color | Element | Description | Example |
|-------|---------|-------------|---------|
| 🟧 **Orange** | Domain Event | Something that happened | "Order Placed" |
| 🟦 **Blue** | Command | Action that triggers event | "Place Order" |
| 🟨 **Yellow** | Actor/User | Who performs the action | "Customer" |
| 🟪 **Purple/Lilac** | Policy | Business rule (when...then) | "When paid, ship order" |
| 🟩 **Green** | Read Model | Information needed | "Product Catalog" |
| 🟥 **Red/Pink** | Hot Spot | Problem or question | "What if payment fails?" |
| 🟫 **Tan/Pale Yellow** | Aggregate | Entity handling commands | "Order" |
| ⬜ **White/Pink** | External System | Third-party integration | "Stripe API" |

## Event Storming Formats

### 1. Big Picture Event Storming

**Purpose:** Explore entire business domain, find bounded contexts  
**Duration:** 2-4 hours  
**Scope:** High-level, end-to-end process

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Big Picture Event Storming                      │
│                                                                      │
│   Customer Journey: Browse → Order → Payment → Fulfillment          │
│                                                                      │
│   🟧────🟧────🟧────🟧────🟧────🟧────🟧────🟧────🟧────🟧          │
│                                                                      │
│   Focus: What happens in the business?                              │
│   Output: Domain overview, bounded contexts, hot spots              │
└─────────────────────────────────────────────────────────────────────┘
```

### 2. Process Modeling Event Storming

**Purpose:** Detail a specific business process  
**Duration:** 2-4 hours  
**Scope:** Single process or subdomain

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Process Modeling Event Storming                   │
│                                                                      │
│   Order Checkout Process (detailed):                                │
│                                                                      │
│   🟨→🟦→🟧→🟪→🟦→🟧→⬜→🟧→🟦→🟧                                    │
│   │  │  │  │  │  │  │  │  │  │                                      │
│   │  │  │  │  │  │  │  │  │  └── Order Confirmed                    │
│   │  │  │  │  │  │  │  │  └───── Confirm Order                      │
│   │  │  │  │  │  │  │  └──────── Payment Received                   │
│   │  │  │  │  │  │  └─────────── Payment Gateway                    │
│   │  │  │  │  │  └────────────── Payment Processed                  │
│   │  │  │  │  └───────────────── Process Payment                    │
│   │  │  │  └──────────────────── When cart valid, request payment   │
│   │  │  └─────────────────────── Cart Validated                     │
│   │  └────────────────────────── Submit Cart                        │
│   └───────────────────────────── Customer                           │
│                                                                      │
│   Focus: How does this process work in detail?                      │
│   Output: Detailed flow, commands, policies, aggregates             │
└─────────────────────────────────────────────────────────────────────┘
```

### 3. Software Design Event Storming

**Purpose:** Design software implementation  
**Duration:** 4-8 hours  
**Scope:** Technical design with aggregates, bounded contexts

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Software Design Event Storming                    │
│                                                                      │
│   ┌─────────────────┐    ┌─────────────────┐    ┌────────────────┐  │
│   │ Order Context   │    │ Payment Context │    │ Shipping       │  │
│   │                 │    │                 │    │ Context        │  │
│   │  🟫 Order       │───►│  🟫 Payment     │───►│  🟫 Shipment   │  │
│   │  🟧 Events...   │    │  🟧 Events...   │    │  🟧 Events...  │  │
│   └─────────────────┘    └─────────────────┘    └────────────────┘  │
│                                                                      │
│   Focus: How do we build this?                                      │
│   Output: Aggregates, bounded contexts, integration points          │
└─────────────────────────────────────────────────────────────────────┘
```

## Step-by-Step Process

### Phase 1: Chaotic Exploration (15-30 min)

**Goal:** Get all domain events on the wall

```
Instructions:
─────────────
1. Everyone grabs orange sticky notes
2. Write ONE event per sticky (past tense!)
3. Place on wall roughly in time order (left to right)
4. No discussion yet—just dump everything
5. Duplicates are OK for now

Result:
───────
🟧 🟧   🟧 🟧 🟧   🟧   🟧 🟧 🟧   🟧 🟧
  🟧 🟧     🟧   🟧 🟧     🟧 🟧 🟧     🟧
    🟧       🟧             🟧       🟧
          (Chaos is expected!)
```

### Phase 2: Timeline Enforcement (15-20 min)

**Goal:** Organize events chronologically

```
Instructions:
─────────────
1. Group related events
2. Remove exact duplicates
3. Arrange left-to-right in time order
4. Start discussions: "Does X happen before Y?"

Result:
───────
Start ──►                                            ──► End
🟧───🟧───🟧───🟧───🟧───🟧───🟧───🟧───🟧───🟧───🟧───🟧
         (Organized timeline)
```

### Phase 3: Identify Pain Points (10-15 min)

**Goal:** Mark problems, questions, conflicts

```
Instructions:
─────────────
1. Add 🟥 red/pink stickies for:
   - Unclear processes
   - Conflicting opinions
   - Missing information
   - Known problems

Result:
───────
🟧───🟧───🟧───🟥───🟧───🟧───🟥───🟧───🟧───🟥───🟧
              ⚠️           ⚠️           ⚠️
         "What if       "Who        "How long
         order fails?"  approves?"   to wait?"
```

### Phase 4: Add Commands and Actors (20-30 min)

**Goal:** Discover what triggers events

```
Instructions:
─────────────
1. For each event, ask "What caused this?"
2. Add 🟦 blue command in front of event
3. Add 🟨 yellow actor above command

Result:
───────
      🟨              🟨              🟨
   Customer        System         Warehouse
      │               │               │
      ▼               ▼               ▼
   🟦 Place       🟦 Validate     🟦 Ship
      Order          Payment         Order
      │               │               │
      ▼               ▼               ▼
   🟧 Order       🟧 Payment      🟧 Order
      Placed         Validated       Shipped
```

### Phase 5: Add Policies and Read Models (15-20 min)

**Goal:** Capture business rules and information needs

```
Instructions:
─────────────
1. Add 🟪 purple policies between events
   "When X happens, then do Y"
2. Add 🟩 green read models for information needed

Result:
───────
                    🟩 Order
                       Details
                         │
      🟨                 │              🟨
   Customer              │           System
      │                  │              │
      ▼                  ▼              ▼
   🟦 Place ─────► 🟪 When order ─► 🟦 Process
      Order          placed,           Payment
      │              validate          │
      ▼              payment           ▼
   🟧 Order    ─────────────────►  🟧 Payment
      Placed                          Processed
```

### Phase 6: Identify Aggregates and Boundaries (20-30 min)

**Goal:** Group related elements, find bounded contexts

```
Instructions:
─────────────
1. Add 🟫 tan stickies for aggregates (entities that handle commands)
2. Draw boundaries around related clusters
3. Name each bounded context

Result:
───────
┌─ Order Context ────────────┐  ┌─ Payment Context ──────────┐
│                            │  │                            │
│  🟫 Order                  │  │  🟫 Payment                │
│     │                      │  │     │                      │
│  🟦─┴─🟧───🟧───🟧         │──│  🟦─┴─🟧───🟧              │
│                            │  │                            │
└────────────────────────────┘  └────────────────────────────┘
```

## Visual Example: E-Commerce Order Flow

```
═══════════════════════════════════════════════════════════════════════════════
                         E-COMMERCE ORDER FLOW
═══════════════════════════════════════════════════════════════════════════════

  BROWSE              ORDER                PAYMENT             FULFILLMENT
  CONTEXT             CONTEXT              CONTEXT             CONTEXT
 ┌──────────┐       ┌───────────┐        ┌───────────┐       ┌───────────┐
 │          │       │           │        │           │       │           │
 │  🟨 Cust │       │  🟨 Cust  │        │  🟨 Syst  │       │  🟨 Wareh │
 │    │     │       │    │      │        │    │      │       │    │      │
 │    ▼     │       │    ▼      │        │    ▼      │       │    ▼      │
 │ 🟦Browse │       │ 🟦 Add    │        │ 🟦Process │       │ 🟦 Pick   │
 │  Catalog │       │   to Cart │        │  Payment  │       │   Items   │
 │    │     │       │    │      │        │    │      │       │    │      │
 │    ▼     │       │    ▼      │        │    ▼      │       │    ▼      │
 │ 🟧Product│       │ 🟧 Item   │        │ 🟧Payment │       │ 🟧 Items  │
 │  Viewed  │       │   Added   │        │  Processed│       │   Picked  │
 │          │       │    │      │        │    │      │       │    │      │
 │ 🟩Product│       │    ▼      │        │    │      │       │    ▼      │
 │  Catalog │       │ 🟦Checkout│        │    │      │       │ 🟦 Ship   │
 │          │       │    │      │        │    │      │       │   Order   │
 │          │       │    ▼      │        │    │      │       │    │      │
 │          │       │ 🟧 Order  │───────►│    │      │       │    ▼      │
 │          │       │   Placed  │        │    │      │       │ 🟧 Order  │
 │          │       │           │        │    │      │       │   Shipped │
 │          │       │    🟪     │        │    ▼      │       │           │
 │          │       │  When     │        │   🟪      │       │    🟪     │
 │          │       │  placed,  │───────►│ When paid │──────►│ When ship │
 │          │       │  charge   │        │ fulfill   │       │ notify    │
 │          │       │           │        │           │       │ customer  │
 │          │       │   🟥      │        │   🟥      │       │           │
 │          │       │ What if   │        │ Timeout?  │       │           │
 │          │       │ OOS?      │        │           │       │           │
 │          │       │           │        │           │       │           │
 │  🟫      │       │  🟫       │        │  🟫       │       │  🟫       │
 │ Product  │       │  Order    │        │  Payment  │       │ Shipment  │
 └──────────┘       └───────────┘        └───────────┘       └───────────┘
      │                   │                    │                   │
      │                   │                    │                   │
      └───────────────────┴────────────────────┴───────────────────┘
                                    │
                              ⬜ Stripe API
                              ⬜ Shipping Provider
```

## Identifying Bounded Contexts

Event Storming naturally reveals **bounded contexts**—areas where:
- Language changes (same word, different meaning)
- Different teams own different parts
- Clear integration points exist

### Signs of Boundaries

```
Look for:
─────────
1. 🔄 Pivotal Events - Events that trigger new phases
   "Order Placed" → shifts from shopping to fulfillment

2. 📝 Language Changes - Same term, different meaning
   "Order" in Sales vs "Order" in Warehouse

3. 👥 Different Actors - Different people/systems involved
   Customer vs Warehouse Staff vs Finance

4. ⏰ Time Gaps - Natural delays between processes
   Order → Payment processing → Shipping (hours/days)

5. 🔴 Swimlanes - Events cluster into distinct flows
```

### Boundary Visualization

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Discovering Bounded Contexts                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Before (flat timeline):                                            │
│  🟧─🟧─🟧─🟧─🟧─🟧─🟧─🟧─🟧─🟧─🟧─🟧─🟧─🟧─🟧─🟧                    │
│                                                                      │
│  After (bounded contexts identified):                               │
│                                                                      │
│  ┌─ Sales ─────────┐  ┌─ Payment ────┐  ┌─ Fulfillment ──────────┐ │
│  │ 🟧─🟧─🟧─🟧─🟧  │──│ 🟧─🟧─🟧    │──│ 🟧─🟧─🟧─🟧─🟧─🟧     │ │
│  │                 │  │              │  │                        │ │
│  │ "Order" = what  │  │ "Order" =    │  │ "Order" = items to    │ │
│  │ customer wants  │  │ what to      │  │ pick and ship         │ │
│  │                 │  │ charge       │  │                        │ │
│  └─────────────────┘  └──────────────┘  └────────────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Common Patterns Discovered

### 1. Pivotal Events

Events that represent major state transitions:

```
🟧 Order Placed        → Triggers fulfillment
🟧 Payment Received    → Triggers shipping
🟧 Item Shipped        → Triggers notifications
🟧 Return Requested    → Triggers reverse logistics
```

### 2. Swimlanes

Parallel processes that happen simultaneously:

```
┌─ Main Flow ────────────────────────────────────────────┐
│ 🟧 Order Placed → 🟧 Payment OK → 🟧 Order Shipped     │
└────────────────────────────────────────────────────────┘
          │
          ├──────────────────────────────────────────────┐
          │              Parallel Processes              │
          │                                              │
┌─────────▼──────────┐  ┌─────────────────────────────┐ │
│ 🟧 Inventory       │  │ 🟧 Fraud Check Started      │ │
│    Reserved        │  │ 🟧 Fraud Check Passed       │ │
└────────────────────┘  └─────────────────────────────┘ │
                                                        │
└───────────────────────────────────────────────────────┘
```

### 3. Exception Flows

What happens when things go wrong:

```
Happy Path:
🟧 Order Placed → 🟧 Payment OK → 🟧 Shipped

Exception Paths:
🟧 Order Placed → 🟧 Payment Failed → 🟧 Customer Notified → 🟧 Order Cancelled
🟧 Order Placed → 🟧 Out of Stock → 🟧 Backordered
🟧 Shipped → 🟧 Delivery Failed → 🟧 Return to Sender
```

## Tips for Facilitation

### Do's ✅

| Tip | Why |
|-----|-----|
| **Use a LARGE space** | Need room to spread out (8+ meters of wall) |
| **Enforce past tense** | "Order Placed" not "Place Order" |
| **Encourage chaos first** | Don't organize too early |
| **Welcome conflicts** | Different views = valuable discussion |
| **Take breaks** | Every 45-60 minutes |
| **Capture hot spots** | Don't solve problems, just mark them |
| **Stand up** | Keeps energy high |

### Don'ts ❌

| Anti-pattern | Problem |
|--------------|---------|
| **Too few people** | Missing perspectives |
| **Too many people** | Can't collaborate (max 10-12) |
| **Solving during discovery** | Slows down exploration |
| **Digital-only from start** | Loses tactile engagement |
| **Facilitator dominates** | Should guide, not dictate |
| **Skipping domain experts** | Technical-only view is incomplete |

## Remote Event Storming

### Tools for Virtual Sessions

| Tool | Strengths |
|------|-----------|
| **Miro** | Best sticky note simulation, templates |
| **Mural** | Good collaboration features |
| **FigJam** | Simple, integrates with Figma |
| **Lucidspark** | Good for larger teams |

### Remote Tips

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Remote Event Storming Setup                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. Pre-work: Send color legend and examples                        │
│  2. Shorter sessions: 90 min max (screen fatigue)                   │
│  3. Cameras on: Maintain engagement                                 │
│  4. Breakout rooms: Small group discussions                         │
│  5. Clear zones: Divide board into sections                         │
│  6. Facilitator controls: Prevent chaos                             │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                         Miro Board                            │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │  │
│  │  │ Parking │ │ Start   │ │ Middle  │ │ End     │ │ Legend  │ │  │
│  │  │ Lot     │ │ Events  │ │ Events  │ │ Events  │ │         │ │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Outcomes and Artifacts

### What You Get

| Artifact | Use |
|----------|-----|
| **Domain Events List** | Input for event sourcing |
| **Bounded Contexts** | Microservice boundaries |
| **Ubiquitous Language** | Shared vocabulary |
| **Hot Spots** | Prioritized problem list |
| **Process Flows** | Documentation |
| **Aggregate Candidates** | DDD implementation guide |
| **Integration Points** | API/event contracts |

### Translating to Code

```
Event Storming                    Code
──────────────────────────────────────────────────────
🟧 Order Placed         →    OrderPlacedEvent
🟦 Place Order          →    PlaceOrderCommand
🟨 Customer             →    CustomerRole / Actor
🟪 When paid, ship      →    OrderPaidPolicy
🟫 Order                →    OrderAggregate
🟩 Order Summary        →    OrderSummaryReadModel
⬜ Payment Gateway      →    IPaymentGateway interface
```

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| **Modeling the solution, not domain** | Focus on business events, not technical |
| **Too detailed too soon** | Start with big picture |
| **No domain experts** | Reschedule if they can't attend |
| **Trying to be complete** | It's exploration, not documentation |
| **Analysis paralysis on hot spots** | Mark and move on |
| **Digital tools too early** | Start physical if possible |
| **No follow-up** | Plan next steps immediately |

## Event Storming vs Other Techniques

| Technique | Focus | When to Use |
|-----------|-------|-------------|
| **Event Storming** | Domain events, processes | Domain discovery, DDD |
| **User Story Mapping** | User journeys, features | Product planning |
| **Process Mapping** | Workflows, steps | Process improvement |
| **Domain Modeling** | Entities, relationships | Data design |
| **Impact Mapping** | Goals, outcomes | Strategy alignment |
| **Wardley Mapping** | Value chain, evolution | Strategic planning |

### Complementary Usage

```
1. Event Storming      → Discover the domain
2. Domain Modeling     → Design the entities  
3. User Story Mapping  → Plan the features
4. Implementation      → Build the system
```

## References

- [Alberto Brandolini - Introducing Event Storming](https://www.eventstorming.com/)
- [Event Storming Book (Leanpub)](https://leanpub.com/introducing_eventstorming)
- [DDD Europe - Event Storming Talks](https://www.youtube.com/results?search_query=event+storming+ddd+europe)
- [Miro Event Storming Template](https://miro.com/templates/event-storming/)
- [Virtual Event Storming Guide](https://www.eventstorming.com/resources/)
- [Domain-Driven Design Reference](https://www.domainlanguage.com/ddd/reference/)

---
type: Article
title: "Event-Driven vs. Workflow-Driven Architecture: How to Choose"
source: "https://levelup.gitconnected.com/event-driven-vs-workflow-driven-architecture-how-to-choose-8619cf96e2a5"
author:
  - "Daniel Stauffer"
published: 2026-09-17
created: 2026-10-04
description: "Choosing between event-driven and workflow-driven architecture: choreography vs orchestration tradeoffs, distributed spaghetti trap, decision framework, and hybrid partition patterns."
tags:
  - "event-driven-architecture"
  - "workflow-orchestration"
  - "saga-pattern"
  - "messaging"
  - "system-design"
---

# Event-Driven vs. Workflow-Driven Architecture: How to Choose

> **Series**: Part 3 of Architecture Tradecraft  
> **Author**: Daniel Stauffer  
> **Source**: [Level Up Coding / Medium](https://levelup.gitconnected.com/event-driven-vs-workflow-driven-architecture-how-to-choose-8619cf96e2a5)  
> **Related Takeaways**: [Event-Driven vs. Workflow-Driven Architecture — Key Takeaways](../../system-design-architecture/messaging/event-driven-vs-workflow-driven-takeaways.md)

> Both patterns handle async processes. One gives you decoupling. One gives you visibility. The teams that get this wrong end up with systems that are impossible to debug and even harder to change.

![Event-Driven vs Workflow-Driven Architecture](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*FbzsA_t0mrB55_8ewyUyzg.jpeg)

*Part 3 of my series on [Architecture Tradecraft](https://medium.com/@the-architect-ds/list/architecture-tradecraft-793021113071). Last time, we covered [when NOT to use microservices](https://medium.com/gitconnected/when-not-to-use-microservices-92dfcc0bcfef): the decision framework that prevents distributed monoliths. This time: one of the most consequential async architecture decisions you’ll make, choosing between event-driven and workflow-driven, and why teams consistently underestimate the consequences until they’re living with them. Follow along for more on how senior architects actually make decisions.*

There’s a conversation I’ve had with engineering teams at least a dozen times. It starts with: “We went event-driven 18 months ago and we can’t tell what’s happening in our system anymore.” Sometimes the variant is: “We tried to implement a saga for our order flow and it’s unmaintainable.” Occasionally: “Our Kafka topics have 40 consumers and we have no idea who owns which.”

The pattern underneath all of these is the same. The team chose an architecture pattern (event-driven, saga, event sourcing) because it was the right answer to one set of questions, then discovered it created a different set of problems they hadn’t anticipated. The choice wasn’t wrong, exactly. It was incomplete. They optimized for one dimension (decoupling, scalability, auditability) without modeling the tradeoffs on the dimensions that matter at runtime: debuggability, operational visibility, compensating transaction complexity.

This article is about making that choice deliberately.

---

## What the Patterns Actually Mean

The industry uses these terms loosely enough that two people saying “we’re event-driven” can mean completely different things. Being precise here matters for the decision.

**Event-driven architecture (EDA)** means services communicate through events: things that happened. `OrderPlaced`. `PaymentProcessed`. `InventoryReserved`. A producer emits an event to a bus (Kafka, EventBridge, Pub/Sub). Consumers subscribe independently. The producer has no knowledge of who's listening or what they'll do. This is true decoupling: the producing service doesn't depend on downstream services at all.

**Workflow orchestration** means a central coordinator (the orchestrator) knows the steps of a process and drives execution. “First call inventory service, then call payment service, then call fulfillment service.” If any step fails, the orchestrator handles retry, timeout, and compensation. The business process is explicit and visible in one place. Temporal, Netflix Conductor, AWS Step Functions, and Camunda are orchestration engines. The orchestrator creates coupling (it knows about all the services it coordinates) but makes the process observable and manageable.

**Choreography (saga pattern)** sits between these two. Services still communicate through events, but each service knows what event to emit after completing its local step and what events to listen for. No central coordinator. The process emerges from the interaction of the services following their individual rules. Services stay decoupled from each other while handling multi-step distributed transactions. The catch: the process logic is spread across every participating service, which makes it hard to change and harder to debug when something goes wrong.

These aren’t competing patterns. They solve different problems. The mistake is applying one to a problem it wasn’t designed for.

---

## When Event-Driven Is the Right Choice

Event-driven architecture works well in a specific set of conditions, and I think it’s genuinely good at these.

**Multiple independent consumers with no coordination requirement.** A `UserRegistered` event might trigger email confirmation, analytics processing, fraud scoring, and CRM sync. These consumers don't need to coordinate with each other or complete in any order. If one fails, the others should proceed. Pure event-driven is exactly right here: the producer emits once, consumers subscribe independently, and adding a new consumer requires no change to the producer. This is the fan-out case, and events handle it better than any other pattern.

**Audit trails and event sourcing.** If you need a complete, immutable record of everything that happened to a domain object (not just its current state, but every state it ever had) event sourcing combined with event-driven architecture is purpose-built for this. Financial systems, compliance-heavy domains, and systems where replay is a first-class requirement benefit from storing events as the primary record rather than mutable state.

**High-volume, fire-and-forget processing.** When you’re ingesting millions of events per second for processing that doesn’t need synchronous feedback (clickstream data, sensor telemetry, log aggregation) event-driven architecture scales in ways synchronous RPC doesn’t.

What event-driven doesn’t give you is visibility into multi-step processes. If an order goes through eight state transitions across six services, pure event-driven will tell you each event fired. Finding out why an order is stuck at step 4 requires reconstructing its history from event logs across multiple systems. At 2 AM during an active incident, that reconstruction is expensive and slow. I’ve been in that situation. Not fun.

---

## When Workflow Orchestration Is the Right Choice

Workflow orchestration solves the problem event-driven creates: how do you manage a multi-step business process that needs to complete reliably, with observable state, and with defined failure handling?

**Long-running business processes with defined steps.** Payment processing is the canonical example. The steps: reserve inventory, authorize payment, confirm inventory reservation, capture payment, trigger fulfillment, send confirmation. If authorization succeeds but inventory confirmation fails, you need to reverse the payment authorization. If capture succeeds but fulfillment fails, you need human review. Every step has defined success criteria, failure modes, and compensating actions. An orchestrator makes this process explicit, visible, and testable. The business process lives in one place and can be read like a specification.

**Processes where visibility is non-negotiable.** Operations teams at e-commerce companies need to answer questions like: “How many orders are currently between payment authorization and capture?” “What’s the P99 time for the inventory reservation step?” “Show me all orders in fulfillment-pending state for more than 30 minutes.” These questions are trivially answerable with a workflow orchestrator because process state is a first-class concept. With pure choreography, answering them requires custom queries across multiple services’ data stores or expensive event log reconstruction.

**Processes with complex failure handling.** Compensating transactions (the undo operations that run when a later step fails in a distributed transaction) are manageable in an orchestrator and nightmarish in pure choreography. With an orchestrator, the compensation logic lives adjacent to the failing step and the orchestrator drives it. The counterargument I take most seriously: orchestrators can become bottlenecks for high-throughput synchronous flows. Temporal handles this through workflow partitioning and parallel execution; the bottleneck risk is real but largely mitigated for async workflows where the orchestrator coordinates rather than waits.

**When you need to change the process.** Business processes change. Payment flows get additional fraud checks. Fulfillment workflows get new carrier integrations. With orchestration, you update the workflow definition and redeploy. With choreography, a process change may require coordinated changes to every participating service, because the process logic is distributed across them. This is the hidden coupling of saga choreography: the services look decoupled, but they’re coupled through the shared event contract of the process.

---

## The Trap: Distributed Spaghetti

The most common mistake I see is teams adopting event-driven choreography for processes that actually need orchestration, because choreography sounds architecturally purer or because they want to avoid the coupling an orchestrator creates.

The result is what I call distributed spaghetti: a set of services that communicate through events, where the business process is implicit in the choreography of those events, and nobody can tell what the process actually is without reading all the services simultaneously.

Here’s what this looks like in practice. A team builds an order management system using saga choreography. OrderService emits `OrderCreated`. InventoryService listens, reserves inventory, emits `InventoryReserved`. PaymentService listens, processes payment, emits `PaymentProcessed`. FulfillmentService listens, triggers shipment, emits `OrderShipped`. Looks clean on the happy path diagram.

Now add failure handling. When InventoryService emits `InventoryReservationFailed`, OrderService needs to listen and update the order status. When PaymentService fails after InventoryService succeeded, InventoryService needs to listen for `PaymentFailed` and release the reservation. When FulfillmentService fails after both InventoryService and PaymentService succeeded, both need to be compensated, in the right order, with verification that compensation completed.

By the time you’ve fully specified the failure handling for a four-step process, every service has event subscriptions spanning the entire workflow. The “decoupling” you thought you were getting has dissolved. The process logic is distributed across four services in ways that are invisible in any one codebase. When an order gets stuck, finding out why requires correlating event logs across all four services for a specific order ID. When you need to add a fifth step, you’re touching all four existing services to update their event handling.

This is distributed spaghetti. A failure of pattern selection, not implementation.

---

## The Decision Framework

Three questions determine the choice:

### 1. Does this process need observable state at runtime?

If operations needs to answer “where is this specific business transaction right now?” use orchestration. If the process is fire-and-forget and you only care about aggregate outcomes, events are fine.

### 2. How complex is the failure handling?

If failure means “retry and log,” events work. If failure means “compensate previous steps, notify the user, and escalate to human review,” orchestration is worth the coupling cost.

### 3. How often will this process change?

If the process is stable and well-understood, choreography can work. If the business process evolves frequently, put it in an orchestrator where it’s visible and changeable in one place.

A practical rule of thumb: if you can draw the process on a whiteboard in under two minutes and the failure cases fit on a sticky note, choreography may be appropriate. If you need a flowchart and the failure handling has conditional branches, use an orchestrator.

---

## Hybrid Patterns: The Practical Reality

Most real systems are hybrids, and the right architecture partitions which concerns use which pattern.

A payment system might use Temporal to orchestrate the payment flow (reserve, authorize, capture, fulfill) because that process needs visibility and reliable failure handling, while using Kafka events to broadcast `PaymentCompleted` to downstream consumers (analytics, CRM, fraud scoring) because those consumers are independent and broadcast semantics are exactly right.

The partition rule: use orchestration for processes, use events for notifications.

- A **process** is a multi-step transaction with defined success criteria, failure modes, and business meaning. Use orchestration for the steps that get you to the outcome.
- A **notification** is “this thing happened, and interested parties should know.” Use events. An order reaching `Fulfilled` might trigger inventory reorder, loyalty points calculation, and sales analytics updates. These are notifications. They don't need to coordinate with each other or with the process that produced them.

Netflix described a similar partition in their Conductor migration: choreography for fan-out notifications to independent consumers, Conductor for multi-step workflows requiring visibility and retry management (Netflix Technology Blog, 2016). The combination gave them the scalability of events where it mattered and the operational control of orchestration where it was needed.

Worth noting separately: this hybrid approach is also how you migrate from choreography to orchestration without a big-bang rewrite. Identify the processes (the multi-step transactions with failure complexity) and migrate those to an orchestrator first. The notification fan-outs stay as events. The scope of the migration stays manageable.

---

## Tooling Choices

**Temporal** is the current benchmark for durable workflow orchestration. It models workflows as code (Go, Java, TypeScript, Python) rather than YAML/JSON DSLs, giving workflow logic the same testability and refactoring support as any application code. Temporal handles durable execution, exactly-once semantics, retry policies, and human-in-the-loop steps. The tradeoff: operational complexity. Temporal Cloud removes the operational burden but adds cost at scale.

I’ve used Temporal in production for payment flows and the developer experience is genuinely good once you’re past the initial learning curve. The “workflow as code” model pays off the first time you need to add a step to a running workflow definition without breaking in-flight instances.

**AWS Step Functions** is the managed alternative for AWS-native teams. Standard workflows are durable and auditable; use these for business-critical processes. Express workflows are high-throughput but designed for short-duration, less-durable use cases. The visual workflow designer is useful for stakeholder communication even if you prefer infrastructure-as-code for the actual definitions.

**Kafka** (and managed equivalents: Confluent Cloud, MSK, Pub/Sub) is purpose-built for high-volume event streaming. Good for broadcast, fan-out, event sourcing, and stream processing. Using Kafka as an orchestrator (through topic/consumer group patterns that simulate workflow state) is a common and painful mistake. If you’re doing this, you’ve probably already noticed the operational complexity. Temporal or Step Functions will fix it.

---

## A Real Decision: Grab’s Order Management

In 2019, Grab published a detailed account of their order management system architecture evolution (Grab Engineering Blog, 2019). They’d started with a choreography-based saga for their food delivery order flow and run into the predictable problems: unclear process state, complex failure handling distributed across services, debugging that required correlating logs across four systems.

The migration moved order flow orchestration to an explicit state machine with a central coordinator. Failure handling (previously implicit in the choreography) became explicit in the state machine definition. The question “how many orders are currently awaiting driver acceptance?” became a simple query rather than a distributed log reconstruction.

Their conclusion: choreography had worked fine for simple, stable processes with minimal failure complexity. It broke down when the process had more than three or four steps and when failure handling required coordinated compensation across services.

Worth noting separately: Grab was operating at a scale where the investment in a full orchestration migration was clearly justified. For a smaller team with a three-step flow and a well-understood failure model, choreography might still be the right call. The maintenance cost of a full orchestration stack can exceed the debugging cost of manageable choreography at smaller scale. Know your scale before committing to the migration.

---

## Key Takeaways

- Event-driven architecture gives you decoupling and scalability for independent consumers. It doesn’t give you visibility into multi-step processes or manageable failure handling for complex transactions.
- Workflow orchestration gives you observable, auditable, changeable business processes. It creates coupling between the orchestrator and every service it coordinates; that coupling is the price of the visibility.
- Choreography (saga) works for simple, stable processes with minimal failure complexity. It becomes distributed spaghetti when applied to processes with more than three or four steps or complex compensating transactions.
- The partition rule: use orchestration for processes (multi-step transactions with defined outcomes), use events for notifications (independent consumers that need to know something happened).
- Temporal and Step Functions are orchestrators. Kafka is a streaming platform. Using Kafka as an orchestrator is a common and painful mistake.

---

## Action Items

1. List your current async processes. For each one, ask: does operations need observable state at runtime? If yes, evaluate whether you have that visibility today.
2. For any choreography-based sagas in your system, draw the full failure handling (including compensation paths) on a whiteboard. If you can’t draw it cleanly, the complexity has exceeded what choreography can manage.
3. Identify which event topics are being used for process coordination vs. notification. These are different concerns and may deserve different infrastructure.
4. If you’re considering Temporal or Step Functions, run a proof of concept on your most complex current saga before committing. The migration effort from choreography to orchestration is real; validate the payoff first.
5. Review your most painful recent production incident involving an async process. Was the difficulty in finding what state the process was in? That’s an orchestration signal.

---

## Tools and Resources

### Workflow Orchestration

- [Temporal](https://temporal.io/): The current benchmark for durable workflow orchestration; supports Go, Java, TypeScript, Python
- [AWS Step Functions](https://aws.amazon.com/step-functions/): Managed orchestration for AWS-native teams; Standard vs. Express workflow distinction matters
- [Netflix Conductor](https://conductor.netflix.com/): Netflix’s open-source orchestration engine; the original at-scale reference implementation

### Event Streaming

- [Apache Kafka](https://kafka.apache.org/): The reference implementation for high-volume event streaming; not an orchestrator
- [AWS EventBridge](https://aws.amazon.com/eventbridge/): Managed event routing within AWS; well-suited for notification fan-out

### Architecture References

- [Grab Engineering Blog](https://engineering.grab.com/): The 2019 order management post is a detailed real-world account of a choreography-to-orchestration migration
- [Netflix Technology Blog: Conductor](https://netflixtechblog.com/conductor-a-microservices-orchestrator-2e8d4771bf40): Original Conductor announcement with rationale for orchestration over choreography at Netflix scale

---

## Series Navigation

- **Previous Article**: [When NOT to Use Microservices](https://medium.com/gitconnected/when-not-to-use-microservices-92dfcc0bcfef)
- **Next Article**: Conway’s Law in Practice *(Coming September 28)*

*Daniel Stauffer is an Enterprise Architect specializing in platform engineering, AI systems, and sustainable software practices. He writes about the decisions that separate good architecture from great architecture.*

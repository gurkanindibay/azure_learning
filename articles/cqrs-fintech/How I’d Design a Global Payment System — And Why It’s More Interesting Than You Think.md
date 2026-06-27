---
type: Article
title: "How I’d Design a Global Payment System — And Why It’s More Interesting Than You Think"
description: "A deep dive into the architecture behind global payment systems like PayPal, covering microservices, async messaging, idempotency, and resilience patterns."
source: "https://levelup.gitconnected.com/how-id-design-a-global-payment-system-and-why-it-s-more-interesting-than-you-think-bcf08ed9fafb"
author: "Harsh Shukla"
published: 2026-05-04
created: 2026-06-18
tags:
  - clippings
  - fintech
  - system-design
  - microservices
---

# How I’d Design a Global Payment System — And Why It’s More Interesting Than You Think

> **Source**: [Level Up Coding](https://levelup.gitconnected.com/how-id-design-a-global-payment-system-and-why-it-s-more-interesting-than-you-think-bcf08ed9fafb)  
> **Author**: Harsh Shukla

*A deep dive into the architecture behind systems like PayPal — and the beautiful chaos underneath*

I’ve been thinking about payment systems a lot lately. Not in a “I’m broke and anxiously refreshing my bank account” kind of way but more in a “how does this actually work at scale?” kind of way. Because if you’ve ever tapped your phone to pay for a coffee and the transaction went through in under a second, you probably didn’t think about the minor miracle that just happened. Thousands of moving parts, banks talking to card networks talking to your phone, all working in harmony so you can pay for an overpriced latte without friction.

So let’s talk about what it would take to design a global payment system — something at the scale of PayPal, capable of handling thousands of transactions per second from users all over the world. This is also, by the way, exactly the kind of problem that shows up in system design interviews at places like Meta and Google. But honestly, I find it fascinating enough to think about even outside of that context.

Let’s get into it.

## First, Let’s Get Our Terms Straight

Before we throw words like “payment gateway” and “payment processor” around interchangeably (like so many people do, and it’s fine, but let’s be precise), let me quickly clarify what each one actually does.

A **payment gateway** is the bridge between your device and the bank. Think of it as the bouncer at the door of a very exclusive financial club. When you type your card number into a website, the gateway encrypts that information and sends it along for approval. It handles the “is this person who they say they are?” part of the puzzle.

A **payment processor**, on the other hand, is the engine that runs after the bouncer nods you in. It talks to card networks like **Visa** and **Mastercard**, communicates with your bank to check if you have the funds, and actually moves the money from your account to the merchant’s. If the gateway is the bouncer, the processor is the whole club infrastructure — the bar, the music, the fire safety compliance.

![](https://miro.medium.com/v2/resize:fit:2880/format:webp/1*Dh_teXVDcRyq0KTQvwcD5A.png)

Orchestrated payment gateway and processor visualization diagram

Most people never need to care about this distinction. But you’re here, reading a system design deep-dive, so clearly you’re not most people.

## What Are We Actually Building?

Let’s set some requirements, because you can’t design anything well without knowing what “good” looks like.

![](https://miro.medium.com/v2/resize:fit:1240/format:webp/1*fqKonrFiUbINGcaRwh-yZg.png)

Our system needs to serve both merchants and consumers, globally. That means one-time payments, recurring billing, refunds, and dispute resolutions — the full suite. We’re supporting multiple currencies with real-time exchange rates, because the world is stubbornly not on a single monetary standard despite everyone’s best efforts.

On the scale front: we’re talking **thousands of transactions per second**. Not “a lot.” Thousands. Per second. That’s the PayPal-level territory we’re targeting. The system must also comply with international regulations like PCI DSS (Payment Card Industry Data Security Standard) and KYC (Know Your Customer) requirements, because financial regulators have exactly zero sense of humor about these things.

Non-functionally, we want:

- **High availability** — 99.99% uptime. That sounds like a small number until you realize it means less than an hour of downtime per year.
- **Low latency** — nobody wants to stare at a spinning loader while buying something.
- **Scalability** — handle peak loads without sweating.
- **Ironclad security** — because this is literally people’s money.

With those goals in mind, we can start designing.

## The Architecture: Three Layers, Infinite Complexity

At a high level, the system breaks down into three layers. I like to think of these as the front-of-house, the kitchen, and the storage room of a very expensive restaurant.

## 1\. The Client Layer (Front of House)

This is where users actually interact with the system — web apps, mobile apps, and third-party APIs. It’s responsible for collecting user intent (like “I want to pay $499 for this thing I probably don’t need”) and firing off requests to the backend.

Third-party merchants also live here, integrating our payment system into their own platforms via APIs. This is how a random e-commerce site can take payments without building all of this infrastructure themselves. They get to stand on our shoulders, which is the whole point of platforms.

## 2\. The Service Layer (The Kitchen)

This is where the magic happens — and also where things can go wrong in ways that would make a junior engineer cry. The service layer is built on **microservices**, each responsible for one thing and doing that one thing well.

The key services are:

- **API Gateway** — The single entry point for all requests. Built on something like Amazon API Gateway, it handles authentication, rate limiting, and routing. It’s the maître d’ of our architecture.
- **User Service** — Handles authentication and user profile management. Validates credentials, issues JWT tokens, manages session state.
- **Payment Service** — The core of the system. Manages transaction processing, talks to external payment gateways and banks, and orchestrates the whole payment flow.
- **Account Service** — Keeps track of user balances across multiple currencies. Critical for avoiding the nightmare scenario where you charge someone twice or forget to deduct the payment.
- **Transaction Service** — Records every transaction in meticulous detail. This is the system’s paper trail, and it needs to be bulletproof.
- **Fraud Detection Service** — Real-time monitoring using machine learning models. If something smells funny, this service flags it before the money moves.
- **Notification Service** — Sends confirmation emails, SMS messages, and push notifications. Arguably the least sexy service, but you’ll hear about it immediately if it fails.

These services communicate **asynchronously** through message queues — specifically Kafka — which is a fancy way of saying they don’t have to wait around for each other to finish. This is crucial at scale. If your notification service is slow, it shouldn’t block payment confirmations. Kafka handles all of this gracefully, like a very well-organized traffic system that never actually gets traffic jams.

## 3\. The Data Layer (The Storage Room)

Not all data is equal, and our storage choices reflect that.

**Relational databases** (we’re using PostgreSQL) handle transactional data. When money is moving, we need ACID compliance — Atomicity, Consistency, Isolation, Durability. These are the four pillars that ensure your account doesn’t somehow lose 500 bucks because two database writes happened at the same time and fought each other.

**NoSQL databases** (Cassandra or MongoDB) handle less critical but high-volume data — logs, session information, event data. Speed over strictness.

**Redis** acts as our caching layer, storing frequently accessed information like account balances in memory for millisecond-level reads. Because hitting the main database every time a balance check comes in would be like asking your chef to grow the vegetables from seed every time someone orders a salad.

## Database Ownership: One Service, One Database

In a microservices world, each service owns its own data. This is not just a good practice — it’s load-bearing. If services share databases, you’ve just built a monolith in a trench coat.

Here’s how it maps out:

- **User Service DB**: user profiles, authentication details, KYC status

![](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*jHhQiTd6L3jjk5VHJDzQNg.png)

User Table

- **Account Service DB**: balances across currencies, ACID-compliant for financial integrity

![](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*Afakyh3BgFuaX9_-ZuczQQ.png)

Account Table

- **Payment Service DB**: payment request metadata — who initiated it, for which merchant, what currency, what status

![](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*MOyQKGnFzZga4yw_uB-zyQ.png)

Payment Table

![](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*nABgcSf2HZZtqcSLCijh9g.png)

Currency Exchange Rates Table

The currency exchange rate table deserves a special mention. It stores the exchange rates used *at the time* of a payment request — not just the current rate. This matters enormously for audit trails. The rate when someone initiated a cross-currency payment is legally and financially meaningful information.

- **Transaction Service DB**: complete transaction records, durable and traceable

![](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*6ofnvmaLcqQxmsKq_qGveA.png)

Transactions Table

- **Fraud Detection DB**: flagged transactions, fraud scores, historical behavioral data for ML training

![](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*OEwLs7_7665QL3PdUiSQOA.png)

Fraud Detection Table

- **Notification Service DB**: notification logs — was the email sent? Did the SMS go through?

![](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*4P0-AyTVS0xpNo3byqsNNQ.png)

Notifications Table

![](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*xZh3zPI63ciIaGKpKDFuaA.png)

session data

- **Event Logs** captures the actions taken by users or system events like logins, payments and password changes and they need to be stored efficiently to support high write throughput.

![](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*d3xJ5Jy1QJQ4M_8Ccsmy8A.png)

Event Logs

## The Kafka Topics: The Nervous System of the System

Services talk to each other through Kafka topics. It ensures asynchronous communication and decoupling. Here’s a quick map of the key ones:

- `balance-check-queue` — Payment Service asks Account Service: "Does this person have enough money?"
- `balance-response-queue` — Account Service replies: "Yes/No/sort of"
- `transaction-recording-queue` — Payment Service tells Transaction Service to log the transaction
- `account-update-queue` — Account Service is notified to deduct the payment amount
- `notification-queue` — Notification Service is told to send a confirmation
- `fraud-detection-queue` — Transaction data is sent to the Fraud Detection Service for analysis
- `payment-gateway-queue` — Asynchronous communication with external payment gateways (Visa, Mastercard, etc.)
- `gateway-response-queue` — The external gateway's response comes back here

The beauty of this setup is that if the Fraud Detection Service is overwhelmed and slow, transactions don’t grind to a halt — the messages just sit in the queue until the service processes them. This decoupling is what makes the whole thing resilient.

## A Transaction, Step by Step

Let me walk through what actually happens when a user initiates a payment. Buckle up — this is where everything comes together.

![](https://miro.medium.com/v2/resize:fit:4352/format:webp/1*Sz8qSUDZsv8Ky55ukf0vVA.png)

Detailed Component Interaction

**Step 1: Authentication** The user logs in via the web or mobile app. The request hits the API Gateway (**sitting behind a load balancer**), which forwards it to the User Service. The User Service checks Redis for a cached user profile. Cache hit? Great, fast. Cache miss? Fetch from the database. Credentials validate, a JWT token is issued, session data is stored in Redis. The client gets the token and uses it for all future requests.

**Step 2: Payment Initiation** User initiates a payment. The API Gateway verifies the JWT token. Authenticated? Forwarded to the Payment Service.

**Step 3: Balance Check** The Payment Service checks Redis for a cached balance. If it’s there and sufficient, the amount is locked in Redis right away. If not, it publishes a message to the `balance-check-queue`. The Account Service picks this up, checks its own Redis cache (or falls back to PostgreSQL), and responds on the `balance-response-queue`. Sufficient funds? Great. Insufficient? The Payment Service tells the user their payment failed — end of story, no harm done.

**Step 4: External Payment Processing** Here’s where our system talks to the outside world. The Payment Service publishes to the `payment-gateway-queue`, and the external gateway — Visa, Mastercard, or a bank network — processes the transaction asynchronously. This is done asynchronously because **external services are *slow*** (relatively speaking) and you don't want the user's experience to be held hostage by Visa's response time.

![](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*8cjSGmaFGMAnP1fQNv1eFQ.png)

Our service layer implements both Payment Gateway and processor functionality

The response comes back on the `gateway-response-queue`. Approved? The transaction proceeds. Declined? The user is notified.

If the gateway doesn't respond at all, we implement retries with **exponential backoff** — trying again after increasingly longer intervals, so we don't just hammer an already-struggling service into oblivion.

**Step 5: Recording the Transaction** Once confirmed, the Payment Service notifies the Transaction Service via Kafka to record the transaction details — ID, timestamp, amount, status. Crucially, an **idempotency key** is sent along with this request. This key ensures that if the same request is retried (due to a network hiccup), the Transaction Service won’t create duplicate records or charge the user twice. It checks whether it’s seen this key before and, if so, politely ignores the duplicate request.

**Step 6: Updating the Account Balance** The Account Service is notified via the `account-update-queue` to deduct the payment amount and update both PostgreSQL and Redis.

**Step 7: Notification** The Notification Service picks up a message from the `notification-queue` and sends the user a confirmation — email, SMS, or push notification, depending on their preferences. This all happens asynchronously, which means it doesn't slow down the main payment flow. You get your confirmation a moment after the transaction, not as part of it.

**Step 8: Fraud Detection (Running in Parallel)** While all of this is happening, the Fraud Detection Service is doing its own analysis asynchronously. It runs machine learning models against the transaction data, generating a fraud risk score. If the score exceeds a threshold, it can trigger a hold on the transaction or require additional verification — like a multi-factor authentication challenge. If the transaction has already been recorded, compensating transactions can be issued to reverse it.

## Resilience Patterns That Deserve More Credit Than They Get

Let me briefly highlight three architectural patterns that make this whole system actually work under pressure:

**Circuit Breaker**: When an external service (like a payment gateway) starts misbehaving — slow responses, errors — the circuit breaker “trips” and stops sending requests to it temporarily. This prevents our system from cascading into failure trying to reach a service that clearly isn’t home. When the external service recovers, the circuit breaker resets.

**Idempotency Keys**: Already covered above, but worth emphasizing. In distributed systems, retries are inevitable. Idempotency keys are the mechanism that ensures retrying an operation is safe — you get the same outcome without side effects.

**Saga Pattern**: For distributed transactions that span multiple services — payment, account, fraud detection — the Saga pattern coordinates the sequence of operations. If something fails mid-way, compensating actions are triggered. Think of it as the system’s version of ctrl+Z, but for money.

## Security: Because This Is People’s Money

Security isn’t an afterthought here — it’s woven into every layer.

- **Encryption in transit**: All data is encrypted using TLS. Always.
- **Encryption at rest**: Sensitive information in databases is encrypted. Your card details are never stored in plain text anywhere in this system.
- **Multi-factor authentication**: For high-risk operations, the user is asked to prove who they are twice.
- **Role-based access control (RBAC)**: Not everyone in the system needs access to everything. RBAC limits blast radius if any component is compromised.
- **Fraud detection**: Real-time ML-based monitoring, as described, acts as the system’s immune system.

## Scaling to PayPal-Level Traffic

Everything above is the *what*. The *how we make it fast* comes down to a few key levers:

**Microservices architecture** means each service can scale independently. If payments spike but notifications are quiet, only the payment service needs more instances — not the whole system. This saves cost and reduces complexity.

**Load balancing** distributes traffic intelligently, routing requests to the least-loaded available server. Global load balancers ensure traffic goes to the closest performant server, reducing latency for users in different regions.

**Caching with Redis** keeps the most frequently accessed data — like account balances — in memory, where reads take microseconds instead of milliseconds.

**Asynchronous processing** with Kafka means the main payment flow isn’t blocked by secondary operations like fraud detection or notification delivery.

**Database optimization** through read replicas (copies of the database used for read-heavy operations) and horizontal partitioning (sharding data by user ID or region) ensures the database doesn’t become the bottleneck.

## Final Thoughts

If you’ve read this far, you now have a reasonably solid mental model of how a global payment system actually hangs together.

The short version: it’s a lot of well-orchestrated services talking to each other through queues, with an obsessive focus on reliability, idempotency, and making sure no one gets charged twice for their overpriced coffee.

The funny thing about payment systems is that when they work well, nobody notices. No one tweets “ *wow, my payment went through seamlessly.*” They only tweet when it doesn’t. That invisibility is, in a weird way, the highest form of engineering success.

> Build it right, and the system disappears into the background of everyday life. Build it wrong, and you’ll be on the front page of the news for all the wrong reasons.

*Have thoughts on this? I’d love to hear how you’d approach it differently — especially around the saga pattern and distributed transaction management, which is a rabbit hole I could disappear into for hours.*

Payments

Software Engineering

Software Architecture

Microservices

PayPal

[![Harsh Shukla](https://miro.medium.com/v2/resize:fill:96:96/1*Dwb5xWnVShH8CUAnV-0kJg.png)](https://harshshuklaa.medium.com/?source=post_page---post_author_info--bcf08ed9fafb---------------------------------------)I am a software developer with a keen interest in breaking down nerdy, geeky and complex stuff into fairly simple bits
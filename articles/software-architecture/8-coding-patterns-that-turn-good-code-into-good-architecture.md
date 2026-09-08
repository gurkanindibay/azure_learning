---
type: Article
title: "8 Coding Patterns That Turn Good Code Into Good Architecture"
description: "The real architecture of a system lives in its state models, boundaries, failures, retries, naming, and everyday code changes."
generated: { by: process:format-agent, at: 2026-09-09T00:30:00+03:00 }
source: "https://medium.com/@rkdixit3/8-coding-patterns-that-turn-good-code-into-good-architecture-0986c4ac0712"
author:
  - "[[Rajesh Kumar]]"
published: 2026-08-29
created: 2026-09-09
tags:
  - "clippings"
  - "software-architecture"
  - "coding-patterns"
---

# 8 Coding Patterns That Turn Good Code Into Good Architecture

## The real architecture of a system lives in its state models, boundaries, failures, retries, naming, and everyday code changes.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*ny-dNA5lpMZ4hFzKS7sq2A.png)

*Not a Medium member?* [**Click here**](https://medium.com/@rkdixit3/8-coding-patterns-that-turn-good-code-into-good-architecture-0986c4ac0712?sk=7f49c8c07ccdcbaadbb468a2c90c196c)

Most engineers can explain architecture from a diagram.

**The harder question is:** *Can you look at a pull request and tell whether it made the system easier — or harder — to change?*

Because architecture does not live only in diagrams. It shows up in everyday decisions:

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*imzKrtjE4rj4LH0fzsSd1Q.png)

These may look like coding details.

**Together, they determine:** *Maintainability. Reliability. Testability. Operability. Changeability.*

Here are eight patterns I repeatedly come back to when designing systems and reviewing code.

## 1. Model State Explicitly

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*ahCSo28up6nRIoEinXIcSw.png)

A common source of bugs is a model that can represent states that should never exist. Consider a payment:

```java
public class OrderPayment {
    private String id;
    private String status;
    private String authorizationId;
    private String transactionId;
    private String failureReason;
}
```

Looks reasonable. But what does this model allow?

- *Can a failed payment have a transaction ID?*
- *Can a pending payment have an authorization ID?*
- *Can a completed payment exist without a transaction ID?*

The model does not tell us. So business rules slowly become null checks:

```java
if (payment.getTransactionId() != null) {
    receiptService.generate(payment.getTransactionId());
}
```

Now a null check is carrying business meaning.

***A stronger model makes the states explicit:***

```java
public sealed interface OrderPayment
        permits PendingPayment,
                AuthorizedPayment,
                CompletedPayment,
                FailedPayment {
}

public record PendingPayment(
        String paymentId
) implements OrderPayment {}

public record AuthorizedPayment(
        String paymentId,
        String authorizationId
) implements OrderPayment {}

public record CompletedPayment(
        String paymentId,
        String transactionId
) implements OrderPayment {}

public record FailedPayment(
        String paymentId,
        String reason
) implements OrderPayment {}
```

***Now this is possible:***

```java
public void generateReceipt(CompletedPayment payment) {
    receiptService.generate(payment.transactionId());
}
```

A pending payment cannot accidentally reach this method. The compiler carries part of the business rule.

You do not need sealed interfaces everywhere. Enums, constructors, validation, state machines, and database constraints can provide similar guarantees.

**The important question is:** *Can this model represent something that should never happen?*

If yes, the rest of the system will eventually have to defend against it.

**Architectural principle:** *Make invalid states difficult to represent.*

## 2. Keep External Systems at the Boundary

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*SigDJyua5xBNheZz06Rtyg.png)

Every external system has its own data model, naming, and quirks. The problem starts when those details leak into your business logic.

Suppose a shipping provider sends this:

```json
{
  "shipment_state": "D",
  "tracking_no": "TRK123",
  "carrier_code": "BLUEDART"
}
```

And application code starts doing this everywhere:

```java
if ("D".equals(shipmentResponse.getShipmentState())) {
    order.markDelivered();
}
```

Now your domain depends on the provider’s vocabulary.

If `"D"` changes to `"DELIVERED"`, or you add another carrier with a different status model, business logic starts changing across the codebase.

Translate once at the boundary:

```java
private ShipmentStatus mapStatus(String providerStatus) {
    return switch (providerStatus) {
        case "D" -> ShipmentStatus.DELIVERED;
        case "T" -> ShipmentStatus.IN_TRANSIT;
        case "F" -> ShipmentStatus.FAILED;
        default  -> ShipmentStatus.UNKNOWN;
    };
}
```

The rest of the system works with domain concepts:

```java
Shipment shipment = shippingGateway.getShipment(shipmentId);

if (shipment.status() == ShipmentStatus.DELIVERED) {
    order.markDelivered();
}
```

Now the provider can change without forcing the business domain to change with it.

```text
Provider: "D" → Boundary: Translate → Domain: DELIVERED
```

The same rule applies to HTTP payloads, Kafka events, SDK models, database rows, configuration, and framework request objects:

Translate external representations once, then let the domain speak its own language. Stripe, Slack, GitHub, Salesforce, shipping carriers — or any external dependency — should influence the adapter, **not become the vocabulary of your codebase.**

> ***A boundary defines where another system’s meaning ends and yours begins.***

**Architectural principle:** *Let external systems influence the boundary, not define the domain.*

## 3. Separate Business Decisions From Side Effects

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*m9I3OwJ9wFEGG6Fy6fYUMw.png)

Many methods mix two different things:

1. Should this action happen?
2. Actually perform the action.

Consider invoice cancellation. Before cancelling, system may need to check:

- Is the invoice already paid?
- Is it already cancelled?
- Does a credit note exist?

These are **business decisions**.

Only after the decision is made should system perform **side effects** such as updating database, reversing accounting entries or sending notifications.

```java
CancellationDecision decision = canCancel(invoice);

if (!decision.allowed()) {
    throw new ValidationException(decision.reason());
}

invoiceRepository.cancel(invoice.id());
accountingService.reverseInvoice(invoice);
notificationService.notifyCancellation(invoice.customerId());
```

**Now the flow is clear:** *Policy decides → Execution acts*

This also makes `canCancel()` easy to test because it contains business logic without database or notification dependencies.

The same idea works well for *pricing, eligibility, permissions, approvals, refunds and workflow transitions*.

Not every `if` needs its own abstraction. But important business rules should have a clear place.

**Architectural principle:** *Keep business decisions separate from side effects.*

## 4. Treat Errors as Part of the Contract

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*TWeoJ1fH0n-CmhC4gqq_Zg.png)

Errors should tell the caller **what failed, whether it can recover, and how to trace it**.

Imagine a customer tries to pay an invoice twice. A weak API returns:

```json
{ "message": "Payment failed" }
```

Now the client has to guess:

- Should it retry?
- Was the card declined?
- Was the invoice already paid?
- Is this a server problem?

A better contract makes the failure explicit:

```json
{
  "code": "INVOICE_ALREADY_PAID",
  "message": "Invoice INV-123 has already been paid.",
  "retryable": false,
  "requestId": "req_9a271"
}
```

Now each field has a purpose:

`**code**` → software decides what to do  
`**message**` → humans understand the problem  
`**retryable**` → clients know whether retrying makes sense  
`**requestId**` → engineers can trace the failure

The same applies to logs.

```text
# Weak:
Payment failed

# Useful:
payment_rejected
invoice=INV-123
reason=ALREADY_PAID
request_id=req_9a271
```

A good error does not just report failure.

***It tells the next system what to do with it.***

**Architectural principle:** *Design failures as part of the API contract, not as an afterthought.*

## 5. Build for Retries, Not Just Success

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*aZ1fY3-rBYxpD4h7cfmkXA.png)

Distributed systems repeat work.

Clients retry. Queues redeliver. Workers restart. Webhooks may arrive more than once.

**So every design should answer one question:** *What happens if this operation runs again?*

Consider a refund.

The payment provider processes it successfully, but your service crashes before saving the result. The request is retried.

Without protection, the customer may be refunded twice.

The fix starts by giving the **business operation a stable identity**:

```java
String operationId = "refund:" + payment.id();
Refund existing = refundRepository.findByOperationId(operationId);

if (existing != null) {
    return existing;
}

return paymentProvider.refund(
        payment.externalTransactionId(),
        payment.amount(),
        operationId
);
```

**The mental model changes from:**

*“Refund ₹5,000.”*

to: *“Execute the refund for payment* `*P123*` *once.”*

**That is idempotency:** repeating the same operation should not create a second effect.

The same idea applies to payments, credits, inventory updates, event consumers, webhooks, and scheduled jobs.

And a simple existence check may not be enough. Concurrency and crash windows may still require ***unique constraints, transactions, idempotency keys, or inbox/outbox patterns***.

Retries are not exceptional in distributed systems. *They are normal behavior.*

**Architectural principle:** *Design side effects for retries and partial failures, not just the happy path.*

## 6. Keep the Main Path Easy to See

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*aCZ9yT8vAb1X0msq_o1ADA.png)

Control flow should reveal what the operation does.

Consider:

```java
public void updateAccount(String accountId, AccountUpdate request) {

    Account account = accountRepository.findById(accountId);
    if (account != null) {
        if (!account.isClosed()) {
            if (request.email() != null) {
                if (account.canBeEdited()) {
                    accountRepository.update(account, request);
                    return;
                }
            }
        }
    }
    throw new RuntimeException("Unable to update account");
}
```

It works.

But the important action is buried under four levels of conditions, and every failure becomes the same error.

Reject invalid conditions first:

```java
public void updateAccount(String accountId, AccountUpdate request) {
    Account account = accountRepository.findById(accountId);
    if (account == null) {
        throw new AccountNotFoundException(accountId);
    }
    if (account.isClosed()) {
        throw new AccountClosedException(accountId);
    }
    if (request.email() == null) {
        throw new ValidationException("Email is required");
    }
    if (!account.canBeEdited()) {
        throw new ForbiddenException("Account cannot be edited");
    }
    accountRepository.update(account, request);
}
```

Now the method reads almost like a specification:

```text
Find account → Reject invalid states → Update account
```

These are often called guard clauses.

**The name is less important than the effect:** *the main path becomes obvious.*

**Architectural principle:** Make the important execution path the easiest path to understand.

## 7. Name Things by Business Meaning

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*XskEHnsDb34NLDCu-GNDPg.png)

Poor names make simple code expensive to understand.

Consider:

```java
List<Account> result = accountRepository.findByStatus("ACTIVE");
for (Account item : result) {
    if (item.getDueAmount().signum() > 0) {
        process(item);
    }
}
```

Nothing is technically wrong. But the reader must reverse-engineer the business meaning.

What is `result`? Why does `dueAmount > 0` matter? What does `process()` do?

Compare:

```java
List<Account> accountsWithOutstandingBalance =
        accountRepository.findAccountsWithOutstandingBalance();

for (Account account : accountsWithOutstandingBalance) {
    collectionService.scheduleFollowUp(account);
}
```

Now the code explains the business operation.

The same applies to rules.

Instead of exposing implementation details:

```java
if (subscription.status() == Status.ACTIVE && subscription.balance().signum() >= 0) {
    billingService.charge(subscription);
}
```

expose the meaning:

```java
if (subscription.isEligibleForBilling()) {
    billingService.charge(subscription);
}
```

The rule can evolve independently:

```java
public boolean isEligibleForBilling() {
    return status == Status.ACTIVE && !billingBlocked && balance.signum() >= 0;
}
```

Callers depend on **what the rule means**, not how it happens to be implemented today.

*A vague name does not remove complexity.* ***It moves complexity into the reader’s head.***

**Architectural principle:** Name concepts by what they mean, not merely by how they are implemented.

## 8. Design for Change, Not Just the Final State

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*ou_hFW9QZqK6xoSqbe0sSw.png)

A good design should not only describe **where the system should end up**.

It should also explain **how to get there safely**.

Suppose an invoice API currently exposes:

```text
paymentStatus
```

Later, one status is no longer enough:

```text
paymentStatus
settlementStatus
```

The risky migration is:

```text
Old → New
```

*Change the producer → Change every consumer → Change reports and events → Deploy everything together → Hope nothing breaks.*

A safer migration introduces a **compatible intermediate state**:

```text
1. Add settlementStatus
2. Populate both fields
3. Migrate consumers gradually
4. Move business rules to the new field
5. Measure remaining usage
6. Deprecate the old meaning
7. Remove it when nothing depends on it
```

Real migrations usually look like:

```text
Old → Compatible State → Migration → Verification → New
```

This applies to APIs, database schemas, event contracts, identifiers, service boundaries, and feature migrations.

The same thinking should shape pull requests.

A PR that changes the model, API, business rules, event schema, and unrelated validation at once may still be correct — but it is harder to review, verify, and reverse.

Where possible, separate **structural change** from **behavioral change**.

A reviewer should be able to answer:

- What changed?
- Why?
- What behavior changed?
- How was it verified?
- Can we safely roll it back?

Rollback is not just an operational concern.

**The migration path is part of the architecture.**

**Architectural principle:** *Design how the system evolves, not just what the final system should look like.*

## What These Patterns Have in Common

These eight patterns solve different problems:

- **Explicit state** improves correctness.
- **Boundaries** contain external change.
- **Separated decisions** improve testability.
- **Structured errors** improve diagnosis.
- **Idempotency** improves reliability.
- **Clear control flow** improves readability.
- **Domain naming** reduces accidental coupling.
- **Safe migrations** reduce change risk.

But underneath, they all do the same thing:

## They reduce ambiguity.

Good architecture reduces ambiguity. It makes the important questions easy to answer:

***What is valid? What can fail? What can repeat? Where does complexity belong?***

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*9vwlsEDG3fFoPa64FGFy9g.png)

But architecture is ultimately shaped by the decisions that make a system easier to understand, safer to operate, and cheaper to change.

**Complexity will always exist. The real design choice is where you let it live.**

> *Good architecture makes the system easier to understand today — and safer to change tomorrow.*

### Liked this one? You may enjoy these too

1. [*Distributed Systems Don’t Just Replicate State. They Agree on History*](https://medium.com/@rkdixit3/distributed-systems-dont-just-replicate-state-they-agree-on-history-2f183fdd2d23)
2. [*Your Query Took 12 ms. It Can Still Hurt Production.*](https://medium.com/@rkdixit3/your-query-took-12-ms-it-can-still-hurt-production-6636bc92bcea)
3. [*Postgres as a Queue: You Probably Don’t Need RabbitMQ Yet*](https://medium.com/@rkdixit3/postgres-as-a-queue-you-probably-dont-need-rabbitmq-yet-7c2812f32bdf)
4. [*Postgres UNLOGGED Tables: A Pragmatic Redis Alternative for Ephemeral Data*](https://medium.com/@rkdixit3/postgres-unlogged-tables-a-pragmatic-redis-alternative-for-ephemeral-data-c0bbe810ce1d)
5. [*Split-Brain: When Two Leaders Both Think They’re Right*](https://medium.com/@rkdixit3/split-brain-when-two-leaders-both-think-theyre-right-bd20ede974d3)
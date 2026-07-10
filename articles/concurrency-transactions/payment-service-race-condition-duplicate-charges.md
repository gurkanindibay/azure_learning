---
type: Article
title: "A Race Condition in Our Payment Service Charged 14,000 Customers Twice"
description: "A payment-service race condition caused duplicate charges when retries arrived before the original transaction was recorded."
source: "https://medium.com/beyond-localhost/a-race-condition-in-our-payment-service-charged-14-000-customers-twice-c5373ad57f88"
author:
  - "[[The Speedcraft Lab]]"
published: 2026-04-04
created: 2026-07-10
description: "The test suite had 94% coverage. It missed the one case that mattered."
tags:
  - "clippings"
---

# A Race Condition in Our Payment Service Charged 14,000 Customers Twice

## The test suite had 94% coverage. It missed the one case that mattered.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*tlGjWz-V4jdPzctsm2I--w.png)

One click, two charges, fourteen thousand people and a safety check that ran at exactly the wrong moment.

## The Number Kept Climbing

I was refilling my coffee when the first message came in. A customer support agent. Casual tone, almost apologetic about bothering engineering. “Hey, quick one. Getting a few reports of duplicate charges. Probably a payment provider glitch?”

I opened the payments dashboard expecting maybe five or six cases. Something small. Something explainable.

The number was 3,000. And it was moving.

By the time I actually said words out loud to my manager, it was past 14,000. Every single one of those was a real human being who opened their banking app and saw money missing that shouldn’t have been. Some of them had already filed disputes. Some of them were posting about it online.

I remember the moment my stomach actually dropped. It wasn’t when I saw the total count. It was when I noticed the individual amounts. These weren’t $2 charges. These were real purchases. Real money, taken twice, from people who trusted us.

## I Was So Sure We Had This

Our payment service had been humming along for over a year. I’d personally reviewed the flow. We had unit tests. Integration tests. A staging environment that mirrored production. 94% coverage, which, if I’m being honest, I was a little proud of. The kind of proud that makes you stop looking as carefully as you should.

There’s a specific flavour of confidence that comes from watching green checkmarks pile up in CI. It feels like safety. It felt like safety for an entire year.

I thought I understood our payment system. I did not.

## The Bug Was Hiding in Plain Sight

Here’s what happened. And I want to walk through this slowly, because the most unsettling part is how reasonable every single decision looked from the inside.

Our checkout flow was simple. User clicks “Pay.” Frontend sends a request to our payment service. The service calls the payment provider, gets a success response, writes the transaction to the database, returns a confirmation. Clean. Tested. Reviewed. Boring, even. Boring was supposed to be good.

The problem started when the payment provider responded slowly. When that happened, the user saw a loading spinner that eventually gave up. And what does a normal person do when a payment screen shows an error? They click “Pay” again. Of course they do. The UI basically told them to.

So a second request arrives at our service. The service does exactly what it’s supposed to do. It checks the database. “Has this transaction already been recorded?” The database says no. Because the first request is still in flight. Still waiting on the provider. Hasn’t written anything yet.

So the service sends a second charge. Happily. Confidently. Correctly, as far as it knows.

Wait. That’s the thing I keep coming back to. The bug wasn’t that we forgot to check for duplicates. We absolutely checked. The bug was that the check ran before the first transaction existed in the database. Two requests, racing each other, and the guard that was supposed to prevent this exact scenario was completely useless because of when it ran, not whether it ran. A race condition wearing the disguise of a safety check.

You have seen this in a different shape. A guard clause that looks right in code review. That passes every test. That works perfectly when requests arrive one at a time, politely, in order. And then falls apart the moment reality gets messy. Reality is always messy.

The part that kept me up that night was the math. This bug had been possible since the service launched. For an entire year it sat there, dormant, waiting for the right combination of slow provider response and impatient user. We didn’t find it through testing or monitoring or code review. We found it because 14,000 people got hurt.

## What Quiet Damage Looks Like

My manager didn’t raise his voice. He just looked at the dashboard and said, “How fast can we stop it?” That calm was somehow worse than yelling would have been.

We disabled the endpoint within twenty minutes. The refund process took much, much longer. Thousands of individual reversals. Each one a support ticket. Each ticket a person. Some of them wrote back with a single line that just said “I’m switching to a competitor.” I can’t tell you those messages don’t stick with you. They do.

## The Letter on the Envelope

The fix, once we understood the problem, was almost embarrassingly simple. And that’s its own kind of painful, when the solution is easy and the damage was enormous.

Think of it like sending a letter. You’re worried the post office might deliver it twice. So you write a unique number on the envelope. The recipient checks that number before doing anything. Already seen it? Toss the duplicate. Same letter, same number, processed once.

That’s an idempotency key. The frontend generates a unique identifier for every checkout attempt. When our payment service receives the request, it writes that key to the database immediately. Before calling the provider. Before doing anything else. If a second request arrives with the same key, the service doesn’t send a new charge. It just returns whatever happened with the original.

The critical shift is when the key gets recorded. Our old flow checked the database after the provider call. The new flow writes the key before. That closes the window where two requests can race past each other. The gap disappears.

Now, I’d be dishonest if I didn’t mention the tradeoff. Writing the key before the provider call means you end up with records in your database for transactions that might never complete. Provider call fails? The key is already there. You need a cleanup process for those orphaned records. And you need to decide how long a key stays valid before it expires. Too short and you let duplicates back in. Too long and you block legitimate retries. It’s solvable, but it’s not free.

## The Question I Ask in Every Review Now

Every payment flow I look at, every service that mutates state with real consequences, I ask one question before anything else: “What happens if this exact request arrives twice within 50 milliseconds?”

Not “could this theoretically happen.” Not “how likely is this.” Just: what happens. Right now. With the code as it is.

That question has caught three similar bugs in other services since this incident. Three bugs that were sitting there patiently, exactly the way ours was, behind guards that looked correct.

If you work on anything that charges money or changes state that can’t be easily reversed, try something. Fire two identical requests at your critical endpoint at the same time. On purpose. See what your database looks like after. You might not like what you find. But you’ll like it a lot more than finding out the way we did.

## I Still Think About That Slack Message

Sometimes I picture that first message from the support agent. The casual tone. “Probably a payment provider glitch.” And how the number was already in the thousands while we were still treating it like a minor thing.

The payment service works differently now. Every request carries an idempotency key. The key hits the database before any external call goes out. The race condition window that sat open for a year, invisible and patient, is closed.

But I keep circling back to one question, and I don’t think I’ll ever fully let go of it. How many of your services have a check and then a write with a gap between them? And have you ever tested what happens when two requests hit that gap at the exact same time? Because we had 94% coverage. And the answer was still no.

Follow me for more such content.
---
type: Article
title: "How Discord Handles 200M Users Going Online at Once"
source: "https://medium.com/beyond-localhost/how-discord-handles-200m-users-going-online-at-once-a77f6f79b04c"
author:
  - "[[The Speedcraft Lab]]"
published: 2026-07-01
created: 2026-07-04
description: "How Discord's presence system handles 200M users: WebSocket gateways, pub/sub fanout, lazy subscriptions, heartbeats, and gateway failure recovery — a real-world architecture walkthrough with concrete numbers."
tags:
  - "system-design"
  - "real-time"
  - "presence"
  - "case-study"
---

# How Discord Handles 200M Users Going Online at Once

## I bombed the Discord presence question in a system design interview. Here is the architecture I should have walked through, with numbers you can apply to your own systems.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*vKMz9CDyaXGTjODo4OigPA.png)

One status flip, a million ripples. This is why presence at scale is harder than it looks.

I was about twenty minutes into a system design interview when the interviewer leaned forward and asked how I would build the little green dot next to every Discord user’s name.

I almost smiled. A green dot. How hard could it be.

Five minutes later I was sweating. That little green dot is one of the most deceptively brutal realtime systems problems out there, and I had walked straight into the trap most candidates do. I want to take you through the reasoning I should have used, with numbers, so the next time you meet a problem like this in an interview or in your own product, you have something concrete to apply.

## The answer I gave first

Here is what I said, more or less word for word. Store each user’s status in the database with an is\_online column. Flip it to true on connect, false on disconnect. The user’s friends poll the API every few seconds to see who is online.

A reasonable answer. I have shipped systems that look almost exactly like this in smaller products. They work.

Then the interviewer pointed out that Discord has around 200 million monthly users and tens of millions connected at once, and asked me to walk through what happens at that scale.

I started doing the math in my head and the math was not kind. Polling every five seconds from 10 million clients is two million API requests per second, almost all of them returning unchanged data. That was the moment I realised the problem was not about storing the flag. It was about everything around it.

## The reframe that changes the whole design

Here is the insight I wish I had led with. Presence is not a state problem. It is a fanout problem.

The expensive part is not where you keep the bit. It is the amplification. One user going online produces N notifications, where N is the number of people who care about that user’s status. On Discord, N is your friends plus everyone in every shared server.

Put real numbers on it. Suppose your average active user has 50 friends and is in 20 servers averaging 5,000 members each. The number of people who might care about one status flip is in the order of 100,000. Multiply that by 10 million concurrent users toggling activity a few times an hour and you are at billions of potential notifications per hour.

Once you see it as fanout, every later decision falls into place.

## The architecture, step by step

Here is how I would walk through it now, in build order.

```
                        DISCORD PRESENCE ARCHITECTURE
                        =============================

    ┌──────────┐                          ┌──────────┐
    │  Client  │  persistent WebSocket    │  Client  │
    │  (Alice) │ ════════════════════════▶│  (Bob)   │
    │          │◀════════════════════════  │          │
    └────┬─────┘                          └────┬─────┘
         │  ① Kill polling                    │  ① Kill polling
         │  (no more 5s API polls)            │
         │                                     │
    ┌────▼──────────────────┐          ┌──────▼────────────────┐
    │  Gateway A (Elixir)   │          │  Gateway B (Elixir)   │
    │                       │          │                       │
    │  ② Stateful:          │          │  ② Stateful:          │
    │  ┌─────────────────┐  │          │  ┌─────────────────┐  │
    │  │ Session store    │  │          │  │ Session store    │  │
    │  │ (in memory)      │  │          │  │ (in memory)      │  │
    │  │ • Alice: online  │  │          │  │ • Bob: online    │  │
    │  │ • subs: [Bob,    │  │          │  │ • subs: [Alice,  │  │
    │  │   Carol, 47 more]│  │          │  │   Dave, 51 more] │  │
    │  └─────────────────┘  │          │  └─────────────────┘  │
    │                       │          │                       │
    │  ④ Heartbeats         │          │  ④ Heartbeats         │
    │  (30-60s ping/pong)   │          │  (30-60s ping/pong)   │
    │                       │          │                       │
    └────┬──────────────────┘          └────┬──────────────────┘
         │                                  │
         │  ③ Pub/Sub                       │
         │  ┌──────────────────────────┐    │
         └─▶│   Internal Message Bus   │◀───┘
            │                          │
            │  topic: presence/alice   │
            │  topic: presence/bob     │
            │  topic: presence/carol   │
            │  ...                     │
            └──────────────────────────┘
                      │
                      │ ⑤ Lazy Subscriptions
                      │
            ┌─────────▼──────────┐
            │  What's on screen  │
            │  (50-200 entities) │
            │                    │
            │  • Visible friends │
            │  • Visible members │
            │  • Active DMs      │
            │                    │
            │  ⚡ Dynamic:        │
            │  update on scroll, │
            │  tab switch, DM    │
            │  open/close        │
            └────────────────────┘

    Flow: Alice goes offline
    ─────────────────────────

    1. Gateway A detects Alice disconnect (WebSocket close OR heartbeat miss)
    2. Gateway A marks Alice offline in its session store
    3. Gateway A publishes {user: alice, status: offline} to message bus
    4. Gateway B is subscribed to topic "presence/alice" (Bob is Alice's friend)
    5. Gateway B receives event, looks up Bob's subscription set
    6. Bob's visible set includes Alice → push to Bob's WebSocket
    7. Bob sees the green dot turn gray
```

**1\. Kill polling.** You cannot poll your way out of this. Each client opens a persistent WebSocket to a gateway server and keeps it open for the duration of the session. Connection cost is paid once, not every few seconds.

**2\. Make gateways stateful.** Each gateway holds the live sessions for some slice of users in memory. It knows who is connected, what their current status is, and what subscriptions they hold. Based on Discord’s publicly shared engineering posts, this fleet runs on Elixir, which is well suited to keeping millions of persistent connections per node alive without falling over.

**3\. Put pub/sub between gateways.** When a user’s status changes on gateway A, gateway A publishes the event to an internal message bus, a pub/sub system. Gateway B, which holds the connection of one of that user’s friends, is subscribed to the right topic and receives the event. Gateway B pushes it down its own WebSocket to the right client. No gateway needs to know which other gateways exist. They only need to know what topics to subscribe to.

**4\. Add heartbeats.** TCP will not tell you fast enough when a connection has gone dead. Each client pings every 30 to 60 seconds. If the gateway misses two consecutive pings, it marks the session offline and publishes the event. Without this you leak online states for hours and your users start asking why their friend has been online for three days.

**5\. Load subscriptions lazily.** This is the step most engineers skip and the one that makes the system actually work at scale. Clients do not subscribe to presence for every user they might theoretically care about. They subscribe to the small slice currently rendered on screen, the visible friends, the visible chunk of a member list, the active DMs. When you scroll, the subscription set updates.

Those five steps are the whole architecture. Drop any one of them and the system starts collapsing at a different threshold.

> **The gateway is the central architectural element here.** It plays four roles simultaneously: (1) **connection terminator** — holds persistent WebSocket connections so the per-request cost is paid once, (2) **in-memory session store** — knows who is connected, their status, and their subscriptions without a database round-trip, (3) **pub/sub participant** — publishes status changes to the message bus and subscribes to topics its own clients care about, without ever discovering which other gateways exist, and (4) **heartbeat enforcer** — detects dead connections via missed pings and publishes offline events. The trade-off is that stateful gateways make failure expensive — a crash triggers a presence storm — but the operational simplicity of in-memory state is worth the failure-mode complexity at this scale.

## A worked example you can apply

Let me make it concrete with numbers you can plug into your own design.

You are building presence for one million concurrent users. The average user has 100 friends. The average user toggles status three times per hour. What does the load look like?

Status events per second works out to one million multiplied by three, divided by 3,600, which gives roughly 833 events per second on the bus. Comfortable.

Naive fanout to friends is 833 multiplied by 100, or 83,300 push messages per second. Still comfortable for a properly sized cluster.

Now add servers, the group chats, with an average of 1,000 members each. Each status flip can now fan out to thousands of people instead of dozens. In the worst case you are at low millions of push messages per second on a system you designed for tens of thousands. This is where lazy subscriptions stop being optional.

With lazy subscriptions, your fanout is bounded by what is on each user’s screen, maybe 50 to 200 entities at any time. The system load scales with your concurrent user count, not with your social graph size. That one decision is what separates a presence system that holds at a million users from one that needs a rewrite at fifty thousand.

If you remember nothing else from this article, remember that calculation. It is the same shape for typing indicators, read receipts, live cursors in collaborative editors, and viewer counts on streams. Same maths, same answer.

## The next question that gets you in round two

The next question I would now expect is what happens when a gateway dies and 100,000 sessions migrate to its neighbours all at once.

The honest answer is that you get a brief presence storm. Every reconnect republishes the user’s status, every subscription rebuilds, and every interested gateway sees a flood of events. You handle it with two things. The first is exponential backoff on client reconnects so they do not all hit at the same millisecond. The second is event deduplication on the subscriber side so a client does not see the same friend come online three times in a row.

It is not glamorous work. It is the work that keeps the system honest under failure, and it is the kind of detail that separates a strong answer from an exceptional one.

## The line worth remembering

If your social graph is small and updates are rare, broadcast everything. If your graph is large, push only to active subscribers and let clients subscribe based on what they render. If both your graph and your update rate are massive, the constraint you cannot escape is subscription management itself, not delivery.

In an interview, the sentence I would lead with goes something like this. Presence is state that gets read far more than it gets written, so I would optimise the fanout path before I optimise the store.

## Closing thought

The little green dot is a teaching object. Once you see it as a fanout problem instead of a storage problem, the same reasoning works for every other realtime indicator you will ever design. The next time someone asks you how a deceptively simple feature scales, do the maths on the fanout before you reach for a database.

While I was preparing for my own interviews I came across a platform called [**PracHub**](https://prachub.com/?utm_source=medium&utm_campaign=the_speedcraft_lab), which has a genuinely useful interview question guide with more depth than the recycled lists you find on most aggregator sites. I am planning to use it for my FAANG prep next, and I will share what works and what does not as I go.

If you found this breakdown valuable, follow along for more like it.

Follow me for more such content.
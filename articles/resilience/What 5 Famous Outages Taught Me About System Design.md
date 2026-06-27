---
type: Article
title: "What 5 Famous Outages Taught Me About System Design"
source: "https://levelup.gitconnected.com/what-5-famous-outages-taught-me-about-system-design-85f6b57b00b6"
author:
  - "[[Freeze Francis]]"
published: 2026-05-15
created: 2026-06-19
description: "Five famous outages that shaped how I think about system design, the questions I now ask in design reviews, the assumptions I no longer trust, and the failure modes I look for everywhere."
tags:
  - "clippings"
  - "resilience"
  - "outages"
  - "post-mortems"
  - "system-design"
---

# What 5 Famous Outages Taught Me About System Design

## Five famous outages that shaped how I think about system design, the questions I now ask in design reviews, the assumptions I no longer trust, and the failure modes I look for everywhere.

(*Non-Medium members can READ the full article for FREE:* [here](https://freezefrancis.medium.com/what-5-famous-outages-taught-me-about-system-design-85f6b57b00b6?sk=0f91a5a3db95dda2826d87df8f8d55c6))

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*zrvQsRRpXBKigV-iJM1jpg.png)

A few months ago, I was reviewing a design document at work, and a question came to me that I never would have asked three years earlier. *“What’s the blast radius of this config change?”*

I didn’t learn to ask that from a textbook. I learned it from reading Cloudflare’s post-mortem of their November 2025 outage, where a single permissions change in one database propagated across their entire global network and started returning HTTP 5xx errors for every customer.

For a long time, I treated post-mortems as casual reading. A few rough design reviews at work changed that. I started catching gaps in my own thinking that only post-mortems had taught me to look for. These write-ups are the closest thing engineers have to a free masterclass. If my earlier article on [**how I cracked the system design interview**](https://blog.stackademic.com/how-i-finally-cracked-the-system-design-interview-082eb6a7e15c) was about building the skill itself, this one is about what happens when those elegant designs collide with reality.

Here are my top five picks, ordered to tell a story that moves from “systems fail in surprising technical ways” all the way to “sometimes the failure isn’t even technical.”

## 1\. 🎮 Roblox, October 2021: 73 Hours in the Dark

👉 [**Read the full write-up here**](https://blog.roblox.com/2022/01/roblox-return-to-service-10-28-10-31-2021/)

This is the one I always recommend first.

In October 2021, Roblox went completely dark for 73 hours. Fifty million daily players couldn’t access the platform for three straight days. The root cause? A recently enabled streaming feature in HashiCorp Consul, their service discovery layer, introduced severe contention under high read/write loads. Consul’s KV write latency jumped from under 300 milliseconds to 2 seconds. Because virtually every service depended on Consul to locate other services, this single degradation brought down the entire stack. Nomad couldn’t schedule containers. Vault couldn’t serve secrets.

But here is what makes this write-up special. Hiding underneath the Consul issue was a second problem: BoltDB, which Consul uses to store Raft operation logs, had a pathological performance issue. A 7.8MB freelist was being rewritten to disk for every 16KB append, causing catastrophic write amplification. The team didn’t find this until deep into the investigation.

And they were debugging blind. Their monitoring infrastructure had a circular dependency on Consul. When Consul went down, telemetry went down with it. The blog post walks you through several failed hypotheses, each one sounding perfectly reasonable, before finally landing on the real root cause through flame graph analysis over two days into the outage. If you only read one post-mortem from this list, make it this one.

**The lesson:** Your observability stack should never depend on the same infrastructure it monitors. And if you are enabling a new feature in a critical dependency, test it under realistic load before it goes live.

## 2\. ☁️ Cloudflare, November 2025: The Routine Permissions Change That Took Down the Internet

👉 [**Read the full write-up here**](https://blog.cloudflare.com/18-november-2025-outage/)

This one terrified me when I first read it, because the trigger was so mundane.

Cloudflare made a routine permissions change in ClickHouse to make certain table metadata explicitly visible. That’s it. But their Bot Management feature file generator ran a SQL query that didn’t filter by database name. After the permissions change, the query returned duplicate column metadata, and the configuration file more than doubled in size.

This bloated file then propagated across Cloudflare’s entire global network. The Bot Management module had a hardcoded memory limit of 200 ML features (normal usage was around 60). When the doubled file exceeded this limit, the Rust code panicked. Every machine serving traffic started returning HTTP 5xx errors. Core traffic began failing at around 11:20 UTC, and it took until roughly 14:30 UTC to recover core services, with full normalisation by 17:06 UTC.

Their write-up is textbook Cloudflare: they published the exact SQL query, the Rust panic message, a service-by-service impact table, and a detailed timeline. The most striking admission was their commitment to “hardening ingestion of Cloudflare-generated configuration files in the same way we would for user-generated input.” That is the line I keep coming back to, because it captures something most teams (mine included) get wrong.

**The lesson:** Configuration propagation is one of the most underestimated risks in distributed systems. A single change in one database can reach every machine in your network within minutes. Validate internal configuration files with the same rigour you apply to user-generated input.

## 3\. 🐕 Datadog, March 2023: What If Your “Independent” Regions Aren’t?

This post-mortem is unique because it’s not just one blog post. It’s four. [**Start with the main post-mortem**](https://www.datadoghq.com/blog/2023-03-08-multiregion-infrastructure-connectivity-issue/), then read the deep dives on [platform impact](https://www.datadoghq.com/blog/engineering/2023-03-08-deep-dive-into-platform-level-impact/), [incident response](https://www.datadoghq.com/blog/engineering/2023-03-08-deep-dive-into-incident-response/), and [recovery](https://www.datadoghq.com/blog/engineering/2023-03-08-deep-dive-into-platform-level-recovery/).

In March 2023, a routine Ubuntu security update to systemd was automatically applied to tens of thousands of Datadog VMs between 06:00 and 07:00 UTC. When systemd-networkd restarted, it forcibly deleted the routing rules managed by Cilium, its CNI plugin. Nodes lost connectivity instantly.

The truly unsettling part: all five Datadog regions were affected simultaneously. US1, EU1, US3, US4, US5. All of them, at the same time. Datadog had specifically designed its regions to operate independently on different cloud providers with no direct network coupling. But they all shared one thing nobody had considered: a legacy automatic update channel in the base OS image, configured to apply patches in the same time window. That single shared schedule turned five independent regions into one correlated failure domain.

The response involved 450 to 750 active incident responders across four shifts. One insight from their recovery process stuck with me: they prioritised restoring the most recent data over historical backfill, because keeping alerts and dashboards functional during an outage is more valuable than preserving weeks-old metrics. That is the kind of prioritisation you only learn from operating at this scale.

**The lesson:** Regional independence is an architectural assumption, not a guarantee. If your regions share anything, even something as invisible as an OS update schedule, they can fail together.

## 4\. 🌐 Meta, October 2021: When Routine Backbone Maintenance Erased Facebook

👉 [**Read the full write-up here**](https://engineering.fb.com/2021/10/05/networking-traffic/outage-details/)

I remember reading about this one in real time. Facebook, Instagram, WhatsApp, and Messenger all vanished from the internet for roughly six hours. Not degraded. Gone.

During routine backbone network maintenance, an engineer issued a command meant to assess the availability of global backbone capacity. A bug in the audit tool that was supposed to prevent such mistakes failed to stop the command. The result: all connections in Meta’s backbone network were taken down, effectively disconnecting their data centres globally.

Meta’s DNS servers have a built-in safety mechanism. If they can’t reach the data centres, they automatically withdraw their BGP route advertisements. The idea is sound. You don’t want DNS pointing users to servers that can’t respond. But when every data centre went dark simultaneously, every DNS server withdrew its routes at the same time. The rest of the internet suddenly had no way to resolve facebook.com. As Meta’s own engineering team put it, their DNS servers “became unreachable even though they were still operational.”

What I love about this one is that you can read it from two angles. Meta’s engineering blog gives you the insider view. [Cloudflare published a separate analysis](https://blog.cloudflare.com/october-2021-facebook-outage/) showing what the outage looked like from the outside, watching Meta’s BGP routes disappear in real time. Reading both together gives you a deeper understanding of BGP and DNS than any textbook chapter I have come across.

**The lesson:** Always ask this question about your safety mechanisms: what happens when they all fire at the same time during a widespread failure? A safeguard designed for partial outages can amplify a total one.

## 5\. 🤝 Atlassian, April 2022: What Happens When a Script Runs With the Wrong Identifiers

👉 [**Read the full write-up here**](https://www.atlassian.com/engineering/april-2022-outage-update)

I saved this one for last on purpose, because it changes the framing entirely.

In April 2022, 775 Atlassian Cloud customers across 883 sites lost access to all products. ==The full restoration process took until April 18, two weeks after the incident started. The cause wasn’t a cascading system failure or a misconfigured dependency. It was a miscommunication between two teams.==

One team needed to deactivate a specific app called Insight (an asset management tool) across certain sites. They sent the request to the execution team. But instead of providing the app IDs, they accidentally provided the cloud site IDs. The execution script had two modes: “mark for deletion” (recoverable) and “permanently delete” (irreversible, meant for compliance use cases). It ran with the wrong mode and the wrong identifiers. Instead of deactivating one app feature, it permanently deleted 883 entire customer sites.

Recovery was painfully slow because their data stores held information from multiple customers. Each environment had to be manually extracted and rebuilt from backups. Each site took 4 to 5 days to restore. The team eventually scaled to batching 60 sites in parallel, but the damage was already done. The write-up itself is brutally transparent about everything: the communication gap, the script design flaw, and the lack of safeguards against passing the wrong type of identifier.

**The lesson:** When you design systems, you need to design for the humans who operate them. A script that accepts site-level IDs when it expects app-level IDs, with a “permanently delete” mode accessible in routine workflows, is an incident waiting to happen.

## Final Thoughts

When I look back at my own growth as an engineer, the moments that sharpened my instincts the most weren’t the textbooks or the courses. They were the times I sat down with a post-mortem and thought, “I would have made the same mistake.” That is a humbling realisation, and it is exactly the kind of thinking that makes you a better architect.

These five reports rewired the questions I now ask in my own design reviews. *“If our monitoring depends on the thing it monitors, will we even see when it breaks?”* comes from Roblox. *“Are these regions truly independent, or do they share anything?”* comes from Datadog. *“What happens to our safety mechanisms during a total outage, not a partial one?”* comes from Meta. The questions didn’t come from any course I paid for. They came from other engineers’ worst days.

And it doesn’t stop at the famous ones. Some of the most useful post-mortems I have read were internal incidents at the companies I worked at, where I already knew the systems and the people involved. Famous outages give you breadth. Internal ones give you context that no textbook ever will. If your company shares incident reports internally, treat them like gold.

If you want to build production instincts, my honest advice is to make post-mortems a regular habit. The five reports above are a strong starting point, not the destination. The actual write-ups are where the timelines, the wrong hypotheses, and the four-day recoveries live. That is where the gap between “interview-ready” and “production-ready” quietly closes.

Thanks for reading! If this story resonated with you, I’d appreciate a few claps 👏. It really helps more people discover this post.

> If my work provided some value today, you can support me [**here**](https://buymeacoffee.com/freezefrancis) *🤝*.

For system design preparation, check out these pieces:

## [How I Finally Cracked the System Design Interview](https://blog.stackademic.com/how-i-finally-cracked-the-system-design-interview-082eb6a7e15c?source=post_page-----85f6b57b00b6---------------------------------------)

### A personal journey into mastering system design & architecture, overcoming impostor syndrome, thinking like an…

blog.stackademic.com

## [Every System Design Question I Was Asked in Real Interviews at 10+ Companies](https://freezefrancis.medium.com/every-system-design-question-i-was-asked-in-real-interviews-at-10-companies-1b19f4d197c4?source=post_page-----85f6b57b00b6---------------------------------------)

### 10 real system design questions from interviews I actually took — including the ones I bombed.

freezefrancis.medium.com
---
type: System Design Case
title: "Handling a large-scale outage"
description: "This is a true story about handling a large-scale outage written by Staff Engineers at Discord Sahn Lam. About 10 years ago, I witnessed the most impactful UI bugs in my career. It was 9PM on a Fri..."
tags: [system-design]
generated: { by: process:okf-migrate, at: 2026-08-22T00:00:00Z }
---

# Handling a large-scale outage

> **Source**: ByteByteGo — System Design compilation PDF

This is a true story about handling a large-scale outage written by Staff Engineers at Discord Sahn Lam. About 10 years ago, I witnessed the most impactful UI bugs in my career. It was 9PM on a Friday. I was on the team responsible for one of the largest social games at the time. It had about 30 million DAU. I just so happened to glance at the operational dashboard before shutting down for the night. Every line on the dashboard was at zero. At that very moment, I got a phone call from my boss. He said the entire game was down. Firefighting mode. Full on. Everything had shut down. Every single instance on AWS was terminated. HA proxy instances, PHP web servers, MySQL databases, Memcache nodes, everything. It took 50 people 10 hours to bring everything back up. It was quite a feat. That in itself is a story for another day. We used a cloud management software vendor to manage our AWS deployment. This was before Infrastructure as Code was a thing. There was no Terraform. It was so early in cloud computing and we were so big that AWS required an advanced warning before we scaled up. What had gone wrong? The software vendor had introduced a bug that week in their confirmation dialog flow. When terminating a subset of nodes in the UI, it would correctly show in the confirmation dialog box the list of nodes to be terminated, but under the hood, it terminated everything. Shortly before 9PM that fateful evening, one of our poor SREs fulfilled our routine request and terminated an unused Memcache pool. I could only imagine the horror and the phone conversation that ensured.

What kind of code structure could allow this disastrous bug to slip through? We could only guess. We never received a full explanation. What are some of the most impactful software bugs you encountered in your career?

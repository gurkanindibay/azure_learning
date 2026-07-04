---
type: Article
title: "PART 1 — Distinguished Engineer — Behavioural Interview Questions"
description: "Behavioural interview questions and STAR-model answers for Distinguished Engineer roles, covering technical leadership, influence without authority, production incidents, mentoring, and trade-off decisions."
timestamp: 2026-06-18T00:00:00Z
source: "https://medium.com/@rameshwar.blog/part-1-distinguished-engineer-behavioural-interview-questions-323af57f1d53"
author:
  - "Rameshwar Singh"
published: 2026-04-28
tags:
  - "clippings"
  - "interviews"
  - "leadership"
---

# PART 1 — Distinguished Engineer — Behavioural Interview Questions

> **Author**: [Rameshwar Singh](https://medium.com/@rameshwar.blog)  
> **Original**: [Medium Article](https://medium.com/@rameshwar.blog/part-1-distinguished-engineer-behavioural-interview-questions-323af57f1d53)  
> **Published**: April 28, 2026

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*K4K6NKUputIMLgC5fcQRWQ.png)

*Welcome back folks! In this new tech blog I am putting down real-world, experience-based behavioural interview questions for Distinguished Level Engineer roles. These questions often probe complex scenarios involving massive scale, silent failures, organizational politics and long-term system evolution — beyond day-to-day coding.*

> **Interviewer’s Tip** — At this seniority level, interviewers need to focus on the major role-based skills like technical leadership, ambiguous high-stakes decision-making, cross-team influence without authority, driving large-scale impact, handling production crises, mentoring/growing senior talent and balancing technical excellence with business realities.
>
> **Candidate’s Tip** — For each question, candidates should provide an **expert-level deep-dive response** structured using the [STAR method](https://www.amazon.jobs/content/en-gb/how-we-hire/interview-loop#headingFour) (Situation, Task, Action & Result). Be ready to share complex problems, realistic composites drawn from common engineering experiences (large-scale migrations, outages, architectural pivots etc.). Emphasize **depth**: trade-offs, metrics, failure modes considered, stakeholder management and lessons learned. At this level, answers should highlight **ownership**, **strategic thinking** and **measurable business impact** while remaining concise (1.5–3 minutes when spoken)!

---

## Contents

- [Question 1: Significant technical decision impacting multiple teams](#question-1-significant-technical-decision-impacting-multiple-teams)
- [Question 2: Influence a major technical change without direct authority](#question-2-influence-a-major-technical-change-without-direct-authority)
- [Question 3: Hardest technical problem solved](#question-3-hardest-technical-problem-solved)
- [Question 4: Balance technical excellence with business constraints](#question-4-balance-technical-excellence-with-business-constraints)
- [Question 5: Major production incident or outage](#question-5-major-production-incident-or-outage)
- [Question 6: Mentor or develop senior engineers](#question-6-mentor-or-develop-senior-engineers)
- [Question 7: Disagreement with a peer or stakeholder](#question-7-disagreement-with-a-peer-or-stakeholder)
- [Question 8: Initiative on an unassigned improvement](#question-8-initiative-on-an-unassigned-improvement)
- [Question 9: Failure or project that did not go as planned](#question-9-failure-or-project-that-did-not-go-as-planned)
- [Question 10: Prioritize competing projects or technical debt](#question-10-prioritize-competing-projects-or-technical-debt)
- [Key Takeaways](#key-takeaways)
- [References](#references)

---

## Question 1: Significant technical decision impacting multiple teams

**Question**: Tell me about a time you made a significant technical decision that impacted multiple teams or the entire organization.

**Answer: STAR Response**

**Situation**: At a previous company, our core user-facing platform was built on a monolithic architecture that was struggling with 10× traffic growth and frequent outages during peak events. Multiple product teams were blocked on velocity and the platform team was overwhelmed with firefighting.

**Task**: As the lead engineer/architect, I needed to decide whether to incrementally refactor the monolith or pursue a full [strangler fig](https://martinfowler.com/bliki/StranglerFigApplication.html) migration to microservices, knowing it would affect 8+ teams, timelines and customer experience.

**Action**: I first conducted a thorough risk assessment with data from production metrics (latency, error rates, deployment frequency etc.). I then prototyped both approaches (refactor the monolith or migrate to microservices) in a shadow environment and ran chaos experiments. I facilitated a few workshops with cross-functional leads to gather input on dependencies and pain points, then presented a phased migration plan with clear success criteria (for instance, 50% traffic shifted in 3 months). I influenced without direct authority by aligning on shared metrics and piloting with one high-impact service first, incorporating feedback loops.

**Result**: We successfully migrated 70% of traffic within 4 months with zero major incidents. Velocity increased by 3× for product teams and outage frequency dropped by 65%. The decision also established a reusable migration playbook adopted organization-wide.

> **My Learnings**: Early stakeholder alignment and data-driven pilots reduce resistance far more than top-down mandates.

*Interviewer may ask a couple of follow-up questions as well.*

### Follow-up Questions

**FQ1**: What alternatives did you consider, and why did you ultimately reject them?

**Answer**: I evaluated a full big-bang rewrite (too risky, high chance of prolonged downtime) and a pure lift-and-shift (wouldn’t solve underlying scaling issues). The incremental strangler fig approach won because it allowed parallel running, early value delivery and low-risk validation through pilots. Data from the shadow environment showed it minimized blast radius while enabling measurable progress every sprint.

**FQ2**: How did you handle resistance from teams who preferred the status quo?

**Answer**: I addressed it through transparency and shared ownership. I ran joint workshops where teams surfaced their constraints then incorporated their feedback into the plan. By starting with a willing pilot team and broadcasting early wins (for instance, 40% latency improvement), momentum built organically. I also tied the migration to their own OKRs so it felt more collaborative rather than imposed.

**FQ3**: What would you do differently if you had to do it again?

**Answer**: I would invest even earlier in automated contract testing and golden signal monitoring for the migration boundary. While we succeeded that time, we had a few integration surprises in later phases. Adding those would have reduced debugging time by another 20–30%.

---

## Question 2: Influence a major technical change without direct authority

**Question**: Describe a time when you had to influence a major technical change without having direct authority over all involved teams.

**Answer: STAR Response**

**Situation**: I was working in a leading SaaS company. Our organization was using a legacy relational database for a high-write analytics pipeline, causing hotspots and scaling bottlenecks as data volume hit petabytes.

**Task**: I needed to drive adoption of a distributed NoSQL solution across backend, data and infra teams who were comfortable with the status quo and cautious about the migration risks.

**Action**: I started by diving deep into the bottlenecks myself — analyzing query patterns and running benchmarks. I built a proof-of-concept (PoC) with quantifiable gains (2× throughput, 40% cost reduction with levers for adjustments) and shared it transparently in the architecture review forums. I addressed concerns through 1:1s and joint war room sessions, co-authoring a decision record that outlined trade-offs (consistency vs. availability). I volunteered to own the first service migration and provided hands-on support to reduce perceived risk.

**Result**: All major teams adopted the new NoSQL data store within a year, improving system reliability and enabling new features. The change saved millions in scaling costs annually.

> **My Learnings**: Influence comes from shared ownership and demonstrating value rather than pushing mandates.

### Follow-up Questions

**FQ1**: How did you measure and demonstrate the value of the change to skeptical stakeholders?

**Answer**: I used concrete benchmarks like before/after throughput (2×), p99 latency reduction and projected cost savings using current growth curves. I presented these in a one-page decision record with visuals and ran a live PoC demo. Quantifying risk reduction (for instance, elimination of hotspots) helped shift the conversation from opinion to data.

**FQ2**: What was the biggest pushback you received and how did you respond?

**Answer**: The data team was worried about query rewrites and consistency. I responded by co-owning a joint spike with them, providing migration scripts and [dual-write](https://developer.confluent.io/courses/microservices/the-dual-write-problem/) [patterns](https://microservices.io/patterns/data/transactional-outbox.html) during transition. This reduced their perceived burden and built trust through shared accountability.

**FQ3**: How do you know the change had lasting impact beyond the initial adoption?

**Answer**: One year later, the new datastore enabled two new product features that were previously infeasible due to scale limits. Cost savings materialized as projected and the pattern became the default for new services, showing cultural adoption.

---

## Question 3: Hardest technical problem solved

**Question**: Tell me about the hardest technical problem you solved and how you approached it.

**Answer: STAR Response**

**Situation**: While working for a leading healthcare enterprise company, I once faced a silent data corruption issue in a globally distributed key-value store serving billions of requests daily. Corruption was intermittent, only surfacing days later in downstream systems.

**Task**: Identify root cause, contain impact and prevent recurrence while maintaining 99.99% availability.

**Action**: I led a cross-functional tiger team along with using distributed tracing and custom checksum tools to isolate the issue to a rare race condition in replication during network partitions. We implemented [Merkle tree](https://en.wikipedia.org/wiki/Merkle_tree)-based [anti-entropy](https://www.geeksforgeeks.org/system-design/anti-entropy-in-distributed-systems/) repairs, added proactive validation in the write path and rolled out canary deployments with synthetic data load. I coordinated with our SRE team for monitoring enhancements (new SLIs for data integrity) and documented the incident for organizational learning.

**Result**: Corruption incidents dropped to zero and we improved overall system resilience. The fixes became part of our standard reliability patterns.

> **My Learnings**: Promote the value of early investments in observability framework to deal with the “unknown unknowns” at scale.

### Follow-up Questions

**FQ1**: How did you isolate the root cause in such a complex distributed system?

**Answer**: I combined distributed tracing, custom checksums at write/read boundaries and targeted chaos experiments simulating network partitions. The race condition only manifested under specific replication lag + failover timing, so we built a reproducer in a staging environment to confirm before patching.

**FQ2**: What monitoring or observability improvements did you introduce afterward?

**Answer**: We added new SLIs for data integrity (checksum mismatch rate + repair success rate) and integrated Merkle tree sync metrics into our dashboards. We also implemented synthetic end-to-end validation jobs that run continuously.

**FQ3**: How did this incident change your approach to designing resilient systems?

**Answer**: It reinforced my understanding of “[defense in depth](https://en.wikipedia.org/wiki/Defense_in_depth_\(computing\))” — never relying on a single mechanism. I now mandate anti-entropy mechanisms and proactive validation in all storage layers and I push for regular “corruption fire drills” in [chaos engineering](https://en.wikipedia.org/wiki/Chaos_engineering).

---

## Question 4: Balance technical excellence with business constraints

**Question**: Give an example of a time you had to balance technical excellence with business constraints (like tight deadlines or limited resources).

**Answer: STAR Response**

**Situation**: A critical product launch required new real-time ML features but our team was understaffed and the deadline was non-negotiable due to market timing (we were heading for a major conference and planning for a product demo to a wide audience).

**Task**: Deliver functional, scalable features without accumulating unsustainable technical debt.

**Action**: I prioritized by mapping features to user impact and risk, advocating for a phased MVP (core path first, with extensibility hooks). I enabled feature flags for safe rollouts and accepted calculated shortcuts (temporary monolith extensions) while creating a parallel tech debt backlog with owners and timelines. I mentored the team on pragmatic trade-offs and negotiated a 2-week buffer by showing data on launch risks.

**Result**: We launched on time with 95% of target functionality. Post-launch, we paid down technical debt in the next sprint and the system was able to handle 5× expected load.

> **My Learnings**: The unmatched experience gain of highlighting the importance of transparent trade-off communication with cross-functional leadership.

### Follow-up Questions

**FQ1**: How did you decide which technical debt was acceptable to take on?

**Answer**: I scored debt items by risk (blast radius & fix complexity) and impact on velocity/SLOs. Shortcuts were limited to non-core paths with clear rollback plans and feature flags. I maintained a visible debt register with owners and quarterly payback commitments.

**FQ2**: How did you communicate these trade-offs to leadership?

**Answer**: I used a simple framework: “*Here’s what we will gain short-term, here’s the risk and mitigation cost and here’s the payback plan.*” Data on potential launch delay vs. stability risk helped secure the buffer we needed.

**FQ3**: What was the long-term outcome of the debt you incurred?

**Answer**: We paid it down within two sprints post-launch with minimal disruption. The experience improved our team’s ability to have pragmatic technical discussions with product partners.

---

## Question 5: Major production incident or outage

**Question**: Tell me about a time you dealt with a major production incident or outage. How did you handle it?

**Answer: STAR Response**

**Situation**: Recently during a peak traffic event, our notification system experienced cascading failures — delaying millions of critical alerts for over an hour and suspending all the downstream notification pipelines.

**Task**: Restore service quickly, perform root cause analysis and prevent future occurrences while managing stakeholder communication.

**Action**: I jumped into the war room, triaged using dashboards and tracing to identify a [thundering herd](https://en.wikipedia.org/wiki/Thundering_herd_problem) on a downstream dependency. We applied circuit breakers and rate limiting as immediate mitigations then rerouted traffic. Post-incident, I led a blameless postmortem, implemented chaos engineering tests and introduced canary (with other progressive delivery methods like feature flags/blue-green/A-B testing etc.) for future changes. I communicated transparently with execs using clear impact metrics.

**Result**: Notification service was restored in under 30 minutes. Follow-up changes reduced similar outage risk by 80%.

> **My Learnings**: The adoption of continuous postmortem rituals should become a standard template for any organization, strengthening the culture of resilience.

### Follow-up Questions

**FQ1**: Walk me through your immediate actions during the incident.

**Answer**: I first ensured clear command structure in the war room then used tracing to pinpoint the [thundering herd](https://en.wikipedia.org/wiki/Thundering_herd_problem). We applied emergency circuit breakers and rerouted to a secondary path while scaling the affected dependency. Parallel communication channels kept stakeholders informed without noise.

**FQ2**: How did you ensure the postmortem was blameless and actionable?

**Answer**: I set ground rules focused on systems and processes, not people. We identified gaps (missing backpressure, insufficient capacity planning etc.) and turned them into concrete OKRs with owners and timelines.

**FQ3**: What lasting changes resulted from this incident?

**Answer**: We introduced progressive delivery for all notification changes and added [load-shedding](https://cloud.google.com/blog/products/gcp/using-load-shedding-to-survive-a-success-disaster-cre-life-lessons) patterns. Similar outage risk dropped ~80% and the postmortem template was adopted company-wide.

---

## Question 6: Mentor or develop senior engineers

**Question**: Describe a situation where you had to mentor or develop other senior engineers or lead technical growth in your team/organization.

**Answer: STAR Response**

**Situation**: Our engineering org had several strong individual contributors but lacked depth in distributed systems and observability, leading to repeated preventable issues.

**Task**: Elevate the team’s technical capabilities without slowing delivery.

**Action**: I started “architecture office hours,” paired senior engineers on complex tasks and created a reading/group discussion series on papers (like [Dynamo](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf), [Raft](https://raft.github.io/raft.pdf) etc.). I advocated for dedicated learning time to be added into OKRs and personally reviewed designs with constructive feedback. For high-potential individuals, I sponsored a couple of stretch projects with clear success criteria.

**Result**: Within a year, three engineers were promoted to staff level and team-wide incident rates dropped 50%. Knowledge sharing became embedded in our culture, improving overall velocity and quality.

> **My Learnings**: Early adoption of best practices with a mentorship program goes a long way.

### Follow-up Questions

**FQ1**: How did you measure the effectiveness of your mentoring efforts?

**Answer**: Promotion rates (three to staff level), reduction in team incident rates (50%) and qualitative feedback via 360 reviews. I also tracked how often mentees independently led complex designs.

**FQ2**: What challenges did you face in developing senior talent and how did you overcome them?

**Answer**: Some resisted structured learning due to delivery pressure. I solved this by embedding learning into our OKRs and pairing it with high-visibility stretch projects, showing direct career benefits.

**FQ3**: How do you scale mentoring beyond one-on-one?

**Answer**: I used dedicated architecture office hours, internal tech talks and design review guilds. This always creates a multiplier effect where knowledge spreads organically.

---

## Question 7: Disagreement with a peer or stakeholder

**Question**: Tell me about a time you had a disagreement with a peer or stakeholder on a technical approach. How did you resolve it?

**Answer: STAR Response**

**Situation**: Last year, a Product Manager pushed for a quick but brittle solution to a caching problem, while I advocated for a more robust distributed cache with proper invalidation.

**Task**: Reach consensus without delaying the feature while protecting long-term system health.

**Action**: I listened first to understand their timeline pressures then presented data from benchmarks and past incidents showing risks of the shortcut. We ran a joint spike comparing both options quantitatively. I proposed a hybrid solution: implement the robust version behind a flag with a rollback plan.

**Result**: We shipped the better solution on time. The stakeholder later acknowledged the value and it prevented downstream issues.

> **My Learnings**: Building early cross-functional trust strengthens the whole product delivery cycle.

### Follow-up Questions

**FQ1**: How did you ensure the discussion stayed constructive?

**Answer**: I focused on shared goals first (user experience and system health) then presented data neutrally. The joint spike turned it from a debate into a collaborative discovery.

**FQ2**: What would you have done if the stakeholder still disagreed strongly?

**Answer**: I would have escalated with a clear decision record outlining trade-offs and risks, while proposing a time-boxed experiment to gather real data. Escalation should always include actionable options.

**FQ3**: How has this experience shaped how you handle future disagreements?

**Answer**: I now default to “[disagree and commit](https://cdn.cms.amazon.jobs/78/9e/b433c3a04687911b2484b5c16350/have-backbone-disagree-and-commit-transcript.pdf)” language earlier and always document assumptions. It has improved both speed and quality of decisions.

---

## Question 8: Initiative on an unassigned improvement

**Question**: Give an example of when you took initiative on a project or improvement that wasn’t directly assigned to you.

**Answer: STAR Response**

**Situation**: During a FinTech SaaS production incident, I noticed our API gateway was becoming a bottleneck for observability and rate limiting across hundreds of microservices.

**Task**: Improve it proactively to unblock teams.

**Action**: I prototyped enhancements (plugin-based [rate limiting](https://en.wikipedia.org/wiki/Rate_limiting) + [OpenTelemetry](https://opentelemetry.io/docs/what-is-opentelemetry/) integration), quantified benefits (reduced latency variance, better debugging) and pitched it in a tech forum. I then led a small working group to implement and roll it out incrementally.

**Result**: Adoption was rapid, improving debug time by 40% and preventing several potential outages.

> **My Learnings**: It demonstrated how proactive platform enhancement investments compound at scale.

### Follow-up Questions

**FQ1**: How did you prioritize this initiative among your other responsibilities?

**Answer**: I quantified the bottleneck’s impact on team velocity and outage risk then pitched it as a platform investment with clear ROI. I carved out capacity by deferring lower-impact work after alignment with my manager.

**FQ2**: What risks did you identify before starting and how did you mitigate them?

**Answer**: Introducing changes to a critical gateway risked [regressions](https://en.wikipedia.org/wiki/Regression_testing). I mitigated with extensive canary rollouts, rollback plans and shadow testing.

**FQ3**: How was adoption driven across teams?

**Answer**: By making integration trivial (self-serve plugins) and sharing success metrics early. Teams saw immediate debugging and reliability gains, creating pull rather than push!

---

## Question 9: Failure or project that did not go as planned

**Question**: Tell me about a time you failed at work or a project didn’t go as planned. What did you learn?

**Answer: STAR Response**

**Situation**: An ambitious multi-region active-active deployment for a critical data service experienced subtle consistency issues during failover testing, delaying rollout by weeks. This was a complete disaster.

**Task**: Recover the project and extract maximum learning.

**Action**: I owned the setback, conducted a deep retrospective including external experts and identified gaps in our consistency model testing. We adjusted the design to use [CRDTs](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type) for certain paths and added more rigorous chaos scenarios. I shared the lessons broadly via an internal post-mortem meeting with all the stakeholders.

**Result**: The revised rollout succeeded and became more resilient than originally planned. The failure improved our testing standards organization-wide.

> **My Learnings**: Over-optimism on edge cases at global scale requires humility and rigorous validation.

### Follow-up Questions

**FQ1**: What was your personal role in the failure and what else did you learn about yourself?

**Answer**: I underestimated the subtlety of consistency edge cases in active-active setups. It taught me to apply more rigor to “[happy path](https://en.wikipedia.org/wiki/Happy_path)” assumptions in global systems and to seek external reviews earlier on high-ambiguity designs.

**FQ2**: How did you regain momentum after the setback?

**Answer**: I owned the retrospective publicly, brought in external experts for fresh perspectives and broke the revised plan into smaller validated steps with enhanced testing.

**FQ3**: How did you share the lessons learned more broadly?

**Answer**: I presented an internal tech talk and updated our design review checklist with new consistency validation patterns. Several teams later avoided similar pitfalls.

---

## Question 10: Prioritize competing projects or technical debt

**Question**: Describe a time when you had to prioritize or make trade-offs across multiple competing projects or technical debts under pressure.

**Answer: STAR Response**

**Situation**: We had urgent customer requests for new features alongside accumulating tech debt in core infrastructure, with limited engineering bandwidth.

**Task**: Decide what to tackle first without compromising stability or growth.

**Action**: I introduced a weighted scoring framework (business impact, risk, effort, strategic alignment and capital expenses/CapEx vs operational expenses/OpEx price tags) and facilitated a prioritization workshop with product and engineering executives. We ring-fenced 20% capacity for debt and used data from error budgets to justify choices. I communicated the rationale transparently to the senior leadership team.

**Result**: We delivered high-impact features while reducing key risks, maintaining SLOs. This framework was later adopted for quarterly planning, leading to more predictable delivery.

> **My Learnings**: Having a scoring framework with multiple levers helps mitigate such prioritization tasks.

### Follow-up Questions

**FQ1**: How did you handle conflicting priorities from different stakeholders?

**Answer**: The weighted scoring framework made discussions objective. I facilitated a workshop where stakeholders defended their items against the criteria, fostering buy-in for the final list.

**FQ2**: What metrics did you use to validate your prioritization decisions?

**Answer**: Business impact (revenue/user growth), risk to SLOs, CapEx vs OpEx and engineering velocity. Post-quarter reviews showed we hit key features while staying within error budgets.

**FQ3**: How has this framework evolved or been adopted since?

**Answer**: It became the standard for quarterly planning. Teams now come prepared with scored proposals, making prioritization faster and less political.

---

## Final Tips

> For a **Distinguished Engineer** role, strong answers go beyond “what I did” to **why** (strategic reasoning, data/metrics), **how** (influence, trade-offs, failure anticipation) and **impact** (quantified business outcomes + organizational learning). Practice varying your examples to cover different themes (leadership, resilience, influence for example). Interviewers often follow up with “What would you do differently?” or “How did you measure success?” — prepare for depth. Use these as templates and adapt with your real experiences for authenticity!
>
> - Keep follow-up answers data-oriented and reflective.
> - Show you consider second-order effects and organizational impact.
> - Balance confidence with humility (**“what I learned” is powerful**).
> - Practice the full flow: **STAR → Follow-up → Deeper “what if” scenarios**.

*If the above content helped you in your interview preparation, give it a high five!*

---

## Key Takeaways

This article is a source article rather than a system-design case study, so its primary value is the behavioural interview framework and the technical anecdotes that illustrate it. The reusable themes are:

1. **Use the STAR method with depth** — every answer should surface the situation, the decision criteria, concrete actions, quantified results and a personal learning.
2. **Data beats opinion** — benchmarks, error budgets, cost curves, latency/throughput numbers and SLO risk data are the currency of influence at Distinguished level.
3. **Prefer incremental, reversible changes** — strangler-fig migrations, canaries, feature flags, MVPs and phased rollouts reduce blast radius and build organizational buy-in.
4. **Own reliability end-to-end** — the examples repeatedly combine detection (distributed tracing, checksums, synthetic validation), mitigation (circuit breakers, rate limiting, load shedding) and learning (blameless postmortems, chaos engineering, error budgets).
5. **Influence through shared ownership** — workshops, pilot teams, decision records, OKR alignment and transparent metrics turn resistance into momentum.
6. **Invest in organizational learning** — architecture office hours, reading groups, stretch projects, postmortem rituals and reusable playbooks scale impact beyond the individual.

Technical concepts referenced in the answers that have dictionary entries in this repo include [Strangler Fig](../reference-dictionary/architecture-patterns.md#strangler-fig), [Microservices](../reference-dictionary/architecture-patterns.md#microservices), [Monolith](../reference-dictionary/architecture-patterns.md#monolith), [Circuit Breaker](../reference-dictionary/resilience.md#circuit-breaker), [Rate Limiting](../reference-dictionary/api-design.md#rate-limiting), [Thundering Herd](../reference-dictionary/resilience.md#thundering-herd), [Load Shedding](../reference-dictionary/resilience.md#load-shedding), [Defense in Depth](../reference-dictionary/resilience.md#defense-in-depth), [Chaos Engineering](../reference-dictionary/resilience.md#chaos-engineering), [Backpressure](../reference-dictionary/resilience.md#backpressure), [Merkle Tree](../reference-dictionary/databases.md#merkle-tree), [Anti-Entropy](../reference-dictionary/databases.md#anti-entropy), [NoSQL](../reference-dictionary/databases.md#nosql), [CRDT](../reference-dictionary/data-concurrency.md#crdt-conflict-free-replicated-data-type), [Outbox Pattern](../reference-dictionary/cqrs-event-driven.md#outbox-pattern), [Dual-Write Problem](../reference-dictionary/cqrs-event-driven.md#dual-write-problem), [Blue-Green Deployment](../reference-dictionary/architecture-patterns.md#blue-green), [Canary Deployment](../reference-dictionary/architecture-patterns.md#canary-deployment), [Progressive Delivery](../reference-dictionary/architecture-patterns.md#progressive-delivery), [Feature Flag](../reference-dictionary/architecture-patterns.md#feature-flag), [A/B Testing](../reference-dictionary/architecture-patterns.md#ab-testing), [Active-Active](../reference-dictionary/architecture-patterns.md#active-active), [Shadow Testing](../reference-dictionary/architecture-patterns.md#shadow-testing), [OpenTelemetry](../reference-dictionary/observability.md#opentelemetry), [Golden Signals](../reference-dictionary/observability.md#golden-signals), [Error Budget](../reference-dictionary/observability.md#error-budget), [Blameless Postmortem](../reference-dictionary/observability.md#blameless-postmortem) and [Technical Debt](../reference-dictionary/architecture-patterns.md#technical-debt).

---

## References

- [https://aosabook.org/en/v1/nosql.html](https://aosabook.org/en/v1/nosql.html)
- [https://systemdesignschool.io/blog/anti-entropy](https://systemdesignschool.io/blog/anti-entropy)
- [https://en.wikipedia.org/wiki/Collaborative_real-time_editor](https://en.wikipedia.org/wiki/Collaborative_real-time_editor)
- [https://en.wikipedia.org/wiki/Defense_in_depth_(computing)](https://en.wikipedia.org/wiki/Defense_in_depth_\(computing\))
- [https://en.wikipedia.org/wiki/Amdahl%27s_law](https://en.wikipedia.org/wiki/Amdahl%27s_law)
- [http://www.perfdynamics.com/Manifesto/USLscalability.html](http://www.perfdynamics.com/Manifesto/USLscalability.html)
- [https://raft.github.io/](https://raft.github.io/)
- [https://www.aboutamazon.com/news/company-news/2016-letter-to-shareholders](https://www.aboutamazon.com/news/company-news/2016-letter-to-shareholders)

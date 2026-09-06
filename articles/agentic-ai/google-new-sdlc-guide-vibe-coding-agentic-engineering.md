---
type: Article
title: "Google’s New SDLC Guide Draws a Hard Line Between Vibe Coding and Agentic Engineering"
source: "https://medium.com/data-science-collective/googles-new-sdlc-guide-draws-a-hard-line-between-vibe-coding-and-agentic-engineering-29ee5514c48c"
author:
  - "[[Mehmet Özel]]"
published: 2026-06-26
created: 2026-09-06
description: "How Google’s new SDLC framework replaces vibe coding with structured agentic engineering for safer, more reliable AI-powered software delivery."
  - "clippings"
---
## How Google’s new SDLC framework replaces vibe coding with structured agentic engineering for safer, more reliable AI-powered software delivery.

![](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*I3mtqaM0OlNVL6loMx-oug.png)

A split-panel illustration contrasting vibe coding chaotic, fast, unverified against agentic engineering structured, deliberate, production-ready. The dividing line between them is verification.

In February 2025, Andrej Karpathy posted something that quietly broke the internet. He described a new way of programming where you “fully give in to the vibes, embrace exponentials, and forget that the code even exists.” Prompt. Accept. Run. If it breaks, paste the error back and try again.
The term went viral instantly. Not because it was new developers were already working this way. It just finally had a name.
# Google’s New SDLC Guide Draws a Hard Line Between Vibe Coding and Agentic Engineering

How Google’s new SDLC framework replaces vibe coding with structured agentic engineering for safer, more reliable AI-powered software delivery.
Sixteen months later, Google published a 50-page whitepaper titled [The New SDLC With Vibe Coding](https://www.kaggle.com/whitepaper-the-new-SDLC-with-vibe-coding), co-authored by Addy Osmani, Shubham Saboo, and Sokratis Kartakis. The paper is technically dense, carefully structured, and worth reading in full. But its central message is uncomfortable: vibe coding worked fine for prototypes. It is quietly destroying production systems, and most engineering teams don’t realize it yet because the damage accumulates slowly.

**The architectural decision of what belongs in static versus dynamic context is not a configuration detail. It is a first-class engineering trade-off that should be versioned, reviewed, and treated with the same rigor as any other system design decision.**
This piece breaks down what the guide actually argues, where it draws the hard line, and what it means for anyone building software with AI agents in 2026.

**Edge cases. Implicit business logic that exists in institutional memory but not in any document. Integration points between services built by different teams years apart. Subtle correctness requirements that only become visible under real load or real user behavior.**
## Why Vibe Coding Isn’t Enough Anymore

Vibe coding succeeded because it lowered the floor. Developers could prototype features in minutes, non-engineers could build functional tools, and the feedback loop between idea and running code collapsed from days to hours. That is genuinely valuable. Dismissing it entirely is engineering snobbery.

But the floor isn’t the problem. The ceiling is.

As AI agents have become more capable, teams have started applying the same casual, prompt-and-accept workflow to production systems payment APIs, authentication logic, data pipelines, healthcare tooling. The output looks clean. It often passes basic tests. It ships. And then, weeks or months later, something breaks in a way that is expensive and non-obvious to trace.

The reason is structural. Vibe coding was never designed to handle production-grade correctness requirements. It was designed to get something running fast. Those are fundamentally different goals, and the blurring of that line is where the current crisis lives.

Google’s paper is, at its core, an attempt to give engineering teams the vocabulary and framework to stop blurring it.

## The Spectrum: Where Are You Actually Operating?

The paper maps a spectrum from vibe coding on one end to agentic engineering on the other. Most practitioners sit somewhere in the middle and don’t know exactly where which is itself the problem.

![](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*MMw-YL3z5bXLEHVpCuthtg.png)

The spectrum from vibe coding to agentic engineering across three dimensions: intent specification, verification rigor, and risk profile. The differentiating factor is not tooling it is how outputs get verified.

The single differentiating factor across the entire spectrum is not which model you use, not how sophisticated your prompts are, not the tool. It is how outputs get verified.

Without both deterministic tests does this function produce the right output given this input and trajectory evaluations did the agent take the right sequence of reasoning steps to reach that output you are vibe coding regardless of how elaborate your setup appears. A fluent, well-formatted output that skipped its verification steps is not a success. It is a more dangerous failure than one with a visible error, because it is invisible until it hits production.

That is the hard line. And it explains why so many teams running sophisticated agentic workflows are still, technically, vibe coding.

## Agent = Model + Harness

This is the most important technical reframe in the entire paper, and it is the one most developers get wrong.

When an agent misbehaves, the default reaction is to blame the model. The model is too weak, too slow, too hallucination-prone. The fix must be a better model. This reasoning is almost always incorrect.

The model is one component. Everything surrounding it the prompts, the tools, the context policies, the execution sandboxes, the sub-agents, the observability infrastructure is called the harness. Agent behavior is dominated by harness quality far more than model quality.

The paper cites two data points that make this concrete. On Terminal Bench 2.0, one team moved a coding agent from outside the Top 30 to the Top 5 by changing only the harness no model change at all. Separately, a LangChain study raised a coding agent’s benchmark score by 13.7 points purely through changes to the system prompt, tools, and middleware around a fixed underlying model.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*Di6IAxE2o-AZVSeGnLN6CQ.png)

Agent behavior is dominated by harness quality, not model quality. The harness includes everything that surrounds the model: rule files, tools, sandboxes, orchestration logic, guardrails, and observability infrastructure.

The harness is entirely the team’s responsibility. The model provider ships the engine. The team builds the factory floor around it. Most agent failures, examined honestly, are not model failures. They are configuration failures: a missing tool, a vague rule, an absent guardrail, a context window flooded with irrelevant noise. The model gets blamed because it is the visible surface. The harness is where the actual failure lives.

This distinction matters enormously for how teams invest their time. Chasing model upgrades while ignoring harness quality is the engineering equivalent of buying a faster engine and bolting it into a car with no brakes.

## Context Engineering: The Real Competitive Moat

Prompt engineering, as a standalone discipline, is largely obsolete. The skill that replaced it is context engineering the practice of providing agents with rich, structured information about the codebase, architecture, conventions, and intent they are operating within.

The paper identifies six types of context every agent requires: instructions, knowledge, memory, examples, tools, and guardrails. Each of these can be either static always loaded into every interaction or dynamic loaded on demand when the task requires it.

Static context is expensive. Every token is present in every model call, regardless of whether it is relevant. Too much static context wastes tokens, dilutes signal, and can actively degrade agent performance by burying critical rules under noise. Dynamic context is efficient it is fetched from RAG pipelines, triggered by task matching, or pulled from tool results only when the agent actually needs it.

==The architectural decision of what belongs in static versus dynamic context is not a configuration detail. It is a first-class engineering trade-off that should be versioned, reviewed, and treated with the same rigor as any other system design decision.==

The most powerful pattern for managing this is Agent Skills structured, portable packages of procedural knowledge that load only when the task calls for them. Rather than embedding all specialized knowledge into the system prompt, skills let the agent stay a lightweight generalist and flex into specialist behavior on demand.

Example AGENTS.md that handles this boundary cleanly:

```hs
# Project: PaymentService API

## Architecture
- REST API, Node.js, PostgreSQL
- Never modify /src/core/billing without explicit approval

## Agent Skills (load on demand)
- skill:stripe-integration → load when task involves payments
- skill:database-migrations → load when task involves schema changes

## Hard Constraints
- No hardcoded credentials
- All new endpoints require integration tests before merge
```

The syntax is secondary. What matters is intent encoded as constraint. The agent knows what it is, what it can touch, what triggers specialist behavior, and what it can never do without loading all of that into every single context window. This is the difference between an agent that stays reliable across hundreds of tasks and one that drifts unpredictably after the first dozen.

## The 80% Problem: Why Speed Is the Trap

AI agents can generate roughly 80% of the code for any given feature rapidly. That 80% often looks clean, passes surface-level review, and ships without incident. This is where the trap is set.

The remaining 20% is where systems die. ==Edge cases. Implicit business logic that exists in institutional memory but not in any document. Integration points between services built by different teams years apart. Subtle correctness requirements that only become visible under real load or real user behavior.==

What makes this particularly treacherous is that AI errors have evolved in character. Early AI coding tools produced obvious syntax mistakes easy to catch in review. Current generation agents produce conceptual failures: wrong assumptions about business logic, missing edge cases that look plausible, architectural decisions that create hidden long-term maintenance debt. The code looks right. It may pass the test suite. The failure is structural, deferred, and often exponentially more expensive to fix than it would have been to prevent.

This is why trajectory evaluation checking not just the output but the reasoning path the agent took to produce it is not optional in production agentic systems. Output evaluation answers: did the function produce the right result? Trajectory evaluation answers: did the agent understand the problem correctly before generating the function? Both questions are necessary. Only checking output is how the 20% slips through undetected.

The developers navigating this most effectively are not trying to be faster by accepting everything the agent produces. They are faster by focusing their own judgment precisely where AI judgment is structurally weakest ambiguous requirements, architectural trade-offs, and correctness verification at system boundaries.

## Conductor or Orchestrator: The Role Transition That Is Already Happening

The paper describes two operational modes that developers move between, and the shift between them is the most practically significant career transition in software engineering right now.

Conductor mode is real-time and hands-on. The developer is in the IDE, watching code appear, guiding the agent with corrections, maintaining fine-grained control over each change. This mode preserves the intuition and sense of understanding that most engineers are trained toward. The risk is throughput if the developer is personally directing every interaction, the productivity gains from AI are fundamentally capped.

Orchestrator mode operates at a higher abstraction level. The developer defines goals, assigns them to agents, and reviews outputs but is not watching code materialize line by line. Agents run in parallel, in background sandboxes, sometimes for hours, producing pull requests as output. The developer checks in periodically, evaluates results, and provides course corrections.

![](https://miro.medium.com/v2/resize:fit:2000/format:webp/1*UMEBETuFl3istkr3AGzmBA.png)

Conductor mode: real-time, hands-on, single agent. Orchestrator mode: async, parallel agents, pull request as output. Most developers are trained conductors. The transition to orchestrator is the most significant role shift in software engineering right now.

Orchestrator mode demands a different skill set than conductor mode entirely:

Conductor skills center on deep language and syntax knowledge, rapid debugging, codebase intuition, and real-time error interpretation. Orchestrator skills center on precise specification, task decomposition, output evaluation speed, and system design designing the constraints, tests, and feedback loops that keep agents operating reliably without constant supervision.

Most senior developers are highly trained conductors. Orchestration feels uncomfortable because it feels like loss of control. Sometimes it is. Which is exactly why harness infrastructure, eval coverage, and context engineering must be in place before significant orchestration begins. Delegating without verification infrastructure isn’t engineering. It is vibe coding at scale.

## The Economics No One Is Talking About Plainly

The paper introduces a cost model that reframes the entire vibe-coding-versus-agentic-engineering debate as an economics question rather than a methodology debate.

Vibe coding has near-zero upfront cost no spec discipline, no eval infrastructure, no harness design, no AGENTS.md maintenance. But it accumulates hidden operational debt rapidly: token waste from unstructured context, compounding bug surface area from unverified outputs, developer time spent debugging failures that should have been caught by automated evals.

Agentic engineering requires real upfront investment. Specification rigor, evaluation infrastructure, harness design, context architecture. The CapEx is real and it is front-loaded. But the marginal cost per feature drops substantially once the system is built. Each new agent capability benefits from the same harness, the same eval suite, the same context architecture already in place.

At small scale a single developer, a prototype, a side project the vibe coding economics are clearly better. There is no production to protect and the debt never compounds dangerously.

At team scale, the crossover point arrives faster than most people expect. A team of five engineers vibe coding for three months can easily reach a state where a third of their capacity is absorbed by debugging and rework that systematic verification would have prevented. The upfront investment in agentic engineering infrastructure pays for itself, but only if the team makes it before the debt compounds past the tipping point.

## What This Means Going Forward

Google’s paper is not a product announcement. It is a framework document, and it is more useful than most framework documents because its central claims are empirically testable.

The harness effect is real and measurable the benchmark data the paper cites proves that. The 80% problem is real and growing more acute as agents are trusted with more complex tasks. The conductor-to-orchestrator transition is already underway at every serious engineering organization operating at scale.

What the paper leaves unresolved deliberately, it seems is the question of exactly where on the spectrum any given team should operate. That answer depends on stakes, team size, deadline pressure, and technical maturity in ways that no framework document can prescribe. The paper offers the vocabulary and the mental model. The judgment call remains human.

That is probably the most honest thing it could have said.

Structure scales. Vibes don’t. The developers who internalize that distinction now are building on fundamentally different ground than the ones who will learn it the expensive way in production.

## Sources & Further Reading

> [***The New SDLC With Vibe Coding — Addy Osmani, Shubham Saboo, Sokratis Kartakis***](https://www.kaggle.com/whitepaper-the-new-SDLC-with-vibe-coding)*  
> Google’s full 50-page whitepaper. The primary source for everything discussed in this piece.*
> 
> [***Beyond Vibe Coding — Addy Osmani***](https://beyond.addy.ie/)*  
> Osmani’s companion guide expanding on agentic engineering patterns and context design.*
> 
> [***Building Effective AI Agents — Anthropic***](https://www.anthropic.com/research/building-effective-agents)*  
> Anthropic’s foundational research on agent architecture, tool use, and when not to over-engineer.*
> 
> [***Vibe Coding and Agentic Engineering Are Getting Closer Than I’d Like — Simon Willison***](https://simonwillison.net/2026/May/6/vibe-coding-and-agentic-engineering/)*  
> A critical, grounded perspective on where the two paradigms are dangerously converging.*
> 
> [***Agentic Engineering: A Practitioner’s Playbook — Domino.ai***](https://domino.ai/blog/agentic-engineering-practitioners-playbook)*  
> Practical, production-focused breakdown of best practices for teams already operating at scale.*
> 
> [***Google Publishes Scaling Principles for Agentic Architectures — InfoQ***](https://www.infoq.com/news/2026/03/google-multi-agent/)*  
> Coverage of Google and MIT’s framework for scaling multi-agent systems predictably.*

> **All Infographics and diagrams in this article are created by GPT image 2.0**
> 
> ***Thanks For Reading!***
> 
> ***💡 Curious for more? I regularly publish new AI projects on*** [***GitHub***](https://github.com/madara88645)***. If AI chatter is your guilty pleasure, join the convo on*** [***Reddit***](https://www.reddit.com/user/hero88645/)***.***
> 
> ***You can also connect with me on*** [***LinkedIn***](http://www.linkedin.com/in/mehmet-ozel-695227300) ***for more professional insights and updates.  
> Don’t forget to follow me on*** [***Instagram***](https://www.instagram.com/mehmt_ozell/) ***for behind-the-scenes AI content and daily inspiration!***
> 
> ***Thanks for reading — happy prompting! 🙌***
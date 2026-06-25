---
type: Article
title: "You don't need ten agents. You need two tracks."
description: "A two-track agentic development workflow: a high-attention spec track (PRD + technical design) paired with a low-attention implementation track, bounded by the Theory of Constraints."
timestamp: 2026-06-18T00:00:00Z
source: "https://x.com/hugobarauna/status/2067690067288572209"
author: "Hugo Baraúna (@hugobarauna)"
published: 2026-06-18
tags:
  - agentic-ai
  - workflow
  - software-development
---
![Resim](https://pbs.twimg.com/media/HLHpCEVWsAANAeF?format=jpg&name=large)

Spend enough time on the internet, and you'll see someone showing off a terminal with ten coding agents running in parallel. The implied promise is simple: more agents, more productivity. Ship ten times faster! I don't buy that.

Instead of ten, I run only two agents.

I use this workflow to build real software: the back-office system of the [Elixir Radar newsletter](https://elixir-radar.com/), which I use to curate and assemble each issue, send it through my email platform, and let customers manage their own sponsorships.

Now, let me explain the workflow.

## The two tracks

The workflow I use is composed of two tracks: the spec track and the implementation track.

**The spec track**

In the spec track, you start with a feature idea, maybe just a couple of sentences, and end up with a complete functional specification (spec) and a technical design (plan).

First, I ask the agent to help me brainstorm this feature idea. Along the way, the agent will ask me questions to help me clarify my thinking, read the codebase to understand what's already there, and go through it with me step by step. At the end, we have a document outlining the functional requirements for this feature, or what product people call a PRD (product requirements document).

The second step is to ask the agent to create a technical design (architecture) based on the functional spec. Again, the agent will read the codebase, show me a technical design, and ask me questions before I approve it. At the end, the agent creates an implementation plan that includes both the technical design and the work broken down into "engineering tasks".

Once both steps are complete, we have everything we need to start the second track.

**The implementation track**

Using the inputs from the spec track, we can start an implementation track. We say to the agent: "Here's a spec and an implementation plan, please implement this".

Unlike the first track, we don't need to give the agent our full attention on this one, because the agent already has all the input it needs to work on its own for a while. You can decide to review the code as each task finishes or at the end. Either way, we now have time to do some parallel work.

As the agent implements the first feature, you start the next spec. Sometimes the implementation agent needs your attention here and there; you step in, give some feedback, and go back to the spec.

By the time you review and approve the implementation, chances are you've either finished the new spec or are close to it. Once it's ready, you start another implementation agent and keep that cycle going.

## Why only two agents?

There's no perfect number of agents you can run in parallel. But as I used this workflow, I felt that a few things pushed me toward using two agents in parallel rather than ten.

**Balancing two types of attention needs**

In the spec track, the agent needs lots of my attention, while in the implementation track, it doesn't. And because of that, it's possible to work in those two tracks in parallel.

In the spec track, it's not possible to just say to the agent, \*"hey, here's the name of this feature I want to build, and here's a couple of sentences, create a spec and an implementation plan"\*. This is not enough input for the agent; that's why you should have it ask you lots of questions, answer, review... so that by the end, you have well-thought-out input for a more autonomous work.

Now, in the implementation track, you have input artifacts that enable the agent to work more autonomously. Yes, after it finishes generating code, you want to review it. But it will take time for the agent to implement and need feedback, and during that time, you can do something else: the next spec.

Now, contrast that with a scenario where you try to make two specs in parallel: that's much harder to manage. Given that a spec track needs continuous attention, it's hard to parallelize. Which leads us to the next reason to use two tracks instead of ten.

**Specs are the first bottleneck**

Let's say you have ten implementation agents at your disposal. But there's just one of you creating the specs for those agents. How fast do you think this system can go?

The implementation agents can only go as fast as you give them inputs. And you can only create one spec at a time, not ten.

**Finishing the code isn't finishing the work**

Ok, now let's say you got to this point where you were able to write ten (independent) feature specs, and you can now give each of your ten implementation agents one of them in parallel. As they work on that, you could work on another spec, and that cycle could go that way.

But there's a problem. Once one of your implementation agents finishes work, you have human bottlenecks again. Code review, functional human testing, UI improvements.

Software development has different phases, like specification, implementation, and verification. Agents can perform autonomous work on implementation, but specification and verification still require a lot of human touch. You can't make this system go faster by parallelizing phases that aren't the bottleneck.

**You can't delegate UX**

When you're building customer-facing features and you want to build a great product, you can't delegate UX to an agent.

Yes, the agent can implement front-end code and wire it all up to your full stack. But once this part is done, you still need to iterate on the UI. Not because it has to be pixel-perfect, but because building a great product is subjective and opinionated, and that comes from you, not your agent.

## Who is this for?

I believe this workflow is mostly valuable for builders. People who hold the product decisions and the code at the same time. Solo devs, indie hackers, technical founders.

That's not to say it's useless for developers. If a product manager hands you a fully decided spec, the functional requirements work is done, but you still need to turn that into a technical design and an implementation plan for your agent. And while the agent builds it, you can start the technical design for the next item in the product backlog. So maybe you can handle more than two tracks, but still, probably not ten.

All that said, there's a context where this workflow is not useful. Specs, plans, and code review only pay for themselves on code that's meant to live. For any kind of work that will be thrown away at the end, vibe coding is fine.

## A working example

As I said, this isn't theory. It's how I built the software I use to run Elixir Radar. So I recorded a video to make it concrete: an unedited, end-to-end run of the two-track workflow being applied on a production app.

<video preload="none" tabindex="-1" playsinline="" aria-label="Yerleştirilmiş video" poster="https://pbs.twimg.com/amplify_video_thumb/2067688382457630720/img/6IQRYhDGzAzEaOTw.jpg" style="width: 100%; height: 100%; position: absolute; background-color: black; top: 0%; left: 0%; transform: rotate(0deg) scale(1.005);"><source type="video/mp4" src="blob:https://x.com/cd6a0594-fdae-4f73-a1f3-5955c56b0dbd"></video>

0:35 / 20:01

Besides showing the workflow in action, I also show the tools I use to implement it:

- [Tidewave](https://tidewave.ai/): the agentic dev environment for Phoenix and Rails
- [Superpowers](https://github.com/obra/superpowers): agent skills for creating specs and implementation plans

## Evolution, not disruption

After reflecting on why this workflow is working for me, I noticed it's not by accident. There's actually a lot of knowledge and practice in software engineering and systems thinking that led me to it.

For example, the fact that a system can only go as fast as its bottleneck is from the theory of constraints and queueing theory.

The idea of finishing and reviewing what you have before starting more in parallel comes from Kanban's "Stop starting, start finishing".

The "two tracks" name I got from "Dual-Track Development", which was popularized back then by Marty Cagan, from the product management community.

We need to remember that there's already a lot of established knowledge and theory we can leverage; we're not in completely uncharted territory. Yes, the new tools are remarkable, but the principles still apply. It's a matter of adapting them to an agentic development world.
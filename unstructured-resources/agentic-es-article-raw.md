---
type: Unstructured Note
title: "Building an Agentic AI Platform to Facilitate Event Storming Sessions"
source: "https://medium.com/gitconnected/building-an-agentic-ai-platform-to-facilitate-event-storming-sessions-590f1d528ecb"
author:
- "[[Matt Bentley]]"
published: 2026-10-12
created: 2026-10-13
description: "Navigating the challenges and iterations of architecting a multi-agent AI platform."
tags:
- "clippings"
---

## Navigating the challenges and iterations of architecting a multi-agent AI platform.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*PocFnB8smbfbxKvh_C-8ow.png)

Screenshot of AI Generated HTML by Author

E ==vent Storming (ES) is my favourite technique for breaking down complex== software problems and designing reliable systems. Never heard of Event Storming? Fear not, that’s kind of the point here!

I love ES because it brings different teams together to collaborate and also forces us to think about problems in the right way — focusing on Events (behaviours and side-effects) first and then working through a data model at the very end of the process. Far too often I see teams jump straight to a data model first and then develop some weird unhealthy obsession with it, which gets in the way of focusing on what really matters: the behaviour of the system.

The prescriptive process that ES imposes is what drives us to think about systems in the right way, but it also creates a very high barrier to entry, which I find often puts people off from jumping in to try it. Being the facilitator of an ES session is a particularly daunting prospect because getting a good quality outcome depends so heavily on having an effective facilitator. I generally recommend having an experienced architect facilitating sessions, and they are particularly hard to come by.

LLMs are brilliant for ES because they understand everything about software architecture and they also understand everything about Event Storming. We can easily teach them about the domain that we’re modelling.

When most apps add AI features, it tends to be in an unimaginative chat bot. That doesn’t really work for ES, since a good facilitator should be probing and prompting the team — not the other way around. So, I wanted to flip the typical status quo and have AI prompt the people from the session autonomously instead, just as a good facilitator would. Throughout this article, I’ll cover the different iterations I went through to get there and challenges that I faced along the way.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*YtxdfvehJNCWNO8235azbQ.png)

Iterations of Event Storming Agent Platform

## Event Storming Basics

I’ll only scratch the surface of ES here — if you want a proper deep dive, I have previously written an article about it here: [Why You Should Be Using Event Storming](https://medium.com/better-programming/why-you-should-be-using-event-storming-2f32e5280c8c).

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*6KgVMLUyfJefLj4I1tAH7A.png)

Event Storming Note Types

The first phase invites everyone to note down as many Events (Orange sticky) as possible and roughly try to order them by time. An Event must be something that happened in the past e.g. Item Added to Basket.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*Ph4PkZcfa9iuii_mNQSGkg.png)

Identifying Events

The next phase focuses on logic and side-effects by working through Commands (Blue sticky) that initiated Events and Policies (Pink sticky) which follow Events. Commands can be automated or manual; manual Commands get a small yellow User Role sticky on them. Commands essentially map to chunks of code that will be written to do stuff. Policies map to logic, which acts as the glue between different Events and Commands across a system.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*QFWGdo_rkd1wVkgpQ7qRdA.png)

Adding Commands & Policies

Often not everything can be answered in a single session — any questions or points to come back to are noted as Concerns (Red sticky).

The final stage assigns Aggregates (Yellow sticky) throughout the system, based on the Events and Commands. These are the data structures which will be written in code and generally stored in a database. The names of the Aggregates generally fall straight out of Commands and Events that have already been worked through. This works way better than trying to shoehorn code and logic into data structures which have already been set in stone.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*cwNoihPbR_jubqN8lAxBnw.png)

Defining Aggregates

You should finish with a clear, well documented and well understood system design, which engineers can easily take forward to build.

## StormSpace

I already had an interactive web app which could be used to run collaborative ES sessions: StormSpace. It uses HTML canvas to allow multiple users to add sticky notes to different ES boards. It also uses ASP.NET and SignalR to provide real-time updates across all boards and users.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*56P4ofmXJxf_RZuCRX33Rw.gif)

StormSpace App

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*OUGyuPuykXUKwns5vbwttw.png)

A StormSpace Board

StormSpace is designed to guide boards through 5 distinct Event Storming phases:

1. **Set Context:** Define the domain boundary, business goal, actors, and session scope.
2. **Identify Events:** Brainstorm past-tense domain events and arrange them chronologically.
3. **Add Commands & Policies:** Identify what triggers each event and the resulting business rules.
4. **Define Aggregates:** Group related behaviour around the core domain objects responsible for consistency.
5. **Break It Down:** Identify bounded contexts, subdomains, and integration boundaries.

An architecture technique known as Event Sourcing is used to store all actions that have happened on a board as a series of events, known as an Event Stream. This allows the full history of a board to be kept and replayed or undone as required.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*59iRjP0d9RTKzjerrk9YvQ.png)

StormSpace Event Sourcing

## AI Agents

We will use AI Agents as the main building block. Before starting, let’s loosely define what that is:

> An AI agent is an AI component that can independently decide what actions to take and use connected tools to achieve a user-provided goal.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*EVsX38mgAGuY45yBZsfxOg.png)

Anatomy of an AI Agent

Often agents are given a custom “ **System Prompt** ” which defines a specific role, behaviours and guardrails that the AI component adheres to.

### Tools

Custom tools are the most important ingredient for cooking up powerful agents. They can provide agents the ability to execute and read things that vanilla LLM can’t.

StormSpace already has logic throughout the system to perform any events storming activity that we need. The first step is simply segregating this code into separate blocks of code called functions which we can expose as tools to an agent.

Here are the functions that I created for StormSpace:

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*a8oIE5cZicZfEAuq3GKv-w.png)

StormSpace Toolbox

### Microsoft Agent Framework

Microsoft Agent Framework (MAF) is a framework which makes it super easy to create agents in code. It currently supports Python and.NET. There’s loads of other great frameworks out there which do this too, such as Pydantic and LangChain, but since StormSpace is built in.NET this is the best choice.

MAF supports decorating your functions so that the agent can understand what they do, when to invoke them and the format of any inputs and outputs.

<iframe src="https://medium.com/media/20be3e0451ddc4f46fa7185710b5dd1a" allowfullscreen="" frameborder="0" height="888" width="680" title="EventNoteTool.cs"></iframe>

Example MAF Agent.NET Tool

MAF handles all of the complicated plumbing for wiring up the tools and system prompt to an agent and its specified LLM. It also handles passing messages in and out of agents for your system to consume, and even supports different agents talking to each other too.

<iframe src="https://medium.com/media/d988cc569cf20ed4d6f5b27d84686507" allowfullscreen="" frameborder="0" height="917" width="680" title="WorkshopAgentExample.cs"></iframe>

Example MAF.NET Agent Setup

## Iterative Development Process

### Iteration 1: Single Agent Assistant

As a first step, I just wanted to get a basic chat assistant setup, so that I could quickly validate whether AI was capable of orchestrating the different tools that I had made available within an Event Storming context.

I just setup a single MAF agent and gave it access to all of my StormSpace tools and GPT-5.6 Terra. I also had to setup an extremely long system prompt to explain StormSpace, my exact ES rules and the persona that I wanted the agent to take on. It’s important for the agent to be inquisitive and try to tease answers out of the board users, rather than jump to give them all of the answers — that is exactly what a good facilitator should do.

I also wired up the agent to a chat section in the UI. I really wanted good visibility into what exactly the agent was doing on a board, so I added callouts to show which tools the agent was using in real-time. I did this by publishing SignalR events whenever a tool call starts and ends, and subscribed to these on the frontend.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*_jQEEFNO1F8T7RiKV-kQhQ.png)

Facilitator Agent

Straight out of the gate I found that my simple Terra agent was extremely impressive! It could comfortably work with my boards and arrange different sticky notes in the exact layout that I wanted. It was also brilliant at taking on the questioning nature that I wanted from my facilitator.

### Iteration 2: Single Agent Autonomous Facilitator

Next I wanted to add the real differentiator for my agent: enabling it to run autonomously, without being prompted by a board user. I designed the autonomous triggers for the agent based on how an experienced human facilitator would act. The agent will fire on the earliest occurrence of:

- **User Activity Debounce:** Any user changed the board and then remained inactive for at least *30 seconds* e.g. Note creation, movement, editing, deletion.
- **Timer:** *3 minutes* passed since the previous agent turn (including user-initiated turns).
![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*A9j_wH30ISJtBdjkuZZVCw.png)

Facilitator Agent Activity Loop

I used a basic prompt to fire the agent when an autonomous turn was required:

```c
[AUTONOMOUS_FACILITATOR_LOOP]
Autonomous facilitator loop trigger: { userActivityDebounce | timer}.
Review the board and recent activity before acting.

- Call GetRecentEvents as well as GetBoardState so you can tell whether a phase has just started or changed.
- Ask at most one concise question or perform one small facilitation move.
- When a phase has just started, you may perform a small starter demonstration example.
- Autonomous facilitation must not delete existing notes or connections.
- If there is nothing meaningful to add right now, do not call any tools and return an empty response.
- If the workshop is clearly complete, use the CompleteAutonomousSession tool.
```

I also added an option in the UI to configure whether the autonomous facilitator was enabled for each board.

I run the autonomous facilitator in a background thread in the StormSpace API. This makes it simple to host, since there’s only 1 process to manage/host. StormSpace is only designed to run a few boards at once — if I were to scale-out to more boards, then it would be better to run the autonomous facilitator in a separately hosted process.

### Iteration 3: Context-Driven System Prompt

The autonomous facilitator worked very well initially, however I found that it started to hallucinate and miss key concepts towards the later ES phases as boards grew. My original system prompt had tonnes of different rules for the agent to follow across all 5 phases, and it was way too much for it to handle as the number of notes on the board increased. The other issue I found was that the agent was too generic — it didn’t perform well on certain domains or when there was lots of niche domain-specific language used on the board.

I addressed both of these issues by dynamically configuring the agent system prompt as followed:

- **Phase-Specific Instructions:** Only the rules and guardrails for the current ES phase of the board were added. This meant that the agent had less constraints to focus on, enabling it to do a better job of the actual phase in-progress.
- **Custom Board Context:** Custom domain-specific context could be configured for each board and added to the system prompt. This enabled teams to tell the agent about areas that the underlying LLM didn’t already understand.
![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*KccByoDwAj7bxTe1QLKQvw.png)

Configurable Board Context

### Iteration 4: Agentic (Multi-Agent) Facilitator

Making the system prompt more dynamic improved the agent but it was still making a few mistakes when the boards got very complex. It was also taking quite a long time to complete its turns as well. I was using a fairly powerful model (GPT-5.6 Terra), but the problem was that the agent was doing way too much — it was providing architecture guidance, facilitating sessions, explaining Event Storming concepts, making changes to the board, reviewing the board, cleaning up the board, showing demonstration examples and giving advice about the domain being modeled. AI agents perform best when they are only taking on 1 specific role. I was asking it to take on many roles all at once!

This is exactly why multi-agent patterns are so powerful. Each agent can take on a small role only from the problem space and do it well. There are many different patterns for architecting multi-agent systems — I decided to go with an orchestrated subagent pattern. There was a central orchestrator (Facilitator agent) which all turns would be initiated through and a team of subagents which it could “delegate” to.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*TuUof5B2wp54Ch-tjMoppA.png)

Facilitator Subagent Integrations

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*9hknNYCrwPm9OLZDo2dFag.png)

Multi-Agent Collaboration

MAF supports different agent integration patterns, however I found that I got more control and better results by building my own integrations. I did this by creating a `DelegateToAgent` tool, which the Facilitator could call to delegate something to another agent.

Each agent has its own system prompt which is designed for the exact role that it needs to perform. I added configuration to control which specific ES phases each agent would activate across. The available tools are also limited for each agent, depending on what it needs to do. Breaking the problem down across multiple agents also means that different LLM models and reasoning levels can be chosen for each agent. I found that I could now switch most of the agents to a much cheaper model (GPT-5.6 Luna) and it would perform even better than before and much faster too.

### Iteration 5: Extended Agent Integration Options

I now had a multi-agent system which was absolutely nailing managing boards and guiding teams through a whole session end-to-end. However, for some of the more complex domains it wasn’t always suggesting the correct terminologies and designs. I still had agents which were responsible for managing a specific phase, as well as being responsible for being domain experts too. I wanted to add a Domain Expert agent which other agents could call on for domain knowledge instead, so they can purely focus on their task at hand. The Domain Expert wouldn’t be able to manipulate boards, it could just offer expert advice on the specific domain being modeled for the session.

I achieved this by creating a Domain Expert agent which only had access to read-only tools across boards. I also added a new `AstQuestion` integration tool which allowed agents to ask other agents questions and receive a response. I also changed the system prompts in the other agents to tell them to ask the Domain Expert agent whenever they need to make a change to a board.

This provides a really interesting behaviour across the agentic system where the agents have conversations and work together on a board, just as we would do as humans in an ES session.

I also added a `RequestBoardReview` tool which allowed agents to request other agents to review areas of the board which they specialised in.

![](https://miro.medium.com/v2/resize:fit:1340/format:webp/1*M3EMFjxwxZEYLsSkTxWRww.png)

Extended Agent Integrations

### Iteration 6: Customisable Agentic Platform

By this stage the agentic system was performing amazingly across even the most complex boards and domains being modeled. I had all of my agents softly configured, so that it was easy to create different dynamic integration patterns. Having dynamic configurations for my agents and integrations also meant that I could easily surface that to users of StormSpace for customization per board.

I created a simple UI which allowed users to customise the agents for a specific board — this included configuring the system prompts, tools for each ES phase and integration patterns via Delegate, AskQuestions and Review. I also provided users a way of removing and adding agents, so that completely different agentic behaviours could be achieved.

For example, when modelling a particularly complex domain it may work better to break down the DomainExpert into a set of different roles, such as Software Architect, Risk Manager, Accountant, Warehouse Manager etc.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*dH0F_o8ztJoViaitRz-yfQ.png)

Agent Configuration UI

We now have a powerful, flexible agentic platform which can be customised to handle even the most complex ES domains. We can customise the agent behaviours and integrations, as well as how the ES sessions run across the various different phases. Everything is tied to a board, which can be exported and imported as needed.

Building an agentic system is difficult. Even the most capable frontier models have limitations — but if you can provide an easy way to break-down the problem using granular agents which perform a specific role, then you can get some pretty impressive results! Generally the super users of your systems are the ones who are best placed to understand what works best for them, so giving them a flexible platform and tooling which enables them to build their own agents can be extremely powerful. The libraries and models out there at the moment make this easier than ever!

*All of the code for StormSpace can be found on be GitHub below.*

## [GitHub - matt-bentley/StormSpace: StormSpace is a collaborative interactive Event Storming web…](https://github.com/matt-bentley/StormSpace?source=post_page-----590f1d528ecb-----------------------------------------)

### StormSpace is a collaborative interactive Event Storming web application. StormSpace allows multiple users to…

github.com
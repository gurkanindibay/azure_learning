---
type: Article
title: "Harness, Loop, and Graph Engineering: Understand Clearly in 15 Minutes+"
description: "A layered breakdown of agent architecture — harness (scaffolding), loop (feedback cycle), and graph (control flow) — with pseudocode, diagnostics, and common failure patterns."
timestamp: 2026-08-08T00:00:00Z
source: "https://medium.com/ai-in-plain-english/harness-loop-and-graph-engineering-understand-clearly-in-10-minutes-bfaa86480724"
author: "Nick T. (Ph.D.)"
---

# Harness, Loop, and Graph Engineering: Understand Clearly in 15 Minutes+

> **Source**: [Medium — AI in Plain English](https://medium.com/ai-in-plain-english/harness-loop-and-graph-engineering-understand-clearly-in-10-minutes-bfaa86480724) (2026-07-30)
> **Related**: [Agent Harness](../../reference-dictionary/ai-ml-llm.md#agent-harness), [Loop Engineering](../../reference-dictionary/ai-ml-llm.md#loop-engineering), [Graph Engineering](../../reference-dictionary/ai-ml-llm.md#graph-engineering)

---

If you've spent any time in agent-building circles, you've probably heard "harness engineering," "loop engineering," and "graph engineering" tossed around as if they were interchangeable. They aren't.

They sit near each other, they all touch the same model, and yes, all three can technically involve something that loops — which is exactly why people mash them together. But they answer three different design questions, and mixing them up is how teams end up debugging the wrong layer for weeks.

## The One-Paragraph Version

1. **Harness engineering** is about building the scaffolding a model lives inside — its tools, memory, permissions, and execution environment.
2. **Loop engineering** is about designing the cycle of attempt, check, and retry that turns a single model call into a process with a real stopping point.
3. **Graph engineering** is about drawing the map of what's allowed to run next: the nodes, branches, parallel paths, and merge points that keep a multi-step workflow from turning into spaghetti.

> **A useful shorthand**: harness is the environment, loop is the feedback cycle, graph is the flow.

## Layer 1: Agent Harness Engineering

### What It Actually Is

LangChain frames it most cleanly: an **agent = model + harness**, where the harness covers every bit of code, configuration, and execution logic surrounding the model but not part of it.

In practice that means the system prompt, tool definitions, memory, the filesystem the agent can touch, sandboxing, model-routing decisions, agent-to-agent handoffs, middleware hooks, context compaction, permission boundaries, logging, and whatever interfaces check the agent's output.

OpenAI's Agents SDK describes the identical layer from a different angle — the runtime side. Their "runner" is the piece that calls the model, executes whatever tools the model requests, manages handoffs between agents, carries state forward between turns, and only stops once the run hits a genuine terminal condition rather than just running out of things to say.

### Why "Harness" Is the Right Word

Calling this layer a harness (instead of, say, "the app" or "the wrapper") does real work: it pulls attention away from treating the model as the whole story. Two teams can point the exact same foundation model at the exact same problem and get wildly different results, because one team gave it well-scoped tools, a stable place to work, tight permissions, and state it can inspect — while the other gave it a loose prompt and a flaky API client held together with retries. The raw intelligence is comparable. The working conditions are not.

**Picture a support-ticket triage agent:**

- Team A wires it up with a narrow `search_knowledge_base(query)` tool, a `draft_reply(ticket_id, text)` tool that writes to a review queue instead of sending directly, a permission model that blocks it from touching billing records, and a log of every tool call it makes.
- Team B gives it a single `call_internal_api(endpoint, payload)` tool with no schema, full write access to the ticket database, and no logging. Both run the same underlying model. Team A's agent is debuggable, auditable, and safe to leave running overnight. Team B's agent will eventually do something nobody can explain, and nobody will be able to reconstruct why.

### The Pieces a Well-Engineered Harness Usually Includes

Six major component groupings in a harness:

- **Context injection** — instructions, retrieved documents, prior conversation turns, loaded skills, and any task-specific policy the agent needs before it starts.
- **Action surfaces** — the APIs, browser control, shell access, code execution sandbox, database connections, and MCP-style tools the agent is actually allowed to call.
- **Persistence** — files, checkpoints, session records, running progress logs, git history, and any longer-term memory store.
- **Execution control** — timeouts, retry limits, spend budgets, which model handles which sub-task, the ability to spawn sub-agents, and approval checkpoints before risky actions.
- **Safety and governance** — permission scopes, sandbox isolation, allow-lists for tools and domains, secret handling, and human sign-off requirements.
- **Observability** — full traces, recorded tool inputs and outputs, state transition history, cost tracking, latency, and evaluation scores.

A quick diagnostic: strip the model out of your architecture diagram entirely. Everything still standing — the tool layer, the data connections, the state store, the sandbox, the middleware, the graders, the retry policy, the UI shell — that's your harness.

### Where Harness Work Pays Off the Most

Anthropic's engineering team ran into this directly while building agents for multi-day coding tasks. Context compaction alone — just summarizing old messages to save space — wasn't enough to keep a coding agent oriented across sessions.

**What actually fixed it wasn't a smarter prompt; it was restructuring the harness itself**: an initializer step that sets up a clean starting state, a persistent `claude-progress.txt` file that narrates what's been done and what's left, real git commits marking milestones, and a discipline of small, verifiable increments so that a brand-new context window can orient itself in seconds instead of replaying the whole history.

```
on session_start():
    if not exists("claude-progress.txt"):
        run initializer_agent()
        # scaffolds repo, writes initial progress file, first commit
    progress = read("claude-progress.txt")
    recent_commits = git_log(limit=10)
    context = build_context(progress, recent_commits)  # not the full history

on task_step_complete(step_result):
    append("claude-progress.txt", summarize(step_result))
    git_commit(message=step_result.summary)

on session_end():
    checkpoint_state()
    # so the next session, possibly a different context window,
    # can resume without re-deriving what already happened
```

That's a harness fix, not a prompt fix. No amount of "please remember what you did earlier" phrasing solves a problem that lives in the absence of durable state.

Reach for harness engineering when the agent lacks a capability it needs, can't recover cleanly from an interruption, loses track of where it is, has more access than the task requires, can't be audited after the fact, or behaves inconsistently depending on which environment it's running in. Those are all environment problems, and no amount of prompt tuning fixes an environment problem.

There's outside evidence for how much this layer matters on its own:

- LangChain reported jumping from outside the top 30 to rank 5 on TerminalBench 2.0 by changing nothing but the harness around an unchanged model.
- Stanford's IRIS Lab and KRAFTON AI went a step further with a "Meta-Harness" project that used an LLM to iteratively redesign its own harness and outperformed every hand-built system on the leaderboard. Same intelligence, different scaffolding, very different scores.

## Layer 2: Loop Engineering

### The Loop That's Already There

Every tool-using agent already contains a small, implicit loop: call the model, look at what came back, run whatever tool it asked for, feed the result back in, and repeat until the model produces a final answer. That's the baseline.

> Loop engineering starts the moment a team deliberately wraps additional cycles around that baseline instead of leaving it as one unstructured while-loop.

- A **verification loop** lets the agent produce something, run it through a deterministic check or a grading step, get specific feedback about what failed, and try again only if there's actual evidence of a problem.
- An **event-driven loop** wakes the agent on a schedule, a webhook, or the arrival of a new document rather than waiting for a human to press go.
- An **improvement loop** studies traces and past failures, adjusts the agent's instructions or toolset, and tests whether the new version genuinely performs better before adopting it. LangChain's 2026 framing calls this a "stack of loops," which is a better mental model than imagining one magic retry statement doing all the work.

### Anatomy of a Loop Worth Calling "Engineered"

- **Trigger** — what kicks off another cycle: a user request, a schedule, a failed test, fresh data, or feedback from an evaluator.
- **Goal** — a concrete state to reach, not an open-ended instruction like "keep improving it."
- **State and memory** — the minimum the next cycle needs to know, without forcing it to replay everything that came before.
- **Action policy** — exactly what the agent is permitted to change, call, delegate, or spend on this cycle.
- **Evidence** — a passing test suite, valid output against a schema, resolvable citations, a clean diff, a metric that clears its threshold, or an actual human reviewer approving the result.
- **Feedback** — a short, specific explanation of why the evidence came back negative, not just a pass/fail flag.
- **Stopping rule** — success, budget exhausted, timeout, an error that can't be recovered from, or escalation to a person.

### Worked Example: An Agent That Writes and Validates SQL

Say the task is turning a stakeholder's plain-English question into a query against a production warehouse.

```
def sql_verification_loop(question, max_attempts=4):
    attempt = 0
    feedback = None

    while attempt < max_attempts:
        query = model.generate_sql(question, prior_feedback=feedback)
        result = run_against_read_replica(query)  # never the primary

        checks = [
            schema_matches(query, warehouse_schema),
            explain_plan_cost(query) < COST_BUDGET,
            result.row_count > 0 or question.expects_empty_ok,
        ]

        if all(checks):
            # evidence-based success, not "the model says it's done"
            return query, result

        # specific: "column `user_id` doesn't exist on `orders`"
        feedback = describe_failures(checks)
        attempt += 1

    return escalate_to_human(question, last_attempt=query, reason=feedback)
```

Notice what the loop does **not** do: it never asks the model "are you confident this is correct?" and treats "yes" as a stopping condition. It stops on schema validation, a cost check, and a sanity check on the result set — all external, all checkable without asking the model to grade its own work.

That's the core discipline: **loop on evidence, not on confidence.**

- "The agent claims it's finished" isn't a stopping condition.
- "The tests pass, the citations resolve, the schema validates, and a reviewer signed off" is.

Recent field guides on this pattern describe a related idea worth stealing: the **loop contract** — writing down the goal, scope, verifier, state, stop condition, escalation path, and budget *before* the agent starts, rather than discovering the stopping logic by watching it run forever in a terminal. Some practitioners frame it as an "operator test": if the agent can't produce proof that it's done, you haven't built a loop, you've automated drift.

### Loop Engineering Isn't Just a Fancier Prompt

A prompt shapes what the model does *during* one call. A loop determines what the system does *after* the call comes back:

- how it inspects the result,
- what feedback it extracts,
- whether it goes again,
- how it saves progress, and
- what makes it stop.

Prompt quality still matters inside each cycle, but the loop is what turns a single instruction into a managed, checkable process instead of a one-shot guess.

### Trade-off / Risks

**The tradeoff is cost and latency** — every additional grader, reviewer pass, or retry is another model call or tool execution, and that adds up fast at scale. Anthropic's general guidance on agent design is to default to the simplest architecture that works and only add agentic machinery once there's measurable evidence it earns its cost.

**The same rule applies one level down to loops specifically**: add a verification or retry cycle where the cost of a bad output is clearly higher than the cost of checking for one — not everywhere, by default, because it feels safer.

## Layer 3: Graph Engineering

### The Question a Graph Answers

Graph engineering isn't primarily about what a single agent should do next — it's about **which component is allowed to run next at all.** Steps become nodes. Legal transitions between them become edges. Those edges can represent a simple sequence, a conditional branch, a fan-out into parallel work, a join where parallel branches recombine, a controlled cycle, or a pause for human input. State moves through the graph, and the shape of the graph itself is what enforces the control flow you actually want — rather than hoping the model infers it correctly every time.

Two mainstream frameworks show this from different angles.

1. **LangGraph** bills itself as a lower-level runtime built specifically for agents that run long and need to hold state — durable execution, persisted checkpoints, and built-in pause points for a human to step in, all in service of giving the developer real control instead of hiding the workflow behind a tidy abstraction.
2. **Microsoft's AutoGen**, through its GraphFlow pattern, states the trigger condition plainly: reach for a graph once you need strict control over agent execution order, different outcomes to route to different next steps, branching that has to be deterministic, or a multi-step process where cycles are a legitimate, planned part of the design.

### What a Graph Engineer Is Actually Deciding

- **Node boundaries** — which piece of work belongs in a deterministic function, which belongs in a single LLM call, which needs a specialist agent, and which needs a human in the loop.
- **State schema** — what each node is allowed to read or write, and how conflicting updates from parallel branches get merged.
- **Routing conditions** — which piece of evidence sends the work forward, sends it back for another pass, redirects it sideways, or escalates it.
- **Concurrency** — what's safe to run in parallel, what has to join back together before continuing, and which shared resources need coordination to avoid collisions.
- **Cycles and exits** — exactly where a retry is legal, how many are allowed before the system gives up, and what guarantees the cycle can't spin forever.
- **Durability** — where the system checkpoints progress, and how a run resumes cleanly after a crash or a deliberate pause.

### Use Case: A Research-and-Publish Pipeline for a Weekly Industry Brief

An intake node classifies the request, three research nodes run in parallel against different source types, a join node merges their output once all three land, a drafting node writes the piece, a fact-check node grades it against the research artifacts, a conditional edge sends it back to drafting on failure or forward on success, and a human-approval node gates final publication.

```
graph = WorkflowGraph()
graph.add_node("classify_request", fn=classify_topic)
graph.add_node("research_news", fn=search_news_sources)
graph.add_node("research_papers", fn=search_academic_sources)
graph.add_node("research_filings", fn=search_company_filings)
graph.add_node("merge_research", fn=join_and_dedupe)
graph.add_node("draft_brief", fn=write_draft)
graph.add_node("fact_check", fn=verify_claims_against_sources)
graph.add_node("human_approval", fn=await_editor_signoff)
graph.add_node("publish", fn=publish_to_medium)
graph.add_edge("classify_request", ["research_news", "research_papers", "research_filings"])  # fan-out
graph.add_join(["research_news", "research_papers", "research_filings"], "merge_research")     # join
graph.add_edge("merge_research", "draft_brief")
graph.add_edge("draft_brief", "fact_check")
graph.add_conditional_edge(
    "fact_check",
    condition=lambda state: state.unverified_claims == 0,
    on_pass="human_approval",
    on_fail="draft_brief",       # controlled cycle, capped at 3 loops
    max_cycles=3,
)
graph.add_edge("human_approval", "publish")
graph.set_checkpointing(after_every_node=True)  # resume cleanly if interrupted mid-run
```

That structure makes the multi-agent system inspectable — you can look at a failed run and immediately see which node it died in, rather than reverse-engineering a transcript.

To be clear, this is a **different construct from a *knowledge* graph**, where nodes and edges represent entities and facts in a dataset. Here, the graph represents control flow and state transitions in a running process, not stored knowledge.

### When a Graph Is Worth It — and When It Isn't

Graphs earn their complexity when a process genuinely has meaningful branches, real parallel work, required approvals, recovery paths, or several specialist agents that need a defined handoff order.

**They earn a lot less when the job is really just "give one capable agent three tools and let it figure out the order."**

A graph can make debugging dramatically easier, but it can also lock in assumptions before you've learned enough to make them. If the task genuinely requires the model to improvise its plan on the fly, forcing every conceivable path into a fixed diagram ahead of time tends to make the system more brittle, not more reliable.

## Watching All Three Layers Work Together

Take that research-and-publish example and zoom out.

- The **graph** defines the route: classify, fan out to research, join, draft, fact-check, approve, publish.
- Inside the fact-check-and-redraft segment, a **loop** governs the retry: generate evidence, check claims against sources, get specific feedback on what's unsupported, redraft, and stop either on a clean pass or after three attempts.
- Wrapping the entire thing is the **harness**: the search tools and CMS API the nodes call, the durable state store that survives a restart mid-pipeline, the permission boundary that keeps a research node from accidentally invoking the publish action, and the trace log an engineer can replay after something goes wrong.

The nesting is what matters here:

- the graph is contained by the harness, each loop is contained by a node somewhere in that graph, and the harness is the thing quietly supplying the state, tools, and evaluators every one of those loops relies on.
- The boundaries between the three get fuzzy in practice, the way boundaries between any real software layers tend to — but each layer still gives your team its own, distinct lever to pull once something breaks.

## The Expensive Mistakes That Keep Showing Up

1. **Drawing the graph before anyone's watched the agent actually work.**
   It's tempting to translate a business process straight into forty nodes on day one. The better sequence is to run a simpler harness first, collect real traces, see which paths the agent actually takes and where it struggles, then formalize only the parts that turn out to be stable.

2. **Letting one model write its own homework and grade it too.**
   Self-review has some value, but it shares the same blind spots as the model that produced the work in the first place — it tends to miss exactly the errors it was already prone to making. Favour deterministic checks wherever you can get them, give any reviewing model a genuinely separate context, and require a human sign-off on anything with real consequences.

3. **Writing "keep trying" where a loop specification should be.**
   An unbounded retry with no defined success criteria is just a slow way to burn budget. Every loop needs a measurable goal, fresh evidence on each pass, a hard cap on attempts, and a named path to escalate to a human.

4. **Treating the harness like a junk drawer.**
   Piling on more tools and more memory doesn't automatically make an agent better. A cluttered toolset increases the odds the model picks the wrong tool, a noisy context window increases confusion, and overly broad permissions increase your blast radius when something does go wrong.

5. **Blaming the model for what's really an orchestration problem.**
   A model has no way to reliably paper over stale state, ambiguous tool schemas, a flaky API, or missing exit conditions — no matter how good the underlying weights are. Fix the layer that actually owns the failure instead of reaching for a bigger or "smarter" model as the default answer.

## Diagnosing a Failure: Which Layer Do You Actually Fix?

| Symptom | Start With | Likely Fix |
|:---|:---|:---|
| The agent can't safely reach the data or tool it needs. | Harness | Tool definitions, permission scopes, sandbox configuration |
| The agent loses the thread across sessions. | Harness | A state store that survives restarts, checkpoints, a running progress log, and better compaction |
| The first attempt is usually close but not dependable. | Loop | Add a verification loop with evidence-based stopping criteria |
| The agent keeps grinding after it's already succeeded, or quits before proving it worked. | Loop | Evidence-based terminal states, budget-aware stop rules |
| Multiple specialists need to run in a strict, controlled order. | Graph + Harness | Traces that line up with graph nodes and state transitions |
| The workflow shifts too often to justify a fixed diagram. | Simpler harness | Keep the control model-driven for now; hold off on formalizing a graph |

## The Short Version

- **Harness engineering** builds the machine the model runs inside.
- **Loop engineering** makes the process iterative, checkable, and resumable instead of one-shot.
- **Graph engineering** takes a genuinely complex execution path and makes it explicit and controllable instead of implicit and hoped-for.

None of the three substitutes for the other two:

- A gorgeous graph diagram won't save you if the harness underneath can't hold state.
- The most carefully tuned harness in the world is money wasted if nothing verifies the work or knows when to stop.
- And a well-specified loop still turns into unmanageable ad-hoc code once branching, parallel work, and approval gates start getting bolted on without a graph to hold them.

Design the three together, understand what each one is actually responsible for, and reliable agent systems stop being a matter of luck.

## Sources

- [LangChain — The Anatomy of an Agent Harness](https://www.langchain.com/blog/the-anatomy-of-an-agent-harness)
- [OpenAI Agents SDK — Agents documentation](https://openai.github.io/openai-agents-python/agents/)
- [OpenAI Agents SDK — Handoffs documentation](https://openai.github.io/openai-agents-python/handoffs/)
- [Anthropic Engineering — Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Anthropic Engineering — Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [LangGraph overview — LangChain Docs](https://docs.langchain.com/oss/python/langgraph/overview)
- [Microsoft AutoGen — GraphFlow (Workflows)](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/graph-flow.html)

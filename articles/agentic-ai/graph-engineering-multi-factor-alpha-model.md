---
type: Article
title: "How to Use Graph Engineering to Build a Multi-Factor Alpha Model"
description: "A step-by-step guide to building a self-running multi-factor alpha model using graph engineering — progressing from prompts to loops to swarms to AI agent graphs that coordinate factor construction, validation, and risk decomposition autonomously."
source: "https://x.com/RohOnChain/status/2080296261576687751"
author: "Roan (@RohOnChain)"
published: 2026-07-23
created: 2026-08-06
generated: { by: process:okf-migrate, at: 2026-08-06T00:00:00Z }
---

# How to Use Graph Engineering to Build a Multi-Factor Alpha Model

> **Source**: [X.com — @RohOnChain](https://x.com/RohOnChain/status/2080296261576687751)

I am going to break down exactly how to build a hedge fund grade multi-factor alpha model using graph engineering.

Multi-factor investing is how every serious hedge fund on Wall Street generates returns. They do not trade single ideas. They stack factors. This is the same process AQR runs. The same process Two Sigma runs. The same process Bridgewater runs. And it is the first time it has been executable by a solo builder.

The problem has always been that building this required a research team. Factor engineers. Statisticians. Portfolio construction specialists. Risk analysts. Execution engineers. You need at least ten people per factor family, and no solo quant can build that team.

**That is why retail quants stick to single strategies and hedge funds print alpha.** Until now.

In prior articles the author walked through **loop engineering** and how to build a **swarm of AI agents that hunts alpha 24/7**. Once you have loops and swarms, the layer that holds them together as one working system is a graph.

> **Graph engineering is the practice of designing that layer. You define the nodes. You define the edges. The graph runs itself.**

---

## Part 1: What Graph Engineering Actually Is

Every quant working with AI is somewhere on the same progression. Naming where you are makes it obvious where to go next.

| Stage | Description |
|:---|:---|
| **Stage 1: Prompts** | You type a prompt. You wait. You read the output. You type the next one. You are the loop. Nothing survives when you close the laptop. |
| **Stage 2: Loops** | You write a script that wraps the prompt and fires on a schedule. The loop holds state. It survives after you close the laptop. One agent, one job, running forever. |
| **Stage 3: Swarms** | You fan the loop out into many agents with specialized roles. One generates signals. One validates them. One executes. Multiple agents in parallel, coordinated by hand through Python glue code. |
| **Stage 4: Graphs** | You describe the coordination structure once. Nodes are agents. Edges are data hand-offs. The graph knows when to parallel, when to wait, when to retry, when to escalate. You do not touch the glue code again. |

Graph engineering is the practice of designing that coordination structure.

A graph is not a script. That distinction matters more than anyone tells you.

A script breaks the moment one agent needs to wait on another. A script breaks the moment state has to persist across cycles. A script breaks the moment you want six loops in parallel on different models. Every retail quant who has tried to build a multi-agent system has hit these three walls.

> A graph does not have those failure modes. Parallel is native. State is persistent. Failure is scoped to the node, not the pipeline. When a node breaks, the rest of the graph keeps running, and you patch the broken node by describing the failure in plain English.

That is the promise of graph engineering.

---

## Part 2: The Tool That Runs The Graph

Graphs are architectural diagrams. They do not run themselves. They need a runtime.

The runtime is what most people building multi-agent systems get wrong. They assume the hard part is designing the graph. It is not. The hard part is finding infrastructure that can actually execute it.

The tool used is **Slate**, built by [@wearerandomlabs](https://x.com/wearerandomlabs). It runs in the terminal, picks up existing model subscriptions, and fans out work across them.

A key capability is **Programs** — a graph written in JavaScript that Slate runs continuously. A prompt runs once and stops. A Program keeps going until the task is done.

You do not write the Program alone. You tell Slate what you want in plain English. Slate drafts the graph, presents a diagram, and you iterate until satisfied.

### Example Programs

**`/goal` — Graphs That Run Until Verifiably Done**

Slate spins up a graph: one node writes a function, another writes the verification test, a third runs both, a fourth grades whether outputs match. If they do not match, the graph loops back with the specific mismatch as feedback. This is the **maker-checker pattern** in a runtime — the maker never grades the maker's own work.

**`/deepresearch` — Graphs That Parallelize Research**

Slate dispatches multiple worker agents at once. Each owns a different angle of the question. One reads recent papers. Another checks arXiv. Another pulls data from academic libraries. They all report back to a central orchestrator that synthesizes the findings.

The reason `/deepresearch` matters for this build is that it demonstrates the exact pattern needed for factor construction: seven factor agents, each owning a different factor, all running in parallel, all reporting to a central orchestrator.

---

## Part 3: The Multi-Factor Alpha Graph

Multi-factor investing decomposes stock returns into systematic drivers plus a residual. The foundational version is the Fama-French three-factor model, published in 1993:

$$R_i - R_f = \alpha + \beta_1(R_m - R_f) + \beta_2(\text{SMB}) + \beta_3(\text{HML}) + \epsilon$$

Where $R_i$ is stock return, $R_f$ is risk-free rate, $R_m$ is market return, SMB is size premium, and HML is value premium. The alpha $\alpha$ is what the model cannot explain — that residual is what you are hunting.

Carhart added momentum in 1997. Fama and French added profitability (RMW) and investment (CMA) in 2015.

### The Seven Factors (2026)

| # | Factor | Description |
|:---|:---|:---|
| 1 | **Market Beta** | Rolling 60-month regression of stock excess return against market excess return |
| 2 | **Size (SMB)** | Small cap outperforms large cap on a risk-adjusted basis |
| 3 | **Value (HML)** | High book-to-market outperforms low book-to-market over long horizons |
| 4 | **Momentum (MOM)** | Recent 12-month winners keep winning for 3-12 months |
| 5 | **Profitability (RMW)** | Robust operators outperform weak operators |
| 6 | **Investment (CMA)** | Conservative asset growth outperforms aggressive expansion |
| 7 | **Low Volatility** | Low-vol stocks earn higher risk-adjusted returns than theory predicts |

Every fund runs a version of this. Solo builders cannot because it needs a research team. **Graph engineering solves that. Each factor becomes a node.**

### The Full Graph — 11 Nodes

**Factor Construction Nodes (run in parallel):**

| Node | Agent | Task |
|:---|:---|:---|
| 1 | **Market Beta Agent** | Runs the rolling 60-month regression; outputs a beta for every stock |
| 2 | **Size Agent** | Sorts by market cap; computes the small-big spread |
| 3 | **Value Agent** | Sorts by book-to-market; computes the high-low spread |
| 4 | **Momentum Agent** | Computes 12-minus-1 month momentum; constructs MOM from the decile spread |
| 5 | **Profitability Agent** | Computes gross profitability; constructs RMW |
| 6 | **Investment Agent** | Computes annual asset growth; constructs CMA |
| 7 | **Low Vol Agent** | Computes trailing 60-day realized volatility; constructs low-vol from the decile spread |

**Coordination Nodes (run in sequence):**

| Node | Agent | Task |
|:---|:---|:---|
| 8 | **The Validator** | Runs Newey-West adjusted t-statistics on each factor. Bootstrap resamples 10,000 iterations. Kills any factor with in-sample vs out-of-sample degradation above 30%. Runs on a stronger reasoning model — the maker never validates the maker's own work. |
| 9 | **The Regime Auditor** | Segments the 20-year history into three regimes using a Hidden Markov Model on volatility and returns. Kills anything that only works in one regime. |
| 10 | **The Portfolio Constructor** | Combines surviving factors into a long-short portfolio using risk parity weights. Enforces sector, beta, and dollar neutrality. |
| 11 | **The Risk Decomposer** | Regresses the portfolio against the seven factors plus style and macro factors. Reports residual alpha and t-statistic. |

Only signals where the residual alpha survives factor decomposition are genuine new alpha. Everything else is repackaged style with extra steps.

---

## Part 4: How To Build It Step By Step

### Step 1: Install Slate

```bash
npm i -g @randomlabs/slate
```

### Step 2: Create Your Project Directory

```bash
mkdir ~/projects/multifactor-alpha
cd ~/projects/multifactor-alpha
```

State namespacing is per workspace — do not run other Slate projects out of the same folder.

### Step 3: Launch Slate

```bash
slate
```

### Step 4: Connect Your Providers

Inside Slate, type `/providers`. Random Labs authenticates by default. You can also connect OpenAI Codex and GitHub Copilot directly.

### Step 5: Connect Your Models

Type `/models`. You want two model tiers: a fast tier for the seven factor construction agents (e.g., Claude Sonnet), and a stronger reasoning tier for the validator, regime auditor, and risk decomposer (e.g., Claude Opus).

### Step 6: Warm Up With `/goal` and `/deepresearch`

Spend 30 minutes with the shipped example Programs to build graph engineering intuition before drafting your own.

### Step 7: Draft The Multi-Factor Program

Describe the graph in plain English:

```plaintext
draft me a program that runs seven multi-factor research agents in parallel:
market beta, size, value, momentum, profitability, investment, and low-volatility.
After all seven complete, run a validator, a regime auditor, a portfolio
constructor, and a risk decomposer in sequence. Use Claude Sonnet for the seven
factor agents and Claude Opus for validator, regime auditor, and risk decomposer.
Run the whole pipeline every 24 hours. Use file system as memory. Set a budget
of $30 per run. Enforce Newey-West t-stat above 2.5, bootstrap 10,000 iterations,
and reject any factor with in-sample versus out-of-sample Sharpe degradation
above 30 percent.
```

Slate reads carefully and asks clarifying questions: which data source, what backtest window, which universe, what regime classifier.

### Step 8: Review The Graph Diagram

Slate renders a diagram of the graph. You look at the coordination structure: seven factor nodes in parallel, a sync point, four coordination nodes in sequence, a persistence step, a sleep node, a loop back to the top. Ask questions before running.

### Step 9: Save And Run

```bash
slate run multifactor-alpha.js
```

The first run takes 15-25 minutes. Subsequent daily runs are faster because the state file already holds history.

### Step 10: Set A Budget

```bash
/budget $30/run
```

### Step 11: Debug When It Breaks

You describe the problem to Slate. Slate patches the node. You do not chase a stack trace.

---

## Part 5: What Actually Happened When I Ran It

Slate drafted the entire Program in one pass — full JavaScript, eleven nodes wired together, parallel factor construction, sequential validation, filesystem shared memory with timestamped run directories, budget allocations. It came back with three specific decisions to confirm:

1. **Portfolio constructor model** — defaulted to Opus but flagged as flippable to Sonnet
2. **Model versions** — used current stable versions, offered newer ones
3. **Budget enforcement** — explicitly noted the $30/run cap was advisory, not a hard kill switch (no real-time cost metering primitive exists)

The third callout is why the author trusts this tool: most agent frameworks would silently pretend the budget was enforced. Slate told exactly what layer of enforcement it could actually provide.

---

## Part 6: What Happens Every 24 Hours

At 3am, the graph wakes up:

1. **Seven factor agents fire in parallel** — each pulls the latest 24 hours of price and fundamental data, updates its factor time series
2. **Validator** runs Newey-West t-tests, bootstraps 10,000 samples, kills anything that failed out-of-sample (~80% of what looks promising on a first backtest gets rejected here)
3. **Regime auditor** takes what survived, segments history using HMM, recomputes Sharpe per regime. A factor that only works in one regime is not alpha — it is beta to that regime
4. **Portfolio constructor** builds the long-short portfolio with neutrality constraints enforced
5. **Risk decomposer** regresses the portfolio against the broad style and macro factor set

If the residual alpha t-stat is above 2.5, the signal survives. If not, the day is logged as "no signal" and the graph sleeps until tomorrow.

Every morning you wake up to a Slack message. Either you have a signal you can trade, or you have documented evidence that today was noise. Both outcomes are useful. Neither required you to be at the keyboard.

---

## The Blueprint

1. **Understand the progression** — Prompts became loops. Loops became swarms. Swarms became graphs.
2. **Know your factors** — Market, size, value, momentum, profitability, investment, low volatility. Seven factors. Each becomes a node.
3. **Design eleven nodes** — Seven factor agents in parallel. Four coordination agents in sequence. Draw the graph before writing code.
4. **Use different models for different nodes** — Sonnet for factor construction. Opus for validation and decomposition. Maker never validates maker.
5. **Enforce hard rules** — Newey-West t-stat above 2.5. Bootstrap 10,000 iterations. Regime robustness across three HMM states. Residual alpha t-stat above 2.5.
6. **Warm up with `/goal` and `/deepresearch`** — Graph engineering intuition comes from watching graphs, not reading about them.
7. **Let it compound** — Month one is finding bugs. Month two is refining factors. By month three, your graph produces signals you can actually trade.

---

> **Original Source**: [X.com — @RohOnChain](https://x.com/RohOnChain/status/2080296261576687751)
> **Tool Referenced**: Slate by [@wearerandomlabs](https://x.com/wearerandomlabs) — available at [randomlabs.ai/rr](http://randomlabs.ai/rr)

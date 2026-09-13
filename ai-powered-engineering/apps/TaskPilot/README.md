# TaskPilot: Standalone Enterprise Task & Workflow Management App

> **Architecture**: .NET 8 / 10 Standalone Clean Architecture Application  
> **Framework Dependencies**: **Zero Agent / Zero LLM Dependencies**  
> **Role in Catalog**: Developed *using* the 4-layer Agentic Engineering system (Harness, Loop, Agents) as the developer bot, producing a pure standalone software product.  

---

## 1. Overview

**TaskPilot** is a production-grade, standalone task and workflow management system built with Clean Architecture in C# / .NET. 

Unlike embedded agent systems where the AI loop runs as part of the application's runtime, **TaskPilot is a pure, traditional business application**:
- Zero dependencies on agent loops, prompt templates, or AI harnesses.
- Strong domain models and state-machine transitions (`Backlog` $\rightarrow$ `InProgress` $\rightarrow$ `Review` $\rightarrow$ `Done`).
- Thread-safe, atomic file-backed JSON repository with in-memory caching.
- Rich CLI interface with color-coded status, priority tags, and overdue tracking.
- Independent 100% passing xUnit test suite.

---

## 2. Architecture & Layering

```
apps/TaskPilot/
├── TaskPilot.sln                       # Solution file
├── src/
│   ├── TaskPilot.Core/                 # Domain models, enums, interfaces, state validation
│   ├── TaskPilot.Infrastructure/       # JsonTaskRepository (async lock, atomic file writes)
│   ├── TaskPilot.Services/             # TaskService (business workflows, metrics, query filters)
│   └── TaskPilot.Cli/                  # Standalone CLI console entry point
└── tests/
    └── TaskPilot.Tests/                # 13 xUnit unit tests
```

### Domain Invariants & Rules
1. **Title Validation**: Non-empty, maximum 200 characters.
2. **Workflow Progression**: Tasks in `Backlog` cannot jump directly to `Done` without being in progress or under review.
3. **Timestamp Tracking**: Reaching `Done` stamps `CompletedAtUtc`; reopening a task clears the completion timestamp.
4. **Overdue Detection**: Dynamically flags incomplete tasks whose due date is in the past.

---

## 3. Quickstart & Usage

### 1. Run Unit Tests
```bash
cd ai-powered-engineering/apps/TaskPilot
dotnet test
```
**Output**: `Passed! - Failed: 0, Passed: 13, Skipped: 0, Total: 13, Duration: 82 ms`

### 2. Run CLI Commands

```bash
# Seed initial sample tasks
dotnet run --project src/TaskPilot.Cli -- seed

# List all tasks
dotnet run --project src/TaskPilot.Cli -- list

# Filter tasks by priority, status, or tag
dotnet run --project src/TaskPilot.Cli -- list --priority Critical
dotnet run --project src/TaskPilot.Cli -- list --tag backend
dotnet run --project src/TaskPilot.Cli -- list --overdue

# Add a new task
dotnet run --project src/TaskPilot.Cli -- add "Refactor Billing Service" --priority High --due 2026-09-30 --tags fintech,billing

# Transition workflow state
dotnet run --project src/TaskPilot.Cli -- move <task-id> InProgress
dotnet run --project src/TaskPilot.Cli -- move <task-id> Done

# View workflow summary metrics
dotnet run --project src/TaskPilot.Cli -- summary
```

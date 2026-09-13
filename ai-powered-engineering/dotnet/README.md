# PatchMaster: AI-Powered Agentic Refactoring Bot (.NET)

> **Platform**: .NET 8 / C# 12  
> **Core Concepts**: Roslyn AST Syntax Gate, Sandboxed `dotnet test` Execution, 5-Phase Self-Healing Loop, Directed State Graph, xUnit Benchmark Evals.

---

## 1. Architectural Overview

| Layer | .NET Implementation | Role |
|:---|:---|:---|
| **1. Harness** | [`src/PatchMaster.Harness/RoslynSyntaxGate.cs`](src/PatchMaster.Harness/RoslynSyntaxGate.cs)<br>[`src/PatchMaster.Harness/DotnetTestSandbox.cs`](src/PatchMaster.Harness/DotnetTestSandbox.cs)<br>[`src/PatchMaster.Harness/ContextManager.cs`](src/PatchMaster.Harness/ContextManager.cs) | In-memory Roslyn AST check, isolated ephemeral `dotnet test` runner, and stack trace distillation. |
| **2. Loop** | [`src/PatchMaster.Loop/VerifyGate.cs`](src/PatchMaster.Loop/VerifyGate.cs)<br>[`src/PatchMaster.Loop/LoopController.cs`](src/PatchMaster.Loop/LoopController.cs) | 5-phase loop (`Discover` $\rightarrow$ `Plan` $\rightarrow$ `Execute` $\rightarrow$ `Verify` $\rightarrow$ `Iterate`) with Maker/Checker separation. |
| **3. Graph** | [`src/PatchMaster.Graph/RefactorGraphEngine.cs`](src/PatchMaster.Graph/RefactorGraphEngine.cs) | Explicit state machine with fast delivery, diagnostic feedback cycling, and max iteration escalation. |
| **4. Evals** | [`benchmarks/PatchMaster.Benchmarks/`](benchmarks/PatchMaster.Benchmarks/) | Automated benchmark suite evaluating C# defect scenarios and computing Pass@1 / Pass@3 metrics. |

---

## 2. Project Layout

```
ai-powered-engineering/dotnet/
├── PatchMaster.sln
├── src/
│   ├── PatchMaster.Core/          # State, Phase enum, VerificationResult, Interfaces
│   ├── PatchMaster.Harness/       # Roslyn AST parser, Process Sandbox, ContextManager
│   ├── PatchMaster.Agents/        # IMakerAgent, HeuristicMakerAgent, RuleBasedCheckerAgent
│   ├── PatchMaster.Loop/          # Deterministic VerifyGate, LoopController
│   ├── PatchMaster.Graph/         # RefactorGraphEngine state machine & step tracing
│   └── PatchMaster.Cli/           # Command-line application
├── benchmarks/
│   └── PatchMaster.Benchmarks/    # Benchmark runner & C# defect fixtures (xUnit)
└── tests/
    └── PatchMaster.Tests/         # xUnit unit tests for all architectural layers
```

---

## 3. How to Run

### Run Benchmark Evaluation Suite
```bash
# Via benchmarks project directly
dotnet run --project benchmarks/PatchMaster.Benchmarks

# Or via unified CLI
dotnet run --project src/PatchMaster.Cli -- --benchmark
```

### Run Unit Tests
```bash
dotnet test tests/PatchMaster.Tests
```

### Run CLI on an Individual Target File
```bash
# Using local heuristic agent (0 API keys needed)
dotnet run --project src/PatchMaster.Cli -- \
  --target benchmarks/PatchMaster.Benchmarks/Fixtures/case_01_off_by_one/Solution.cs \
  --test benchmarks/PatchMaster.Benchmarks/Fixtures/case_01_off_by_one/SolutionTests.cs

# Using live LLM (OpenAI / Azure / Gemini API key)
export OPENAI_API_KEY="your-api-key"
dotnet run --project src/PatchMaster.Cli -- \
  --target benchmarks/PatchMaster.Benchmarks/Fixtures/case_01_off_by_one/Solution.cs \
  --test benchmarks/PatchMaster.Benchmarks/Fixtures/case_01_off_by_one/SolutionTests.cs \
  --llm
```

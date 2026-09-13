using Xunit;
using PatchMaster.Core;
using PatchMaster.Agents;
using PatchMaster.Loop;

namespace PatchMaster.Tests;

public class FakeSandbox : ISandbox
{
    private readonly Func<string, (bool Passed, int ExitCode, string Stdout, string Stderr)> _handler;

    public FakeSandbox(Func<string, (bool Passed, int ExitCode, string Stdout, string Stderr)> handler)
    {
        _handler = handler;
    }

    public (bool Passed, int ExitCode, string Stdout, string Stderr) RunTests(string code, string testCode)
    {
        return _handler(code);
    }
}

public class LoopTests
{
    [Fact]
    public void RuleBasedCheckerAgent_RejectsSecurityViolations()
    {
        var checker = new RuleBasedCheckerAgent();
        var maliciousCode = "class A { void Run() { System.Diagnostics.Process.Start(\"calc\"); } }";
        var (approved, reason) = checker.Audit(maliciousCode, "class A {}");

        Assert.False(approved);
        Assert.Contains("Security Violation", reason);
    }

    [Fact]
    public void VerifyGate_SyntaxError_FailsBeforeSandbox()
    {
        var fakeSandbox = new FakeSandbox(_ => throw new Exception("Sandbox should not be called on syntax error"));
        var gate = new VerifyGate(fakeSandbox);

        var brokenCode = "public class Bad { int x = ; }";
        var res = gate.Verify("class A {}", brokenCode, "class T {}");

        Assert.False(res.Passed);
        Assert.False(res.AstValid);
        Assert.Contains("Roslyn AST Syntax Check Failed", res.ErrorSummary);
    }

    [Fact]
    public void LoopController_ConvergesOnSecondIteration()
    {
        var failingCode = "public class Calc { public int Add(int a, int b) => a - b; }";
        var passingCode = "public class Calc { public int Add(int a, int b) => a + b; }";

        var fakeSandbox = new FakeSandbox(code =>
        {
            var passed = code.Contains("a + b");
            return (passed, passed ? 0 : 1, passed ? "Passed" : "Failed", string.Empty);
        });

        var maker = new MockMakerAgent(new List<string> { failingCode, passingCode });
        var gate = new VerifyGate(fakeSandbox);
        var controller = new LoopController(maker, verifyGate: gate);

        var state = new AgentState
        {
            TaskId = "test_loop",
            OriginalCode = failingCode,
            CurrentCode = failingCode,
            TestCode = "test",
            MaxIterations = 3
        };

        // Step 1: Discover
        state = controller.StepDiscover(state);
        Assert.False(state.LatestVerification!.Passed);

        // Iteration 1 (Maker emits failingCode)
        state = controller.StepPlan(state);
        state = controller.StepExecute(state);
        state = controller.StepVerify(state);
        Assert.False(state.LatestVerification!.Passed);
        state = controller.StepIterate(state);
        Assert.Equal(1, state.Iteration);
        Assert.False(state.IsTerminal);

        // Iteration 2 (Maker emits passingCode)
        state = controller.StepPlan(state);
        state = controller.StepExecute(state);
        state = controller.StepVerify(state);
        Assert.True(state.LatestVerification!.Passed);
        state = controller.StepIterate(state);
        Assert.True(state.IsTerminal);
        Assert.Equal(Phase.Deliver, state.CurrentPhase);
    }
}

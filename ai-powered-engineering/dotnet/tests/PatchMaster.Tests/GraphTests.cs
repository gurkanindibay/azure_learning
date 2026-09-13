using Xunit;
using PatchMaster.Core;
using PatchMaster.Agents;
using PatchMaster.Loop;
using PatchMaster.Graph;

namespace PatchMaster.Tests;

public class GraphTests
{
    [Fact]
    public void RefactorGraphEngine_FastPathDelivery_WhenAlreadyPassing()
    {
        var passingCode = "public class A {}";
        var fakeSandbox = new FakeSandbox(_ => (true, 0, "Passed", string.Empty));
        var gate = new VerifyGate(fakeSandbox);
        var controller = new LoopController(new MockMakerAgent(), verifyGate: gate);
        var engine = new RefactorGraphEngine(controller);

        var state = new AgentState
        {
            TaskId = "fast_pass",
            OriginalCode = passingCode,
            CurrentCode = passingCode,
            TestCode = "test"
        };

        var finalState = engine.Run(state);
        Assert.Equal(Phase.Deliver, finalState.CurrentPhase);
        Assert.True(finalState.IsTerminal);
        Assert.Equal(0, finalState.Iteration);

        var nodesVisited = engine.TraceLog.Select(t => t.Node).ToList();
        Assert.Equal(new[] { "triage", "deliver" }, nodesVisited);
    }

    [Fact]
    public void RefactorGraphEngine_Escalates_WhenBudgetExhausted()
    {
        var failingCode = "public class Broken {}";
        var fakeSandbox = new FakeSandbox(_ => (false, 1, string.Empty, "Error"));
        var gate = new VerifyGate(fakeSandbox);
        var maker = new MockMakerAgent(new List<string> { failingCode, failingCode, failingCode });
        var controller = new LoopController(maker, verifyGate: gate);
        var engine = new RefactorGraphEngine(controller);

        var state = new AgentState
        {
            TaskId = "exhaust",
            OriginalCode = failingCode,
            CurrentCode = failingCode,
            TestCode = "test",
            MaxIterations = 2
        };

        var finalState = engine.Run(state);
        Assert.Equal(Phase.Escalate, finalState.CurrentPhase);
        Assert.True(finalState.IsTerminal);
        Assert.Equal(2, finalState.Iteration);
        Assert.Contains("Escalation", finalState.DeliveryReport);
    }
}

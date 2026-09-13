using AuditGuard.Agents;
using AuditGuard.Core;
using AuditGuard.Loop;
using Xunit;

namespace AuditGuard.Tests;

public class AuditLoopControllerTests
{
    [Fact]
    public void StepExtract_SetsCurrentPhaseAndExtractsClaim()
    {
        var rawReceipt = """
        --- Test Bistro ---
        Date: 2026-09-10
        - 1x Salad: $15.00
        Subtotal: $15.00
        Tax: $1.50
        Total: $16.50
        """;

        var controller = new AuditLoopController(new HeuristicExtractorAgent());
        var state = new AuditState { RawText = rawReceipt };

        var nextState = controller.StepExtract(state);

        Assert.Equal(AuditPhase.Extract, nextState.CurrentPhase);
        Assert.NotNull(nextState.ExtractedClaim);
        Assert.Equal("Test Bistro", nextState.ExtractedClaim.MerchantName);
        Assert.Equal(15.00m, nextState.ExtractedClaim.Subtotal);
    }

    [Fact]
    public void StepReconcile_ExhaustsBudget_MarksRejected()
    {
        var controller = new AuditLoopController(new HeuristicExtractorAgent());
        var state = new AuditState
        {
            Iteration = 3,
            MaxIterations = 3,
            LatestMathResult = new MathVerificationResult { Passed = false, ErrorSummary = "Unresolvable math" },
            LatestDiagnostic = "Unresolvable math"
        };

        var nextState = controller.StepReconcile(state);

        Assert.True(nextState.IsTerminal);
        Assert.Equal(AuditStatus.Rejected, nextState.FinalStatus);
        Assert.Equal(AuditPhase.Escalate, nextState.CurrentPhase);
    }
}

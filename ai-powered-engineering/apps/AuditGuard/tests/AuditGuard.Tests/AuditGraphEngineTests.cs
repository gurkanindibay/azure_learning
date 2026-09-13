using AuditGuard.Agents;
using AuditGuard.Core;
using AuditGuard.Graph;
using AuditGuard.Loop;
using Xunit;

namespace AuditGuard.Tests;

public class AuditGraphEngineTests
{
    [Fact]
    public void Run_CleanReceipt_ReachesTerminalAutoApprovedWithTrace()
    {
        var rawReceipt = """
        --- Downtown Cafe ---
        Date: 2026-09-10
        - 1x Sandwich: $12.00
        - 1x Coffee: $4.00
        Subtotal: $16.00
        Tax: $1.60
        Tip: $2.00
        Total: $19.60
        """;

        var controller = new AuditLoopController(new HeuristicExtractorAgent());
        var engine = new AuditGraphEngine(controller);
        var state = new AuditState { RawText = rawReceipt, MaxIterations = 3 };

        var finalState = engine.Run(state);

        Assert.True(finalState.IsTerminal);
        Assert.Equal(AuditStatus.AutoApproved, finalState.FinalStatus);
        Assert.NotEmpty(engine.TraceLog);
        Assert.Contains(engine.TraceLog, t => t.Node == "auto_approve");
    }

    [Fact]
    public void Run_PolicyViolation_ReachesTerminalEscalateWithTrace()
    {
        var rawReceipt = """
        --- Bar & Grill ---
        Date: 2026-09-10
        - 1x Craft IPA: $8.00
        Subtotal: $8.00
        Tax: $0.80
        Total: $8.80
        """;

        var controller = new AuditLoopController(new HeuristicExtractorAgent());
        var engine = new AuditGraphEngine(controller);
        var state = new AuditState { RawText = rawReceipt, MaxIterations = 3 };

        var finalState = engine.Run(state);

        Assert.True(finalState.IsTerminal);
        Assert.Equal(AuditStatus.RequiresHumanReview, finalState.FinalStatus);
        Assert.Contains(engine.TraceLog, t => t.Node == "escalate");
    }
}

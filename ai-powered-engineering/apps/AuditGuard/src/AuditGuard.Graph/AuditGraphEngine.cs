using System.Diagnostics;
using AuditGuard.Core;
using AuditGuard.Loop;

namespace AuditGuard.Graph;

public class AuditGraphEngine
{
    private readonly AuditLoopController _controller;
    public List<AuditStepTrace> TraceLog { get; } = new();

    public AuditGraphEngine(AuditLoopController controller)
    {
        _controller = controller;
    }

    private void LogStep(string nodeName, AuditState state, double durationMs)
    {
        var diag = state.LatestDiagnostic ?? string.Empty;
        TraceLog.Add(new AuditStepTrace
        {
            StepIndex = TraceLog.Count + 1,
            Node = nodeName,
            Phase = state.CurrentPhase.ToString(),
            Iteration = state.Iteration,
            IsTerminal = state.IsTerminal,
            DurationMs = Math.Round(durationMs, 2),
            Diagnostic = diag.Length > 150 ? diag.Substring(0, 150) : diag
        });
    }

    public AuditState Run(AuditState state)
    {
        TraceLog.Clear();
        var sw = Stopwatch.StartNew();

        while (!state.IsTerminal)
        {
            // Node 1: Extract
            sw.Restart();
            state = _controller.StepExtract(state);
            LogStep("extract", state, sw.Elapsed.TotalMilliseconds);

            // Node 2: VerifyMath Gate
            sw.Restart();
            state = _controller.StepVerifyMath(state);
            LogStep("verify_math", state, sw.Elapsed.TotalMilliseconds);

            // If math passed, run Policy Gate
            if (state.LatestMathResult != null && state.LatestMathResult.Passed)
            {
                sw.Restart();
                state = _controller.StepAuditPolicy(state);
                LogStep("audit_policy", state, sw.Elapsed.TotalMilliseconds);
            }

            // Node 3: Reconcile / Route
            sw.Restart();
            state = _controller.StepReconcile(state);
            LogStep("reconcile", state, sw.Elapsed.TotalMilliseconds);

            if (state.IsTerminal)
            {
                var terminalNode = state.FinalStatus == AuditStatus.AutoApproved ? "auto_approve" : "escalate";
                LogStep(terminalNode, state, 0.01);
                break;
            }
        }

        return state;
    }
}

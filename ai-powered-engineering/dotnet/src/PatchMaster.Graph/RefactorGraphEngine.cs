using System.Diagnostics;
using PatchMaster.Core;
using PatchMaster.Loop;

namespace PatchMaster.Graph;

public class RefactorGraphEngine
{
    private readonly LoopController _controller;
    public List<GraphStepTrace> TraceLog { get; } = new();

    public RefactorGraphEngine(LoopController controller)
    {
        _controller = controller;
    }

    private void LogStep(string nodeName, AgentState state, double durationMs)
    {
        var diag = state.LatestDiagnostic ?? string.Empty;
        TraceLog.Add(new GraphStepTrace
        {
            StepIndex = TraceLog.Count + 1,
            Node = nodeName,
            Phase = state.CurrentPhase.ToString(),
            Iteration = state.Iteration,
            IsTerminal = state.IsTerminal,
            DurationMs = Math.Round(durationMs, 2),
            LatestDiagnostic = diag.Length > 150 ? diag.Substring(0, 150) : diag
        });
    }

    public AgentState Run(AgentState state)
    {
        TraceLog.Clear();
        var sw = Stopwatch.StartNew();

        // 1. Triage Node (Discover initial state)
        sw.Restart();
        state = _controller.StepDiscover(state);
        LogStep("triage", state, sw.Elapsed.TotalMilliseconds);

        if (state.LatestVerification != null && state.LatestVerification.Passed)
        {
            sw.Restart();
            state.CurrentPhase = Phase.Deliver;
            state.IsTerminal = true;
            state.DeliveryReport = "Initial code already satisfies all tests.";
            LogStep("deliver", state, sw.Elapsed.TotalMilliseconds);
            return state;
        }

        // 2. Iterative Graph Cycle
        while (!state.IsTerminal)
        {
            // Planner Node
            sw.Restart();
            state = _controller.StepPlan(state);
            LogStep("planner", state, sw.Elapsed.TotalMilliseconds);

            // Maker Node
            sw.Restart();
            state = _controller.StepExecute(state);
            LogStep("maker", state, sw.Elapsed.TotalMilliseconds);

            // Verify Gate Node
            sw.Restart();
            state = _controller.StepVerify(state);
            LogStep("verify_gate", state, sw.Elapsed.TotalMilliseconds);

            // Conditional Edge: Passed?
            if (state.LatestVerification != null && state.LatestVerification.Passed)
            {
                sw.Restart();
                state.CurrentPhase = Phase.Deliver;
                state.IsTerminal = true;
                state.DeliveryReport = $"Success: Solution verified after {state.Iteration + 1} iteration(s).";
                LogStep("deliver", state, sw.Elapsed.TotalMilliseconds);
                break;
            }

            // Diagnose / Iterate Node
            sw.Restart();
            state = _controller.StepIterate(state);
            LogStep("diagnose", state, sw.Elapsed.TotalMilliseconds);

            if (state.IsTerminal)
            {
                sw.Restart();
                state.CurrentPhase = Phase.Escalate;
                LogStep("escalate", state, sw.Elapsed.TotalMilliseconds);
                break;
            }
        }

        return state;
    }
}

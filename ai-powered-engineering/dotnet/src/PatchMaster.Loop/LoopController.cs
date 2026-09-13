using PatchMaster.Core;
using PatchMaster.Agents;

namespace PatchMaster.Loop;

public class LoopController
{
    private readonly IMakerAgent _maker;
    private readonly ICheckerAgent _checker;
    private readonly IVerifyGate _verifyGate;

    public LoopController(
        IMakerAgent maker,
        ICheckerAgent? checker = null,
        IVerifyGate? verifyGate = null)
    {
        _maker = maker;
        _checker = checker ?? new RuleBasedCheckerAgent();
        _verifyGate = verifyGate ?? new VerifyGate();
    }

    public AgentState StepDiscover(AgentState state)
    {
        state.CurrentPhase = Phase.Discover;
        var initial = _verifyGate.Verify(state.OriginalCode, state.CurrentCode, state.TestCode);
        state.LatestVerification = initial;
        state.LatestDiagnostic = string.IsNullOrEmpty(initial.ErrorSummary) ? initial.Stderr : initial.ErrorSummary;
        return state;
    }

    public AgentState StepPlan(AgentState state)
    {
        state.CurrentPhase = Phase.Plan;
        state.LatestPlan = _maker.GeneratePlan(state);
        return state;
    }

    public AgentState StepExecute(AgentState state)
    {
        state.CurrentPhase = Phase.Execute;
        state.CurrentCode = _maker.GeneratePatch(state);
        return state;
    }

    public AgentState StepVerify(AgentState state)
    {
        state.CurrentPhase = Phase.Verify;
        var verif = _verifyGate.Verify(state.OriginalCode, state.CurrentCode, state.TestCode);

        if (verif.Passed)
        {
            var (approved, reason) = _checker.Audit(state.CurrentCode, state.OriginalCode);
            if (!approved)
            {
                verif.Passed = false;
                verif.ErrorSummary = reason;
            }
        }

        state.LatestVerification = verif;
        state.LatestDiagnostic = string.IsNullOrEmpty(verif.ErrorSummary) ? verif.Stderr : verif.ErrorSummary;

        var record = new IterationRecord
        {
            Iteration = state.Iteration,
            Plan = state.LatestPlan,
            ProposedCode = state.CurrentCode,
            Verification = verif,
            DiagnosticFeedback = state.LatestDiagnostic
        };
        state.History.Add(record);

        return state;
    }

    public AgentState StepIterate(AgentState state)
    {
        state.CurrentPhase = Phase.Iterate;
        state.Iteration++;

        if (state.LatestVerification != null && state.LatestVerification.Passed)
        {
            state.CurrentPhase = Phase.Deliver;
            state.IsTerminal = true;
            state.DeliveryReport = $"Success: Solution verified after {state.Iteration} iteration(s).";
        }
        else if (state.Iteration >= state.MaxIterations)
        {
            state.CurrentPhase = Phase.Escalate;
            state.IsTerminal = true;
            state.DeliveryReport = $"Escalation: Max retry budget ({state.MaxIterations}) exhausted.\nLast Error: {state.LatestDiagnostic}";
        }
        else
        {
            state.CurrentPhase = Phase.Plan;
        }

        return state;
    }
}

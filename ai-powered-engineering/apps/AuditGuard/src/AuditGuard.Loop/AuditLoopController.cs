using AuditGuard.Core;
using AuditGuard.Harness;
using AuditGuard.Agents;

namespace AuditGuard.Loop;

public class AuditLoopController
{
    private readonly IExtractorAgent _extractor;
    private readonly IMathVerifyGate _mathGate;
    private readonly IPolicyAuditGate _policyGate;
    private readonly CompanyPolicy _policy;

    public AuditLoopController(
        IExtractorAgent extractor,
        IMathVerifyGate? mathGate = null,
        IPolicyAuditGate? policyGate = null,
        CompanyPolicy? policy = null)
    {
        _extractor = extractor;
        _mathGate = mathGate ?? new MathVerifyGate();
        _policyGate = policyGate ?? new PolicyAuditGate();
        _policy = policy ?? PolicyCatalog.DefaultCorporatePolicy;
    }

    public AuditState StepExtract(AuditState state)
    {
        state.CurrentPhase = AuditPhase.Extract;
        state.ExtractedClaim = _extractor.Extract(state.RawText, state.LatestDiagnostic);
        return state;
    }

    public AuditState StepVerifyMath(AuditState state)
    {
        state.CurrentPhase = AuditPhase.VerifyMath;
        if (state.ExtractedClaim == null)
        {
            state.LatestDiagnostic = "Extraction failed: no claim object returned.";
            return state;
        }

        var mathRes = _mathGate.VerifyMath(state.ExtractedClaim);
        state.LatestMathResult = mathRes;
        state.LatestDiagnostic = mathRes.Passed ? string.Empty : mathRes.ErrorSummary;
        return state;
    }

    public AuditState StepAuditPolicy(AuditState state)
    {
        state.CurrentPhase = AuditPhase.AuditPolicy;
        if (state.ExtractedClaim == null) return state;

        var policyRes = _policyGate.AuditPolicy(state.ExtractedClaim, _policy);
        state.LatestPolicyResult = policyRes;
        return state;
    }

    public AuditState StepReconcile(AuditState state)
    {
        state.CurrentPhase = AuditPhase.Reconcile;
        state.Iteration++;

        // If math passed, check policy outcome
        if (state.LatestMathResult != null && state.LatestMathResult.Passed)
        {
            if (state.LatestPolicyResult != null && state.LatestPolicyResult.Passed)
            {
                // Both math and policy clean!
                state.CurrentPhase = AuditPhase.Approve;
                state.FinalStatus = AuditStatus.AutoApproved;
                state.IsTerminal = true;
                state.AuditReport = $"Auto-Approved: All math verified (Subtotal: ${state.ExtractedClaim?.Subtotal:F2}, Total: ${state.ExtractedClaim?.GrandTotal:F2}) and compliant with company policy.";
            }
            else
            {
                // Math is clean, but corporate policy violations detected
                state.CurrentPhase = AuditPhase.Escalate;
                state.FinalStatus = AuditStatus.RequiresHumanReview;
                state.IsTerminal = true;
                var violationsText = string.Join("; ", state.LatestPolicyResult?.Violations.Select(v => $"[{v.RuleName}] {v.Explanation}") ?? Array.Empty<string>());
                state.AuditReport = $"Flagged for Managerial Review: {violationsText}";
            }
        }
        else if (state.Iteration >= state.MaxIterations)
        {
            // Math reconciliation failed after max retry budget
            state.CurrentPhase = AuditPhase.Escalate;
            state.FinalStatus = AuditStatus.Rejected;
            state.IsTerminal = true;
            state.AuditReport = $"Rejected / Escalated: Mathematical mismatch could not be reconciled after {state.MaxIterations} iterations. Last error: {state.LatestDiagnostic}";
        }
        else
        {
            // Loop back for reconciliation
            state.CurrentPhase = AuditPhase.Extract;
        }

        return state;
    }
}

using AuditGuard.Core;

namespace AuditGuard.Loop;

public class MathVerifyGate : IMathVerifyGate
{
    public MathVerificationResult VerifyMath(ExpenseClaim claim)
    {
        var computedSubtotal = claim.LineItems.Sum(i => i.TotalPrice);
        var subtotalDelta = Math.Abs(computedSubtotal - claim.Subtotal);
        var subtotalMatches = subtotalDelta < 0.01m;

        var computedGrandTotal = claim.Subtotal + claim.Tax + claim.Tip;
        var grandTotalDelta = Math.Abs(computedGrandTotal - claim.GrandTotal);
        var grandTotalMatches = grandTotalDelta < 0.01m;

        var errors = new List<string>();
        if (!subtotalMatches)
        {
            errors.Add($"Subtotal mismatch: Sum of items is ${computedSubtotal:F2} but receipt stated ${claim.Subtotal:F2} (Diff: ${subtotalDelta:F2})");
        }
        if (!grandTotalMatches)
        {
            errors.Add($"Grand total mismatch: Subtotal (${claim.Subtotal:F2}) + Tax (${claim.Tax:F2}) + Tip (${claim.Tip:F2}) = ${computedGrandTotal:F2}, but receipt stated ${claim.GrandTotal:F2} (Diff: ${grandTotalDelta:F2})");
        }

        return new MathVerificationResult
        {
            Passed = subtotalMatches && grandTotalMatches,
            CalculatedSubtotal = computedSubtotal,
            ExtractedSubtotal = claim.Subtotal,
            CalculatedGrandTotal = computedGrandTotal,
            ExtractedGrandTotal = claim.GrandTotal,
            SubtotalDelta = subtotalDelta,
            GrandTotalDelta = grandTotalDelta,
            ErrorSummary = string.Join("; ", errors)
        };
    }
}

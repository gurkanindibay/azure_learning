using System.Text.Json;
using AuditGuard.Core;

namespace AuditGuard.Harness;

public class ContextCompactor
{
    public static string FormatReconciliationPrompt(string rawReceiptText, MathVerificationResult mathError, int iteration)
    {
        return $@"### SYSTEM RECONCILIATION FEEDBACK (Attempt #{iteration + 1}):
Your previous extraction had mathematical discrepancies that failed our deterministic audit gate:
{mathError.ErrorSummary}

Line item sum: ${mathError.CalculatedSubtotal:F2}
Extracted Subtotal: ${mathError.ExtractedSubtotal:F2} (Delta: ${mathError.SubtotalDelta:F2})
Calculated Grand Total: ${mathError.CalculatedGrandTotal:F2}
Extracted Grand Total: ${mathError.ExtractedGrandTotal:F2} (Delta: ${mathError.GrandTotalDelta:F2})

### INSTRUCTION:
Re-read the original receipt text carefully. Ensure that every line item unit price and quantity is correctly captured so that:
1. sum(LineItems.TotalPrice) EXACTLY matches Subtotal.
2. Subtotal + Tax + Tip EXACTLY matches GrandTotal.

### ORIGINAL RECEIPT TEXT:
{rawReceiptText}";
    }
}

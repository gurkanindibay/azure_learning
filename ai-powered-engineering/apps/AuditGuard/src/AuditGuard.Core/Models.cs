namespace AuditGuard.Core;

public enum AuditStatus
{
    AutoApproved,
    RequiresHumanReview,
    Rejected
}

public enum AuditPhase
{
    Ingest,
    Extract,
    VerifyMath,
    AuditPolicy,
    Reconcile,
    Approve,
    Escalate
}

public class ReceiptLineItem
{
    public string Description { get; set; } = string.Empty;
    public int Quantity { get; set; } = 1;
    public decimal UnitPrice { get; set; }
    public decimal TotalPrice { get; set; }
    public string Category { get; set; } = "General";
}

public class ExpenseClaim
{
    public string ClaimId { get; set; } = Guid.NewGuid().ToString("N");
    public string EmployeeName { get; set; } = string.Empty;
    public string MerchantName { get; set; } = string.Empty;
    public DateTime TransactionDate { get; set; } = DateTime.UtcNow;
    public List<ReceiptLineItem> LineItems { get; set; } = new();
    public decimal Subtotal { get; set; }
    public decimal Tax { get; set; }
    public decimal Tip { get; set; }
    public decimal GrandTotal { get; set; }
    public string Currency { get; set; } = "USD";
    public string RawReceiptText { get; set; } = string.Empty;
}

public class MathVerificationResult
{
    public bool Passed { get; set; }
    public decimal CalculatedSubtotal { get; set; }
    public decimal ExtractedSubtotal { get; set; }
    public decimal CalculatedGrandTotal { get; set; }
    public decimal ExtractedGrandTotal { get; set; }
    public decimal SubtotalDelta { get; set; }
    public decimal GrandTotalDelta { get; set; }
    public string ErrorSummary { get; set; } = string.Empty;
}

public enum PolicySeverity
{
    Warning,
    Critical
}

public class PolicyViolation
{
    public string RuleName { get; set; } = string.Empty;
    public PolicySeverity Severity { get; set; } = PolicySeverity.Critical;
    public string Explanation { get; set; } = string.Empty;
}

public class PolicyAuditResult
{
    public bool Passed { get; set; }
    public List<PolicyViolation> Violations { get; set; } = new();
    public bool RequiresEscalation => Violations.Count > 0;
}

public class AuditState
{
    public string TaskId { get; set; } = string.Empty;
    public string RawText { get; set; } = string.Empty;
    public ExpenseClaim? ExtractedClaim { get; set; }

    public AuditPhase CurrentPhase { get; set; } = AuditPhase.Ingest;
    public int Iteration { get; set; } = 0;
    public int MaxIterations { get; set; } = 3;

    public MathVerificationResult? LatestMathResult { get; set; }
    public PolicyAuditResult? LatestPolicyResult { get; set; }
    public string LatestDiagnostic { get; set; } = string.Empty;

    public bool IsTerminal { get; set; } = false;
    public AuditStatus? FinalStatus { get; set; }
    public string? AuditReport { get; set; }
}

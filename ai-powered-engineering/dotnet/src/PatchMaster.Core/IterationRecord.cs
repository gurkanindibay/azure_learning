namespace PatchMaster.Core;

public class IterationRecord
{
    public int Iteration { get; set; }
    public string Plan { get; set; } = string.Empty;
    public string ProposedCode { get; set; } = string.Empty;
    public VerificationResult Verification { get; set; } = new();
    public string? DiagnosticFeedback { get; set; }
}

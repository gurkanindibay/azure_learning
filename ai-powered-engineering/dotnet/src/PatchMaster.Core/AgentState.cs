namespace PatchMaster.Core;

public class AgentState
{
    public string TaskId { get; set; } = string.Empty;
    public string OriginalCode { get; set; } = string.Empty;
    public string CurrentCode { get; set; } = string.Empty;
    public string TestCode { get; set; } = string.Empty;

    public Phase CurrentPhase { get; set; } = Phase.Discover;
    public int Iteration { get; set; } = 0;
    public int MaxIterations { get; set; } = 3;

    public List<IterationRecord> History { get; set; } = new();
    public VerificationResult? LatestVerification { get; set; }
    public string LatestPlan { get; set; } = string.Empty;
    public string LatestDiagnostic { get; set; } = string.Empty;

    public bool IsTerminal { get; set; } = false;
    public string? DeliveryReport { get; set; }
}

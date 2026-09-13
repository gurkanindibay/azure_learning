namespace AuditGuard.Graph;

public class AuditStepTrace
{
    public int StepIndex { get; set; }
    public string Node { get; set; } = string.Empty;
    public string Phase { get; set; } = string.Empty;
    public int Iteration { get; set; }
    public bool IsTerminal { get; set; }
    public double DurationMs { get; set; }
    public string Diagnostic { get; set; } = string.Empty;
}

namespace PatchMaster.Graph;

public class GraphStepTrace
{
    public int StepIndex { get; set; }
    public string Node { get; set; } = string.Empty;
    public string Phase { get; set; } = string.Empty;
    public int Iteration { get; set; }
    public bool IsTerminal { get; set; }
    public double DurationMs { get; set; }
    public string LatestDiagnostic { get; set; } = string.Empty;
}

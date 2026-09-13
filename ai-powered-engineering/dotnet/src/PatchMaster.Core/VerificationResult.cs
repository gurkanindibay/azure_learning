namespace PatchMaster.Core;

public class VerificationResult
{
    public bool Passed { get; set; }
    public bool AstValid { get; set; }
    public bool DiffValid { get; set; }
    public bool TestsPassed { get; set; }
    public int TotalTests { get; set; }
    public int FailedTests { get; set; }
    public string Stdout { get; set; } = string.Empty;
    public string Stderr { get; set; } = string.Empty;
    public string ErrorSummary { get; set; } = string.Empty;
}

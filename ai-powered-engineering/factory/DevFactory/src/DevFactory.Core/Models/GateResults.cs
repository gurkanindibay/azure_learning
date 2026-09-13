namespace DevFactory.Core.Models;

public class ProjectSourceFile
{
    public string ProjectName { get; set; } = string.Empty;
    public string RelativePath { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
}

public class SyntaxGateResult
{
    public bool IsValid { get; set; }
    public List<string> SyntaxErrors { get; set; } = new();
}

public class BuildGateResult
{
    public bool Passed { get; set; }
    public List<string> Errors { get; set; } = new();
    public string RawOutput { get; set; } = string.Empty;
}

public class TestGateResult
{
    public bool Passed { get; set; }
    public int TotalTests { get; set; }
    public int PassedCount { get; set; }
    public int FailedCount { get; set; }
    public List<string> FailedTestSummaries { get; set; } = new();
    public string RawOutput { get; set; } = string.Empty;
}

public class AssemblyTraceItem
{
    public int StepIndex { get; set; }
    public string Stage { get; set; } = string.Empty;
    public string Status { get; set; } = "Running";
    public double DurationMs { get; set; }
    public string Detail { get; set; } = string.Empty;
}

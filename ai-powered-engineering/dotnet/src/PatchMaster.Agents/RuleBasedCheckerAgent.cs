using PatchMaster.Core;

namespace PatchMaster.Agents;

public class RuleBasedCheckerAgent : ICheckerAgent
{
    private static readonly string[] DangerousPatterns = new[]
    {
        "Process.Start(",
        "File.Delete(",
        "Directory.Delete(",
        "Environment.Exit("
    };

    public (bool Approved, string Reason) Audit(string candidateCode, string originalCode)
    {
        foreach (var pattern in DangerousPatterns)
        {
            if (candidateCode.Contains(pattern) && !originalCode.Contains(pattern))
            {
                return (false, $"Security Violation: Candidate code introduces prohibited pattern '{pattern}'.");
            }
        }

        if (string.IsNullOrWhiteSpace(candidateCode))
        {
            return (false, "Quality Rejection: Code is completely empty.");
        }

        return (true, "Checker Audit Passed: No security regressions or suspicious calls detected.");
    }
}

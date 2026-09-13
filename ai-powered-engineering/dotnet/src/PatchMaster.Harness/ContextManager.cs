using System.Text.RegularExpressions;
using PatchMaster.Core;

namespace PatchMaster.Harness;

public class ContextManager
{
    public static string ExtractFailureSignal(string stdout, string stderr)
    {
        var combined = (stdout ?? "") + "\n" + (stderr ?? "");
        var lines = combined.Split('\n');
        var extracted = new List<string>();
        var capture = false;

        foreach (var rawLine in lines)
        {
            var line = rawLine.TrimEnd('\r');
            if (line.Contains("Failed") || line.Contains("Error") || line.Contains("Exception") || line.Contains("Assert."))
            {
                capture = true;
            }

            if (capture)
            {
                // Strip ANSI escape sequences if any
                var clean = Regex.Replace(line, @"\x1b\[[0-9;]*m", "");
                extracted.Add(clean);
            }
        }

        if (extracted.Count == 0)
        {
            extracted = lines.TakeLast(15).Select(l => l.TrimEnd('\r')).ToList();
        }

        return string.Join("\n", extracted.Take(25));
    }

    public static string FormatIterationPrompt(
        string originalCode,
        string currentCode,
        string testCode,
        List<IterationRecord> history,
        string diagnosticHint)
    {
        var historySummary = new List<string>();
        foreach (var rec in history)
        {
            var err = string.IsNullOrEmpty(rec.Verification.ErrorSummary)
                ? "Failed tests"
                : rec.Verification.ErrorSummary;
            historySummary.Add($"- Attempt #{rec.Iteration}: {err}");
        }

        var historyText = historySummary.Count > 0 ? string.Join("\n", historySummary) : "No prior attempts.";

        return $@"### TASK: Fix the following C# code to make all xUnit tests pass.

### CURRENT SOURCE CODE:
```csharp
{currentCode}
```

### TEST SUITE:
```csharp
{testCode}
```

### PRIOR ATTEMPTS & FAILURES:
{historyText}

### LATEST VERIFICATION FEEDBACK:
{diagnosticHint}

### INSTRUCTIONS:
- Return ONLY the updated, self-contained C# code.
- Do NOT alter test expectations; fix the logic in the source code.
- Ensure zero compiler errors and complete edge-case handling.";
    }
}

using System.Text.RegularExpressions;

namespace DevFactory.Harness;

public static class DiagnosticExtractor
{
    public static List<string> ExtractBuildErrors(string buildOutput)
    {
        var errors = new List<string>();
        var lines = buildOutput.Split(new[] { "\r\n", "\r", "\n" }, StringSplitOptions.RemoveEmptyEntries);

        foreach (var line in lines)
        {
            if (line.Contains(": error CS", StringComparison.OrdinalIgnoreCase))
            {
                var match = Regex.Match(line, @"(?:[a-zA-Z0-9_\-\.\/\\]+\(\d+,\d+\))?:\s*(error CS\d+:[^\r\n\[]+)");
                if (match.Success)
                {
                    errors.Add(match.Groups[1].Value.Trim());
                }
                else
                {
                    errors.Add(line.Trim());
                }
            }
        }

        return errors.Distinct().ToList();
    }

    public static List<string> ExtractTestFailures(string testOutput)
    {
        var failures = new List<string>();
        var lines = testOutput.Split(new[] { "\r\n", "\r", "\n" }, StringSplitOptions.RemoveEmptyEntries);

        for (int i = 0; i < lines.Length; i++)
        {
            if (lines[i].Contains("[FAIL]", StringComparison.OrdinalIgnoreCase) || lines[i].Contains("Failed ", StringComparison.OrdinalIgnoreCase))
            {
                var summary = lines[i].Trim();
                if (i + 1 < lines.Length && lines[i + 1].Contains("Error Message:", StringComparison.OrdinalIgnoreCase))
                {
                    summary += " => " + lines[i + 1].Trim();
                }
                failures.Add(summary);
            }
        }

        return failures.Distinct().ToList();
    }
}

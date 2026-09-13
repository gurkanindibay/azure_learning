using System.Text.RegularExpressions;
using DevFactory.Core.Interfaces;
using DevFactory.Core.Models;
using DevFactory.Harness;

namespace DevFactory.Loop;

public class TestVerifyGate : ITestGate
{
    public async Task<TestGateResult> RunTestsAsync(string workingDirectory, CancellationToken ct = default)
    {
        var runResult = await DotnetProcessRunner.RunAsync("test --no-build --nologo", workingDirectory, timeoutSeconds: 60, ct);

        var combinedOutput = runResult.StandardOutput + "\n" + runResult.StandardError;
        var failures = DiagnosticExtractor.ExtractTestFailures(combinedOutput);

        int total = 0;
        int passed = 0;
        int failed = 0;

        // Example match: Passed! - Failed: 0, Passed: 13, Skipped: 0, Total: 13
        var summaryMatch = Regex.Match(combinedOutput, @"Passed!\s*-\s*Failed:\s*(\d+),\s*Passed:\s*(\d+),\s*Skipped:\s*(\d+),\s*Total:\s*(\d+)", RegexOptions.IgnoreCase);
        if (summaryMatch.Success)
        {
            failed = int.Parse(summaryMatch.Groups[1].Value);
            passed = int.Parse(summaryMatch.Groups[2].Value);
            total = int.Parse(summaryMatch.Groups[4].Value);
        }
        else
        {
            var failMatch = Regex.Match(combinedOutput, @"Failed!\s*-\s*Failed:\s*(\d+),\s*Passed:\s*(\d+),\s*Skipped:\s*(\d+),\s*Total:\s*(\d+)", RegexOptions.IgnoreCase);
            if (failMatch.Success)
            {
                failed = int.Parse(failMatch.Groups[1].Value);
                passed = int.Parse(failMatch.Groups[2].Value);
                total = int.Parse(failMatch.Groups[4].Value);
            }
            else
            {
                failed = failures.Count;
                total = failed;
            }
        }

        return new TestGateResult
        {
            Passed = runResult.ExitCode == 0 && failed == 0,
            TotalTests = total,
            PassedCount = passed,
            FailedCount = failed,
            FailedTestSummaries = failures,
            RawOutput = combinedOutput
        };
    }
}

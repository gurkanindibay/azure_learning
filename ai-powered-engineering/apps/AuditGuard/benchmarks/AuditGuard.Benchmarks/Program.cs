using System.Diagnostics;
using System.Text;
using AuditGuard.Agents;
using AuditGuard.Core;
using AuditGuard.Graph;
using AuditGuard.Harness;
using AuditGuard.Loop;

namespace AuditGuard.Benchmarks;

public record BenchmarkCase(
    string FixtureName,
    string Description,
    AuditStatus ExpectedStatus,
    bool ExpectedMathPass,
    bool ExpectedPolicyPass,
    int ExpectedMaxIterations
);

public class Program
{
    public static int Main(string[] args)
    {
        Console.OutputEncoding = Encoding.UTF8;
        Console.ForegroundColor = ConsoleColor.Cyan;
        Console.WriteLine("""
        ========================================================================
             AUDITGUARD BENCHMARK & EVALUATION HARNESS
             Autonomous Expense & Invoice Audit Microservice
        ========================================================================
        """);
        Console.ResetColor();

        var fixturesDir = FindFixturesDirectory();
        if (fixturesDir == null)
        {
            Console.ForegroundColor = ConsoleColor.Red;
            Console.WriteLine("[Error] Could not locate Fixtures/ directory.");
            Console.ResetColor();
            return 1;
        }

        Console.WriteLine($"Discovered Fixtures Directory: {fixturesDir}\n");

        var testCases = new List<BenchmarkCase>
        {
            new("claim_01_clean_lunch.txt", "Clean compliant business lunch", AuditStatus.AutoApproved, true, true, 1),
            new("claim_02_tax_math_error.txt", "Math mismatch requiring self-healing reconcile", AuditStatus.AutoApproved, true, true, 2),
            new("claim_03_alcohol_violation.txt", "Alcohol policy violation (Draft IPA)", AuditStatus.RequiresHumanReview, true, false, 1),
            new("claim_04_missing_subtotal.txt", "Missing subtotal reconciled from items", AuditStatus.AutoApproved, true, true, 2),
            new("claim_05_high_value_escalation.txt", "Exceeds $500 corporate ceiling ($680.40)", AuditStatus.RequiresHumanReview, true, false, 1),
            new("claim_06_weekend_travel.txt", "Weekend Sunday taxi transaction", AuditStatus.RequiresHumanReview, true, false, 1)
        };

        int totalCases = testCases.Count;
        int passedEvaluations = 0;
        int passAt1Count = 0;
        int autoApprovedCount = 0;
        int escalatedCount = 0;
        var latencies = new List<double>();

        Console.WriteLine($"{"Case",-32} {"Status",-18} {"Math",-6} {"Policy",-8} {"Iter",-6} {"Latency",-10} {"Result"}");
        Console.WriteLine(new string('-', 92));

        foreach (var tc in testCases)
        {
            var filePath = Path.Combine(fixturesDir, tc.FixtureName);
            if (!File.Exists(filePath))
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine($"Missing fixture file: {tc.FixtureName}");
                Console.ResetColor();
                continue;
            }

            var receiptText = File.ReadAllText(filePath);
            var extractor = new HeuristicExtractorAgent();
            var mathGate = new MathVerifyGate();
            var policyGate = new PolicyAuditGate();
            var policy = PolicyCatalog.DefaultCorporatePolicy;
            var controller = new AuditLoopController(extractor, mathGate, policyGate, policy);
            var engine = new AuditGraphEngine(controller);

            var state = new AuditState
            {
                RawText = receiptText,
                MaxIterations = 3
            };

            var sw = Stopwatch.StartNew();
            var finalState = engine.Run(state);
            sw.Stop();
            var elapsedMs = Math.Round(sw.Elapsed.TotalMilliseconds, 2);
            latencies.Add(elapsedMs);

            bool mathMatched = (finalState.LatestMathResult?.Passed == tc.ExpectedMathPass);
            bool policyMatched = (finalState.LatestPolicyResult?.Passed == tc.ExpectedPolicyPass);
            bool statusMatched = (finalState.FinalStatus == tc.ExpectedStatus);
            bool iterWithinBudget = (finalState.Iteration <= tc.ExpectedMaxIterations);

            bool evalPassed = mathMatched && policyMatched && statusMatched && iterWithinBudget;
            if (evalPassed) passedEvaluations++;
            if (finalState.Iteration == 1 && statusMatched) passAt1Count++;
            if (finalState.FinalStatus == AuditStatus.AutoApproved) autoApprovedCount++;
            if (finalState.FinalStatus == AuditStatus.RequiresHumanReview) escalatedCount++;

            var statusStr = finalState.FinalStatus?.ToString() ?? "Unknown";
            var mathStr = (finalState.LatestMathResult?.Passed ?? false) ? "PASS" : "FAIL";
            var polStr = (finalState.LatestPolicyResult?.Passed ?? false) ? "PASS" : "FAIL";

            var resultLabel = evalPassed ? "[PASS]" : "[FAIL]";
            if (evalPassed)
            {
                Console.ForegroundColor = ConsoleColor.Green;
            }
            else
            {
                Console.ForegroundColor = ConsoleColor.Red;
            }

            Console.WriteLine($"{tc.FixtureName,-32} {statusStr,-18} {mathStr,-6} {polStr,-8} {finalState.Iteration,-6} {elapsedMs + "ms",-10} {resultLabel}");
            Console.ResetColor();
        }

        Console.WriteLine(new string('=', 92));
        Console.ForegroundColor = ConsoleColor.Cyan;
        Console.WriteLine("BENCHMARK EVALUATION SUMMARY:");
        Console.ResetColor();
        Console.WriteLine($"  Total Benchmarks:      {totalCases}");
        Console.WriteLine($"  Evaluations Passed:    {passedEvaluations} / {totalCases} ({(double)passedEvaluations / totalCases:P0})");
        Console.WriteLine($"  Pass@1 Accuracy:       {passAt1Count} / {totalCases} ({(double)passAt1Count / totalCases:P0})");
        Console.WriteLine($"  Pass@3 (Reconciled):   {passedEvaluations} / {totalCases} ({(double)passedEvaluations / totalCases:P0})");
        Console.WriteLine($"  Auto-Approval Rate:    {autoApprovedCount} / {totalCases} ({(double)autoApprovedCount / totalCases:P0})");
        Console.WriteLine($"  Escalation Rate:       {escalatedCount} / {totalCases} ({(double)escalatedCount / totalCases:P0})");
        Console.WriteLine($"  Average Latency:       {latencies.Average():F2} ms");
        Console.WriteLine("========================================================================\n");

        return passedEvaluations == totalCases ? 0 : 1;
    }

    private static string? FindFixturesDirectory()
    {
        var candidates = new[]
        {
            Path.Combine(AppContext.BaseDirectory, "Fixtures"),
            Path.Combine(Directory.GetCurrentDirectory(), "Fixtures"),
            Path.Combine(Directory.GetCurrentDirectory(), "benchmarks", "AuditGuard.Benchmarks", "Fixtures")
        };

        foreach (var c in candidates)
        {
            if (Directory.Exists(c)) return c;
        }

        return null;
    }
}

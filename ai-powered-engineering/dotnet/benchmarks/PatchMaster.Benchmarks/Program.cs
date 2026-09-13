using System.Diagnostics;
using PatchMaster.Core;
using PatchMaster.Harness;
using PatchMaster.Loop;
using PatchMaster.Graph;
using PatchMaster.Agents;

namespace PatchMaster.Benchmarks;

public class Program
{
    public static void Main(string[] args)
    {
        Console.WriteLine("\n🚀 Running .NET Agentic Refactor Benchmarks across test fixtures...\n");

        var baseDir = AppContext.BaseDirectory;
        // Search for Fixtures directory
        var current = new DirectoryInfo(baseDir);
        DirectoryInfo? fixturesDir = null;

        while (current != null)
        {
            var candidate = Path.Combine(current.FullName, "Fixtures");
            if (Directory.Exists(candidate))
            {
                fixturesDir = new DirectoryInfo(candidate);
                break;
            }
            // Also check project folder
            var candidate2 = Path.Combine(current.FullName, "benchmarks", "PatchMaster.Benchmarks", "Fixtures");
            if (Directory.Exists(candidate2))
            {
                fixturesDir = new DirectoryInfo(candidate2);
                break;
            }
            current = current.Parent;
        }

        if (fixturesDir == null || !fixturesDir.Exists)
        {
            Console.WriteLine("Error: Fixtures directory could not be located.");
            return;
        }

        var fixtureFolders = fixturesDir.GetDirectories().OrderBy(d => d.Name).ToList();
        var total = fixtureFolders.Count;
        var passAt1 = 0;
        var passAt3 = 0;

        var sandbox = new DotnetTestSandbox(timeoutSeconds: 15);
        var verifyGate = new VerifyGate(sandbox);
        var maker = new HeuristicMakerAgent();
        var checker = new RuleBasedCheckerAgent();
        var controller = new LoopController(maker, checker, verifyGate);
        var engine = new RefactorGraphEngine(controller);

        Console.WriteLine($"{"FIXTURE ID",-25} | {"STATUS",-10} | {"ITERS",-6} | {"TIME (s)",-8} | {"PASS@1",-6}");
        Console.WriteLine(new string('-', 65));

        foreach (var dir in fixtureFolders)
        {
            var solPath = Path.Combine(dir.FullName, "Solution.cs");
            var testPath = Path.Combine(dir.FullName, "SolutionTests.cs");

            if (!File.Exists(solPath) || !File.Exists(testPath))
            {
                continue;
            }

            var origCode = File.ReadAllText(solPath);
            var testCode = File.ReadAllText(testPath);

            var state = new AgentState
            {
                TaskId = dir.Name,
                OriginalCode = origCode,
                CurrentCode = origCode,
                TestCode = testCode,
                MaxIterations = 3
            };

            var sw = Stopwatch.StartNew();
            var finalState = engine.Run(state);
            sw.Stop();
            var duration = Math.Round(sw.Elapsed.TotalSeconds, 3);

            var isSuccess = finalState.CurrentPhase == Phase.Deliver;
            var iters = finalState.Iteration;
            var p1 = isSuccess && iters <= 1;

            if (isSuccess)
            {
                passAt3++;
                if (p1) passAt1++;
            }

            var statusStr = isSuccess ? "PASSED" : "ESCALATED";
            var p1Str = p1 ? "YES" : "NO";

            Console.WriteLine($"{dir.Name,-25} | {statusStr,-10} | {iters,-6} | {duration,-8:F3} | {p1Str,-6}");
        }

        var p1Pct = total > 0 ? Math.Round((double)passAt1 / total * 100, 1) : 0.0;
        var p3Pct = total > 0 ? Math.Round((double)passAt3 / total * 100, 1) : 0.0;

        Console.WriteLine(new string('-', 65));
        Console.WriteLine($"📊 SUMMARY: Pass@1: {p1Pct}% | Pass@3: {p3Pct}% | Solved: {passAt3}/{total}\n");
    }
}

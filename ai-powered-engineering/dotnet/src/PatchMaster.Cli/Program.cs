using PatchMaster.Core;
using PatchMaster.Harness;
using PatchMaster.Loop;
using PatchMaster.Graph;
using PatchMaster.Agents;

namespace PatchMaster.Cli;

public class Program
{
    public static void Main(string[] args)
    {
        if (args.Contains("--benchmark"))
        {
            PatchMaster.Benchmarks.Program.Main(args);
            return;
        }

        if (args.Length == 0 || args.Contains("--help") || args.Contains("-h"))
        {
            Console.WriteLine("PatchMaster: Self-Healing Agentic Refactoring Bot (.NET)");
            Console.WriteLine("\nUsage:");
            Console.WriteLine("  dotnet run --project src/PatchMaster.Cli -- --benchmark");
            Console.WriteLine("  dotnet run --project src/PatchMaster.Cli -- --target <file.cs> --test <test.cs>");
            Console.WriteLine("  dotnet run --project src/PatchMaster.Cli -- --target <file.cs> --test <test.cs> --llm");
            return;
        }

        string? targetPath = null;
        string? testPath = null;
        int maxIter = 3;
        bool useLlm = args.Contains("--llm");

        for (int i = 0; i < args.Length; i++)
        {
            if (args[i] == "--target" && i + 1 < args.Length) targetPath = args[++i];
            if (args[i] == "--test" && i + 1 < args.Length) testPath = args[++i];
            if (args[i] == "--max-iter" && i + 1 < args.Length) int.TryParse(args[++i], out maxIter);
        }

        if (string.IsNullOrEmpty(targetPath) || string.IsNullOrEmpty(testPath) || !File.Exists(targetPath) || !File.Exists(testPath))
        {
            Console.WriteLine($"Error: Target ({targetPath}) or Test ({testPath}) file not found.");
            return;
        }

        var origCode = File.ReadAllText(targetPath);
        var testCode = File.ReadAllText(testPath);

        var sandbox = new DotnetTestSandbox(timeoutSeconds: 15);
        var verifyGate = new VerifyGate(sandbox);
        IMakerAgent maker = useLlm ? new LlmMakerAgent() : new HeuristicMakerAgent();
        var checker = new RuleBasedCheckerAgent();
        var controller = new LoopController(maker, checker, verifyGate);
        var engine = new RefactorGraphEngine(controller);

        var state = new AgentState
        {
            TaskId = Path.GetFileNameWithoutExtension(targetPath),
            OriginalCode = origCode,
            CurrentCode = origCode,
            TestCode = testCode,
            MaxIterations = maxIter
        };

        Console.WriteLine($"\n[PatchMaster] Starting .NET refactor task for: {Path.GetFileName(targetPath)}");
        Console.WriteLine($"[PatchMaster] Maker: {maker.GetType().Name} | Max Iterations: {maxIter}\n");

        var finalState = engine.Run(state);

        Console.WriteLine("\n" + new string('=', 50));
        Console.WriteLine($"Final Status: {finalState.CurrentPhase}");
        Console.WriteLine($"Iterations:   {finalState.Iteration}/{finalState.MaxIterations}");
        Console.WriteLine($"Report:       {finalState.DeliveryReport}");
        Console.WriteLine(new string('=', 50));

        Console.WriteLine("\nExecution Graph Trace:");
        foreach (var step in engine.TraceLog)
        {
            Console.WriteLine($"  Step {step.StepIndex}: Node={step.Node,-12} Phase={step.Phase,-10} Duration={step.DurationMs}ms");
        }

        if (finalState.CurrentPhase == Phase.Deliver)
        {
            Console.WriteLine("\nProposed Verified Solution:");
            Console.WriteLine(new string('-', 40));
            Console.WriteLine(finalState.CurrentCode);
            Console.WriteLine(new string('-', 40));
        }
    }
}

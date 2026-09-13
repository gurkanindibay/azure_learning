using System.Diagnostics;
using DevFactory.Core.Interfaces;
using DevFactory.Core.Models;
using DevFactory.Harness;
using DevFactory.Loop;

namespace DevFactory.Graph;

public class ManufacturingReport
{
    public bool Success { get; set; }
    public string AppName { get; set; } = string.Empty;
    public string OutputDirectory { get; set; } = string.Empty;
    public int Iterations { get; set; }
    public int TotalFilesGenerated { get; set; }
    public double TotalDurationMs { get; set; }
    public List<AssemblyTraceItem> AssemblyTrace { get; set; } = new();
    public string Summary { get; set; } = string.Empty;
}

public class FactoryGraphEngine
{
    private readonly IArchitectAgent _architect;
    private readonly IEngineerAgent _engineer;
    private readonly IQAAgent _qa;
    private readonly FactoryLoopController _loopController;

    public List<AssemblyTraceItem> TraceLog { get; } = new();

    public FactoryGraphEngine(
        IArchitectAgent architect,
        IEngineerAgent engineer,
        IQAAgent qa,
        FactoryLoopController loopController)
    {
        _architect = architect;
        _engineer = engineer;
        _qa = qa;
        _loopController = loopController;
    }

    private void LogStep(string stage, string status, double durationMs, string detail)
    {
        TraceLog.Add(new AssemblyTraceItem
        {
            StepIndex = TraceLog.Count + 1,
            Stage = stage,
            Status = status,
            DurationMs = Math.Round(durationMs, 2),
            Detail = detail
        });
    }

    public async Task<ManufacturingReport> ManufactureAsync(
        SoftwareSpec spec,
        string targetOutputDirectory,
        Action<string>? onLog = null,
        CancellationToken ct = default)
    {
        TraceLog.Clear();
        var totalSw = Stopwatch.StartNew();
        var stepSw = Stopwatch.StartNew();

        onLog?.Invoke($"[Assembly Line Started] Manufacturing standalone application '{spec.AppName}'...");

        // Node 1: Analyze & Architect
        stepSw.Restart();
        var blueprint = _architect.DesignBlueprint(spec);
        stepSw.Stop();
        LogStep("ARCHITECT", "COMPLETED", stepSw.Elapsed.TotalMilliseconds, $"Designed blueprint for {blueprint.Projects.Count} projects with {blueprint.AcceptanceCriteria.Count} acceptance criteria.");
        onLog?.Invoke($"✓ [Architect] Blueprint designed: {blueprint.Projects.Count} projects specified.");

        // Node 2: Initialize Sandbox
        stepSw.Restart();
        using var sandbox = new WorkspaceSandbox();
        await sandbox.InitializeAsync(ct);
        stepSw.Stop();
        LogStep("SCAFFOLD_SANDBOX", "COMPLETED", stepSw.Elapsed.TotalMilliseconds, $"Initialized isolated build environment at: {sandbox.WorkingDirectory}");
        onLog?.Invoke($"✓ [Sandbox] Isolated environment provisioned.");

        // Node 3: Manufacture Loop (TDD & Build Verification)
        stepSw.Restart();
        var loopResult = await _loopController.ExecuteAsync(sandbox, blueprint, _engineer, _qa, maxIterations: 3, onLog, ct);
        stepSw.Stop();

        if (!loopResult.Success)
        {
            LogStep("MANUFACTURE_LOOP", "FAILED", stepSw.Elapsed.TotalMilliseconds, loopResult.SummaryReport);
            totalSw.Stop();
            return new ManufacturingReport
            {
                Success = false,
                AppName = spec.AppName,
                OutputDirectory = targetOutputDirectory,
                TotalDurationMs = totalSw.Elapsed.TotalMilliseconds,
                AssemblyTrace = new List<AssemblyTraceItem>(TraceLog),
                Summary = loopResult.SummaryReport
            };
        }

        LogStep("MANUFACTURE_LOOP", "PASSED", stepSw.Elapsed.TotalMilliseconds, loopResult.SummaryReport);

        // Node 4: Export Deliverable
        stepSw.Restart();
        await sandbox.ExportToAsync(targetOutputDirectory, ct);
        stepSw.Stop();
        LogStep("DELIVERY", "EXPORTED", stepSw.Elapsed.TotalMilliseconds, $"Exported clean solution to {targetOutputDirectory}");
        onLog?.Invoke($"✓ [Delivery] Clean solution exported to target directory: {targetOutputDirectory}");

        totalSw.Stop();
        LogStep("FACTORY_SUMMARY", "SUCCESS", 0.01, "Application manufactured and verified with 100% clean gates.");

        return new ManufacturingReport
        {
            Success = true,
            AppName = spec.AppName,
            OutputDirectory = targetOutputDirectory,
            Iterations = loopResult.IterationsUsed,
            TotalFilesGenerated = loopResult.FinalFiles.Count,
            TotalDurationMs = totalSw.Elapsed.TotalMilliseconds,
            AssemblyTrace = new List<AssemblyTraceItem>(TraceLog),
            Summary = $"Application '{spec.AppName}' manufactured successfully in {totalSw.Elapsed.TotalSeconds:F2}s ({loopResult.IterationsUsed} iteration(s), {loopResult.FinalFiles.Count} files)."
        };
    }
}

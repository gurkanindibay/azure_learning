using DevFactory.Core.Interfaces;
using DevFactory.Core.Models;

namespace DevFactory.Loop;

public class LoopExecutionResult
{
    public bool Success { get; set; }
    public int IterationsUsed { get; set; }
    public List<ProjectSourceFile> FinalFiles { get; set; } = new();
    public BuildGateResult? LastBuildResult { get; set; }
    public TestGateResult? LastTestResult { get; set; }
    public string SummaryReport { get; set; } = string.Empty;
}

public class FactoryLoopController
{
    private readonly IBuildGate _buildGate;
    private readonly ITestGate _testGate;
    private readonly IRoslynAstGate _astGate;

    public FactoryLoopController(
        IBuildGate? buildGate = null,
        ITestGate? testGate = null,
        IRoslynAstGate? astGate = null)
    {
        _buildGate = buildGate ?? new BuildVerifyGate();
        _testGate = testGate ?? new TestVerifyGate();
        _astGate = astGate ?? new Harness.RoslynAstGate();
    }

    public async Task<LoopExecutionResult> ExecuteAsync(
        IWorkspaceSandbox sandbox,
        SoftwareBlueprint blueprint,
        IEngineerAgent engineer,
        IQAAgent qa,
        int maxIterations = 3,
        Action<string>? onProgress = null,
        CancellationToken ct = default)
    {
        int iteration = 0;
        string? diagnosticFeedback = null;
        List<ProjectSourceFile> currentFiles = new();

        while (iteration < maxIterations)
        {
            iteration++;
            onProgress?.Invoke($"[Loop Iteration {iteration}/{maxIterations}] Synthesizing and verifying source files...");

            // 1. Generate code (incorporating any feedback from previous iteration)
            var sourceFiles = engineer.GenerateSourceFiles(blueprint, diagnosticFeedback);
            var testFiles = qa.GenerateTestFiles(blueprint);
            currentFiles = sourceFiles.Concat(testFiles).ToList();

            // 2. Roslyn In-Memory AST Syntax Gate
            bool syntaxPassed = true;
            foreach (var file in currentFiles.Where(f => f.RelativePath.EndsWith(".cs")))
            {
                var syntaxCheck = _astGate.ValidateSyntax(file.Content);
                if (!syntaxCheck.IsValid)
                {
                    syntaxPassed = false;
                    diagnosticFeedback = $"Syntax errors in {file.RelativePath}: {string.Join("; ", syntaxCheck.SyntaxErrors)}";
                    onProgress?.Invoke($"[AST Syntax Error] {diagnosticFeedback}");
                    break;
                }
            }

            if (!syntaxPassed)
            {
                continue;
            }

            // 3. Write files to isolated sandbox
            await sandbox.WriteFilesAsync(currentFiles, ct);

            // 4. Build Gate
            onProgress?.Invoke("[Build Gate] Compiling solution...");
            var buildResult = await _buildGate.BuildAsync(sandbox.WorkingDirectory, ct);
            if (!buildResult.Passed)
            {
                diagnosticFeedback = $"Build failed with errors:\n" + string.Join("\n", buildResult.Errors);
                onProgress?.Invoke($"[Build Failed] {buildResult.Errors.Count} error(s) detected. Routing diagnostic to engineer agent for self-healing.");
                continue;
            }

            // 5. Test Gate
            onProgress?.Invoke("[Test Gate] Executing xUnit test suite...");
            var testResult = await _testGate.RunTestsAsync(sandbox.WorkingDirectory, ct);
            if (!testResult.Passed)
            {
                diagnosticFeedback = $"Tests failed ({testResult.FailedCount} failed):\n" + string.Join("\n", testResult.FailedTestSummaries);
                onProgress?.Invoke($"[Tests Failed] {testResult.FailedCount} failure(s). Routing failure feedback to engineer agent for self-healing.");
                continue;
            }

            // Both Gates Clean!
            onProgress?.Invoke($"[Quality Gate Passed] 0 build errors. All {testResult.PassedCount} unit tests passed on iteration {iteration}.");
            return new LoopExecutionResult
            {
                Success = true,
                IterationsUsed = iteration,
                FinalFiles = currentFiles,
                LastBuildResult = buildResult,
                LastTestResult = testResult,
                SummaryReport = $"Manufactured successfully with 100% test pass rate ({testResult.PassedCount} tests passing, 0 build errors in {iteration} iteration(s))."
            };
        }

        return new LoopExecutionResult
        {
            Success = false,
            IterationsUsed = iteration,
            FinalFiles = currentFiles,
            SummaryReport = $"Manufacturing failed: Could not reconcile all build/test gates within {maxIterations} iterations. Last error: {diagnosticFeedback}"
        };
    }
}

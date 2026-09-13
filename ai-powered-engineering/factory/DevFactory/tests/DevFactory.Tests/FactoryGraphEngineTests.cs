using DevFactory.Agents;
using DevFactory.Core.Interfaces;
using DevFactory.Core.Models;
using DevFactory.Graph;
using DevFactory.Loop;
using Xunit;

namespace DevFactory.Tests;

public class MockPassingBuildGate : IBuildGate
{
    public Task<BuildGateResult> BuildAsync(string workingDirectory, CancellationToken ct = default)
    {
        return Task.FromResult(new BuildGateResult { Passed = true });
    }
}

public class MockPassingTestGate : ITestGate
{
    public Task<TestGateResult> RunTestsAsync(string workingDirectory, CancellationToken ct = default)
    {
        return Task.FromResult(new TestGateResult
        {
            Passed = true,
            TotalTests = 5,
            PassedCount = 5,
            FailedCount = 0
        });
    }
}

public class FactoryGraphEngineTests : IDisposable
{
    private readonly string _exportDir;

    public FactoryGraphEngineTests()
    {
        _exportDir = Path.Combine(Path.GetTempPath(), $"factory_test_export_{Guid.NewGuid():N}");
    }

    public void Dispose()
    {
        if (Directory.Exists(_exportDir))
        {
            try { Directory.Delete(_exportDir, recursive: true); } catch { /* ignore */ }
        }
    }

    [Fact]
    public async Task ManufactureAsync_OrchestratesAllAssemblyNodesSuccessfully()
    {
        var architect = new ArchitectAgent();
        var engineer = new EngineerAgent();
        var qa = new QAAgent();
        var loopController = new FactoryLoopController(new MockPassingBuildGate(), new MockPassingTestGate());
        var factory = new FactoryGraphEngine(architect, engineer, qa, loopController);

        var spec = new SoftwareSpec
        {
            AppName = "TestManufacturedApp",
            Description = "A test standalone app manufactured by DevFactory"
        };

        var report = await factory.ManufactureAsync(spec, _exportDir);

        Assert.True(report.Success);
        Assert.Equal("TestManufacturedApp", report.AppName);
        Assert.True(report.TotalFilesGenerated > 0);

        // Verify traces
        Assert.Contains(report.AssemblyTrace, t => t.Stage == "ARCHITECT" && t.Status == "COMPLETED");
        Assert.Contains(report.AssemblyTrace, t => t.Stage == "SCAFFOLD_SANDBOX" && t.Status == "COMPLETED");
        Assert.Contains(report.AssemblyTrace, t => t.Stage == "MANUFACTURE_LOOP" && t.Status == "PASSED");
        Assert.Contains(report.AssemblyTrace, t => t.Stage == "DELIVERY" && t.Status == "EXPORTED");

        // Verify exported solution file exists
        Assert.True(File.Exists(Path.Combine(_exportDir, "TestManufacturedApp.sln")));
    }
}

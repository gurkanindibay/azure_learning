using DevFactory.Core.Models;

namespace DevFactory.Core.Interfaces;

public interface IWorkspaceSandbox : IDisposable
{
    string WorkingDirectory { get; }
    Task InitializeAsync(CancellationToken ct = default);
    Task WriteFilesAsync(IEnumerable<ProjectSourceFile> files, CancellationToken ct = default);
    Task<string> ReadFileAsync(string relativePath, CancellationToken ct = default);
    Task ExportToAsync(string destinationDirectory, CancellationToken ct = default);
}

public interface IRoslynAstGate
{
    SyntaxGateResult ValidateSyntax(string csharpSource);
}

public interface IBuildGate
{
    Task<BuildGateResult> BuildAsync(string workingDirectory, CancellationToken ct = default);
}

public interface ITestGate
{
    Task<TestGateResult> RunTestsAsync(string workingDirectory, CancellationToken ct = default);
}

public interface IArchitectAgent
{
    SoftwareBlueprint DesignBlueprint(SoftwareSpec spec);
}

public interface IEngineerAgent
{
    List<ProjectSourceFile> GenerateSourceFiles(SoftwareBlueprint blueprint, string? feedback = null);
}

public interface IQAAgent
{
    List<ProjectSourceFile> GenerateTestFiles(SoftwareBlueprint blueprint);
}

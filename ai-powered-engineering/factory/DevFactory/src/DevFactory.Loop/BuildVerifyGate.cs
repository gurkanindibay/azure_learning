using DevFactory.Core.Interfaces;
using DevFactory.Core.Models;
using DevFactory.Harness;

namespace DevFactory.Loop;

public class BuildVerifyGate : IBuildGate
{
    public async Task<BuildGateResult> BuildAsync(string workingDirectory, CancellationToken ct = default)
    {
        var runResult = await DotnetProcessRunner.RunAsync("build --nologo -v quiet", workingDirectory, timeoutSeconds: 45, ct);

        var errors = DiagnosticExtractor.ExtractBuildErrors(runResult.StandardOutput + "\n" + runResult.StandardError);

        return new BuildGateResult
        {
            Passed = runResult.ExitCode == 0,
            Errors = errors,
            RawOutput = runResult.StandardOutput + "\n" + runResult.StandardError
        };
    }
}

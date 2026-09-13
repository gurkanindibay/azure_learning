using PatchMaster.Core;
using PatchMaster.Harness;

namespace PatchMaster.Loop;

public class VerifyGate : IVerifyGate
{
    private readonly ISandbox _sandbox;

    public VerifyGate(ISandbox? sandbox = null)
    {
        _sandbox = sandbox ?? new DotnetTestSandbox();
    }

    public VerificationResult Verify(string originalCode, string candidateCode, string testCode)
    {
        // 1. Roslyn AST Syntax Gate
        var (astValid, astError) = RoslynSyntaxGate.ValidateSyntax(candidateCode);
        if (!astValid)
        {
            return new VerificationResult
            {
                Passed = false,
                AstValid = false,
                DiffValid = false,
                TestsPassed = false,
                Stderr = astError ?? "Syntax Error",
                ErrorSummary = $"Roslyn AST Syntax Check Failed: {astError}"
            };
        }

        // 2. Diff Sanity Gate
        var (diffValid, diffMessage) = RoslynSyntaxGate.CheckDiffSanity(originalCode, candidateCode);
        if (!diffValid)
        {
            return new VerificationResult
            {
                Passed = false,
                AstValid = true,
                DiffValid = false,
                TestsPassed = false,
                Stderr = diffMessage,
                ErrorSummary = $"Diff Sanity Check Failed: {diffMessage}"
            };
        }

        // 3. Dotnet Test Sandbox Gate
        var (passed, exitCode, stdout, stderr) = _sandbox.RunTests(candidateCode, testCode);
        var summary = passed ? string.Empty : ContextManager.ExtractFailureSignal(stdout, stderr);

        return new VerificationResult
        {
            Passed = passed,
            AstValid = true,
            DiffValid = true,
            TestsPassed = passed,
            TotalTests = 1,
            FailedTests = passed ? 0 : 1,
            Stdout = stdout,
            Stderr = stderr,
            ErrorSummary = summary
        };
    }
}

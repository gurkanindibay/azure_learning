using Xunit;
using PatchMaster.Harness;

namespace PatchMaster.Tests;

public class HarnessTests
{
    [Fact]
    public void RoslynSyntaxGate_ValidCode_ReturnsTrue()
    {
        var code = "public class Calc { public int Add(int a, int b) => a + b; }";
        var (isValid, err) = RoslynSyntaxGate.ValidateSyntax(code);
        Assert.True(isValid);
        Assert.Null(err);
    }

    [Fact]
    public void RoslynSyntaxGate_SyntaxError_ReturnsFalse()
    {
        var code = "public class Calc { public int Add(int a, int b return a + b; }"; // missing ')'
        var (isValid, err) = RoslynSyntaxGate.ValidateSyntax(code);
        Assert.False(isValid);
        Assert.NotNull(err);
        Assert.Contains("Roslyn C# Syntax Error", err);
    }

    [Fact]
    public void RoslynSyntaxGate_EmptyCandidate_FailsSanity()
    {
        var (isValid, msg) = RoslynSyntaxGate.CheckDiffSanity("class A {}", "   ");
        Assert.False(isValid);
        Assert.Contains("completely empty", msg);
    }

    [Fact]
    public void ContextManager_ExtractsAssertionFailure()
    {
        var sample = @"Starting test execution...
[xUnit.net 00:00:00.12] Test failed: SolutionTests.Test1 [FAIL]
  Assert.Equal() Failure
  Expected: 80
  Actual:   20
Stack Trace:
  SolutionTests.cs(5): at SolutionTests.Test1()";

        var signal = ContextManager.ExtractFailureSignal(sample, string.Empty);
        Assert.Contains("Assert.Equal()", signal);
    }
}

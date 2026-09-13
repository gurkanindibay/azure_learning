using DevFactory.Harness;
using Xunit;

namespace DevFactory.Tests;

public class DiagnosticExtractorTests
{
    [Fact]
    public void ExtractBuildErrors_ParsesCompilerErrors()
    {
        var rawBuildOutput = """
        Microsoft (R) Build Engine version 17.8.0 for .NET
        src/MyProject/Models.cs(12,45): error CS1002: ; expected [/home/src/MyProject/MyProject.csproj]
        src/MyProject/Services.cs(4,18): error CS0246: The type or namespace name 'MyType' could not be found [/home/src/MyProject/MyProject.csproj]
        Build FAILED.
        """;

        var errors = DiagnosticExtractor.ExtractBuildErrors(rawBuildOutput);

        Assert.Equal(2, errors.Count);
        Assert.Contains("error CS1002: ; expected", errors[0]);
        Assert.Contains("error CS0246", errors[1]);
    }

    [Fact]
    public void ExtractTestFailures_ParsesFailedTestSummaries()
    {
        var rawTestOutput = """
        Starting test execution, please wait...
        [xUnit.net 00:00:00.12]     MyProject.Tests.ServiceTests.Execute_ThrowsException [FAIL]
          Failed MyProject.Tests.ServiceTests.Execute_ThrowsException [12 ms]
          Error Message:
           Assert.Equal() Failure: Expected 10, Actual 5
        Passed!  - Failed: 1, Passed: 5, Skipped: 0, Total: 6
        """;

        var failures = DiagnosticExtractor.ExtractTestFailures(rawTestOutput);

        Assert.NotEmpty(failures);
        Assert.Contains(failures, f => f.Contains("Execute_ThrowsException"));
    }
}

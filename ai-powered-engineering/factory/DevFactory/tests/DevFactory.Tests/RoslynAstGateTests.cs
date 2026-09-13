using DevFactory.Harness;
using Xunit;

namespace DevFactory.Tests;

public class RoslynAstGateTests
{
    private readonly RoslynAstGate _gate = new();

    [Fact]
    public void ValidateSyntax_ValidCSharp_Passes()
    {
        var code = """
        namespace MyCompany.Core;

        public class UserProfile
        {
            public string Name { get; set; } = string.Empty;
        }
        """;

        var result = _gate.ValidateSyntax(code);

        Assert.True(result.IsValid);
        Assert.Empty(result.SyntaxErrors);
    }

    [Fact]
    public void ValidateSyntax_SyntaxError_FailsWithDiagnostics()
    {
        var malformedCode = """
        namespace MyCompany.Core;

        public class UserProfile
        {
            public string Name { get; set } // missing semicolon
        }
        """;

        var result = _gate.ValidateSyntax(malformedCode);

        Assert.False(result.IsValid);
        Assert.NotEmpty(result.SyntaxErrors);
    }
}

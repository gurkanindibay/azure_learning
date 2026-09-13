using DevFactory.Core.Interfaces;
using DevFactory.Core.Models;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;

namespace DevFactory.Harness;

public class RoslynAstGate : IRoslynAstGate
{
    public SyntaxGateResult ValidateSyntax(string csharpSource)
    {
        var tree = CSharpSyntaxTree.ParseText(csharpSource);
        var diagnostics = tree.GetDiagnostics().Where(d => d.Severity == DiagnosticSeverity.Error).ToList();

        return new SyntaxGateResult
        {
            IsValid = diagnostics.Count == 0,
            SyntaxErrors = diagnostics.Select(d => $"{d.Id} at {d.Location.GetLineSpan().StartLinePosition}: {d.GetMessage()}").ToList()
        };
    }
}

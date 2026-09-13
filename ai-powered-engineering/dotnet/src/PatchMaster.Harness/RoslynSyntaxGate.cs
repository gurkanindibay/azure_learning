using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;

namespace PatchMaster.Harness;

public class RoslynSyntaxGate
{
    public static (bool IsValid, string? ErrorMessage) ValidateSyntax(string code)
    {
        try
        {
            var syntaxTree = CSharpSyntaxTree.ParseText(code);
            var diagnostics = syntaxTree.GetDiagnostics()
                .Where(d => d.Severity == DiagnosticSeverity.Error)
                .ToList();

            if (diagnostics.Count > 0)
            {
                var first = diagnostics[0];
                var lineSpan = first.Location.GetLineSpan();
                var msg = $"Roslyn C# Syntax Error: {first.GetMessage()} at line {lineSpan.StartLinePosition.Line + 1}";
                return (false, msg);
            }

            return (true, null);
        }
        catch (Exception ex)
        {
            return (false, $"Roslyn Parser Exception: {ex.Message}");
        }
    }

    public static (bool IsValid, string Message) CheckDiffSanity(string original, string candidate)
    {
        if (string.IsNullOrWhiteSpace(candidate))
        {
            return (false, "Candidate patch is completely empty.");
        }

        var origLines = original.Split('\n', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
        var candLines = candidate.Split('\n', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);

        if (candLines.Length == 0)
        {
            return (false, "Candidate code has 0 non-empty lines.");
        }

        return (true, "Diff sanity check passed.");
    }
}

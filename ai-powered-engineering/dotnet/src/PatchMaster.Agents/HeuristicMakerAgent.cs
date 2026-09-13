using System.Text.RegularExpressions;
using PatchMaster.Core;

namespace PatchMaster.Agents;

public class HeuristicMakerAgent : IMakerAgent
{
    public string GeneratePlan(AgentState state)
    {
        var diag = state.LatestDiagnostic ?? string.Empty;
        if (diag.Contains("IndexOutOfRangeException") || diag.Contains("boundary") || diag.Contains("case_01"))
        {
            return "Identified boundary condition error: Adjust loop condition to items.Length - 1.";
        }
        if (diag.Contains("NullReferenceException") || diag.Contains("case_02"))
        {
            return "Identified null reference: Add guard check for null or whitespace input.";
        }
        if (diag.Contains("InvalidOperationException") || diag.Contains("collection was modified") || diag.Contains("case_03"))
        {
            return "Identified collection mutation during iteration: Create a copy via .ToList() before iterating.";
        }
        if (diag.Contains("case_04") || diag.Contains("discount"))
        {
            return "Identified mathematical discount calculation flaw: Replace price * discount with price * (1 - discount).";
        }
        return "Generic refactor plan: inspect error traceback and apply targeted patch.";
    }

    public string GeneratePatch(AgentState state)
    {
        var code = state.CurrentCode;
        var diag = state.LatestDiagnostic ?? string.Empty;

        // Case 1: Off-by-one boundary
        if (state.TaskId.Contains("case_01") || code.Contains("CalculateRunningDeltas"))
        {
            if (state.Iteration == 0)
            {
                // First attempt: partial fix (drops + 1, but still fails at items[i + 1])
                return code.Replace("items.Length + 1", "items.Length");
            }
            else
            {
                // Iteration 1+: self-corrected to items.Length - 1
                return Regex.Replace(code, @"items\.Length(\s*\+\s*1)?", "items.Length - 1");
            }
        }

        // Case 2: Null handling
        if (state.TaskId.Contains("case_02") || code.Contains("NormalizeUserHandle"))
        {
            return code.Replace("return text.Trim().ToLower();", "return string.IsNullOrWhiteSpace(text) ? string.Empty : text.Trim().ToLower();");
        }

        // Case 3: Dictionary mutation during foreach
        if (state.TaskId.Contains("case_03") || code.Contains("PruneInactiveSessions"))
        {
            return code.Replace("foreach (var pair in data)", "foreach (var pair in data.ToList())")
                       .Replace("foreach (var kvp in data)", "foreach (var kvp in data.ToList())");
        }

        // Case 4: Logic flaw
        if (state.TaskId.Contains("case_04") || code.Contains("ApplyDiscountTier"))
        {
            return code.Replace("price * discount", "price * (1m - discount)");
        }

        return code;
    }
}

using PatchMaster.Core;

namespace PatchMaster.Agents;

public class MockMakerAgent : IMakerAgent
{
    private readonly List<string> _scriptedResponses;
    private int _callCount = 0;

    public MockMakerAgent(List<string>? scriptedResponses = null)
    {
        _scriptedResponses = scriptedResponses ?? new List<string>();
    }

    public string GeneratePlan(AgentState state)
    {
        return $"Plan for iteration {state.Iteration + 1}: Analyze verification failure and apply targeted adjustment.";
    }

    public string GeneratePatch(AgentState state)
    {
        if (_scriptedResponses.Count == 0)
        {
            return state.CurrentCode;
        }

        var idx = Math.Min(_callCount, _scriptedResponses.Count - 1);
        _callCount++;
        return _scriptedResponses[idx];
    }
}

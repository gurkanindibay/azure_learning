using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using PatchMaster.Core;
using PatchMaster.Harness;

namespace PatchMaster.Agents;

public class LlmMakerAgent : IMakerAgent
{
    private readonly string _modelName;
    private static readonly HttpClient HttpClient = new();

    public LlmMakerAgent(string modelName = "gpt-4o-mini")
    {
        _modelName = modelName;
    }

    public string GeneratePlan(AgentState state)
    {
        var prompt = $"Given C# code that failed with:\n{state.LatestDiagnostic}\nPropose a concise 2-sentence fix plan.";
        return CallLlm(prompt);
    }

    public string GeneratePatch(AgentState state)
    {
        var prompt = ContextManager.FormatIterationPrompt(
            state.OriginalCode,
            state.CurrentCode,
            state.TestCode,
            state.History,
            state.LatestDiagnostic);

        var raw = CallLlm(prompt);

        // Strip markdown code fences if wrapped
        var match = Regex.Match(raw, @"```(?:csharp)?\s*(.*?)\s*```", RegexOptions.Singleline);
        if (match.Success)
        {
            return match.Groups[1].Value.Trim();
        }

        return raw.Trim();
    }

    private string CallLlm(string prompt)
    {
        var apiKey = Environment.GetEnvironmentVariable("OPENAI_API_KEY") 
                  ?? Environment.GetEnvironmentVariable("GEMINI_API_KEY");

        if (string.IsNullOrEmpty(apiKey))
        {
            return "// Error: No OPENAI_API_KEY or GEMINI_API_KEY environment variable configured. Switch to HeuristicMakerAgent or set OPENAI_API_KEY.";
        }

        try
        {
            var requestBody = new
            {
                model = _modelName,
                messages = new[]
                {
                    new { role = "user", content = prompt }
                },
                temperature = 0.2
            };

            var json = JsonSerializer.Serialize(requestBody);
            using var request = new HttpRequestMessage(HttpMethod.Post, "https://api.openai.com/v1/chat/completions")
            {
                Headers = { { "Authorization", $"Bearer {apiKey}" } },
                Content = new StringContent(json, Encoding.UTF8, "application/json")
            };

            var response = HttpClient.Send(request);
            var responseJson = response.Content.ReadAsStringAsync().Result;

            using var doc = JsonDocument.Parse(responseJson);
            var content = doc.RootElement
                .GetProperty("choices")[0]
                .GetProperty("message")
                .GetProperty("content")
                .GetString();

            return content ?? string.Empty;
        }
        catch (Exception ex)
        {
            return $"// LLM API invocation failed: {ex.Message}";
        }
    }
}

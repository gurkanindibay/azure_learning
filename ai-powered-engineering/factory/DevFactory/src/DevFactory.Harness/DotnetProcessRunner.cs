using System.Diagnostics;
using System.Text;

namespace DevFactory.Harness;

public record ProcessRunResult(int ExitCode, string StandardOutput, string StandardError, double DurationMs);

public static class DotnetProcessRunner
{
    public static async Task<ProcessRunResult> RunAsync(string arguments, string workingDirectory, int timeoutSeconds = 30, CancellationToken ct = default)
    {
        var psi = new ProcessStartInfo
        {
            FileName = "dotnet",
            Arguments = arguments,
            WorkingDirectory = workingDirectory,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true
        };

        var stdout = new StringBuilder();
        var stderr = new StringBuilder();
        var sw = Stopwatch.StartNew();

        using var process = new Process { StartInfo = psi };
        process.OutputDataReceived += (_, e) => { if (e.Data != null) stdout.AppendLine(e.Data); };
        process.ErrorDataReceived += (_, e) => { if (e.Data != null) stderr.AppendLine(e.Data); };

        process.Start();
        process.BeginOutputReadLine();
        process.BeginErrorReadLine();

        using var cts = CancellationTokenSource.CreateLinkedTokenSource(ct);
        cts.CancelAfter(TimeSpan.FromSeconds(timeoutSeconds));

        try
        {
            await process.WaitForExitAsync(cts.Token);
        }
        catch (OperationCanceledException)
        {
            try { process.Kill(entireProcessTree: true); } catch { /* ignore */ }
            return new ProcessRunResult(-1, stdout.ToString(), "Process timed out.", sw.Elapsed.TotalMilliseconds);
        }

        sw.Stop();
        return new ProcessRunResult(process.ExitCode, stdout.ToString(), stderr.ToString(), sw.Elapsed.TotalMilliseconds);
    }
}

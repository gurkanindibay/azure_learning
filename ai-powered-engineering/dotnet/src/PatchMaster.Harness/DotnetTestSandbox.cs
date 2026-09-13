using System.Diagnostics;
using PatchMaster.Core;

namespace PatchMaster.Harness;

public class DotnetTestSandbox : ISandbox
{
    private readonly int _timeoutSeconds;

    public DotnetTestSandbox(int timeoutSeconds = 15)
    {
        _timeoutSeconds = timeoutSeconds;
    }

    public (bool Passed, int ExitCode, string Stdout, string Stderr) RunTests(string code, string testCode)
    {
        var tempDir = Path.Combine(Path.GetTempPath(), "patchmaster_dotnet_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(tempDir);

        try
        {
            var csprojContent = @"<Project Sdk=""Microsoft.NET.Sdk"">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <IsPackable>false</IsPackable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include=""Microsoft.NET.Test.Sdk"" Version=""17.8.0"" />
    <PackageReference Include=""xunit"" Version=""2.6.2"" />
    <PackageReference Include=""xunit.runner.visualstudio"" Version=""2.5.4"" />
  </ItemGroup>
</Project>";

            File.WriteAllText(Path.Combine(tempDir, "Sandbox.csproj"), csprojContent);
            File.WriteAllText(Path.Combine(tempDir, "Solution.cs"), code);
            File.WriteAllText(Path.Combine(tempDir, "SolutionTests.cs"), testCode);

            var startInfo = new ProcessStartInfo
            {
                FileName = "dotnet",
                Arguments = "test --no-logo -v q",
                WorkingDirectory = tempDir,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };

            using var process = new Process { StartInfo = startInfo };
            process.Start();

            var stdoutTask = process.StandardOutput.ReadToEndAsync();
            var stderrTask = process.StandardError.ReadToEndAsync();

            if (!process.WaitForExit(TimeSpan.FromSeconds(_timeoutSeconds)))
            {
                try { process.Kill(true); } catch { }
                return (false, -1, string.Empty, $"Execution timed out after {_timeoutSeconds} seconds.");
            }

            Task.WaitAll(stdoutTask, stderrTask);
            var stdout = stdoutTask.Result;
            var stderr = stderrTask.Result;

            var passed = process.ExitCode == 0;
            return (passed, process.ExitCode, stdout, stderr);
        }
        catch (Exception ex)
        {
            return (false, -2, string.Empty, $"Sandbox Exception: {ex.Message}");
        }
        finally
        {
            try
            {
                if (Directory.Exists(tempDir))
                {
                    Directory.Delete(tempDir, true);
                }
            }
            catch { }
        }
    }
}

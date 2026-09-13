using System.Text;
using DevFactory.Agents;
using DevFactory.Core.Models;
using DevFactory.Graph;
using DevFactory.Loop;

namespace DevFactory.Cli;

public class Program
{
    public static async Task<int> Main(string[] args)
    {
        Console.OutputEncoding = Encoding.UTF8;
        PrintBanner();

        if (args.Length == 0 || args.Contains("--help") || args.Contains("-h"))
        {
            PrintUsage();
            return 0;
        }

        string appName = "CacheShield";
        string appDesc = "High-performance multi-tier cache microservice with TTL and concurrency locks";
        string targetOutDir = Path.Combine(Directory.GetCurrentDirectory(), "apps", appName);

        if (args.Contains("demo"))
        {
            Console.WriteLine("[DevFactory] Running manufacturing demonstration for: CacheShield");
        }
        else if (args[0] == "build")
        {
            for (int i = 1; i < args.Length; i++)
            {
                if (args[i] == "--name" && i + 1 < args.Length) appName = args[++i];
                else if (args[i] == "--desc" && i + 1 < args.Length) appDesc = args[++i];
                else if (args[i] == "--out" && i + 1 < args.Length) targetOutDir = Path.GetFullPath(args[++i]);
            }
        }
        else
        {
            PrintUsage();
            return 1;
        }

        var spec = new SoftwareSpec
        {
            AppName = appName,
            Description = appDesc,
            OutputDirectory = targetOutDir
        };

        // Initialize Factory assembly line
        var architect = new ArchitectAgent();
        var engineer = new EngineerAgent();
        var qa = new QAAgent();
        var loopController = new FactoryLoopController();
        var factory = new FactoryGraphEngine(architect, engineer, qa, loopController);

        Console.WriteLine($"Target Application: {appName}");
        Console.WriteLine($"Description:        {appDesc}");
        Console.WriteLine($"Output Destination: {targetOutDir}\n");

        var report = await factory.ManufactureAsync(spec, targetOutDir, onLog: Console.WriteLine);

        Console.WriteLine("\n==========================================================================");
        Console.WriteLine("                  FACTORY ASSEMBLY LINE EXECUTION TRACE                   ");
        Console.WriteLine("==========================================================================");
        Console.WriteLine($"{"Step",-5} {"Stage",-20} {"Status",-12} {"Duration",-12} {"Detail"}");
        Console.WriteLine(new string('-', 74));
        foreach (var item in report.AssemblyTrace)
        {
            Console.WriteLine($"{item.StepIndex,-5} {item.Stage,-20} {item.Status,-12} {item.DurationMs + "ms",-12} {item.Detail}");
        }
        Console.WriteLine(new string('=', 74));

        if (report.Success)
        {
            Console.ForegroundColor = ConsoleColor.Green;
            Console.WriteLine($"\n✓ MANUFACTURING SUCCEEDED: {report.Summary}");
            Console.ResetColor();
            Console.WriteLine($"\nYou can now navigate to your new standalone application:");
            Console.WriteLine($"  cd \"{targetOutDir}\"");
            Console.WriteLine($"  dotnet test");
            Console.WriteLine($"  dotnet run --project src/{appName}.Cli");
            return 0;
        }
        else
        {
            Console.ForegroundColor = ConsoleColor.Red;
            Console.WriteLine($"\n❌ MANUFACTURING FAILED: {report.Summary}");
            Console.ResetColor();
            return 1;
        }
    }

    private static void PrintBanner()
    {
        Console.ForegroundColor = ConsoleColor.Magenta;
        Console.WriteLine(@"
    ____             ______           __                  
   / __ \___ _   __ / ____/____ _____/ /_____  _______  __
  / / / / _ \ | / // /_  / __ `/ ___/ __/ __ \/ ___/ / / /
 / /_/ /  __/ |/ // __/ / /_/ / /__/ /_/ /_/ / /  / /_/ / 
/_____/\___/|___//_/    \__,_/\___/\__/\____/_/   \__, /  
    Autonomous Software Development Factory      /____/   
    Architecture: Harness -> Loop -> Graph Engineering
");
        Console.ResetColor();
    }

    private static void PrintUsage()
    {
        Console.WriteLine("Usage:");
        Console.WriteLine("  devfactory demo                                    # Manufactures demonstration application");
        Console.WriteLine("  devfactory build --name <AppName> [--desc <Desc>] [--out <TargetDir>]");
    }
}

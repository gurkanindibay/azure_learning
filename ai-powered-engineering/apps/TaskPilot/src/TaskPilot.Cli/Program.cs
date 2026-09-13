using System.Globalization;
using System.Text;
using TaskPilot.Core.Interfaces;
using TaskPilot.Core.Models;
using TaskPilot.Infrastructure;
using TaskPilot.Services;

namespace TaskPilot.Cli;

public class Program
{
    public static async Task<int> Main(string[] args)
    {
        Console.OutputEncoding = Encoding.UTF8;

        if (args.Length == 0 || args.Contains("--help") || args.Contains("-h"))
        {
            PrintBanner();
            PrintUsage();
            return 0;
        }

        ITaskRepository repository = new JsonTaskRepository();
        ITaskService service = new TaskService(repository);

        var command = args[0].ToLowerInvariant();

        try
        {
            switch (command)
            {
                case "add":
                    return await HandleAddAsync(service, args.Skip(1).ToArray());
                case "list":
                    return await HandleListAsync(service, args.Skip(1).ToArray());
                case "move":
                    return await HandleMoveAsync(service, args.Skip(1).ToArray());
                case "delete":
                    return await HandleDeleteAsync(service, args.Skip(1).ToArray());
                case "summary":
                    return await HandleSummaryAsync(service);
                case "seed":
                    return await HandleSeedAsync(service);
                default:
                    Console.ForegroundColor = ConsoleColor.Red;
                    Console.WriteLine($"[Error] Unknown command: '{command}'");
                    Console.ResetColor();
                    PrintUsage();
                    return 1;
            }
        }
        catch (Exception ex)
        {
            Console.ForegroundColor = ConsoleColor.Red;
            Console.WriteLine($"[Error] {ex.Message}");
            Console.ResetColor();
            return 1;
        }
    }

    private static async Task<int> HandleAddAsync(ITaskService service, string[] args)
    {
        if (args.Length == 0)
        {
            Console.WriteLine("Usage: taskpilot add \"<title>\" [--desc \"<description>\"] [--priority Low|Medium|High|Critical] [--due YYYY-MM-DD] [--tags t1,t2]");
            return 1;
        }

        var title = args[0];
        string desc = string.Empty;
        var priority = TaskPriority.Medium;
        DateTime? due = null;
        List<string> tags = new();

        for (int i = 1; i < args.Length; i++)
        {
            if (args[i] == "--desc" && i + 1 < args.Length) desc = args[++i];
            else if (args[i] == "--priority" && i + 1 < args.Length)
            {
                if (Enum.TryParse<TaskPriority>(args[++i], true, out var p)) priority = p;
            }
            else if (args[i] == "--due" && i + 1 < args.Length)
            {
                if (DateTime.TryParse(args[++i], CultureInfo.InvariantCulture, out var dt)) due = dt.ToUniversalTime();
            }
            else if (args[i] == "--tags" && i + 1 < args.Length)
            {
                tags = args[++i].Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries).ToList();
            }
        }

        var item = await service.CreateTaskAsync(title, desc, priority, due, tags);
        Console.ForegroundColor = ConsoleColor.Green;
        Console.WriteLine($"✓ Task [{item.Id}] created successfully.");
        Console.ResetColor();
        Console.WriteLine($"  Title:    {item.Title}");
        Console.WriteLine($"  Priority: {item.Priority}");
        Console.WriteLine($"  Status:   {item.Status}");
        if (item.DueDateUtc.HasValue) Console.WriteLine($"  Due:      {item.DueDateUtc.Value:yyyy-MM-dd}");
        if (item.Tags.Count > 0) Console.WriteLine($"  Tags:     {string.Join(", ", item.Tags)}");

        return 0;
    }

    private static async Task<int> HandleListAsync(ITaskService service, string[] args)
    {
        TaskItemStatus? status = null;
        TaskPriority? priority = null;
        string? tag = null;
        bool overdue = false;

        for (int i = 0; i < args.Length; i++)
        {
            if (args[i] == "--status" && i + 1 < args.Length)
            {
                if (Enum.TryParse<TaskItemStatus>(args[++i], true, out var s)) status = s;
            }
            else if (args[i] == "--priority" && i + 1 < args.Length)
            {
                if (Enum.TryParse<TaskPriority>(args[++i], true, out var p)) priority = p;
            }
            else if (args[i] == "--tag" && i + 1 < args.Length)
            {
                tag = args[++i];
            }
            else if (args[i] == "--overdue")
            {
                overdue = true;
            }
        }

        var items = await service.ListTasksAsync(status, priority, tag, overdue);

        if (items.Count == 0)
        {
            Console.WriteLine("No tasks found matching criteria.");
            return 0;
        }

        Console.WriteLine($"\n{"ID",-10} {"STATUS",-12} {"PRIORITY",-10} {"DUE",-12} {"TITLE",-30} {"TAGS"}");
        Console.WriteLine(new string('-', 85));

        foreach (var t in items)
        {
            SetStatusColor(t.Status);
            Console.Write($"{t.Id,-10} {t.Status,-12} ");
            SetPriorityColor(t.Priority);
            Console.Write($"{t.Priority,-10} ");
            Console.ResetColor();

            var dueStr = t.DueDateUtc.HasValue ? t.DueDateUtc.Value.ToString("yyyy-MM-dd") : "-";
            if (t.IsOverdue())
            {
                Console.ForegroundColor = ConsoleColor.Red;
                dueStr += " (!)";
            }
            Console.Write($"{dueStr,-12} ");
            Console.ResetColor();

            var titleStr = t.Title.Length > 28 ? t.Title[..25] + "..." : t.Title;
            Console.Write($"{titleStr,-30} ");

            var tagsStr = t.Tags.Count > 0 ? $"[{string.Join(", ", t.Tags)}]" : string.Empty;
            Console.ForegroundColor = ConsoleColor.DarkGray;
            Console.WriteLine(tagsStr);
            Console.ResetColor();
        }
        Console.WriteLine();
        return 0;
    }

    private static async Task<int> HandleMoveAsync(ITaskService service, string[] args)
    {
        if (args.Length < 2)
        {
            Console.WriteLine("Usage: taskpilot move <id> <Backlog|InProgress|Review|Done>");
            return 1;
        }

        var id = args[0];
        if (!Enum.TryParse<TaskItemStatus>(args[1], true, out var targetStatus))
        {
            Console.ForegroundColor = ConsoleColor.Red;
            Console.WriteLine($"[Error] Invalid status '{args[1]}'. Expected: Backlog, InProgress, Review, or Done.");
            Console.ResetColor();
            return 1;
        }

        var updated = await service.MoveStatusAsync(id, targetStatus);
        Console.ForegroundColor = ConsoleColor.Green;
        Console.WriteLine($"✓ Task [{updated.Id}] moved to {updated.Status}.");
        Console.ResetColor();
        return 0;
    }

    private static async Task<int> HandleDeleteAsync(ITaskService service, string[] args)
    {
        if (args.Length < 1)
        {
            Console.WriteLine("Usage: taskpilot delete <id>");
            return 1;
        }

        var deleted = await service.DeleteTaskAsync(args[0]);
        if (deleted)
        {
            Console.ForegroundColor = ConsoleColor.Green;
            Console.WriteLine($"✓ Task [{args[0]}] deleted.");
        }
        else
        {
            Console.ForegroundColor = ConsoleColor.Yellow;
            Console.WriteLine($"[Warning] Task [{args[0]}] not found.");
        }
        Console.ResetColor();
        return 0;
    }

    private static async Task<int> HandleSummaryAsync(ITaskService service)
    {
        var metrics = await service.GetSummaryMetricsAsync();

        Console.ForegroundColor = ConsoleColor.Cyan;
        Console.WriteLine("\n=== TASKPILOT WORKFLOW SUMMARY ===");
        Console.ResetColor();
        Console.WriteLine($"Total Tasks:       {metrics.TotalTasks}");
        Console.WriteLine($"Completion Rate:   {metrics.CompletionRate:P1}");
        if (metrics.OverdueTasks > 0)
        {
            Console.ForegroundColor = ConsoleColor.Red;
            Console.WriteLine($"Overdue Tasks:     {metrics.OverdueTasks}");
            Console.ResetColor();
        }
        else
        {
            Console.WriteLine($"Overdue Tasks:     0");
        }

        Console.WriteLine("\nStatus Breakdown:");
        foreach (var (st, count) in metrics.StatusBreakdown)
        {
            SetStatusColor(st);
            Console.WriteLine($"  * {st,-12}: {count}");
            Console.ResetColor();
        }

        Console.WriteLine("\nPriority Breakdown:");
        foreach (var (pr, count) in metrics.PriorityBreakdown)
        {
            SetPriorityColor(pr);
            Console.WriteLine($"  * {pr,-12}: {count}");
            Console.ResetColor();
        }
        Console.WriteLine("==================================\n");

        return 0;
    }

    private static async Task<int> HandleSeedAsync(ITaskService service)
    {
        Console.WriteLine("Seeding sample workflow tasks...");
        await service.CreateTaskAsync("Design API Contracts", "Draft OpenAPI / Protobuf specs for auth", TaskPriority.High, DateTime.UtcNow.AddDays(2), new[] { "architecture", "api" });
        await service.CreateTaskAsync("Setup CI/CD Pipeline", "GitHub Actions workflow for .NET build and test", TaskPriority.Critical, DateTime.UtcNow.AddDays(-1), new[] { "devops", "ci" });
        await service.CreateTaskAsync("Implement Health Checks", "Add /healthz and /ready endpoints", TaskPriority.Medium, DateTime.UtcNow.AddDays(4), new[] { "backend" });
        var task4 = await service.CreateTaskAsync("Database Migration Script", "Create idempotent SQL schema scripts", TaskPriority.High, DateTime.UtcNow.AddDays(1), new[] { "database" });
        await service.MoveStatusAsync(task4.Id, TaskItemStatus.InProgress);

        Console.ForegroundColor = ConsoleColor.Green;
        Console.WriteLine("✓ Sample tasks seeded successfully. Run 'taskpilot list' or 'taskpilot summary'.");
        Console.ResetColor();
        return 0;
    }

    private static void SetStatusColor(TaskItemStatus status)
    {
        switch (status)
        {
            case TaskItemStatus.Backlog: Console.ForegroundColor = ConsoleColor.DarkGray; break;
            case TaskItemStatus.InProgress: Console.ForegroundColor = ConsoleColor.Cyan; break;
            case TaskItemStatus.Review: Console.ForegroundColor = ConsoleColor.Yellow; break;
            case TaskItemStatus.Done: Console.ForegroundColor = ConsoleColor.Green; break;
        }
    }

    private static void SetPriorityColor(TaskPriority priority)
    {
        switch (priority)
        {
            case TaskPriority.Low: Console.ForegroundColor = ConsoleColor.Gray; break;
            case TaskPriority.Medium: Console.ForegroundColor = ConsoleColor.Blue; break;
            case TaskPriority.High: Console.ForegroundColor = ConsoleColor.Magenta; break;
            case TaskPriority.Critical: Console.ForegroundColor = ConsoleColor.Red; break;
        }
    }

    private static void PrintBanner()
    {
        Console.ForegroundColor = ConsoleColor.Cyan;
        Console.WriteLine(@"
  _____         _    ____  _ _       _   
 |_   _|_ _ ___| | _|  _ \(_) | ___ | |_ 
   | |/ _` / __| |/ / |_) | | |/ _ \| __|
   | | (_| \__ \   <|  __/| | | (_) | |_ 
   |_|\__,_|___/_|\_\_|   |_|_|\___/ \__|
   Standalone Enterprise Task & Workflow Manager
");
        Console.ResetColor();
    }

    private static void PrintUsage()
    {
        Console.WriteLine("Usage:");
        Console.WriteLine("  taskpilot add \"<title>\" [--desc \"<description>\"] [--priority Low|Medium|High|Critical] [--due YYYY-MM-DD] [--tags t1,t2]");
        Console.WriteLine("  taskpilot list [--status Backlog|InProgress|Review|Done] [--priority ...] [--tag ...] [--overdue]");
        Console.WriteLine("  taskpilot move <id> <Backlog|InProgress|Review|Done>");
        Console.WriteLine("  taskpilot summary");
        Console.WriteLine("  taskpilot delete <id>");
        Console.WriteLine("  taskpilot seed");
    }
}

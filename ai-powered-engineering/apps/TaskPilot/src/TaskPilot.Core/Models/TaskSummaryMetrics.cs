namespace TaskPilot.Core.Models;

public class TaskSummaryMetrics
{
    public int TotalTasks { get; set; }
    public Dictionary<TaskItemStatus, int> StatusBreakdown { get; set; } = new();
    public Dictionary<TaskPriority, int> PriorityBreakdown { get; set; } = new();
    public int OverdueTasks { get; set; }
    public double CompletionRate { get; set; }
}

using TaskPilot.Core.Models;

namespace TaskPilot.Core.Interfaces;

public interface ITaskService
{
    Task<TaskItem> CreateTaskAsync(
        string title,
        string description = "",
        TaskPriority priority = TaskPriority.Medium,
        DateTime? dueDate = null,
        IEnumerable<string>? tags = null,
        CancellationToken ct = default);

    Task<TaskItem> MoveStatusAsync(string id, TaskItemStatus newStatus, CancellationToken ct = default);

    Task<IReadOnlyList<TaskItem>> ListTasksAsync(
        TaskItemStatus? status = null,
        TaskPriority? priority = null,
        string? tag = null,
        bool overdueOnly = false,
        CancellationToken ct = default);

    Task<TaskSummaryMetrics> GetSummaryMetricsAsync(CancellationToken ct = default);
    Task<bool> DeleteTaskAsync(string id, CancellationToken ct = default);
}

using TaskPilot.Core.Interfaces;
using TaskPilot.Core.Models;

namespace TaskPilot.Services;

public class TaskService : ITaskService
{
    private readonly ITaskRepository _repository;

    public TaskService(ITaskRepository repository)
    {
        _repository = repository;
    }

    public async Task<TaskItem> CreateTaskAsync(
        string title,
        string description = "",
        TaskPriority priority = TaskPriority.Medium,
        DateTime? dueDate = null,
        IEnumerable<string>? tags = null,
        CancellationToken ct = default)
    {
        var cleanedTags = (tags ?? Enumerable.Empty<string>())
            .Select(t => t.Trim().ToLowerInvariant())
            .Where(t => !string.IsNullOrWhiteSpace(t))
            .Distinct()
            .ToList();

        var item = new TaskItem
        {
            Title = title.Trim(),
            Description = description.Trim(),
            Priority = priority,
            Status = TaskItemStatus.Backlog,
            DueDateUtc = dueDate,
            Tags = cleanedTags,
            CreatedAtUtc = DateTime.UtcNow
        };

        item.Validate();
        return await _repository.AddAsync(item, ct);
    }

    public async Task<TaskItem> MoveStatusAsync(string id, TaskItemStatus newStatus, CancellationToken ct = default)
    {
        var item = await _repository.GetByIdAsync(id, ct);
        if (item == null)
        {
            throw new KeyNotFoundException($"Task with ID '{id}' was not found.");
        }

        item.TransitionTo(newStatus);
        return await _repository.UpdateAsync(item, ct);
    }

    public async Task<IReadOnlyList<TaskItem>> ListTasksAsync(
        TaskItemStatus? status = null,
        TaskPriority? priority = null,
        string? tag = null,
        bool overdueOnly = false,
        CancellationToken ct = default)
    {
        var all = await _repository.GetAllAsync(ct);
        var query = all.AsEnumerable();

        if (status.HasValue)
        {
            query = query.Where(t => t.Status == status.Value);
        }

        if (priority.HasValue)
        {
            query = query.Where(t => t.Priority == priority.Value);
        }

        if (!string.IsNullOrWhiteSpace(tag))
        {
            var targetTag = tag.Trim().ToLowerInvariant();
            query = query.Where(t => t.Tags.Contains(targetTag));
        }

        if (overdueOnly)
        {
            query = query.Where(t => t.IsOverdue());
        }

        return query.ToList();
    }

    public async Task<TaskSummaryMetrics> GetSummaryMetricsAsync(CancellationToken ct = default)
    {
        var all = await _repository.GetAllAsync(ct);

        var statusMap = Enum.GetValues<TaskItemStatus>().ToDictionary(s => s, s => 0);
        foreach (var group in all.GroupBy(t => t.Status))
        {
            statusMap[group.Key] = group.Count();
        }

        var priorityMap = Enum.GetValues<TaskPriority>().ToDictionary(p => p, p => 0);
        foreach (var group in all.GroupBy(t => t.Priority))
        {
            priorityMap[group.Key] = group.Count();
        }

        var overdue = all.Count(t => t.IsOverdue());
        var done = statusMap[TaskItemStatus.Done];
        var rate = all.Count > 0 ? (double)done / all.Count : 0.0;

        return new TaskSummaryMetrics
        {
            TotalTasks = all.Count,
            StatusBreakdown = statusMap,
            PriorityBreakdown = priorityMap,
            OverdueTasks = overdue,
            CompletionRate = rate
        };
    }

    public async Task<bool> DeleteTaskAsync(string id, CancellationToken ct = default)
    {
        return await _repository.DeleteAsync(id, ct);
    }
}

namespace TaskPilot.Core.Models;

public class TaskItem
{
    public string Id { get; set; } = Guid.NewGuid().ToString("N")[..8];
    public string Title { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public TaskPriority Priority { get; set; } = TaskPriority.Medium;
    public TaskItemStatus Status { get; set; } = TaskItemStatus.Backlog;
    public DateTime CreatedAtUtc { get; set; } = DateTime.UtcNow;
    public DateTime? DueDateUtc { get; set; }
    public DateTime? CompletedAtUtc { get; set; }
    public List<string> Tags { get; set; } = new();

    public void Validate()
    {
        if (string.IsNullOrWhiteSpace(Title))
        {
            throw new ArgumentException("Task title cannot be null or whitespace.", nameof(Title));
        }

        if (Title.Length > 200)
        {
            throw new ArgumentException("Task title cannot exceed 200 characters.", nameof(Title));
        }
    }

    public bool CanTransitionTo(TaskItemStatus newStatus, out string? reason)
    {
        reason = null;

        if (Status == newStatus)
        {
            return true;
        }

        // Domain invariant: Tasks in Backlog cannot jump directly to Done without being in progress or review
        if (Status == TaskItemStatus.Backlog && newStatus == TaskItemStatus.Done)
        {
            reason = "Task cannot jump directly from Backlog to Done. Move to InProgress or Review first.";
            return false;
        }

        return true;
    }

    public void TransitionTo(TaskItemStatus newStatus)
    {
        if (!CanTransitionTo(newStatus, out var reason))
        {
            throw new InvalidOperationException(reason);
        }

        Status = newStatus;

        if (newStatus == TaskItemStatus.Done)
        {
            CompletedAtUtc = DateTime.UtcNow;
        }
        else
        {
            CompletedAtUtc = null;
        }
    }

    public bool IsOverdue()
    {
        if (Status == TaskItemStatus.Done || !DueDateUtc.HasValue)
        {
            return false;
        }

        return DateTime.UtcNow > DueDateUtc.Value;
    }
}

using TaskPilot.Core.Models;
using Xunit;

namespace TaskPilot.Tests;

public class TaskItemDomainTests
{
    [Fact]
    public void Validate_EmptyTitle_ThrowsArgumentException()
    {
        var task = new TaskItem { Title = "   " };

        var ex = Assert.Throws<ArgumentException>(() => task.Validate());
        Assert.Contains("cannot be null or whitespace", ex.Message);
    }

    [Fact]
    public void Validate_TitleExceedsLimit_ThrowsArgumentException()
    {
        var task = new TaskItem { Title = new string('A', 201) };

        var ex = Assert.Throws<ArgumentException>(() => task.Validate());
        Assert.Contains("cannot exceed 200 characters", ex.Message);
    }

    [Fact]
    public void TransitionTo_DirectBacklogToDone_ThrowsInvalidOperationException()
    {
        var task = new TaskItem
        {
            Title = "Implement Core Feature",
            Status = TaskItemStatus.Backlog
        };

        var ex = Assert.Throws<InvalidOperationException>(() => task.TransitionTo(TaskItemStatus.Done));
        Assert.Contains("cannot jump directly from Backlog to Done", ex.Message);
    }

    [Fact]
    public void TransitionTo_ValidFlow_SetsStatusAndCompletedTimestamp()
    {
        var task = new TaskItem
        {
            Title = "Write Unit Tests",
            Status = TaskItemStatus.Backlog
        };

        // 1. Move to InProgress
        task.TransitionTo(TaskItemStatus.InProgress);
        Assert.Equal(TaskItemStatus.InProgress, task.Status);
        Assert.Null(task.CompletedAtUtc);

        // 2. Move to Review
        task.TransitionTo(TaskItemStatus.Review);
        Assert.Equal(TaskItemStatus.Review, task.Status);
        Assert.Null(task.CompletedAtUtc);

        // 3. Move to Done
        task.TransitionTo(TaskItemStatus.Done);
        Assert.Equal(TaskItemStatus.Done, task.Status);
        Assert.NotNull(task.CompletedAtUtc);

        // 4. Reopen task
        task.TransitionTo(TaskItemStatus.InProgress);
        Assert.Equal(TaskItemStatus.InProgress, task.Status);
        Assert.Null(task.CompletedAtUtc);
    }

    [Fact]
    public void IsOverdue_PastDueDateAndNotDone_ReturnsTrue()
    {
        var task = new TaskItem
        {
            Title = "Overdue Bug Fix",
            Status = TaskItemStatus.InProgress,
            DueDateUtc = DateTime.UtcNow.AddDays(-2)
        };

        Assert.True(task.IsOverdue());
    }

    [Fact]
    public void IsOverdue_CompletedTask_ReturnsFalseEvenIfPastDue()
    {
        var task = new TaskItem
        {
            Title = "Resolved Bug Fix",
            Status = TaskItemStatus.Done,
            DueDateUtc = DateTime.UtcNow.AddDays(-2)
        };

        Assert.False(task.IsOverdue());
    }
}

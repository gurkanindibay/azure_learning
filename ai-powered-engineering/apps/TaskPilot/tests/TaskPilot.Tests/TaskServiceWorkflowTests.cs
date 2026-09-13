using TaskPilot.Core.Models;
using TaskPilot.Infrastructure;
using TaskPilot.Services;
using Xunit;

namespace TaskPilot.Tests;

public class TaskServiceWorkflowTests : IDisposable
{
    private readonly string _testFilePath;
    private readonly TaskService _service;

    public TaskServiceWorkflowTests()
    {
        _testFilePath = Path.Combine(Path.GetTempPath(), $"taskpilot_service_test_{Guid.NewGuid():N}.json");
        var repo = new JsonTaskRepository(_testFilePath);
        _service = new TaskService(repo);
    }

    public void Dispose()
    {
        if (File.Exists(_testFilePath))
        {
            try { File.Delete(_testFilePath); } catch { /* ignore */ }
        }
    }

    [Fact]
    public async Task CreateTaskAsync_NormalizesTagsAndInitializesStatus()
    {
        var task = await _service.CreateTaskAsync(
            "Clean Code Base",
            "Refactor legacy controllers",
            TaskPriority.High,
            DateTime.UtcNow.AddDays(3),
            new[] { "  REFACTOR  ", "backend", "Backend" });

        Assert.Equal(TaskItemStatus.Backlog, task.Status);
        Assert.Equal(2, task.Tags.Count); // Deduplicated and trimmed
        Assert.Contains("refactor", task.Tags);
        Assert.Contains("backend", task.Tags);
    }

    [Fact]
    public async Task MoveStatusAsync_ValidatesTransitions()
    {
        var task = await _service.CreateTaskAsync("Test Transitions");

        // Valid transition: Backlog -> InProgress
        var inProgress = await _service.MoveStatusAsync(task.Id, TaskItemStatus.InProgress);
        Assert.Equal(TaskItemStatus.InProgress, inProgress.Status);

        // Valid transition: InProgress -> Done
        var done = await _service.MoveStatusAsync(task.Id, TaskItemStatus.Done);
        Assert.Equal(TaskItemStatus.Done, done.Status);
        Assert.NotNull(done.CompletedAtUtc);
    }

    [Fact]
    public async Task ListTasksAsync_FiltersByStatusAndPriority()
    {
        await _service.CreateTaskAsync("Task 1", priority: TaskPriority.Low);
        var t2 = await _service.CreateTaskAsync("Task 2", priority: TaskPriority.Critical);
        await _service.MoveStatusAsync(t2.Id, TaskItemStatus.InProgress);

        var criticalTasks = await _service.ListTasksAsync(priority: TaskPriority.Critical);
        Assert.Single(criticalTasks);
        Assert.Equal("Task 2", criticalTasks[0].Title);

        var backlogTasks = await _service.ListTasksAsync(status: TaskItemStatus.Backlog);
        Assert.Single(backlogTasks);
        Assert.Equal("Task 1", backlogTasks[0].Title);
    }

    [Fact]
    public async Task GetSummaryMetricsAsync_CalculatesBreakdownsCorrectly()
    {
        var t1 = await _service.CreateTaskAsync("Task 1", priority: TaskPriority.Low);
        var t2 = await _service.CreateTaskAsync("Task 2", priority: TaskPriority.High, dueDate: DateTime.UtcNow.AddDays(-1));
        var t3 = await _service.CreateTaskAsync("Task 3", priority: TaskPriority.Medium);

        await _service.MoveStatusAsync(t1.Id, TaskItemStatus.InProgress);
        await _service.MoveStatusAsync(t1.Id, TaskItemStatus.Done);

        var metrics = await _service.GetSummaryMetricsAsync();

        Assert.Equal(3, metrics.TotalTasks);
        Assert.Equal(1, metrics.StatusBreakdown[TaskItemStatus.Done]);
        Assert.Equal(2, metrics.StatusBreakdown[TaskItemStatus.Backlog]);
        Assert.Equal(1, metrics.OverdueTasks); // t2 is overdue
        Assert.Equal(1.0 / 3.0, metrics.CompletionRate, precision: 2);
    }
}

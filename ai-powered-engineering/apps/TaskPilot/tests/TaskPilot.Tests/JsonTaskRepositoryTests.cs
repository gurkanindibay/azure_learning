using TaskPilot.Core.Models;
using TaskPilot.Infrastructure;
using Xunit;

namespace TaskPilot.Tests;

public class JsonTaskRepositoryTests : IDisposable
{
    private readonly string _testFilePath;

    public JsonTaskRepositoryTests()
    {
        _testFilePath = Path.Combine(Path.GetTempPath(), $"taskpilot_test_{Guid.NewGuid():N}.json");
    }

    public void Dispose()
    {
        if (File.Exists(_testFilePath))
        {
            try { File.Delete(_testFilePath); } catch { /* ignore */ }
        }
    }

    [Fact]
    public async Task AddAndGetByIdAsync_PersistsAndLoadsCorrectly()
    {
        var repo = new JsonTaskRepository(_testFilePath);

        var task = new TaskItem
        {
            Title = "Database Migration",
            Priority = TaskPriority.Critical,
            Tags = new() { "infra", "sql" }
        };

        var saved = await repo.AddAsync(task);
        Assert.NotNull(saved.Id);

        // Load through a new instance pointing to the same file
        var repo2 = new JsonTaskRepository(_testFilePath);
        var loaded = await repo2.GetByIdAsync(saved.Id);

        Assert.NotNull(loaded);
        Assert.Equal("Database Migration", loaded.Title);
        Assert.Equal(TaskPriority.Critical, loaded.Priority);
        Assert.Equal(2, loaded.Tags.Count);
    }

    [Fact]
    public async Task UpdateAsync_ModifiesItemInFile()
    {
        var repo = new JsonTaskRepository(_testFilePath);
        var task = await repo.AddAsync(new TaskItem { Title = "Initial Title" });

        task.Title = "Updated Title";
        task.Priority = TaskPriority.High;
        await repo.UpdateAsync(task);

        var repo2 = new JsonTaskRepository(_testFilePath);
        var updated = await repo2.GetByIdAsync(task.Id);

        Assert.NotNull(updated);
        Assert.Equal("Updated Title", updated.Title);
        Assert.Equal(TaskPriority.High, updated.Priority);
    }

    [Fact]
    public async Task DeleteAsync_RemovesItemFromPersistence()
    {
        var repo = new JsonTaskRepository(_testFilePath);
        var task = await repo.AddAsync(new TaskItem { Title = "Ephemeral Task" });

        var deleted = await repo.DeleteAsync(task.Id);
        Assert.True(deleted);

        var repo2 = new JsonTaskRepository(_testFilePath);
        var missing = await repo2.GetByIdAsync(task.Id);
        Assert.Null(missing);
    }
}

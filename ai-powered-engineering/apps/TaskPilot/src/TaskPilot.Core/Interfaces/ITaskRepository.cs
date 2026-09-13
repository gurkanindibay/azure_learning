using TaskPilot.Core.Models;

namespace TaskPilot.Core.Interfaces;

public interface ITaskRepository
{
    Task<IReadOnlyList<TaskItem>> GetAllAsync(CancellationToken ct = default);
    Task<TaskItem?> GetByIdAsync(string id, CancellationToken ct = default);
    Task<TaskItem> AddAsync(TaskItem item, CancellationToken ct = default);
    Task<TaskItem> UpdateAsync(TaskItem item, CancellationToken ct = default);
    Task<bool> DeleteAsync(string id, CancellationToken ct = default);
}

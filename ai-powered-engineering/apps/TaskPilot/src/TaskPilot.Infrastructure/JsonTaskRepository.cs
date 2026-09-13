using System.Text.Json;
using System.Text.Json.Serialization;
using TaskPilot.Core.Interfaces;
using TaskPilot.Core.Models;

namespace TaskPilot.Infrastructure;

public class JsonTaskRepository : ITaskRepository
{
    private readonly string _filePath;
    private readonly SemaphoreSlim _lock = new(1, 1);
    private readonly Dictionary<string, TaskItem> _cache = new(StringComparer.OrdinalIgnoreCase);
    private bool _isLoaded = false;

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        WriteIndented = true,
        Converters = { new JsonStringEnumConverter() }
    };

    public JsonTaskRepository(string? filePath = null)
    {
        if (string.IsNullOrWhiteSpace(filePath))
        {
            var home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
            var dir = Path.Combine(home, ".taskpilot");
            _filePath = Path.Combine(dir, "tasks.json");
        }
        else
        {
            _filePath = filePath;
        }
    }

    private async Task EnsureLoadedAsync(CancellationToken ct)
    {
        if (_isLoaded) return;

        await _lock.WaitAsync(ct);
        try
        {
            if (_isLoaded) return;

            if (File.Exists(_filePath))
            {
                var json = await File.ReadAllTextAsync(_filePath, ct);
                var items = JsonSerializer.Deserialize<List<TaskItem>>(json, JsonOptions) ?? new();
                _cache.Clear();
                foreach (var item in items)
                {
                    _cache[item.Id] = item;
                }
            }
            _isLoaded = true;
        }
        finally
        {
            _lock.Release();
        }
    }

    private async Task PersistAsync(CancellationToken ct)
    {
        var dir = Path.GetDirectoryName(_filePath);
        if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir))
        {
            Directory.CreateDirectory(dir);
        }

        var items = _cache.Values.ToList();
        var json = JsonSerializer.Serialize(items, JsonOptions);

        var tempPath = _filePath + ".tmp";
        await File.WriteAllTextAsync(tempPath, json, ct);
        File.Move(tempPath, _filePath, overwrite: true);
    }

    public async Task<IReadOnlyList<TaskItem>> GetAllAsync(CancellationToken ct = default)
    {
        await EnsureLoadedAsync(ct);

        await _lock.WaitAsync(ct);
        try
        {
            return _cache.Values.OrderByDescending(t => t.Priority).ThenBy(t => t.DueDateUtc).ToList();
        }
        finally
        {
            _lock.Release();
        }
    }

    public async Task<TaskItem?> GetByIdAsync(string id, CancellationToken ct = default)
    {
        await EnsureLoadedAsync(ct);

        await _lock.WaitAsync(ct);
        try
        {
            return _cache.TryGetValue(id, out var item) ? item : null;
        }
        finally
        {
            _lock.Release();
        }
    }

    public async Task<TaskItem> AddAsync(TaskItem item, CancellationToken ct = default)
    {
        item.Validate();
        await EnsureLoadedAsync(ct);

        await _lock.WaitAsync(ct);
        try
        {
            _cache[item.Id] = item;
            await PersistAsync(ct);
            return item;
        }
        finally
        {
            _lock.Release();
        }
    }

    public async Task<TaskItem> UpdateAsync(TaskItem item, CancellationToken ct = default)
    {
        item.Validate();
        await EnsureLoadedAsync(ct);

        await _lock.WaitAsync(ct);
        try
        {
            if (!_cache.ContainsKey(item.Id))
            {
                throw new KeyNotFoundException($"Task with ID '{item.Id}' was not found.");
            }

            _cache[item.Id] = item;
            await PersistAsync(ct);
            return item;
        }
        finally
        {
            _lock.Release();
        }
    }

    public async Task<bool> DeleteAsync(string id, CancellationToken ct = default)
    {
        await EnsureLoadedAsync(ct);

        await _lock.WaitAsync(ct);
        try
        {
            if (_cache.Remove(id))
            {
                await PersistAsync(ct);
                return true;
            }
            return false;
        }
        finally
        {
            _lock.Release();
        }
    }
}

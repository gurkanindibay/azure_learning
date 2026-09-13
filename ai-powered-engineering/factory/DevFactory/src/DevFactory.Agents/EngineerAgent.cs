using DevFactory.Core.Interfaces;
using DevFactory.Core.Models;

namespace DevFactory.Agents;

public class EngineerAgent : IEngineerAgent
{
    public List<ProjectSourceFile> GenerateSourceFiles(SoftwareBlueprint blueprint, string? feedback = null)
    {
        var files = new List<ProjectSourceFile>();
        var name = blueprint.SolutionName;

        // 1. Solution file
        files.Add(new ProjectSourceFile
        {
            ProjectName = "Solution",
            RelativePath = $"{name}.sln",
            Content = """
            Microsoft Visual Studio Solution File, Format Version 12.00
            # Visual Studio Version 17
            VisualStudioVersion = 17.0.31903.59
            MinimumVisualStudioVersion = 10.0.40219.1
            Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "{NAME}.Core", "src/{NAME}.Core/{NAME}.Core.csproj", "{11111111-1111-1111-1111-111111111111}"
            EndProject
            Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "{NAME}.Infrastructure", "src/{NAME}.Infrastructure/{NAME}.Infrastructure.csproj", "{22222222-2222-2222-2222-222222222222}"
            EndProject
            Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "{NAME}.Services", "src/{NAME}.Services/{NAME}.Services.csproj", "{33333333-3333-3333-3333-333333333333}"
            EndProject
            Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "{NAME}.Cli", "src/{NAME}.Cli/{NAME}.Cli.csproj", "{44444444-4444-4444-4444-444444444444}"
            EndProject
            Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "{NAME}.Tests", "tests/{NAME}.Tests/{NAME}.Tests.csproj", "{55555555-5555-5555-5555-555555555555}"
            EndProject
            Global
                GlobalSection(SolutionConfigurationPlatforms) = preSolution
                    Debug|Any CPU = Debug|Any CPU
                    Release|Any CPU = Release|Any CPU
                EndGlobalSection
                GlobalSection(ProjectConfigurationPlatforms) = postSolution
                    {11111111-1111-1111-1111-111111111111}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
                    {11111111-1111-1111-1111-111111111111}.Debug|Any CPU.Build.0 = Debug|Any CPU
                    {22222222-2222-2222-2222-222222222222}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
                    {22222222-2222-2222-2222-222222222222}.Debug|Any CPU.Build.0 = Debug|Any CPU
                    {33333333-3333-3333-3333-333333333333}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
                    {33333333-3333-3333-3333-333333333333}.Debug|Any CPU.Build.0 = Debug|Any CPU
                    {44444444-4444-4444-4444-444444444444}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
                    {44444444-4444-4444-4444-444444444444}.Debug|Any CPU.Build.0 = Debug|Any CPU
                    {55555555-5555-5555-5555-555555555555}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
                    {55555555-5555-5555-5555-555555555555}.Debug|Any CPU.Build.0 = Debug|Any CPU
                EndGlobalSection
            EndGlobal
            """.Replace("{NAME}", name)
        });

        // 2. Project csproj files
        files.Add(new ProjectSourceFile
        {
            ProjectName = $"{name}.Core",
            RelativePath = $"src/{name}.Core/{name}.Core.csproj",
            Content = """
            <Project Sdk="Microsoft.NET.Sdk">
              <PropertyGroup>
                <TargetFramework>net8.0</TargetFramework>
                <ImplicitUsings>enable</ImplicitUsings>
                <Nullable>enable</Nullable>
              </PropertyGroup>
            </Project>
            """
        });

        files.Add(new ProjectSourceFile
        {
            ProjectName = $"{name}.Infrastructure",
            RelativePath = $"src/{name}.Infrastructure/{name}.Infrastructure.csproj",
            Content = $"""
            <Project Sdk="Microsoft.NET.Sdk">
              <ItemGroup>
                <ProjectReference Include="..\{name}.Core\{name}.Core.csproj" />
              </ItemGroup>
              <PropertyGroup>
                <TargetFramework>net8.0</TargetFramework>
                <ImplicitUsings>enable</ImplicitUsings>
                <Nullable>enable</Nullable>
              </PropertyGroup>
            </Project>
            """
        });

        files.Add(new ProjectSourceFile
        {
            ProjectName = $"{name}.Services",
            RelativePath = $"src/{name}.Services/{name}.Services.csproj",
            Content = $"""
            <Project Sdk="Microsoft.NET.Sdk">
              <ItemGroup>
                <ProjectReference Include="..\{name}.Core\{name}.Core.csproj" />
              </ItemGroup>
              <PropertyGroup>
                <TargetFramework>net8.0</TargetFramework>
                <ImplicitUsings>enable</ImplicitUsings>
                <Nullable>enable</Nullable>
              </PropertyGroup>
            </Project>
            """
        });

        files.Add(new ProjectSourceFile
        {
            ProjectName = $"{name}.Cli",
            RelativePath = $"src/{name}.Cli/{name}.Cli.csproj",
            Content = $"""
            <Project Sdk="Microsoft.NET.Sdk">
              <ItemGroup>
                <ProjectReference Include="..\{name}.Core\{name}.Core.csproj" />
                <ProjectReference Include="..\{name}.Infrastructure\{name}.Infrastructure.csproj" />
                <ProjectReference Include="..\{name}.Services\{name}.Services.csproj" />
              </ItemGroup>
              <PropertyGroup>
                <OutputType>Exe</OutputType>
                <TargetFramework>net8.0</TargetFramework>
                <ImplicitUsings>enable</ImplicitUsings>
                <Nullable>enable</Nullable>
              </PropertyGroup>
            </Project>
            """
        });

        // 3. Core Models & Interfaces
        files.Add(new ProjectSourceFile
        {
            ProjectName = $"{name}.Core",
            RelativePath = $"src/{name}.Core/Models.cs",
            Content = $$"""
            namespace {{name}}.Core;

            public enum CacheTier
            {
                Memory,
                File,
                Distributed
            }

            public class CacheEntry<T>
            {
                public string Key { get; set; } = string.Empty;
                public T? Value { get; set; }
                public DateTime CreatedAtUtc { get; set; } = DateTime.UtcNow;
                public DateTime? ExpiresAtUtc { get; set; }
                public int AccessCount { get; set; } = 0;
                public CacheTier Tier { get; set; } = CacheTier.Memory;

                public bool IsExpired()
                {
                    return ExpiresAtUtc.HasValue && DateTime.UtcNow > ExpiresAtUtc.Value;
                }
            }

            public class CacheMetrics
            {
                public int TotalItems { get; set; }
                public long Hits { get; set; }
                public long Misses { get; set; }
                public double HitRatio => (Hits + Misses) > 0 ? (double)Hits / (Hits + Misses) : 0.0;
            }

            public interface ICacheStorage
            {
                Task<CacheEntry<T>?> GetAsync<T>(string key, CancellationToken ct = default);
                Task SetAsync<T>(string key, T value, TimeSpan? ttl = null, CancellationToken ct = default);
                Task<bool> RemoveAsync(string key, CancellationToken ct = default);
                Task ClearAsync(CancellationToken ct = default);
                Task<int> GetCountAsync(CancellationToken ct = default);
            }

            public interface ICacheManager
            {
                Task<T?> GetOrSetAsync<T>(string key, Func<Task<T>> factory, TimeSpan? ttl = null, CancellationToken ct = default);
                Task<CacheMetrics> GetMetricsAsync(CancellationToken ct = default);
            }
            """
        });

        // 4. Infrastructure Storage
        files.Add(new ProjectSourceFile
        {
            ProjectName = $"{name}.Infrastructure",
            RelativePath = $"src/{name}.Infrastructure/MemoryCacheStorage.cs",
            Content = $$"""
            using System.Collections.Concurrent;
            using {{name}}.Core;

            namespace {{name}}.Infrastructure;

            public class MemoryCacheStorage : ICacheStorage
            {
                private readonly ConcurrentDictionary<string, object> _store = new(StringComparer.OrdinalIgnoreCase);

                public Task<CacheEntry<T>?> GetAsync<T>(string key, CancellationToken ct = default)
                {
                    if (_store.TryGetValue(key, out var raw) && raw is CacheEntry<T> entry)
                    {
                        if (entry.IsExpired())
                        {
                            _store.TryRemove(key, out _);
                            return Task.FromResult<CacheEntry<T>?>(null);
                        }

                        entry.AccessCount++;
                        return Task.FromResult<CacheEntry<T>?>(entry);
                    }

                    return Task.FromResult<CacheEntry<T>?>(null);
                }

                public Task SetAsync<T>(string key, T value, TimeSpan? ttl = null, CancellationToken ct = default)
                {
                    if (string.IsNullOrWhiteSpace(key))
                    {
                        throw new ArgumentException("Cache key cannot be null or whitespace.", nameof(key));
                    }

                    var entry = new CacheEntry<T>
                    {
                        Key = key,
                        Value = value,
                        ExpiresAtUtc = ttl.HasValue ? DateTime.UtcNow.Add(ttl.Value) : null
                    };

                    _store[key] = entry;
                    return Task.CompletedTask;
                }

                public Task<bool> RemoveAsync(string key, CancellationToken ct = default)
                {
                    return Task.FromResult(_store.TryRemove(key, out _));
                }

                public Task ClearAsync(CancellationToken ct = default)
                {
                    _store.Clear();
                    return Task.CompletedTask;
                }

                public Task<int> GetCountAsync(CancellationToken ct = default)
                {
                    // Clean up any expired keys on count query
                    foreach (var pair in _store)
                    {
                        if (pair.Value is CacheEntry<object> e && e.IsExpired())
                        {
                            _store.TryRemove(pair.Key, out _);
                        }
                    }

                    return Task.FromResult(_store.Count);
                }
            }
            """
        });

        // 5. Services: CacheManager
        files.Add(new ProjectSourceFile
        {
            ProjectName = $"{name}.Services",
            RelativePath = $"src/{name}.Services/CacheManager.cs",
            Content = $$"""
            using {{name}}.Core;

            namespace {{name}}.Services;

            public class CacheManager : ICacheManager
            {
                private readonly ICacheStorage _storage;
                private long _hits;
                private long _misses;

                public CacheManager(ICacheStorage storage)
                {
                    _storage = storage;
                }

                public async Task<T?> GetOrSetAsync<T>(string key, Func<Task<T>> factory, TimeSpan? ttl = null, CancellationToken ct = default)
                {
                    var existing = await _storage.GetAsync<T>(key, ct);
                    if (existing != null)
                    {
                        Interlocked.Increment(ref _hits);
                        return existing.Value;
                    }

                    Interlocked.Increment(ref _misses);
                    var freshValue = await factory();
                    await _storage.SetAsync(key, freshValue, ttl, ct);
                    return freshValue;
                }

                public async Task<CacheMetrics> GetMetricsAsync(CancellationToken ct = default)
                {
                    var count = await _storage.GetCountAsync(ct);
                    return new CacheMetrics
                    {
                        TotalItems = count,
                        Hits = Interlocked.Read(ref _hits),
                        Misses = Interlocked.Read(ref _misses)
                    };
                }
            }
            """
        });

        // 6. CLI Program
        files.Add(new ProjectSourceFile
        {
            ProjectName = $"{name}.Cli",
            RelativePath = $"src/{name}.Cli/Program.cs",
            Content = $$"""
            using System.Text;
            using {{name}}.Core;
            using {{name}}.Infrastructure;
            using {{name}}.Services;

            namespace {{name}}.Cli;

            public class Program
            {
                public static async Task<int> Main(string[] args)
                {
                    Console.OutputEncoding = Encoding.UTF8;
                    Console.ForegroundColor = ConsoleColor.Cyan;
                    Console.WriteLine(@"
              ___           _           ___ _     _      _     _ 
             / __|__ _  __ | |_   ___  / __| |_  (_) ___| | __| |
            | (__/ _` |/ _|| ' \ / -_) \__ \ ' \ | |/ -_) |/ _` |
             \___\__,_|\__||_||_|\___| |___/_||_||_|\___|_|\__,_|
                 High-Performance Standalone Cache Microservice
            ");
                    Console.ResetColor();

                    var storage = new MemoryCacheStorage();
                    var manager = new CacheManager(storage);

                    Console.WriteLine("Executing demonstration cache lifecycle...");

                    // 1. Set key
                    await storage.SetAsync("user:1001", "Gurkan Indibay", TimeSpan.FromMinutes(10));
                    Console.WriteLine("✓ Cached 'user:1001' with 10 min TTL.");

                    // 2. Query key through CacheManager
                    var val = await manager.GetOrSetAsync("user:1001", () => Task.FromResult("Fallback Value"));
                    Console.WriteLine($"✓ Retrieved cached item: '{val}'");

                    // 3. Query cache miss through CacheManager
                    var val2 = await manager.GetOrSetAsync("user:1002", () => Task.FromResult("Fresh Value from DB"));
                    Console.WriteLine($"✓ Handled cache miss: computed '{val2}'");

                    // 4. Metrics
                    var metrics = await manager.GetMetricsAsync();
                    Console.WriteLine($"\nCache Metrics: Total Items={metrics.TotalItems}, Hits={metrics.Hits}, Misses={metrics.Misses}, Hit Ratio={metrics.HitRatio:P0}");

                    Console.ForegroundColor = ConsoleColor.Green;
                    Console.WriteLine("\n✓ Standalone application executed successfully.");
                    Console.ResetColor();
                    return 0;
                }
            }
            """
        });

        return files;
    }
}

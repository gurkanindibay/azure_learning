using System.Text;
using CacheShield.Core;
using CacheShield.Infrastructure;
using CacheShield.Services;

namespace CacheShield.Cli;

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
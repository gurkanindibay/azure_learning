using DevFactory.Core.Interfaces;
using DevFactory.Core.Models;

namespace DevFactory.Agents;

public class QAAgent : IQAAgent
{
    public List<ProjectSourceFile> GenerateTestFiles(SoftwareBlueprint blueprint)
    {
        var files = new List<ProjectSourceFile>();
        var name = blueprint.SolutionName;

        // 1. Test csproj
        files.Add(new ProjectSourceFile
        {
            ProjectName = $"{name}.Tests",
            RelativePath = $"tests/{name}.Tests/{name}.Tests.csproj",
            Content = $"""
            <Project Sdk="Microsoft.NET.Sdk">
              <PropertyGroup>
                <TargetFramework>net8.0</TargetFramework>
                <ImplicitUsings>enable</ImplicitUsings>
                <Nullable>enable</Nullable>
                <IsPackable>false</IsPackable>
                <IsTestProject>true</IsTestProject>
              </PropertyGroup>

              <ItemGroup>
                <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.8.0" />
                <PackageReference Include="xunit" Version="2.5.3" />
                <PackageReference Include="xunit.runner.visualstudio" Version="2.5.3" />
              </ItemGroup>

              <ItemGroup>
                <ProjectReference Include="..\..\src\{name}.Core\{name}.Core.csproj" />
                <ProjectReference Include="..\..\src\{name}.Infrastructure\{name}.Infrastructure.csproj" />
                <ProjectReference Include="..\..\src\{name}.Services\{name}.Services.csproj" />
              </ItemGroup>
            </Project>
            """
        });

        // 2. Storage tests
        files.Add(new ProjectSourceFile
        {
            ProjectName = $"{name}.Tests",
            RelativePath = $"tests/{name}.Tests/MemoryCacheStorageTests.cs",
            Content = $$"""
            using {{name}}.Core;
            using {{name}}.Infrastructure;
            using Xunit;

            namespace {{name}}.Tests;

            public class MemoryCacheStorageTests
            {
                [Fact]
                public async Task SetAndGetAsync_ReturnsValidEntry()
                {
                    var storage = new MemoryCacheStorage();
                    await storage.SetAsync("k1", "Hello World");

                    var result = await storage.GetAsync<string>("k1");

                    Assert.NotNull(result);
                    Assert.Equal("Hello World", result.Value);
                    Assert.Equal(1, result.AccessCount);
                }

                [Fact]
                public async Task GetAsync_ExpiredEntry_ReturnsNullAndEvicts()
                {
                    var storage = new MemoryCacheStorage();
                    // Set with negative TTL so it is immediately expired
                    await storage.SetAsync("expired", 123, TimeSpan.FromMilliseconds(-100));

                    var result = await storage.GetAsync<int>("expired");

                    Assert.Null(result);
                }

                [Fact]
                public async Task RemoveAsync_RemovesKeyFromStorage()
                {
                    var storage = new MemoryCacheStorage();
                    await storage.SetAsync("del", 456);

                    var removed = await storage.RemoveAsync("del");
                    var result = await storage.GetAsync<int>("del");

                    Assert.True(removed);
                    Assert.Null(result);
                }
            }
            """
        });

        // 3. Manager tests
        files.Add(new ProjectSourceFile
        {
            ProjectName = $"{name}.Tests",
            RelativePath = $"tests/{name}.Tests/CacheManagerTests.cs",
            Content = $$"""
            using {{name}}.Core;
            using {{name}}.Infrastructure;
            using {{name}}.Services;
            using Xunit;

            namespace {{name}}.Tests;

            public class CacheManagerTests
            {
                [Fact]
                public async Task GetOrSetAsync_CalculatesHitsAndMisses()
                {
                    var storage = new MemoryCacheStorage();
                    var manager = new CacheManager(storage);

                    // First call: Miss
                    var v1 = await manager.GetOrSetAsync("item1", () => Task.FromResult("Value 1"));
                    Assert.Equal("Value 1", v1);

                    // Second call: Hit
                    var v2 = await manager.GetOrSetAsync("item1", () => Task.FromResult("New Computed"));
                    Assert.Equal("Value 1", v2); // Retained cached value

                    var metrics = await manager.GetMetricsAsync();
                    Assert.Equal(1, metrics.Hits);
                    Assert.Equal(1, metrics.Misses);
                    Assert.Equal(0.5, metrics.HitRatio, precision: 2);
                }
            }
            """
        });

        return files;
    }
}

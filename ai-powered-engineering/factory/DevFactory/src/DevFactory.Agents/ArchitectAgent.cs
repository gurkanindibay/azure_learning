using DevFactory.Core.Interfaces;
using DevFactory.Core.Models;

namespace DevFactory.Agents;

public class ArchitectAgent : IArchitectAgent
{
    public SoftwareBlueprint DesignBlueprint(SoftwareSpec spec)
    {
        var appName = string.IsNullOrWhiteSpace(spec.AppName) ? "StandaloneApp" : spec.AppName;

        var blueprint = new SoftwareBlueprint
        {
            SolutionName = appName,
            Description = spec.Description,
            Projects = new List<BlueprintProject>
            {
                new()
                {
                    Name = $"{appName}.Core",
                    ProjectType = "classlib",
                    Dependencies = new()
                },
                new()
                {
                    Name = $"{appName}.Infrastructure",
                    ProjectType = "classlib",
                    Dependencies = new() { $"{appName}.Core" }
                },
                new()
                {
                    Name = $"{appName}.Services",
                    ProjectType = "classlib",
                    Dependencies = new() { $"{appName}.Core" }
                },
                new()
                {
                    Name = $"{appName}.Cli",
                    ProjectType = "console",
                    Dependencies = new() { $"{appName}.Core", $"{appName}.Infrastructure", $"{appName}.Services" }
                },
                new()
                {
                    Name = $"{appName}.Tests",
                    ProjectType = "xunit",
                    Dependencies = new() { $"{appName}.Core", $"{appName}.Infrastructure", $"{appName}.Services" }
                }
            },
            AcceptanceCriteria = new List<string>
            {
                "Core domain models have non-null validations and domain rules.",
                "Storage / Infrastructure layer handles thread-safe persistence and caching.",
                "Service layer implements all workflow operations and query filters.",
                "CLI console application provides full interactive subcommands and formatting.",
                "100% of unit test suites pass without warnings or errors."
            }
        };

        return blueprint;
    }
}

using DevFactory.Agents;
using DevFactory.Core.Models;
using Xunit;

namespace DevFactory.Tests;

public class ArchitectAgentTests
{
    [Fact]
    public void DesignBlueprint_CreatesExpectedProjectLayering()
    {
        var architect = new ArchitectAgent();
        var spec = new SoftwareSpec
        {
            AppName = "AuthVault",
            Description = "Token issuance and validation service"
        };

        var blueprint = architect.DesignBlueprint(spec);

        Assert.Equal("AuthVault", blueprint.SolutionName);
        Assert.Equal(5, blueprint.Projects.Count);
        Assert.Contains(blueprint.Projects, p => p.Name == "AuthVault.Core" && p.ProjectType == "classlib");
        Assert.Contains(blueprint.Projects, p => p.Name == "AuthVault.Infrastructure" && p.ProjectType == "classlib");
        Assert.Contains(blueprint.Projects, p => p.Name == "AuthVault.Services" && p.ProjectType == "classlib");
        Assert.Contains(blueprint.Projects, p => p.Name == "AuthVault.Cli" && p.ProjectType == "console");
        Assert.Contains(blueprint.Projects, p => p.Name == "AuthVault.Tests" && p.ProjectType == "xunit");
    }
}

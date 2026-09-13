namespace DevFactory.Core.Models;

public class SoftwareSpec
{
    public string AppName { get; set; } = "GeneratedApp";
    public string Description { get; set; } = string.Empty;
    public string TargetFramework { get; set; } = "net8.0";
    public string ArchitectureStyle { get; set; } = "CleanArchitecture";
    public List<string> Requirements { get; set; } = new();
    public List<string> Features { get; set; } = new();
    public string OutputDirectory { get; set; } = string.Empty;
}

public class BlueprintProject
{
    public string Name { get; set; } = string.Empty;
    public string ProjectType { get; set; } = "classlib"; // classlib, console, xunit
    public List<string> Dependencies { get; set; } = new();
    public List<string> PackageReferences { get; set; } = new();
}

public class SoftwareBlueprint
{
    public string SolutionName { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public List<BlueprintProject> Projects { get; set; } = new();
    public List<string> AcceptanceCriteria { get; set; } = new();
    public Dictionary<string, string> InitialCodeManifest { get; set; } = new();
}

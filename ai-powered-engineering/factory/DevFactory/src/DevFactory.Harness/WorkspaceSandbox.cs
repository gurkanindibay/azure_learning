using DevFactory.Core.Interfaces;
using DevFactory.Core.Models;

namespace DevFactory.Harness;

public class WorkspaceSandbox : IWorkspaceSandbox
{
    public string WorkingDirectory { get; }
    private readonly bool _preserveOnDispose;

    public WorkspaceSandbox(string? customBaseDir = null, bool preserveOnDispose = false)
    {
        _preserveOnDispose = preserveOnDispose;
        var root = customBaseDir ?? Path.Combine(Path.GetTempPath(), "devfactory_sandboxes");
        Directory.CreateDirectory(root);
        WorkingDirectory = Path.Combine(root, $"build_{Guid.NewGuid():N}");
    }

    public Task InitializeAsync(CancellationToken ct = default)
    {
        if (!Directory.Exists(WorkingDirectory))
        {
            Directory.CreateDirectory(WorkingDirectory);
        }
        return Task.CompletedTask;
    }

    public async Task WriteFilesAsync(IEnumerable<ProjectSourceFile> files, CancellationToken ct = default)
    {
        foreach (var file in files)
        {
            var fullPath = Path.Combine(WorkingDirectory, file.RelativePath);
            var dir = Path.GetDirectoryName(fullPath);
            if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir))
            {
                Directory.CreateDirectory(dir);
            }

            await File.WriteAllTextAsync(fullPath, file.Content, ct);
        }
    }

    public async Task<string> ReadFileAsync(string relativePath, CancellationToken ct = default)
    {
        var fullPath = Path.Combine(WorkingDirectory, relativePath);
        if (!File.Exists(fullPath))
        {
            throw new FileNotFoundException($"File '{relativePath}' not found in sandbox.");
        }

        return await File.ReadAllTextAsync(fullPath, ct);
    }

    public Task ExportToAsync(string destinationDirectory, CancellationToken ct = default)
    {
        if (!Directory.Exists(destinationDirectory))
        {
            Directory.CreateDirectory(destinationDirectory);
        }

        CopyDirectory(WorkingDirectory, destinationDirectory);
        return Task.CompletedTask;
    }

    private static void CopyDirectory(string sourceDir, string targetDir)
    {
        foreach (var dirPath in Directory.GetDirectories(sourceDir, "*", SearchOption.AllDirectories))
        {
            // Skip bin, obj, and git caches
            if (dirPath.Contains(Path.DirectorySeparatorChar + "bin") || dirPath.Contains(Path.DirectorySeparatorChar + "obj"))
            {
                continue;
            }

            var subDir = dirPath.Replace(sourceDir, targetDir);
            Directory.CreateDirectory(subDir);
        }

        foreach (var filePath in Directory.GetFiles(sourceDir, "*.*", SearchOption.AllDirectories))
        {
            if (filePath.Contains(Path.DirectorySeparatorChar + "bin" + Path.DirectorySeparatorChar) ||
                filePath.Contains(Path.DirectorySeparatorChar + "obj" + Path.DirectorySeparatorChar))
            {
                continue;
            }

            var destFile = filePath.Replace(sourceDir, targetDir);
            var destDir = Path.GetDirectoryName(destFile);
            if (!string.IsNullOrEmpty(destDir) && !Directory.Exists(destDir))
            {
                Directory.CreateDirectory(destDir);
            }

            File.Copy(filePath, destFile, overwrite: true);
        }
    }

    public void Dispose()
    {
        if (!_preserveOnDispose && Directory.Exists(WorkingDirectory))
        {
            try
            {
                Directory.Delete(WorkingDirectory, recursive: true);
            }
            catch
            {
                // Ignore transient file lock cleanup errors on OS temp
            }
        }
    }
}

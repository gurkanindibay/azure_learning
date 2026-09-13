using Xunit;

public class SolutionTests
{
    [Fact]
    public void TestNormal() => Assert.Equal("johndoe", Solution.NormalizeUserHandle("  JohnDoe "));

    [Fact]
    public void TestNull() => Assert.Equal(string.Empty, Solution.NormalizeUserHandle(null));

    [Fact]
    public void TestEmpty() => Assert.Equal(string.Empty, Solution.NormalizeUserHandle(""));
}

using Xunit;

public class SolutionTests
{
    [Fact]
    public void TestEmptyList() => Assert.Empty(Solution.CalculateRunningDeltas(Array.Empty<double>()));

    [Fact]
    public void TestSingleElement() => Assert.Empty(Solution.CalculateRunningDeltas(new[] { 10.0 }));

    [Fact]
    public void TestMultipleElements()
    {
        var result = Solution.CalculateRunningDeltas(new[] { 1.0, 3.0, 6.0, 10.0 });
        Assert.Equal(new[] { 2.0, 3.0, 4.0 }, result);
    }
}

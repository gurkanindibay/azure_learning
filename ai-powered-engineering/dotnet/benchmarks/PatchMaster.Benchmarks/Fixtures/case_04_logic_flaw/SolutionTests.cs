using Xunit;

public class SolutionTests
{
    [Fact]
    public void TestTwentyPercent() => Assert.Equal(80.0m, Solution.ApplyDiscountTier(100.0m, 0.20m));

    [Fact]
    public void TestZero() => Assert.Equal(50.0m, Solution.ApplyDiscountTier(50.0m, 0.0m));

    [Fact]
    public void TestFull() => Assert.Equal(0.0m, Solution.ApplyDiscountTier(75.0m, 1.0m));
}

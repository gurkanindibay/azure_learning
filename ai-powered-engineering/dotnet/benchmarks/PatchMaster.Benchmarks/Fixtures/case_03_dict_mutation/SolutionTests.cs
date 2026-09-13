using Xunit;

public class SolutionTests
{
    [Fact]
    public void TestPrune()
    {
        var dict = new Dictionary<string, int> { { "user1", 10 }, { "user2", 55 }, { "user3", 20 }, { "user4", 80 } };
        var res = Solution.PruneInactiveSessions(dict, 30);
        Assert.Equal(2, res.Count);
        Assert.True(res.ContainsKey("user1"));
        Assert.True(res.ContainsKey("user3"));
    }

    [Fact]
    public void TestEmpty() => Assert.Empty(Solution.PruneInactiveSessions(new Dictionary<string, int>(), 30));
}

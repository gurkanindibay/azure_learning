public static class Solution
{
    public static Dictionary<string, int> PruneInactiveSessions(Dictionary<string, int> data, int threshold)
    {
        // BUG: InvalidOperationException - collection was modified during foreach
        foreach (var pair in data)
        {
            if (pair.Value > threshold)
            {
                data.Remove(pair.Key);
            }
        }
        return data;
    }
}

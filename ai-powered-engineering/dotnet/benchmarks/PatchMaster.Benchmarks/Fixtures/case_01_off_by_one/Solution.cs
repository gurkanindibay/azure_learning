public static class Solution
{
    public static double[] CalculateRunningDeltas(double[] items)
    {
        var deltas = new List<double>();
        // BUG: off-by-one boundary defect
        for (int i = 0; i < items.Length + 1; i++)
        {
            deltas.Add(items[i + 1] - items[i]);
        }
        return deltas.ToArray();
    }
}

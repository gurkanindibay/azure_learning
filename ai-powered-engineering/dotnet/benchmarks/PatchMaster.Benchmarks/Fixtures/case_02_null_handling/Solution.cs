public static class Solution
{
    public static string NormalizeUserHandle(string? text)
    {
        // BUG: NullReferenceException when text is null
        return text.Trim().ToLower();
    }
}

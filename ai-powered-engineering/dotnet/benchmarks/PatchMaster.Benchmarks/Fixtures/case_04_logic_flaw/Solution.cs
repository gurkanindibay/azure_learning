public static class Solution
{
    public static decimal ApplyDiscountTier(decimal price, decimal discount)
    {
        // BUG: Multiplies price by discount directly instead of applying price * (1 - discount)
        return Math.Round(price * discount, 2);
    }
}

using AuditGuard.Core;

namespace AuditGuard.Harness;

public static class PolicyCatalog
{
    public static readonly CompanyPolicy DefaultCorporatePolicy = new()
    {
        MaxAutoApproveAmount = 500.00m,
        MaxSingleMealAmount = 75.00m,
        AllowAlcohol = false,
        AllowWeekendExpensesWithoutFlag = false,
        TipPercentageThreshold = 0.25m
    };

    public static readonly HashSet<string> AlcoholKeywords = new(StringComparer.OrdinalIgnoreCase)
    {
        "Beer", "Wine", "Cocktail", "Whiskey", "Vodka", "IPA", "Margarita", "Martini", "Liquor", "Brew", "Draft", "Prosecco"
    };

    public static bool IsAlcoholItem(string description)
    {
        var words = description.Split(new[] { ' ', ',', '-', '/', '&' }, StringSplitOptions.RemoveEmptyEntries);
        return words.Any(w => AlcoholKeywords.Contains(w));
    }
}

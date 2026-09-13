namespace AuditGuard.Core;

public class CompanyPolicy
{
    public decimal MaxAutoApproveAmount { get; set; } = 500.00m;
    public decimal MaxSingleMealAmount { get; set; } = 75.00m;
    public bool AllowAlcohol { get; set; } = false;
    public bool AllowWeekendExpensesWithoutFlag { get; set; } = false;
    public decimal TipPercentageThreshold { get; set; } = 0.25m; // 25% max tip
}

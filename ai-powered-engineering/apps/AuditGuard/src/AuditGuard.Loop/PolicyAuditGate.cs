using AuditGuard.Core;
using AuditGuard.Harness;

namespace AuditGuard.Loop;

public class PolicyAuditGate : IPolicyAuditGate
{
    public PolicyAuditResult AuditPolicy(ExpenseClaim claim, CompanyPolicy policy)
    {
        var violations = new List<PolicyViolation>();

        // Rule 1: High value ceiling
        if (claim.GrandTotal > policy.MaxAutoApproveAmount)
        {
            violations.Add(new PolicyViolation
            {
                RuleName = "HIGH_VALUE_THRESHOLD",
                Severity = PolicySeverity.Critical,
                Explanation = $"Total expense (${claim.GrandTotal:F2}) exceeds auto-approval ceiling (${policy.MaxAutoApproveAmount:F2}). Requires managerial sign-off."
            });
        }

        // Rule 2: Alcohol item prohibition
        if (!policy.AllowAlcohol)
        {
            foreach (var item in claim.LineItems)
            {
                if (PolicyCatalog.IsAlcoholItem(item.Description))
                {
                    violations.Add(new PolicyViolation
                    {
                        RuleName = "ALCOHOL_PROHIBITION",
                        Severity = PolicySeverity.Critical,
                        Explanation = $"Prohibited item detected: '{item.Description}' (${item.TotalPrice:F2}) matches corporate alcohol policy restriction."
                    });
                }
            }
        }

        // Rule 3: Single meal limit
        var mealItems = claim.LineItems.Where(i => i.Category.Equals("Meal", StringComparison.OrdinalIgnoreCase) || i.Category.Equals("Food", StringComparison.OrdinalIgnoreCase));
        foreach (var meal in mealItems)
        {
            if (meal.TotalPrice > policy.MaxSingleMealAmount)
            {
                violations.Add(new PolicyViolation
                {
                    RuleName = "MEAL_LIMIT_EXCEEDED",
                    Severity = PolicySeverity.Warning,
                    Explanation = $"Meal item '{meal.Description}' (${meal.TotalPrice:F2}) exceeds standard single-meal limit of ${policy.MaxSingleMealAmount:F2}."
                });
            }
        }

        // Rule 4: Weekend expense flag
        if (!policy.AllowWeekendExpensesWithoutFlag)
        {
            if (claim.TransactionDate.DayOfWeek == DayOfWeek.Saturday || claim.TransactionDate.DayOfWeek == DayOfWeek.Sunday)
            {
                violations.Add(new PolicyViolation
                {
                    RuleName = "WEEKEND_EXPENSE",
                    Severity = PolicySeverity.Warning,
                    Explanation = $"Transaction occurred on a weekend ({claim.TransactionDate.DayOfWeek:G}). Requires business justification review."
                });
            }
        }

        // Rule 5: Tip threshold check
        if (claim.Subtotal > 0 && claim.Tip > 0)
        {
            var tipRatio = claim.Tip / claim.Subtotal;
            if (tipRatio > policy.TipPercentageThreshold)
            {
                violations.Add(new PolicyViolation
                {
                    RuleName = "EXCESSIVE_TIP",
                    Severity = PolicySeverity.Warning,
                    Explanation = $"Tip percentage ({tipRatio:P1}) exceeds company cap of {policy.TipPercentageThreshold:P0}."
                });
            }
        }

        return new PolicyAuditResult
        {
            Passed = violations.Count == 0,
            Violations = violations
        };
    }
}

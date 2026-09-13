using AuditGuard.Core;
using AuditGuard.Harness;
using AuditGuard.Loop;
using Xunit;

namespace AuditGuard.Tests;

public class PolicyAuditGateTests
{
    private readonly PolicyAuditGate _gate = new();
    private readonly CompanyPolicy _policy = PolicyCatalog.DefaultCorporatePolicy;

    [Fact]
    public void AuditPolicy_CompliantClaim_Passes()
    {
        var claim = new ExpenseClaim
        {
            GrandTotal = 45.00m,
            Subtotal = 35.00m,
            Tip = 5.00m,
            TransactionDate = new DateTime(2026, 9, 10), // Thursday
            LineItems = new()
            {
                new() { Description = "Business Lunch", TotalPrice = 35.00m, Category = "Meal" }
            }
        };

        var result = _gate.AuditPolicy(claim, _policy);

        Assert.True(result.Passed);
        Assert.Empty(result.Violations);
    }

    [Fact]
    public void AuditPolicy_AlcoholItem_FlaggedAsCritical()
    {
        var claim = new ExpenseClaim
        {
            GrandTotal = 50.00m,
            Subtotal = 40.00m,
            TransactionDate = new DateTime(2026, 9, 10),
            LineItems = new()
            {
                new() { Description = "Burger", TotalPrice = 25.00m, Category = "Meal" },
                new() { Description = "Craft IPA Beer", TotalPrice = 15.00m, Category = "Alcohol" }
            }
        };

        var result = _gate.AuditPolicy(claim, _policy);

        Assert.False(result.Passed);
        var violation = Assert.Single(result.Violations);
        Assert.Equal("ALCOHOL_PROHIBITION", violation.RuleName);
        Assert.Equal(PolicySeverity.Critical, violation.Severity);
    }

    [Fact]
    public void AuditPolicy_ExceedsHighValueThreshold_Flagged()
    {
        var claim = new ExpenseClaim
        {
            GrandTotal = 650.00m, // Policy limit is 500.00m
            Subtotal = 600.00m,
            TransactionDate = new DateTime(2026, 9, 10),
            LineItems = new()
            {
                new() { Description = "Monitor", TotalPrice = 600.00m, Category = "Equipment" }
            }
        };

        var result = _gate.AuditPolicy(claim, _policy);

        Assert.False(result.Passed);
        Assert.Contains(result.Violations, v => v.RuleName == "HIGH_VALUE_THRESHOLD");
    }

    [Fact]
    public void AuditPolicy_WeekendExpense_FlaggedForReview()
    {
        var claim = new ExpenseClaim
        {
            GrandTotal = 40.00m,
            Subtotal = 40.00m,
            TransactionDate = new DateTime(2026, 9, 13), // Sunday
            LineItems = new()
            {
                new() { Description = "Airport Shuttle", TotalPrice = 40.00m, Category = "Travel" }
            }
        };

        var result = _gate.AuditPolicy(claim, _policy);

        Assert.False(result.Passed);
        Assert.Contains(result.Violations, v => v.RuleName == "WEEKEND_EXPENSE");
    }

    [Fact]
    public void AuditPolicy_ExcessiveTip_Flagged()
    {
        var claim = new ExpenseClaim
        {
            Subtotal = 50.00m,
            Tip = 20.00m, // 40% tip (policy threshold is 25%)
            GrandTotal = 70.00m,
            TransactionDate = new DateTime(2026, 9, 10),
            LineItems = new()
            {
                new() { Description = "Dinner", TotalPrice = 50.00m, Category = "Meal" }
            }
        };

        var result = _gate.AuditPolicy(claim, _policy);

        Assert.False(result.Passed);
        Assert.Contains(result.Violations, v => v.RuleName == "EXCESSIVE_TIP");
    }
}

using AuditGuard.Core;
using AuditGuard.Loop;
using Xunit;

namespace AuditGuard.Tests;

public class MathVerifyGateTests
{
    private readonly MathVerifyGate _gate = new();

    [Fact]
    public void VerifyMath_CleanClaim_Passes()
    {
        var claim = new ExpenseClaim
        {
            Subtotal = 30.00m,
            Tax = 3.00m,
            Tip = 5.00m,
            GrandTotal = 38.00m,
            LineItems = new()
            {
                new() { Description = "Burger", Quantity = 2, UnitPrice = 10.00m, TotalPrice = 20.00m },
                new() { Description = "Salad", Quantity = 1, UnitPrice = 10.00m, TotalPrice = 10.00m }
            }
        };

        var result = _gate.VerifyMath(claim);

        Assert.True(result.Passed);
        Assert.Equal(0m, result.SubtotalDelta);
        Assert.Equal(0m, result.GrandTotalDelta);
        Assert.Empty(result.ErrorSummary);
    }

    [Fact]
    public void VerifyMath_ItemSumMismatch_FailsWithDiagnostic()
    {
        var claim = new ExpenseClaim
        {
            Subtotal = 50.00m, // Items only equal 30.00
            Tax = 3.00m,
            Tip = 5.00m,
            GrandTotal = 58.00m,
            LineItems = new()
            {
                new() { Description = "Burger", Quantity = 1, UnitPrice = 20.00m, TotalPrice = 20.00m },
                new() { Description = "Drink", Quantity = 1, UnitPrice = 10.00m, TotalPrice = 10.00m }
            }
        };

        var result = _gate.VerifyMath(claim);

        Assert.False(result.Passed);
        Assert.Equal(20.00m, result.SubtotalDelta);
        Assert.Contains("Subtotal mismatch: Sum of items is $30.00", result.ErrorSummary);
    }

    [Fact]
    public void VerifyMath_GrandTotalMismatch_FailsWithDiagnostic()
    {
        var claim = new ExpenseClaim
        {
            Subtotal = 30.00m,
            Tax = 3.00m,
            Tip = 5.00m,
            GrandTotal = 45.00m, // Expected 38.00m
            LineItems = new()
            {
                new() { Description = "Lunch", Quantity = 1, UnitPrice = 30.00m, TotalPrice = 30.00m }
            }
        };

        var result = _gate.VerifyMath(claim);

        Assert.False(result.Passed);
        Assert.Equal(7.00m, result.GrandTotalDelta);
        Assert.Contains("Grand total mismatch", result.ErrorSummary);
    }
}

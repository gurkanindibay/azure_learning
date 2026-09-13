using System.Globalization;
using System.Text.RegularExpressions;
using AuditGuard.Core;

namespace AuditGuard.Agents;

public class HeuristicExtractorAgent : IExtractorAgent
{
    public ExpenseClaim Extract(string rawReceiptText, string diagnosticFeedback = "")
    {
        var claim = new ExpenseClaim
        {
            RawReceiptText = rawReceiptText
        };

        var lines = rawReceiptText.Split(new[] { "\r\n", "\r", "\n" }, StringSplitOptions.RemoveEmptyEntries)
                                  .Select(l => l.Trim())
                                  .ToList();

        // 1. Merchant name (usually first non-empty line)
        if (lines.Count > 0)
        {
            claim.MerchantName = lines[0].Replace("---", "").Trim();
        }

        // 2. Date extraction
        var dateMatch = Regex.Match(rawReceiptText, @"Date:\s*(\d{4}-\d{2}-\d{2})");
        if (dateMatch.Success && DateTime.TryParse(dateMatch.Groups[1].Value, out var dt))
        {
            claim.TransactionDate = dt;
        }

        // 3. Totals extraction
        var subtotalMatch = Regex.Match(rawReceiptText, @"Subtotal:\s*\$?([0-9]+\.[0-9]{2})", RegexOptions.IgnoreCase);
        if (subtotalMatch.Success) claim.Subtotal = decimal.Parse(subtotalMatch.Groups[1].Value, CultureInfo.InvariantCulture);

        var taxMatch = Regex.Match(rawReceiptText, @"Tax:\s*\$?([0-9]+\.[0-9]{2})", RegexOptions.IgnoreCase);
        if (taxMatch.Success) claim.Tax = decimal.Parse(taxMatch.Groups[1].Value, CultureInfo.InvariantCulture);

        var tipMatch = Regex.Match(rawReceiptText, @"Tip:\s*\$?([0-9]+\.[0-9]{2})", RegexOptions.IgnoreCase);
        if (tipMatch.Success) claim.Tip = decimal.Parse(tipMatch.Groups[1].Value, CultureInfo.InvariantCulture);

        var totalMatch = Regex.Match(rawReceiptText, @"(?:Grand Total|(?<!Sub)Total):\s*\$?([0-9]+\.[0-9]{2})", RegexOptions.IgnoreCase);
        if (totalMatch.Success) claim.GrandTotal = decimal.Parse(totalMatch.Groups[1].Value, CultureInfo.InvariantCulture);

        // 4. Line items parsing (e.g., "- 2x Burger: $24.00" or "- Draft Beer: $8.50")
        foreach (var line in lines)
        {
            var itemMatch = Regex.Match(line, @"^-\s*(?:(\d+)x\s*)?([^\$:]+):\s*\$?([0-9]+\.[0-9]{2})");
            if (itemMatch.Success)
            {
                var qty = itemMatch.Groups[1].Success ? int.Parse(itemMatch.Groups[1].Value) : 1;
                var desc = itemMatch.Groups[2].Value.Trim();
                var total = decimal.Parse(itemMatch.Groups[3].Value, CultureInfo.InvariantCulture);
                var unit = qty > 0 ? total / qty : total;

                var category = "General";
                if (desc.Contains("Burger", StringComparison.OrdinalIgnoreCase) || 
                    desc.Contains("Salad", StringComparison.OrdinalIgnoreCase) || 
                    desc.Contains("Steak", StringComparison.OrdinalIgnoreCase) ||
                    desc.Contains("Lunch", StringComparison.OrdinalIgnoreCase))
                {
                    category = "Meal";
                }
                else if (desc.Contains("Beer", StringComparison.OrdinalIgnoreCase) || 
                         desc.Contains("Wine", StringComparison.OrdinalIgnoreCase) ||
                         desc.Contains("Cocktail", StringComparison.OrdinalIgnoreCase))
                {
                    category = "Alcohol";
                }

                claim.LineItems.Add(new ReceiptLineItem
                {
                    Description = desc,
                    Quantity = qty,
                    UnitPrice = unit,
                    TotalPrice = total,
                    Category = category
                });
            }
        }

        // Self-Healing Demonstration: If raw text has a missing subtotal or calculation mismatch
        // and diagnostic feedback is received, reconcile subtotal dynamically from line items!
        if (!string.IsNullOrEmpty(diagnosticFeedback))
        {
            if (claim.Subtotal == 0 || Math.Abs(claim.LineItems.Sum(i => i.TotalPrice) - claim.Subtotal) > 0.01m)
            {
                claim.Subtotal = claim.LineItems.Sum(i => i.TotalPrice);
            }
            if (claim.GrandTotal == 0 || Math.Abs((claim.Subtotal + claim.Tax + claim.Tip) - claim.GrandTotal) > 0.01m)
            {
                claim.GrandTotal = claim.Subtotal + claim.Tax + claim.Tip;
            }
        }

        return claim;
    }
}

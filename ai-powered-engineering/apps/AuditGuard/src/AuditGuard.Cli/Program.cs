using System.Text;
using AuditGuard.Agents;
using AuditGuard.Core;
using AuditGuard.Graph;
using AuditGuard.Harness;
using AuditGuard.Loop;

namespace AuditGuard.Cli;

public class Program
{
    public static int Main(string[] args)
    {
        Console.OutputEncoding = Encoding.UTF8;
        PrintBanner();

        if (args.Length == 0 || args.Contains("--help") || args.Contains("-h"))
        {
            PrintUsage();
            return 0;
        }

        string receiptText = string.Empty;
        string receiptLabel = "Custom Receipt";

        if (args.Contains("--sample"))
        {
            receiptLabel = "Sample Business Lunch";
            receiptText = GetSampleReceipt();
        }
        else
        {
            var receiptIdx = Array.IndexOf(args, "--receipt");
            if (receiptIdx >= 0 && receiptIdx + 1 < args.Length)
            {
                var path = args[receiptIdx + 1];
                if (!File.Exists(path))
                {
                    Console.ForegroundColor = ConsoleColor.Red;
                    Console.WriteLine($"[Error] Receipt file not found: {path}");
                    Console.ResetColor();
                    return 1;
                }
                receiptLabel = Path.GetFileName(path);
                receiptText = File.ReadAllText(path);
            }
            else
            {
                Console.ForegroundColor = ConsoleColor.Yellow;
                Console.WriteLine("[AuditGuard] No receipt file specified. Use --sample or --receipt <path>.");
                Console.ResetColor();
                return 1;
            }
        }

        RunAudit(receiptText, receiptLabel);
        return 0;
    }

    public static void RunAudit(string receiptText, string label)
    {
        Console.WriteLine($"\n=======================================================");
        Console.WriteLine($" AUDITING CLAIM: {label}");
        Console.WriteLine($"=======================================================");
        Console.ForegroundColor = ConsoleColor.DarkGray;
        Console.WriteLine(receiptText.Trim());
        Console.ResetColor();
        Console.WriteLine("-------------------------------------------------------");

        // 1. Initialize 4-layer architecture
        var extractor = new HeuristicExtractorAgent();
        var mathGate = new MathVerifyGate();
        var policyGate = new PolicyAuditGate();
        var policy = PolicyCatalog.DefaultCorporatePolicy;
        var controller = new AuditLoopController(extractor, mathGate, policyGate, policy);
        var engine = new AuditGraphEngine(controller);

        // 2. Initial state
        var state = new AuditState
        {
            RawText = receiptText,
            MaxIterations = 3
        };

        // 3. Run graph execution
        Console.WriteLine("\n[Graph Engine] Executing state machine transitions...");
        var finalState = engine.Run(state);

        // 4. Print Step Trace
        Console.WriteLine("\n--- Graph Execution Trace ---");
        Console.WriteLine($"{"Step",-5} {"Node",-15} {"Phase",-12} {"Iter",-6} {"Duration",-10} {"Diagnostic"}");
        Console.WriteLine(new string('-', 75));
        foreach (var step in engine.TraceLog)
        {
            Console.WriteLine($"{step.StepIndex,-5} {step.Node,-15} {step.Phase,-12} {step.Iteration,-6} {step.DurationMs + "ms",-10} {step.Diagnostic}");
        }

        // 5. Print Extracted Claim Details
        if (finalState.ExtractedClaim != null)
        {
            var claim = finalState.ExtractedClaim;
            Console.WriteLine("\n--- Extracted Claim Entities ---");
            Console.WriteLine($"Merchant: {claim.MerchantName}");
            Console.WriteLine($"Date:     {claim.TransactionDate:yyyy-MM-dd} ({claim.TransactionDate.DayOfWeek})");
            Console.WriteLine("Items:");
            foreach (var item in claim.LineItems)
            {
                Console.WriteLine($"  * {item.Quantity}x {item.Description} @ ${item.UnitPrice:F2} = ${item.TotalPrice:F2} [{item.Category}]");
            }
            Console.WriteLine($"Subtotal: ${claim.Subtotal:F2} | Tax: ${claim.Tax:F2} | Tip: ${claim.Tip:F2} | Total: ${claim.GrandTotal:F2}");
        }

        // 6. Print Verification and Decision
        Console.WriteLine("\n--- Audit Verification & Outcome ---");
        if (finalState.LatestMathResult != null)
        {
            var m = finalState.LatestMathResult;
            Console.Write("Math Check:   ");
            if (m.Passed)
            {
                Console.ForegroundColor = ConsoleColor.Green;
                Console.WriteLine("PASSED (Sum & Totals reconcile perfectly)");
            }
            else
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine($"FAILED (Subtotal Delta: ${m.SubtotalDelta:F2}, Grand Total Delta: ${m.GrandTotalDelta:F2})");
            }
            Console.ResetColor();
        }

        if (finalState.LatestPolicyResult != null)
        {
            var p = finalState.LatestPolicyResult;
            Console.Write("Policy Check: ");
            if (p.Passed)
            {
                Console.ForegroundColor = ConsoleColor.Green;
                Console.WriteLine("PASSED (No corporate policy violations detected)");
            }
            else
            {
                Console.ForegroundColor = ConsoleColor.Yellow;
                Console.WriteLine($"VIOLATIONS DETECTED ({p.Violations.Count} issue(s))");
                Console.ResetColor();
                foreach (var v in p.Violations)
                {
                    Console.WriteLine($"  - [{v.RuleName}] ({v.Severity}) {v.Explanation}");
                }
            }
            Console.ResetColor();
        }

        Console.Write("\nFINAL DECISION: ");
        switch (finalState.FinalStatus)
        {
            case AuditStatus.AutoApproved:
                Console.ForegroundColor = ConsoleColor.Green;
                Console.WriteLine("✅ AUTO-APPROVED");
                break;
            case AuditStatus.RequiresHumanReview:
                Console.ForegroundColor = ConsoleColor.Yellow;
                Console.WriteLine("⚠️ REQUIRES HUMAN REVIEW / ESCALATION");
                break;
            case AuditStatus.Rejected:
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine("❌ REJECTED");
                break;
        }
        Console.ResetColor();
        Console.WriteLine($"Summary: {finalState.AuditReport}");
        Console.WriteLine("=======================================================\n");
    }

    private static void PrintBanner()
    {
        Console.ForegroundColor = ConsoleColor.Cyan;
        Console.WriteLine(@"
   ___             ___ __       ____                     __
  /   | __  ______/ (_) /_     / __ \__  ______ __________/ /
 / /| |/ / / / __  / / __/    / / / / / / / __ `/ ___/ __  / 
/ ___ / /_/ / /_/ / / /_     / /_/ / /_/ / /_/ / /  / /_/ /  
/_/  |_\__,_/\__,_/_/\__/    \___\_\__,_/\__,_/_/   \__,_/   
     Autonomous Expense & Invoice Audit Microservice
     Pattern: Harness -> Loop -> Graph -> Evals (4-Layer)
");
        Console.ResetColor();
    }

    private static void PrintUsage()
    {
        Console.WriteLine("Usage:");
        Console.WriteLine("  dotnet run --project src/AuditGuard.Cli -- --sample");
        Console.WriteLine("  dotnet run --project src/AuditGuard.Cli -- --receipt <path-to-receipt.txt>");
        Console.WriteLine("\nOptions:");
        Console.WriteLine("  --sample               Run audit on embedded business lunch receipt.");
        Console.WriteLine("  --receipt <file>       Path to plain text receipt file to audit.");
        Console.WriteLine("  --help, -h             Show this help screen.");
    }

    private static string GetSampleReceipt()
    {
        return """
        --- Blue Harbour Bistro ---
        Date: 2026-09-10
        Receipt #: BH-88219
        Server: Alex
        
        - 1x Grilled Salmon Lunch: $32.00
        - 1x Caesar Salad: $14.50
        - 1x Sparkling Water: $4.50
        
        Subtotal: $51.00
        Tax: $4.59
        Tip: $8.00
        Total: $63.59
        
        Thank you for dining with us!
        """;
    }
}

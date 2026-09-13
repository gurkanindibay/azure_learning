using AuditGuard.Core;
using AuditGuard.Harness;

namespace AuditGuard.Agents;

public class ComplianceCheckerAgent : IComplianceChecker
{
    private readonly IPolicyAuditGate? _policyGate;

    public ComplianceCheckerAgent(IPolicyAuditGate? policyGate = null)
    {
        _policyGate = policyGate;
    }

    public (bool Approved, List<PolicyViolation> Violations) Audit(ExpenseClaim claim, CompanyPolicy policy)
    {
        if (_policyGate != null)
        {
            var result = _policyGate.AuditPolicy(claim, policy);
            return (result.Passed, result.Violations);
        }

        var violations = new List<PolicyViolation>();
        if (claim.GrandTotal > policy.MaxAutoApproveAmount)
        {
            violations.Add(new PolicyViolation
            {
                RuleName = "HIGH_VALUE_THRESHOLD",
                Severity = PolicySeverity.Critical,
                Explanation = $"Total expense (${claim.GrandTotal:F2}) exceeds auto-approval ceiling (${policy.MaxAutoApproveAmount:F2})."
            });
        }

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

        return (violations.Count == 0, violations);
    }
}


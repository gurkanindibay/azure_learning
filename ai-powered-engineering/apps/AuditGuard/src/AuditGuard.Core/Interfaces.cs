namespace AuditGuard.Core;

public interface IExtractorAgent
{
    ExpenseClaim Extract(string rawReceiptText, string diagnosticFeedback = "");
}

public interface IMathVerifyGate
{
    MathVerificationResult VerifyMath(ExpenseClaim claim);
}

public interface IPolicyAuditGate
{
    PolicyAuditResult AuditPolicy(ExpenseClaim claim, CompanyPolicy policy);
}

public interface IComplianceChecker
{
    (bool Approved, List<PolicyViolation> Violations) Audit(ExpenseClaim claim, CompanyPolicy policy);
}

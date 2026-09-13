namespace PatchMaster.Core;

public interface IMakerAgent
{
    string GeneratePlan(AgentState state);
    string GeneratePatch(AgentState state);
}

public interface ICheckerAgent
{
    (bool Approved, string Reason) Audit(string candidateCode, string originalCode);
}

public interface IVerifyGate
{
    VerificationResult Verify(string originalCode, string candidateCode, string testCode);
}

public interface ISandbox
{
    (bool Passed, int ExitCode, string Stdout, string Stderr) RunTests(string code, string testCode);
}

---
type: System Design
title: "Runtime Performance — Rust Logic Errors Takeaways"
description: "Reusable design lessons from a Python-to-Rust migration: compiler guarantees, wildcard pitfalls, and policy-level correctness checks."
timestamp: 2026-07-18T00:00:00Z
---

# 61. Runtime Performance — Rust Logic Errors Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [Torvalds Said Rust Doesn't Fix Logic Errors. Six Months Into My Own Rust Migration, I Think He's Right](../../articles/performance/torvalds-rust-doesnt-fix-logic-errors.md)
> **Purpose**: Capture reusable system-design rules for runtime migrations where memory safety improves but business-logic correctness still depends on explicit engineering policy.
> **Also see**: [Python to Rust Rewrite Takeaways](python-to-rust-rewrite.md), [Architecture Principles](../software-architecture/architecture-principles.md), [Async Concurrency Patterns](../stream-processing/async-concurrency-patterns.md)
> **Taxonomy Reference**: §7.2 Performance Architecture

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [perf-13](#perf-13-option-handling-eliminates-null-policy-gaps) | Missing-tier policy paths silently pass in dynamic code | Encode absence in types and force explicit handling |
| [perf-14](#perf-14-wildcard-arms-hide-future-business-rules) | New enum variants inherit unsafe defaults | Avoid wildcard arms in policy-critical matches |
| [perf-15](#perf-15-compiler-guarantees-stop-before-business-intent) | Green builds still ship wrong policy decisions | Add intent checks beyond type safety |
| [perf-16](#perf-16-language-safety-needs-operational-policy) | Safety mechanisms can still fail production objectives | Govern panic/default behavior with production rules |

---

## perf-13: Option Handling Eliminates Null Policy Gaps

| | |
|:---|:---|
| **Problem** | A migrated-account edge case returned no tier, then silently propagated into policy evaluation in a dynamic runtime. |
| **Root cause** | The old flow treated missing values as acceptable state and allowed policy lookup to continue without explicit branch handling. |
| **Scale impact** | Rare edge cases survive for long periods and surface only under specific account states, creating latent correctness debt. |

**Strategy — Encode missing-state explicitly and make handling mandatory**:

- Model absence with `Option`/sum types instead of nullable implicit defaults.
- Require match-based handling for every policy lookup path.
- Set a secure explicit fallback policy for `None` cases.

**Tradeoff**: Stronger type modeling increases verbosity and up-front design effort, but it removes a recurring class of hidden runtime failures.

> **Also see**: [Borrow Checker](../../reference-dictionary/concurrency-runtimes.md#borrow-checker) · [Global Interpreter Lock (GIL)](../../reference-dictionary/data-concurrency.md#global-interpreter-lock)

---

## perf-14: Wildcard Arms Hide Future Business Rules

| | |
|:---|:---|
| **Problem** | A newly introduced tier inherited a generic default policy because a wildcard match arm compiled successfully. |
| **Root cause** | Catch-all matching bypassed variant-specific intent and disabled compiler pressure to revisit policy logic when the enum evolved. |
| **Scale impact** | Silent privilege or policy drift can affect entire customer classes without triggering errors or alerts. |

**Strategy — Make policy matches exhaustive, not permissive**:

- Ban wildcard/catch-all arms for authorization, pricing, and compliance-critical enums.
- Require explicit handling for every known variant.
- Add CI linting/code-review rules for policy-match exhaustiveness.

**Tradeoff**: More frequent compile breaks during schema evolution, but those breaks force the exact review point where business intent must be revalidated.

> **Also see**: [Exhaustiveness Checking](../../reference-dictionary/concurrency-runtimes.md#exhaustiveness-checking) · [Wildcard Match Arm](../../reference-dictionary/concurrency-runtimes.md#wildcard-match-arm) · [Least Privilege](../../reference-dictionary/security-iam.md#least-privilege)

---

## perf-15: Compiler Guarantees Stop Before Business Intent

| | |
|:---|:---|
| **Problem** | Teams over-trust language safety and assume passing compile-time checks implies policy correctness. |
| **Root cause** | Type systems validate structure and memory/concurrency rules, not domain intent such as entitlement semantics. |
| **Scale impact** | Logic errors pass quietly through CI and appear as customer-facing misbehavior weeks later. |

**Strategy — Add intent-level verification on top of language guarantees**:

- Add invariant tests for policy correctness across all tier/action combinations.
- Add mutation/regression tests for newly introduced variants.
- Treat compiler output as one gate in a larger correctness pipeline.

**Tradeoff**: Larger test matrix and maintenance cost, but materially lower risk of "green build, wrong behavior" releases.

> **Also see**: [Defensive Programming](../../reference-dictionary/resilience.md#defensive-programming) · [Fail Fast](../../reference-dictionary/design-patterns.md#fail-fast)

---

## perf-16: Language Safety Needs Operational Policy

| | |
|:---|:---|
| **Problem** | Safety escape hatches (panic/default fallbacks) can still violate uptime or correctness goals in production systems. |
| **Root cause** | Runtime-level failure behavior is often left to language defaults instead of explicit service-level policy. |
| **Scale impact** | Incidents shift from memory corruption to availability/correctness outages, especially in boundary-heavy systems. |

**Strategy — Define and enforce production failure policy explicitly**:

- For critical services, prefer recoverable error paths over panic paths.
- Constrain defaults so they are intentionally safe, observable, and reviewable.
- Require decision records for fail-open vs fail-closed behaviors.

**Tradeoff**: Extra policy governance and review overhead, but stronger operational predictability under unknown input states.

> **Also see**: [Architecture Decision Record](../../reference-dictionary/design-patterns.md#architecture-decision-record) · [Graceful Degradation](../../reference-dictionary/resilience.md#graceful-degradation)

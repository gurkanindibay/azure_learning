---
type: Architecture Pattern
title: "MLOps Architecture"
description: "MLOps (Machine Learning Operations) extends DevOps principles to machine learning systems — establishing **CI/CD/CT** (Continuous Integration, Delivery, and Training) pipelines for ML models. MLOps..."
tags: [data-analytics-ai-architecture, ai-ml-architecture]
generated: { by: process:okf-migrate, at: 2026-06-14T00:00:00Z }
---

# MLOps Architecture

> **Taxonomy Reference**: §4.4 AI / ML Architecture

## Overview

MLOps (Machine Learning Operations) extends DevOps principles to machine learning systems — establishing **CI/CD/CT** (Continuous Integration, Delivery, and Training) pipelines for ML models. MLOps addresses the unique challenges of ML: data dependencies, model decay, experiment tracking, and the need for continuous retraining.

## Table of Contents

- [Core Principles](#core-principles)
- [MLOps vs DevOps](#mlops-vs-devops)
- [Architecture Diagram](#architecture-diagram)
- [CI/CD/CT Pipeline](#cicdct-pipeline)
- [Maturity Model](#maturity-model)
- [Model Monitoring & Drift](#model-monitoring-drift)
- [Governance & Compliance](#governance-compliance)
- [Decision Framework](#decision-framework)
- [Related Patterns](#related-patterns)

## Core Principles

| Principle | DevOps | MLOps |
|-----------|--------|-------|
| **Versioning** | Code | Code + Data + Model + Parameters |
| **Testing** | Unit, integration, E2E | + Data validation, model evaluation, fairness |
| **Deployment** | Binary/container | Model artifact + serving infrastructure |
| **Monitoring** | CPU, memory, latency | + Data drift, concept drift, prediction quality |
| **Rollback** | Redeploy previous version | Switch model version in registry |
| **Reproducibility** | Docker image, commit hash | + Data version, seed, hyperparameters |

## MLOps vs DevOps

```mermaid
graph LR
    subgraph "DevOps"
        D_CODE[Code] --> D_BUILD[Build] --> D_TEST[Test] --> D_DEPLOY[Deploy] --> D_MONITOR[Monitor]
    end

    subgraph "MLOps"
        M_DATA[Data] --> M_TRAIN[Train] --> M_EVAL[Evaluate] --> M_REGISTER[Register] --> M_DEPLOY[Deploy] --> M_MONITOR[Monitor]
        M_MONITOR -.->|Retrain| M_DATA
    end

    style M_DATA fill:#ff6b6b,color:#fff
    style M_DEPLOY fill:#4ecdc4,color:#fff
```

## Architecture Diagram

```mermaid
graph TB
    subgraph "MLOps Architecture"
        subgraph "Development"
            NOTEBOOK[Notebooks<br/>Experimentation]
            CODE[Source Code<br/>Git]
            DATA[Data Versioning<br/>DVC / Delta]
        end

        subgraph "CI: Continuous Integration"
            LINT[Lint & Format]
            UNIT[Unit Tests]
            DATA_VAL[Data Validation]
            NOTEBOOK --> LINT
            CODE --> LINT
            LINT --> UNIT
            DATA --> DATA_VAL
            UNIT --> BUILD[Build Pipeline<br/>Package]
            DATA_VAL --> BUILD
        end

        subgraph "CT: Continuous Training"
            TRAIN[Training<br/>Pipeline]
            EVAL[Model<br/>Evaluation]
            REGISTRY[(Model<br/>Registry)]
            BUILD --> TRAIN
            TRAIN --> EVAL
            EVAL -->|Pass threshold| REGISTRY
        end

        subgraph "CD: Continuous Delivery"
            STAGING[Staging<br/>Deployment]
            PROD[Production<br/>Deployment]
            A_B[A/B Testing<br/>Canary]
            REGISTRY --> STAGING
            STAGING --> A_B
            A_B --> PROD
        end

        subgraph "Monitoring & Feedback"
            DRIFT[Drift Detection]
            METRICS[Performance<br/>Metrics]
            ALERT[Alerting]
            FEEDBACK[Feedback Loop]
            PROD --> DRIFT
            PROD --> METRICS
            DRIFT --> ALERT
            METRICS --> ALERT
            ALERT --> FEEDBACK
            FEEDBACK -.->|Auto-retrain| TRAIN
        end
    end

    style REGISTRY fill:#ff6b6b,color:#fff
    style PROD fill:#4ecdc4,color:#fff
    style TRAIN fill:#45b7d1,color:#fff
```

## CI/CD/CT Pipeline

### Continuous Integration (CI)

```yaml
# Example: CI pipeline steps
ci_pipeline:
  steps:
    - lint:
        - black --check .
        - pylint src/
        - mypy src/

    - unit_test:
        - pytest tests/unit/ -v --cov

    - data_validation:
        - great_expectations checkpoint run training_data

    - build:
        - docker build -t ml-pipeline:${VERSION} .
        - docker push ml-pipeline:${VERSION}
```

### Continuous Training (CT)

CT is unique to MLOps — it automates the retraining pipeline:

```python
# Trigger conditions for CT
def should_retrain():
    triggers = []

    # Scheduled retraining (e.g., every Monday)
    if is_scheduled_time():
        triggers.append("scheduled")

    # Data drift detected
    if drift_score > threshold:
        triggers.append("data_drift")

    # Performance degradation
    if current_f1 < baseline_f1 - margin:
        triggers.append("performance_drop")

    # New data volume threshold
    if new_data_rows_since_last_train > 100000:
        triggers.append("new_data_volume")

    return len(triggers) > 0
```

### Continuous Delivery (CD)

| Strategy | Description | Rollback Speed |
|----------|-------------|---------------|
| **Shadow Deployment** | Mirror traffic to new model (no user impact) | Instant |
| **Canary Deployment** | Route X% of traffic to new model | Update routing |
| **A/B Testing** | Split traffic, compare business metrics | Update routing |
| **Blue/Green** | Full switch between old and new | Instant |
| **Multi-Armed Bandit** | Dynamically route to best-performing model | Automatic |

> **Deep dive on deployment strategies**: See [Model Inference Architecture](05-model-inference-architecture.md).

## Maturity Model

```mermaid
graph LR
    L0[Level 0<br/>Manual] --> L1[Level 1<br/>Automated<br/>Training]
    L1 --> L2[Level 2<br/>CI/CD<br/>Pipeline]
    L2 --> L3[Level 3<br/>Full MLOps<br/>Auto-retrain]

    style L0 fill:#ff6b6b,color:#fff
    style L1 fill:#f9ca24,color:#000
    style L2 fill:#4ecdc4,color:#fff
    style L3 fill:#96ceb4,color:#fff
```

| Level | Characteristics | When |
|-------|----------------|------|
| **0: Manual** | Notebooks, manual deploy, no versioning | POC, exploration |
| **1: Automated Training** | Scripted training, experiment tracking, model registry | Small team, few models |
| **2: CI/CD Pipeline** | Automated build/test/deploy, monitoring | Multiple models, growing team |
| **3: Full MLOps** | Auto-retrain on drift, feature store, full governance | Enterprise, dozens of models |

### Level Migration Signals

| From → To | Signal |
|-----------|--------|
| 0 → 1 | "I can't reproduce last month's results" |
| 1 → 2 | "Deploying takes 2 days and something always breaks" |
| 2 → 3 | "We have 20 models and can't manually monitor them all" |

## Model Monitoring & Drift

### Types of Drift

| Drift Type | What Changes | Detection Method |
|------------|-------------|-----------------|
| **Data Drift** | Input feature distribution shifts | KS test, PSI, Jensen-Shannon divergence |
| **Concept Drift** | Relationship between features and target changes | Model performance degradation over time |
| **Prediction Drift** | Model output distribution shifts | Compare prediction distributions |
| **Feature Drift** | Individual feature statistics change | Mean, variance, quantile comparisons |

### Monitoring Dashboard

```
┌──────────────────────────────────────────────────────────┐
│  Model Monitoring Dashboard                               │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  📊 Prediction Volume    ████████████ 12,345 req/s       │
│  ⏱️  P99 Latency          ████         45ms               │
│  🎯 Accuracy (7-day)     ████████     0.94 → 0.91 ⚠️     │
│  📉 Data Drift Score     ██████████   0.15 → 0.42 🔴     │
│  🔄 Days Since Retrain   ██           14 days            │
│                                                           │
│  ⚠️  ALERT: Data drift exceeding threshold (0.3)          │
│  💡 SUGGESTION: Trigger retraining pipeline               │
└──────────────────────────────────────────────────────────┘
```

### Drift Response

```mermaid
graph TD
    DRIFT[Drift Detected] --> SEVERITY{Severity?}

    SEVERITY -->|"Low (< threshold)"| LOG[Log & Continue<br/>Monitoring]
    SEVERITY -->|Medium| INVESTIGATE[Investigate Root Cause<br/>Feature analysis]
    SEVERITY -->|High| RETRAIN[Auto-Trigger<br/>Retraining]
    SEVERITY -->|Critical| ROLLBACK[Rollback to<br/>Previous Model]

    INVESTIGATE --> CAUSE{Root Cause?}
    CAUSE -->|Seasonal| ADJUST[Adjust Baseline]
    CAUSE -->|Data Pipeline Bug| FIX[Fix & Re-ingest]
    CAUSE -->|Real Distribution Change| RETRAIN2[Schedule Retrain]

    style DRIFT fill:#ff6b6b,color:#fff
    style RETRAIN fill:#4ecdc4,color:#fff
    style ROLLBACK fill:#f9ca24,color:#000
```

## Governance & Compliance

| Aspect | Implementation |
|--------|---------------|
| **Model Cards** | Document intended use, limitations, fairness evaluation |
| **Audit Trail** | Log all: data versions, training params, who deployed, when |
| **Fairness** | Measure demographic parity, equal opportunity across groups |
| **Explainability** | SHAP, LIME for feature importance; model cards for transparency |
| **Approval Gates** | Manual approval before production deployment |
| **Data Lineage** | Track data from source → feature → model → prediction |

## Decision Framework

```mermaid
graph TD
    Q1{Number of models<br/>in production?} -->|1-2| MANUAL[Level 0-1<br/>Manual pipelines]
    Q1 -->|3-10| Q2{Do models need<br/>frequent retraining?}
    Q1 -->|10+| Q3{Regulatory requirements?}

    Q2 -->|Monthly+| CI_CD[Level 2: CI/CD pipeline]
    Q2 -->|Weekly/Daily| FULL[Level 3: Full MLOps]

    Q3 -->|"High (finance, healthcare)"| GOVERNED[Full MLOps with<br/>governance & audit]
    Q3 -->|Low| FULL2[Level 3: Auto-retrain]

    style FULL fill:#4ecdc4,color:#fff
    style GOVERNED fill:#ff6b6b,color:#fff
    style CI_CD fill:#45b7d1,color:#fff
```

## Related Patterns

- [Machine Learning Pipeline Architecture](01-machine-learning-pipeline-architecture.md) — End-to-end pipeline design
- [Model Training Architecture](04-model-training-architecture.md) — Training at scale
- [Model Inference Architecture](05-model-inference-architecture.md) — Production serving
- [Feature Store Architecture](03-feature-store-architecture.md) — Feature consistency

> **Azure Implementation**: See [Azure Machine Learning](../../../architecture-azure/data/) (managed MLOps with pipelines, registry, endpoints), [Azure DevOps](https://azure.microsoft.com/en-us/products/devops/) (CI/CD integration), and [Azure Monitor](https://learn.microsoft.com/en-us/azure/azure-monitor/) (drift detection and alerting).

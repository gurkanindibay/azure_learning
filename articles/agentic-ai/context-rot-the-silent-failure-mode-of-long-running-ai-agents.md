---
type: Article
title: "Context Rot: The Silent Failure Mode of Long-Running AI Agents"
description: "How long-running AI agents degrade when accumulating cognitive debris, and why context engineering, active governance, pruning, and working-set management are essential for reliability."
generated: { by: process:okf-migrate, at: 2026-06-14T00:00:00Z }
source: "https://blog.stackademic.com/context-rot-the-silent-failure-mode-of-long-running-ai-agents-ae14616c0a88"
author: "Everton Gomede, PhD"
---

# Context Rot: The Silent Failure Mode of Long-Running AI Agents

> **Source**: [Stackademic / Medium](https://blog.stackademic.com/context-rot-the-silent-failure-mode-of-long-running-ai-agents-ae14616c0a88) (2026-06-14)  
> **Related**: [Context Rot](../../reference-dictionary/ai-ml-llm.md#context-rot), [Context Engineering](../../reference-dictionary/ai-ml-llm.md#context-engineering), [Context Governor](../../reference-dictionary/ai-ml-llm.md#context-governor), [Context Working Set](../../reference-dictionary/ai-ml-llm.md#context-working-set), [Cognitive Debris](../../reference-dictionary/ai-ml-llm.md#cognitive-debris), [Agent Harness](../../reference-dictionary/ai-ml-llm.md#agent-harness)

---

## Abstract

- **Context:** Long-running AI agents now operate across tools, memory, retrieval, and user history.
- **Problem:** More context often creates noise, drift, stale facts, and brittle reasoning.
- **Approach:** Treat context as governed state: route, retrieve, prune, compress, and audit.
- **Results:** Experiments showed strong routing, useful pruning, but residual irrelevant evidence.
- **Conclusion:** Agent reliability now depends on context engineering rather than context accumulation.

**Keywords**: context engineering; retrieval augmented generation; AI agents; enterprise RAG; AgentOps

## When More Context Makes the Agent Worse

What happens when an AI agent has all the information it needs and still makes the wrong decision? That is the uncomfortable reality behind context rot. In production systems, failures are not always caused by missing data, weak models, or poor prompts. Sometimes the agent fails because it has accumulated too much: too many retrieved documents, too many tool outputs, too many previous decisions, too many stale assumptions, and too many partially relevant facts competing for attention. The agent does not collapse dramatically. It degrades quietly. It starts to forget constraints that were explicit ten turns ago. It cites the wrong evidence. It follows a plan that was valid before a tool result contradicted it. It asks for information that the user already provided. It produces answers that sound coherent but are built on contaminated working memory.

For advanced AI practitioners, context rot is not a theoretical nuisance. It is a systems problem. It appears in RAG pipelines, coding agents, troubleshooting agents, research agents, customer-support bots, and multi-agent workflows. It becomes more visible as we push agents from short question-answer interactions into long-running operational tasks. The paradox is that the same mechanisms that make agents useful — memory, retrieval, tool use, planning, reflection, and long context windows — also create the conditions for degradation. The challenge is no longer simply about giving the model more context. The challenge is deciding what deserves to remain in context at each step of the reasoning.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*4Xc1yNN_Cv0WyJ0qYwljSQ.png)

> The best agents do not remember everything; they remember what still matters.

## The Challenge: Agents Accumulate Cognitive Debris

A conventional application has a relatively clean state. A database row, an API response, a transaction log, or a configuration file has structure and a lifecycle. An AI agent, by contrast, often operates inside a messy mixture of natural language, tool traces, retrieved passages, intermediate hypotheses, user corrections, previous summaries, and hidden orchestration instructions. This mixture becomes the agent’s working environment. Over time, it accumulates cognitive debris: information that was once useful but is no longer relevant, evidence that is related but not decisive, assumptions that have expired, and summaries that compress away important uncertainty.

This is especially dangerous because large language models are highly tolerant of surface-level noise. They can produce fluent outputs even when their internal context is inconsistent. In many applications, this creates a deceptive failure mode. The agent does not say, “My working memory is polluted.” It simply answers with misplaced confidence. In a Cisco troubleshooting agent, for example, context rot might cause the system to mix a current BGP adjacency issue with an old OSPF incident, a stale TAC case, and unrelated wireless-controller logs. In a coding agent, it might continue applying instructions from a previous architecture after the repository has changed. In a legal or compliance assistant, it might blend current policy with deprecated guidance. The model is not necessarily hallucinating from nothing; it is often hallucinating from a badly managed context.

The core challenge is that context is not neutral. Every token in the prompt competes for the model's attention. Irrelevant context is not harmless background material; it actively changes the probability distribution of the next answer. Contradictory context does not politely sit on the sidelines; it creates ambiguity. Stale context does not label itself as obsolete; it can appear authoritative simply because it is present. This means that context engineering is not prompt decoration. It is a form of runtime information governance.

## The Insight: Context Quality Matters More Than Context Quantity

The instinctive response to context rot is to ask for a larger context window. That helps only up to a point. A larger window allows the system to include more information, but it does not solve the selection problem. In fact, it may make the problem worse by reducing the pressure to curate. The practitioner’s insight is simple: agent reliability depends less on how much context the model can hold and more on how well the system manages context relevance, freshness, authority, and task alignment.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*fM7h4DqExGEDQ6MISAdAvg.png)

A useful way to think about context rot is as a failure of context lifecycle management. Information enters the agent through the user, retrieval system, memory layer, tool calls, intermediate reasoning steps, and prior outputs. But in many systems, information does not leave cleanly. Old tool results remain visible. Early hypotheses remain semantically active. Retrieved chunks remain in the prompt after they are superseded. Summaries become detached from their original evidence. The agent’s context becomes a landfill rather than a working set.

For practitioners, this reframes the problem. The goal is not to maximize recall at every step. The goal is to maintain a compact, high-signal operational state. The agent should know the current task, which facts are confirmed, which are uncertain, which assumptions have been invalidated, which tools have already been used, what evidence supports the current hypothesis, and what decision must be made next. Everything else should either be excluded, compressed, archived, or retrieved only on demand.

A mature agent architecture treats context as a controlled resource with explicit policies:

1. **Relevance:** Does this information directly affect the next decision?
2. **Freshness:** Is this information still valid after recent tool results or user corrections?
3. **Authority:** Is this source more reliable than conflicting evidence?
4. **Specificity:** Is this context tied to the current entity, version, device, customer, ticket, or codebase?
5. **Traceability:** Can the agent point back to the original evidence if challenged?
6. **Compression safety:** Can this be summarized without losing uncertainty, exceptions, or constraints?

These questions turn context management from an ad hoc prompt-building task into an engineering discipline.

## The Failure Pattern: From Useful Memory to Semantic Contamination

Context rot usually follows a recognizable progression. First, the agent receives a clear task and performs well because the context is small and aligned. Next, it retrieves documents, calls tools, asks clarifying questions, and forms intermediate hypotheses. At this stage, the agent may actually improve because it has gathered more evidence. Then the context begins to saturate. Old hypotheses remain in the prompt. Tool outputs are appended rather than distilled. Retrieval adds overlapping chunks. The user changes direction, but previous instructions remain active. Eventually, the model starts optimizing against a context that no longer represents the real task.

This pattern is common in troubleshooting workflows. Early in the session, the agent may correctly identify that packet loss began after a routing change. Later, after examining logs, configuration diffs, and monitoring alerts, the agent may drift toward an unrelated interface error because that error appears frequently in the context. Even worse, the agent may combine multiple partial explanations into a synthetic conclusion: “The outage was caused by an interface flap that triggered BGP instability due to an OSPF misconfiguration,” even if the evidence only supports one part of that statement. The output sounds plausible because each fragment came from a real source. The reasoning is wrong because the fragments were not governed.

This is why context rot is more subtle than hallucination. A hallucination may be fabricated. Context rot often emerges from real information used at the wrong time, at the wrong priority, or under the wrong assumption. The agent is not inventing randomly; it is overfitting to its own accumulated context.

## The Practitioner’s Model: Context as a Working Set

A robust agent should not treat the prompt as a transcript. It should treat context as a working set. In operating-system terms, the working set contains the pages needed for the current computation. In agent terms, the working set contains the facts, constraints, evidence, and instructions needed for the next reasoning step. Everything else belongs in memory, logs, archives, or retrievable storage — not necessarily in the immediate prompt.

This distinction is critical. Conversation history is not the same as the state. Retrieved documents are not the same as evidence. Tool outputs are not the same as conclusions. A summary is not the same as ground truth. Once these categories are separated, the agent can manage them differently.

A practical context architecture should separate at least five layers:

1. **Instruction context:** stable system rules, safety constraints, domain policies, and output requirements.
2. **Task state:** the current objective, scope, entities, constraints, and success criteria.
3. **Evidence state:** verified facts, source references, tool results, and confidence levels.
4. **Reasoning state:** current hypotheses, rejected hypotheses, open questions, and next actions.
5. **Historical context:** prior conversation, archived traces, previous attempts, and long-term memory.

The mistake is to flatten all five layers into one prompt. Once flattened, the model must infer which parts are authoritative, current, or relevant. That is fragile. The better design is to keep these layers explicit and promote only the required elements into the active context.

## Application: Designing Agents That Resist Context Rot

The first practical defense is aggressive context pruning. This does not mean deleting useful information. It means separating active context from available context. A network troubleshooting agent may have access to thousands of logs, prior TAC cases, vendor documents, and device configurations. But the active prompt should contain only the narrow set of evidence needed for the current diagnostic step. The rest should remain addressable through retrieval or tool calls.

The second defense is a structured state. Instead of relying on a free-form conversation transcript, the agent should maintain a machine-readable state object. For example, a troubleshooting agent might maintain fields such as affected device, affected interface, protocol, symptom onset time, confirmed errors, rejected causes, current hypothesis, next diagnostic command, and confidence. This state should be updated after every meaningful interaction. The model can still reason in natural language, but the system should not rely solely on natural language to retain operational facts.

The third defense is evidence ranking. RAG systems often optimize retrieval relevance, but context rot requires a stricter standard: decision relevance. A document may be semantically similar to the user’s query but operationally irrelevant because it refers to a different version, device family, time period, topology, or customer environment. Advanced agents should rerank retrieved context using metadata and task state, rather than relying solely on embedding similarity. In practice, this means filtering by product, software version, timestamp, topology role, severity, source authority, and diagnostic stage.

The fourth defense is stale-context invalidation. When new evidence contradicts old assumptions, the old assumptions must be explicitly marked as invalid. It is not enough to append the new result and hope the model resolves the contradiction. The state should say: “Previous hypothesis rejected because command output showed X.” This prevents old hypotheses from continuing to influence later reasoning.

The fifth defense is summary discipline. Summarization is necessary in long-running agents, but bad summaries accelerate context rot. A good operational summary should preserve uncertainty, decisions, evidence, and invalidations. A weak summary says, “The issue may be related to routing instability.” A better summary says, “Confirmed: BGP session to peer 10.0.0.2 reset three times between 09:12 and 09:18. Rejected: physical interface flap; interface counters stable. Open hypothesis: hold timer expiry due to packet loss or control-plane policing. Next step: inspect CPU and CoPP drops.” The difference is not style. The difference is whether the summary can safely replace the raw context for the next step.

## A Context-Rot-Resistant Agent Loop

A production-grade agent loop should not simply run: user message → retrieve → reason → answer. That pipeline is too loose for complex work. A more robust loop looks like this:

1. **Parse the task:** identify objective, entities, constraints, and expected output.
2. **Load active state:** bring in only the current operational state, not the entire transcript.
3. **Retrieve selectively:** query external memory based on the current state and decision need.
4. **Rank by decision relevance:** prioritize sources by freshness, authority, specificity, and conflict status.
5. **Execute tools:** call tools with narrow inputs and capture structured outputs.
6. **Update state:** record confirmed facts, rejected hypotheses, and unresolved questions.
7. **Prune context:** remove or archive information that no longer affects the next decision.
8. **Generate response:** produce an answer grounded in the active state and cited evidence where appropriate.
9. **Persist trace:** store the full audit trail outside the immediate prompt.

This loop treats the agent as a stateful system rather than a growing conversation. That shift is essential for reliability. The transcript remains useful for auditability, but it should not be the primary runtime memory.

## What to Measure

Context rot must be measured, not merely discussed. In practice, teams should evaluate agents across increasing context length, increasing retrieval noise, conflicting evidence, stale memory, and multi-turn task changes. A system that performs well on clean single-turn benchmarks may fail under realistic context pressure.

Useful evaluation scenarios include:

1. **Needle retention:** can the agent preserve an important constraint after many irrelevant turns?
2. **Stale fact rejection:** can the agent ignore information that was later contradicted?
3. **Conflict resolution:** can the agent choose the more authoritative source when two sources disagree?
4. **Retrieval noise tolerance:** does performance degrade when semantically similar but irrelevant documents are added?
5. **Task drift resistance:** does the agent maintain the current objective after side discussions?
6. **State consistency:** do final answers match the structured state accumulated during the workflow?

The most important metric is not whether the model can read a long prompt. The important metric is whether the agent can maintain decision quality as context complexity increases.

## Code Walkthrough

The classifier acts as a **router**, the TF-IDF retriever acts as a **memory tool**, the stale-memory injector simulates **context rot**, and the `ContextGovernor` decides what evidence is allowed into the agent’s active working context. The most important design idea is that the agent does not unthinkingly append every retrieved chunk, previous memory fragment, or stale document into the prompt. It classifies the task, retrieves candidate evidence, penalizes stale memory, applies a context budget, rejects low-value material, and generates an answer only from the governed working set. In a real LLM-based system, the final `generate_answer()` method would be replaced by an LLM call, but the context-governance layer should remain outside the model as explicit infrastructure.

```python
"""
Context Rot in a More Agentic Text System
========================================

Dataset:
- 20 Newsgroups from scikit-learn.
- This is a widely used text classification benchmark.
- We use it as a stand-in for a production agent corpus: support tickets, TAC notes,
  incident reports, knowledge-base articles, or discussion threads.

Core idea:
- Context rot happens when an AI agent accumulates too much irrelevant, stale,
  contradictory, or low-value context.
- This example builds a lightweight "agent" that:
    1. Loads a text corpus.
    2. Trains a topic classifier.
    3. Builds a retrieval index.
    4. Accepts user-like text queries.
    5. Retrieves evidence.
    6. Simulates context rot by injecting stale/noisy memory.
    7. Uses a context governor to keep only relevant working context.
    8. Produces an answer grounded in selected evidence.
    9. Evaluates and visualizes performance.

Why no external LLM API?
- The goal is to make the example runnable anywhere.
- The "agentic" behavior is implemented through planning, routing, retrieval,
  memory management, and context pruning.
- In a production system, the final template-based answer could be replaced by
  an LLM call, while keeping the same context-governance layer.
"""

# ============================================================
# Imports
# ============================================================

import re
import textwrap
import random
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.datasets import fetch_20newsgroups
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)
from sklearn.metrics.pairwise import cosine_similarity

# ============================================================
# Global Configuration
# ============================================================

RANDOM_STATE = 42

# We keep the number of classes small so the example runs quickly.
# In an enterprise agent, these categories could be:
# routing, switching, wireless, security, system, application, storage, etc.
CATEGORIES = [
    "sci.space",
    "rec.autos",
    "comp.graphics",
    "talk.politics.misc",
]

# ============================================================
# Utility Functions
# ============================================================

def clean_text(text: str) -> str:
    """
    Normalize raw text.

    Why:
    Agents often receive messy context: email threads, logs, quoted replies,
    pasted documents, ticket history, and tool outputs. Basic cleanup reduces
    accidental noise before retrieval or classification.
    """

    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-z0-9.,:;!?()/%$+\-\s]", " ", text)
    return text.strip()

def shorten(text: str, width: int = 350) -> str:
    """
    Shorten text for readable display.

    Why:
    In context-governed agents, every displayed or injected chunk should be
    intentionally bounded. This prevents raw documents from overwhelming the
    agent's working context.
    """

    return textwrap.shorten(text.replace("\n", " "), width=width, placeholder="...")

# ============================================================
# 1. Data Loading
# ============================================================

def load_text_dataset(
    categories: List[str] = CATEGORIES,
    random_state: int = RANDOM_STATE
) -> pd.DataFrame:
    """
    Load the 20 Newsgroups text dataset.

    Why:
    This gives us a real benchmark corpus from a library rather than synthetic
    examples. In a real agent, this corpus could be historical tickets,
    troubleshooting cases, knowledge-base articles, or incident reports.
    """

    dataset = fetch_20newsgroups(
        subset="all",
        categories=categories,
        remove=("headers", "footers", "quotes"),
        shuffle=True,
        random_state=random_state,
    )

    df = pd.DataFrame(
        {
            "text": dataset.data,
            "target": dataset.target,
            "label": [dataset.target_names[i] for i in dataset.target],
        }
    )

    df["clean_text"] = df["text"].apply(clean_text)
    df["char_len"] = df["clean_text"].str.len()
    df["word_len"] = df["clean_text"].str.split().apply(len)

    # Remove extremely short texts, because they behave like low-information
    # context chunks. In agent systems, tiny fragments often create retrieval noise.
    df = df[df["word_len"] >= 20].reset_index(drop=True)

    print("\n=== DATA LOADING ===")
    print(f"Loaded documents: {len(df)}")
    print(f"Labels: {sorted(df['label'].unique())}")

    return df

# ============================================================
# 2. EDA
# ============================================================

def run_eda(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform exploratory data analysis.

    Why:
    Before trusting an agent corpus, inspect the distribution of labels and
    document lengths. In production, this is equivalent to asking:
    - Are some issue types underrepresented?
    - Are some documents too short to be useful?
    - Are some documents too long and likely to dominate context?
    """

    print("\n=== EDA ===")

    class_counts = df["label"].value_counts()
    length_summary = df.groupby("label")["word_len"].describe()

    print("\nClass counts:")
    print(class_counts)

    print("\nDocument length summary by class:")
    print(length_summary[["count", "mean", "std", "min", "50%", "max"]])

    print("\nSample document:")
    sample = df.sample(1, random_state=RANDOM_STATE).iloc[0]
    print(f"Label: {sample['label']}")
    print(shorten(sample["clean_text"], width=600))

    return {
        "class_counts": class_counts,
        "length_summary": length_summary,
    }

# ============================================================
# 3. Feature Engineering
# ============================================================

def split_data(
    df: pd.DataFrame,
    test_size: float = 0.25,
    random_state: int = RANDOM_STATE
):
    """
    Split documents into train and test sets.

    Why:
    The agent must be tested on unseen text. Otherwise we only measure whether
    it remembers the training corpus, not whether it generalizes.
    """

    X_train, X_test, y_train, y_test = train_test_split(
        df["clean_text"],
        df["label"],
        test_size=test_size,
        stratify=df["label"],
        random_state=random_state,
    )

    print("\n=== TRAIN/TEST SPLIT ===")
    print(f"Train documents: {len(X_train)}")
    print(f"Test documents: {len(X_test)}")

    return X_train, X_test, y_train, y_test

# ============================================================
# 4. Model Selection and Hyperparameter Tuning
# ============================================================

def tune_text_classifier(
    X_train: pd.Series,
    y_train: pd.Series,
    random_state: int = RANDOM_STATE
):
    """
    Train and tune text classifiers using cross-validation.

    Why:
    In an agent, model selection determines how the system routes the user's
    problem. A weak router sends the agent to the wrong tool, wrong memory,
    wrong policy, or wrong evidence set.

    We compare:
    - Logistic Regression: strong linear baseline for TF-IDF text.
    - Multinomial Naive Bayes: classic probabilistic text baseline.

    TF-IDF is used because it converts raw text into weighted features.
    It also acts as a primitive relevance mechanism: frequent but uninformative
    terms receive less weight than discriminative terms.
    """

    pipeline = Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    stop_words="english",
                    lowercase=True,
                    strip_accents="unicode",
                ),
            ),
            ("model", LogisticRegression(max_iter=3000, random_state=random_state)),
        ]
    )

    param_grid = [
        {
            "tfidf__ngram_range": [(1, 1), (1, 2)],
            "tfidf__min_df": [2, 5],
            "tfidf__max_df": [0.8, 0.95],
            "model": [LogisticRegression(max_iter=3000, random_state=random_state)],
            "model__C": [0.1, 1.0, 3.0],
        },
        {
            "tfidf__ngram_range": [(1, 1), (1, 2)],
            "tfidf__min_df": [2, 5],
            "tfidf__max_df": [0.8, 0.95],
            "model": [MultinomialNB()],
            "model__alpha": [0.1, 0.5, 1.0],
        },
    ]

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=random_state,
    )

    search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        scoring="f1_macro",
        cv=cv,
        n_jobs=-1,
        verbose=1,
        return_train_score=True,
    )

    print("\n=== MODEL SELECTION + HYPERPARAMETER TUNING ===")
    search.fit(X_train, y_train)

    print("\nBest CV macro-F1:")
    print(f"{search.best_score_:.4f}")

    print("\nBest parameters:")
    print(search.best_params_)

    cv_results = pd.DataFrame(search.cv_results_).sort_values("rank_test_score")

    print("\nTop 5 configurations:")
    display_cols = [
        "rank_test_score",
        "mean_test_score",
        "std_test_score",
        "mean_train_score",
        "param_model",
        "param_tfidf__ngram_range",
        "param_tfidf__min_df",
        "param_tfidf__max_df",
    ]
    print(cv_results[display_cols].head())

    return search.best_estimator_, cv_results

# ============================================================
# 5. Prediction and Evaluation
# ============================================================

def evaluate_classifier(
    model,
    X_test: pd.Series,
    y_test: pd.Series
) -> Dict[str, Any]:
    """
    Evaluate the tuned classifier.

    Why:
    The classifier is the agent's routing component.
    If routing is wrong, downstream retrieval and reasoning become polluted.
    This mirrors context rot: bad upstream context selection causes bad downstream answers.
    """

    print("\n=== PREDICTION + EVALUATION ===")

    y_pred = model.predict(X_test)

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "macro_f1": f1_score(y_test, y_pred, average="macro"),
        "weighted_f1": f1_score(y_test, y_pred, average="weighted"),
    }

    print("\nMetrics:")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")

    print("\nClassification report:")
    print(classification_report(y_test, y_pred))

    cm = confusion_matrix(y_test, y_pred, labels=model.classes_)

    return {
        "y_pred": y_pred,
        "metrics": metrics,
        "confusion_matrix": cm,
        "classes": model.classes_,
    }

# ============================================================
# 6. Retrieval Index
# ============================================================

@dataclass
class RetrievedDocument:
    doc_id: int
    label: str
    score: float
    text: str
    source: str = "retrieval"

class TfidfRetriever:
    """
    Simple TF-IDF retriever.

    Why:
    RAG agents depend on retrieval quality. A retriever should provide relevant
    context, not just more context. This class gives the agent a searchable
    memory over training documents.
    """

    def __init__(self, max_features: int = 30000):
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            lowercase=True,
            strip_accents="unicode",
            min_df=2,
            max_df=0.95,
            ngram_range=(1, 2),
            max_features=max_features,
        )
        self.doc_matrix = None
        self.documents = None

    def fit(self, documents: pd.DataFrame):
        self.documents = documents.reset_index(drop=True)
        self.doc_matrix = self.vectorizer.fit_transform(self.documents["clean_text"])
        return self

    def retrieve(self, query: str, top_k: int = 8) -> List[RetrievedDocument]:
        query_vec = self.vectorizer.transform([clean_text(query)])
        scores = cosine_similarity(query_vec, self.doc_matrix).ravel()

        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            row = self.documents.iloc[idx]
            results.append(
                RetrievedDocument(
                    doc_id=int(idx),
                    label=row["label"],
                    score=float(scores[idx]),
                    text=row["clean_text"],
                    source="retrieval",
                )
            )

        return results

# ============================================================
# 7. Agent State and Context Governance
# ============================================================

@dataclass
class AgentState:
    """
    Stateful memory for the agent.

    Why:
    A real agent should not rely on an ever-growing transcript.
    It needs a structured state that separates:
    - current objective
    - retrieved evidence
    - stale memory
    - selected working context
    - rejected context
    """

    user_query: str = ""
    predicted_topic: str = ""
    topic_confidence: float = 0.0
    retrieved_docs: List[RetrievedDocument] = field(default_factory=list)
    stale_memory: List[RetrievedDocument] = field(default_factory=list)
    working_context: List[RetrievedDocument] = field(default_factory=list)
    rejected_context: List[RetrievedDocument] = field(default_factory=list)
    final_answer: str = ""

class ContextGovernor:
    """
    Selects which context is allowed into the active working set.

    Why:
    This is the central anti-context-rot mechanism.
    The retriever may return useful evidence, but the agent may also carry stale
    memory from previous steps. The governor prevents old or irrelevant context
    from dominating the answer.
    """

    def __init__(
        self,
        min_relevance_score: float = 0.05,
        max_docs: int = 5,
        max_total_chars: int = 2500,
    ):
        self.min_relevance_score = min_relevance_score
        self.max_docs = max_docs
        self.max_total_chars = max_total_chars

    def select_working_context(
        self,
        query: str,
        retrieved_docs: List[RetrievedDocument],
        stale_memory: List[RetrievedDocument],
    ) -> Tuple[List[RetrievedDocument], List[RetrievedDocument]]:
        """
        Keep high-value context and reject low-value context.

        Policy:
        - Prefer fresh retrieved documents over stale memory.
        - Penalize stale memory so it must be highly relevant to survive.
        - Enforce a context budget so the final answer is not polluted by volume.
        """

        candidates = []

        for doc in retrieved_docs:
            candidates.append(doc)

        for doc in stale_memory:
            # Stale memory is not always useless, but it is dangerous.
            # We penalize it to simulate freshness-aware context management.
            penalized = RetrievedDocument(
                doc_id=doc.doc_id,
                label=doc.label,
                score=doc.score * 0.45,
                text=doc.text,
                source="stale_memory_penalized",
            )
            candidates.append(penalized)

        # Sort by relevance after freshness penalty.
        candidates = sorted(candidates, key=lambda d: d.score, reverse=True)

        selected = []
        rejected = []
        used_chars = 0

        for doc in candidates:
            doc_chars = len(doc.text)

            should_keep = (
                doc.score >= self.min_relevance_score
                and len(selected) < self.max_docs
                and used_chars + doc_chars <= self.max_total_chars
            )

            if should_keep:
                selected.append(doc)
                used_chars += doc_chars
            else:
                rejected.append(doc)

        return selected, rejected

# ============================================================
# 8. Agent Implementation
# ============================================================

class ContextRotAwareTextAgent:
    """
    A small text agent with:
    - classifier-based routing
    - retrieval
    - stale memory injection
    - context pruning
    - answer generation

    Why:
    This mirrors the architecture of a practical RAG agent, but keeps everything
    deterministic and runnable without an LLM API.
    """

    def __init__(
        self,
        classifier,
        retriever: TfidfRetriever,
        context_governor: ContextGovernor,
        label_examples: Dict[str, str],
        random_state: int = RANDOM_STATE,
    ):
        self.classifier = classifier
        self.retriever = retriever
        self.context_governor = context_governor
        self.label_examples = label_examples
        self.rng = random.Random(random_state)

    def classify_query(self, query: str) -> Tuple[str, float]:
        """
        Predict the most likely topic for the user query.

        Why:
        Agentic systems often route tasks before answering.
        Routing determines which tools, documents, and policies should be used.
        """

        predicted = self.classifier.predict([clean_text(query)])[0]

        if hasattr(self.classifier, "predict_proba"):
            proba = self.classifier.predict_proba([clean_text(query)])[0]
            class_index = list(self.classifier.classes_).index(predicted)
            confidence = float(proba[class_index])
        else:
            confidence = 0.0

        return predicted, confidence

    def inject_stale_memory(
        self,
        all_train_docs: pd.DataFrame,
        n_stale_docs: int = 4,
    ) -> List[RetrievedDocument]:
        """
        Simulate context rot by adding irrelevant memory.

        Why:
        In real agents, stale memory can come from:
        - previous user sessions
        - old tickets
        - previous tool outputs
        - outdated documentation
        - earlier hypotheses that were never invalidated

        We intentionally inject random documents to test whether the context
        governor can suppress irrelevant context.
        """

        sample = all_train_docs.sample(
            n=n_stale_docs,
            random_state=self.rng.randint(1, 999999),
        ).reset_index(drop=True)

        stale = []
        for idx, row in sample.iterrows():
            stale.append(
                RetrievedDocument(
                    doc_id=int(idx),
                    label=row["label"],
                    score=0.12,
                    text=row["clean_text"],
                    source="stale_memory_raw",
                )
            )

        return stale

    def generate_answer(self, state: AgentState) -> str:
        """
        Generate a grounded answer from the selected working context.

        Why:
        This is where a production system would call an LLM.
        However, the key idea is that the LLM should only see the governed
        working context, not every retrieved document and stale memory fragment.
        """

        if not state.working_context:
            return (
                "I could not find enough reliable context to answer. "
                "The safe action is to retrieve more targeted evidence before making a decision."
            )

        evidence_labels = pd.Series([doc.label for doc in state.working_context])
        dominant_evidence_label = evidence_labels.value_counts().idxmax()

        evidence_snippets = []
        for i, doc in enumerate(state.working_context, start=1):
            evidence_snippets.append(
                f"{i}. [{doc.source} | label={doc.label} | score={doc.score:.3f}] "
                f"{shorten(doc.text, width=260)}"
            )

        answer = f"""
Agent decision:
The query is most likely associated with topic: {state.predicted_topic}
Classifier confidence: {state.topic_confidence:.3f}

Evidence check:
The dominant label among selected evidence is: {dominant_evidence_label}

Context-governance interpretation:
The agent did not use all available context. It selected only the highest-scoring,
freshest, budget-compatible evidence. This reduces the risk of context rot, where
old or irrelevant memory competes with the current task.

Selected evidence:
{chr(10).join(evidence_snippets)}

Practical answer:
Based on the routed topic and selected evidence, the query appears to belong to
the '{state.predicted_topic}' area. If this were a production AI agent, the next
step would be to call the specialized toolchain for that topic rather than
mixing unrelated context into the response.
"""
        return textwrap.dedent(answer).strip()

    def answer(
        self,
        query: str,
        all_train_docs: pd.DataFrame,
        top_k: int = 8,
        n_stale_docs: int = 4,
    ) -> AgentState:
        """
        Full agent loop.

        Agent loop:
        1. Receive user query.
        2. Classify the query to route the task.
        3. Retrieve candidate evidence.
        4. Inject stale memory to simulate context rot.
        5. Apply context governance.
        6. Generate final answer from governed working context.

        Why:
        This is the operational version of the essay's thesis:
        a reliable agent is not the one that keeps the most context;
        it is the one that keeps the right context.
        """

        state = AgentState(user_query=query)

        # Step 1: Route the query.
        state.predicted_topic, state.topic_confidence = self.classify_query(query)

        # Step 2: Retrieve fresh evidence.
        state.retrieved_docs = self.retriever.retrieve(query, top_k=top_k)

        # Step 3: Add noisy/stale memory to simulate context rot.
        state.stale_memory = self.inject_stale_memory(
            all_train_docs=all_train_docs,
            n_stale_docs=n_stale_docs,
        )

        # Step 4: Context governor decides what survives.
        state.working_context, state.rejected_context = (
            self.context_governor.select_working_context(
                query=query,
                retrieved_docs=state.retrieved_docs,
                stale_memory=state.stale_memory,
            )
        )

        # Step 5: Generate final answer only from selected context.
        state.final_answer = self.generate_answer(state)

        return state

# ============================================================
# 9. Agent Evaluation
# ============================================================

def evaluate_agent_retrieval(
    agent: ContextRotAwareTextAgent,
    test_df: pd.DataFrame,
    train_df: pd.DataFrame,
    n_examples: int = 80,
    random_state: int = RANDOM_STATE,
) -> pd.DataFrame:
    """
    Evaluate whether the agent's selected working context matches the true label.

    Why:
    In real RAG agents, final answer quality depends on whether the working
    context contains relevant evidence. We measure whether the dominant selected
    context label matches the test document's true label.
    """

    sample = test_df.sample(
        n=min(n_examples, len(test_df)),
        random_state=random_state,
    ).reset_index(drop=True)

    records = []

    for _, row in sample.iterrows():
        query = row["clean_text"]

        state = agent.answer(
            query=query,
            all_train_docs=train_df,
            top_k=8,
            n_stale_docs=5,
        )

        if state.working_context:
            selected_labels = pd.Series([doc.label for doc in state.working_context])
            dominant_context_label = selected_labels.value_counts().idxmax()
        else:
            dominant_context_label = "none"

        records.append(
            {
                "true_label": row["label"],
                "predicted_topic": state.predicted_topic,
                "dominant_context_label": dominant_context_label,
                "topic_correct": row["label"] == state.predicted_topic,
                "context_correct": row["label"] == dominant_context_label,
                "n_retrieved": len(state.retrieved_docs),
                "n_stale": len(state.stale_memory),
                "n_selected": len(state.working_context),
                "n_rejected": len(state.rejected_context),
            }
        )

    eval_df = pd.DataFrame(records)

    print("\n=== AGENT RETRIEVAL / CONTEXT GOVERNANCE EVALUATION ===")
    print(f"Topic routing accuracy: {eval_df['topic_correct'].mean():.4f}")
    print(f"Dominant working-context accuracy: {eval_df['context_correct'].mean():.4f}")
    print("\nAverage context counts:")
    print(eval_df[["n_retrieved", "n_stale", "n_selected", "n_rejected"]].mean())

    return eval_df

# ============================================================
# 10. Visualization
# ============================================================

def visualize_results(
    df: pd.DataFrame,
    classifier_eval: Dict[str, Any],
    cv_results: pd.DataFrame,
    agent_eval_df: pd.DataFrame,
):
    """
    Visualize dataset, classifier performance, and agent context behavior.

    Why:
    Observability is essential in context-rot-resistant systems.
    You need to see:
    - class balance
    - classifier errors
    - model-selection behavior
    - how much context the governor rejects
    """

    print("\n=== VISUALIZATION ===")

    # -------------------------------
    # Class distribution
    # -------------------------------
    plt.figure(figsize=(8, 4))
    df["label"].value_counts().sort_index().plot(kind="bar")
    plt.title("Document Count by Topic")
    plt.xlabel("Topic")
    plt.ylabel("Documents")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.show()

    # -------------------------------
    # Document length distribution
    # -------------------------------
    plt.figure(figsize=(8, 4))
    df.boxplot(column="word_len", by="label", rot=30)
    plt.title("Document Length by Topic")
    plt.suptitle("")
    plt.xlabel("Topic")
    plt.ylabel("Word Count")
    plt.tight_layout()
    plt.show()

    # -------------------------------
    # Confusion matrix
    # -------------------------------
    ConfusionMatrixDisplay(
        confusion_matrix=classifier_eval["confusion_matrix"],
        display_labels=classifier_eval["classes"],
    ).plot(xticks_rotation=30)
    plt.title("Classifier Confusion Matrix")
    plt.tight_layout()
    plt.show()

    # -------------------------------
    # CV model comparison
    # -------------------------------
    top_cv = cv_results.head(12).copy()
    top_cv["model_name"] = top_cv["param_model"].astype(str).str[:35]

    plt.figure(figsize=(9, 5))
    plt.barh(
        range(len(top_cv)),
        top_cv["mean_test_score"].iloc[::-1],
    )
    plt.yticks(
        range(len(top_cv)),
        [
            f"rank {r} | {m}"
            for r, m in zip(
                top_cv["rank_test_score"].iloc[::-1],
                top_cv["model_name"].iloc[::-1],
            )
        ],
    )
    plt.title("Top Cross-Validated Model Configurations")
    plt.xlabel("Mean CV Macro-F1")
    plt.tight_layout()
    plt.show()

    # -------------------------------
    # Agent context counts
    # -------------------------------
    avg_counts = agent_eval_df[
        ["n_retrieved", "n_stale", "n_selected", "n_rejected"]
    ].mean()

    plt.figure(figsize=(7, 4))
    avg_counts.plot(kind="bar")
    plt.title("Average Agent Context Flow")
    plt.ylabel("Average Number of Documents")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.show()

# ============================================================
# 11. Full Wrapper Function
# ============================================================

def run_agentic_context_rot_text_example(
    categories: List[str] = CATEGORIES,
    test_size: float = 0.25,
    random_state: int = RANDOM_STATE,
):
    """
    Full end-to-end wrapper.

    Why:
    This mirrors a production agent workflow:
    - load corpus
    - inspect data
    - train router
    - build retrieval memory
    - simulate noisy/stale context
    - govern working context
    - answer queries
    - evaluate and visualize

    This is the agentic version of context-rot mitigation:
    the system does not simply append everything into a prompt.
    It routes, retrieves, filters, budgets, and only then answers.
    """

    # -------------------------------
    # Phase 1: Data loading
    # -------------------------------
    df = load_text_dataset(
        categories=categories,
        random_state=random_state,
    )

    # -------------------------------
    # Phase 2: EDA
    # -------------------------------
    eda_summary = run_eda(df)

    # -------------------------------
    # Phase 3: Feature engineering / split
    # -------------------------------
    X_train, X_test, y_train, y_test = split_data(
        df,
        test_size=test_size,
        random_state=random_state,
    )

    train_df = pd.DataFrame(
        {
            "clean_text": X_train.values,
            "label": y_train.values,
        }
    ).reset_index(drop=True)

    test_df = pd.DataFrame(
        {
            "clean_text": X_test.values,
            "label": y_test.values,
        }
    ).reset_index(drop=True)

    # -------------------------------
    # Phase 4: Model selection / tuning
    # -------------------------------
    classifier, cv_results = tune_text_classifier(
        X_train=X_train,
        y_train=y_train,
        random_state=random_state,
    )

    # -------------------------------
    # Phase 5: Prediction / evaluation
    # -------------------------------
    classifier_eval = evaluate_classifier(
        model=classifier,
        X_test=X_test,
        y_test=y_test,
    )

    # -------------------------------
    # Phase 6: Build retrieval memory
    # -------------------------------
    print("\n=== BUILD RETRIEVAL MEMORY ===")

    retriever = TfidfRetriever(max_features=30000).fit(train_df)

    print(f"Indexed documents: {len(train_df)}")

    # -------------------------------
    # Phase 7: Build agent
    # -------------------------------
    context_governor = ContextGovernor(
        min_relevance_score=0.05,
        max_docs=5,
        max_total_chars=2500,
    )

    label_examples = {
        label: train_df[train_df["label"] == label]["clean_text"].iloc[0]
        for label in sorted(train_df["label"].unique())
    }

    agent = ContextRotAwareTextAgent(
        classifier=classifier,
        retriever=retriever,
        context_governor=context_governor,
        label_examples=label_examples,
        random_state=random_state,
    )

    # -------------------------------
    # Phase 8: Demonstration query
    # -------------------------------
    print("\n=== AGENT DEMONSTRATION QUERY ===")

    demo_query = """
    I am trying to understand whether reusable launch vehicles and orbital platforms
    could reduce the cost of getting payloads into space. What topic does this belong to,
    and what evidence from memory supports it?
    """

    state = agent.answer(
        query=demo_query,
        all_train_docs=train_df,
        top_k=8,
        n_stale_docs=5,
    )

    print("\nUser query:")
    print(shorten(demo_query, width=500))

    print("\nFinal agent answer:")
    print(state.final_answer)

    print("\nRejected context examples:")
    for doc in state.rejected_context[:3]:
        print(
            f"- [{doc.source} | label={doc.label} | score={doc.score:.3f}] "
            f"{shorten(doc.text, width=220)}"
        )

    # -------------------------------
    # Phase 9: Agent evaluation
    # -------------------------------
    agent_eval_df = evaluate_agent_retrieval(
        agent=agent,
        test_df=test_df,
        train_df=train_df,
        n_examples=80,
        random_state=random_state,
    )

    # -------------------------------
    # Phase 10: Visualization
    # -------------------------------
    visualize_results(
        df=df,
        classifier_eval=classifier_eval,
        cv_results=cv_results,
        agent_eval_df=agent_eval_df,
    )

    return {
        "data": df,
        "train_df": train_df,
        "test_df": test_df,
        "eda_summary": eda_summary,
        "classifier": classifier,
        "classifier_eval": classifier_eval,
        "retriever": retriever,
        "agent": agent,
        "demo_state": state,
        "agent_eval": agent_eval_df,
        "cv_results": cv_results,
    }

# ============================================================
# Run Everything
# ============================================================

if __name__ == "__main__":
    results = run_agentic_context_rot_text_example()

    print("\n=== FINAL SUMMARY ===")
    print("Classifier metrics:")
    for metric, value in results["classifier_eval"]["metrics"].items():
        print(f"{metric}: {value:.4f}")

    print("\nAgent demo predicted topic:")
    print(results["demo_state"].predicted_topic)

    print("\nAgent selected working-context documents:")
    for i, doc in enumerate(results["demo_state"].working_context, start=1):
        print(
            f"{i}. label={doc.label} | score={doc.score:.3f} | source={doc.source}"
        )
```

### What We Learned: More Context Is Not the Same as Better Context

The experiment tells a very clear story: the system had access to enough information to make good decisions, but the quality of those decisions depended heavily on how that information was selected, filtered, and governed. This directly reflects the essay's central idea. Context rot is not simply a problem of missing knowledge; it is often a problem of excessive, noisy, stale, or poorly prioritized knowledge. In this experiment, the agent retrieved documents, injected stale memory, applied a context governor, and then generated an answer from the selected working context. The result was a small but realistic simulation of what happens inside production AI agents: the model is surrounded by potentially useful material, but not all of it deserves to influence the final decision.

```python
=== DATA LOADING ===
Loaded documents: 3317
Labels: ['comp.graphics', 'rec.autos', 'sci.space', 'talk.politics.misc']

=== EDA ===

Class counts:
label
sci.space             892
comp.graphics         873
rec.autos             848
talk.politics.misc    704
Name: count, dtype: int64

Document length summary by class:
                    count        mean         std   min    50%     max
label                                                                 
comp.graphics       873.0  221.927835  871.332873  20.0   73.0  9367.0
rec.autos           848.0  133.297170  232.618778  20.0   86.0  4425.0
sci.space           892.0  212.265695  523.990394  20.0   98.0  9251.0
talk.politics.misc  704.0  315.813920  817.446074  20.0  127.0  8131.0

Sample document:
Label: comp.graphics
software retail / sale price //////graphics///////// corel draw 2.0 300 / 25 aldus photo styler 1.1 800 / 100 image in color (2 ) 800 / 100 photo finish (3 of these) 295 / 75 image in scan paint 150 / 20 image in full pack 300 / 45 picture publisher 800 / 100 image prep 200 / 50 snap pro 70 / 20 images inc. 200 / 50 publisher s paintbrush 495 / 50 deluxe paint 2 enchance 129 / 25 softtype ( font workshop) 300 / 25 vista pro 100 / 20 optibase-workshop 149 / 35 gfa cad 100 / 25 ////////utilities ////////// x tree gold for win 99 / 25 tnt (anti virus) 100 / 15 salvation 100 / 15 amish...

=== TRAIN/TEST SPLIT ===
Train documents: 2487
Test documents: 830

=== MODEL SELECTION + HYPERPARAMETER TUNING ===
Fitting 5 folds for each of 48 candidates, totalling 240 fits

Best CV macro-F1:
0.9289

Best parameters:
{'model': MultinomialNB(), 'model__alpha': 0.1, 'tfidf__max_df': 0.8, 'tfidf__min_df': 2, 'tfidf__ngram_range': (1, 2)}

Top 5 configurations:
    rank_test_score  mean_test_score  std_test_score  mean_train_score  \
25                1         0.928872        0.007887          0.996372   
29                1         0.928872        0.007887          0.996372   
28                3         0.926303        0.006931          0.991891   
24                3         0.926303        0.006931          0.991891   
37                5         0.923825        0.011362          0.991641   

        param_model param_tfidf__ngram_range  param_tfidf__min_df  \
25  MultinomialNB()                   (1, 2)                    2   
29  MultinomialNB()                   (1, 2)                    2   
28  MultinomialNB()                   (1, 1)                    2   
24  MultinomialNB()                   (1, 1)                    2   
37  MultinomialNB()                   (1, 2)                    2   

    param_tfidf__max_df  
25                 0.80  
29                 0.95  
28                 0.95  
24                 0.80  
37                 0.95  

=== PREDICTION + EVALUATION ===

Metrics:
accuracy: 0.9289
macro_f1: 0.9285
weighted_f1: 0.9291

Classification report:
                    precision    recall  f1-score   support

     comp.graphics       0.95      0.95      0.95       219
         rec.autos       0.96      0.91      0.93       212
         sci.space       0.92      0.91      0.92       223
talk.politics.misc       0.88      0.95      0.92       176

          accuracy                           0.93       830
         macro avg       0.93      0.93      0.93       830
      weighted avg       0.93      0.93      0.93       830

=== BUILD RETRIEVAL MEMORY ===
Indexed documents: 2487

=== AGENT DEMONSTRATION QUERY ===

User query:
I am trying to understand whether reusable launch vehicles and orbital platforms could reduce the cost of getting payloads into space. What topic does this belong to, and what evidence from memory supports it?

Final agent answer:
Agent decision:
The query is most likely associated with topic: sci.space
Classifier confidence: 0.952

Evidence check:
The dominant label among selected evidence is: sci.space

Context-governance interpretation:
The agent did not use all available context. It selected only the highest-scoring,
freshest, budget-compatible evidence. This reduces the risk of context rot, where
old or irrelevant memory competes with the current task.

Selected evidence:
1. [retrieval | label=sci.space | score=0.177] what would all of you out there in net land think of the big 6 (martin mariatta, boeing, mcdonell douglas, general dynamics, lockheed, rockwell) getting together, and forming a consortium to study exactly what the market price pints are for building...
2. [retrieval | label=rec.autos | score=0.139] i stand corrected. this is all from memory, mind you :-) yeah, that s what i was trying to say. no, really!
3. [retrieval | label=sci.space | score=0.121] it was a test of the first reusable tool. pointy so they can find them or so they will stick into their pants better, and be closer to their brains?
4. [retrieval | label=talk.politics.misc | score=0.107] i replied to your message, however, it is listed as a new topic with the title: rnitedace and violence . possibly line noise or error caused to post as a new topic. i see it here as 100. regards,

Practical answer:
Based on the routed topic and selected evidence, the query appears to belong to
the 'sci.space' area. If this were a production AI agent, the next
step would be to call the specialized toolchain for that topic rather than
mixing unrelated context into the response.

Rejected context examples:
- [retrieval | label=sci.space | score=0.153] commercial space news/space technology investor number 22 this is number twenty-two in an irregular series on commercial space activities. the commentaries included are my thoughts on these developments. sigh... as...
- [retrieval | label=sci.space | score=0.126] ssrt rollout speech delivered by col. simon p. worden, the deputy for technology, sdio mcdonnell douglas - huntington beach april 3,1993 most of you, as am i, are children of the 1960 s. we grew up in an age of...
- [retrieval | label=sci.space | score=0.123] in fact, you probably want to avoid us government anything for such a project. the pricetag is invariably too high, either in money or in hassles. the important thing to realize here is that the big cost of getting to...

=== AGENT RETRIEVAL / CONTEXT GOVERNANCE EVALUATION ===
Topic routing accuracy: 0.9125
Dominant working-context accuracy: 0.8750

Average context counts:
n_retrieved    8.0000
n_stale        5.0000
n_selected     4.1875
n_rejected     8.8125
dtype: float64

=== FINAL SUMMARY ===
Classifier metrics:
accuracy: 0.9289
macro_f1: 0.9285
weighted_f1: 0.9291

Agent demo predicted topic:
sci.space

Agent selected working-context documents:
1. label=sci.space | score=0.177 | source=retrieval
2. label=rec.autos | score=0.139 | source=retrieval
3. label=sci.space | score=0.121 | source=retrieval
4. label=talk.politics.misc | score=0.107 | source=retrieval
```

The dataset itself was reasonably balanced, with `sci.space`, `comp.graphics`, and `rec.autos` having similar document counts, while `talk.politics.misc` had fewer examples. This means the classification task was not dominated by a single class, which is good for evaluating routing behavior. However, the document-length plot showed a more complicated reality. Most documents were short or moderate in length, but each topic had very large outliers, with some texts reaching thousands of words. This is an important signal for agent design. Long documents can behave like oversized pieces of context: they may contain useful evidence, but they can also consume the entire context budget and crowd out other information. In agent terms, one giant log file, one long ticket history, or one verbose knowledge-base article can dominate the working memory even when smaller pieces of evidence are more decisive.

### What Worked: The Classifier Was a Strong Router

The classification component worked well. The best model was `MultinomialNB` with TF-IDF using unigrams and bigrams, achieving a cross-validated macro-F1 of about `0.929` and a test macro-F1 of about `0.9285`. That is a strong result for a lightweight text classifier. In the agent architecture, this classifier serves as a router. Before the agent retrieves evidence or calls tools, it needs to decide what type of problem it is dealing with. The results show that this routing layer was mostly reliable.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*xnU7KpmcVVF-7EISNdmu0w.png)

The confusion matrix confirms this. `comp.graphics` was classified with high accuracy, with 207 correct predictions out of 219. `rec.autos` was also strong, with 192 correct out of 212. `sci.space` achieved 204 correct out of 223, and `talk.politics.misc` achieved 168 correct out of 176. These are good numbers. In practical terms, the agent usually knew which “room” to walk into before searching for evidence. That matters because an agent that routes poorly will contaminate itself from the beginning. If a Cisco troubleshooting agent routes a BGP issue into a wireless-controller workflow, or a coding agent routes a dependency error into a UI-rendering workflow, context rot begins before reasoning even starts.

![](https://miro.medium.com/v2/resize:fit:1260/format:webp/1*4Xlpc6xAXD-bSivDlh6-IA.png)

The agent demonstration query also worked at the routing level. The question about reusable launch vehicles, orbital platforms, and payload costs was correctly classified as `sci.space` with high confidence: `0.952`. This is exactly what we would want from an agent's first stage. The system recognized the question's domain before attempting to build an answer.

### What Partially Worked: The Context Governor Reduced Noise

The context-governance mechanism also worked importantly. On average, the agent retrieved 8 fresh documents and injected 5 stale documents, giving it 13 candidate pieces of context. The governor selected only about 4.19 documents and rejected about 8.81. This is the right architectural instinct. The agent did not unthinkingly append everything to its working memory. It acted more like an experienced analyst with a messy desk. Instead of reading every paper in the pile, it pulled forward only the documents that seemed most relevant to the current decision.

![](https://miro.medium.com/v2/resize:fit:1140/format:webp/1*iWgBjIFL05IU7QGPOsz9TQ.png)

This is the central lesson of context rot mitigation. A reliable agent should not be designed as a transcript accumulator. It should behave like a disciplined investigator. It should ask: “What evidence is current? What evidence is relevant? What evidence is stale? What evidence is merely similar but not actually useful?” The context governor was a first attempt at that discipline. It penalized stale memory, enforced a limit on the number of documents, and applied a character budget. As a result, the final answer was generated from a smaller working set rather than the full noisy context.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*jmLEx-d0AeCWiv32E4ZNvg.png)

The agent-level evaluation also showed meaningful success. Topic routing accuracy over sampled test cases was `0.9125`, and dominant working-context accuracy was `0.8750`. This means that, in most cases, the agent not only classified the topic correctly but also selected evidence whose dominant label matched the true topic. That is promising. It suggests that even a simple context-governance layer can reduce the risk of context rot when compared with an unconstrained “retrieve everything and hope the model sorts it out” approach.

## What Didn’t Work: The Agent Still Let Irrelevant Evidence Into the Room

The most interesting failure is in the demonstration query. The agent correctly classified the query as `sci.space`, and the dominant selected evidence was also `sci.space`. However, the selected working context included documents from `rec.autos` and `talk.politics.misc`. That is a warning sign. The agent did not completely rot, but a few contaminants entered the working memory.

![](https://miro.medium.com/v2/resize:fit:1378/format:webp/1*3gpSgQG8stzjnj6yAeKklw.png)

This is exactly how context rot often appears in real systems. It is rarely a dramatic failure where everything is wrong. Instead, the agent mostly does the right thing while quietly mixing in irrelevant material. In the demo, the final answer still made sense because the routing decision was strong and the dominant evidence was correct. But if a large language model had handled the final generation step, those irrelevant snippets could have influenced the response. The model might have mentioned unrelated “memory,” politics, or automobile content, especially if the relevant evidence had been weaker or the user query more ambiguous.

There was another revealing behavior: some relevant `sci.space` documents appeared in the rejected context examples. This likely happened because of the character budget and document-length constraints. In other words, the context governor sometimes rejected useful but longer documents while allowing shorter but less relevant ones into the working set. This is a very practical lesson. Context budgeting is necessary, but crude budgeting can create its own failure mode. If the system only thinks in terms of “how much text fits,” it may prefer compact but mediocre evidence over longer but stronger evidence. That is like a doctor ignoring a detailed lab report because it is too long and instead reading a short but less relevant note.

The top cross-validation plot also hints at another issue: several configurations performed very similarly, and the best Naive Bayes model had a very high training score, around `0.996`, compared with a lower validation score around `0.929`. This does not invalidate the model, but it suggests that the classifier may be fitting the training distribution very tightly. In production agent systems, this would translate into a router that performs well on familiar historical categories but may be less reliable when new issue types, hybrid topics, or ambiguous user queries appear.

### The Main Story: The Agent Needed a Librarian, Not Just a Bigger Library

A useful metaphor is to think of the agent as a researcher working inside a library. The classifier is the sign above each section: space, cars, graphics, politics. The retriever is the librarian bringing books to the table. The stale-memory injector is the pile of old books someone forgot to remove from yesterday’s research session. The context governor is the person deciding which books actually stay open on the desk.

The experiment shows that the signs were mostly correct and the librarian was helpful, but the desk still got a little messy. A few irrelevant books stayed open. A few useful books were pushed aside because they were too large. The researcher still produced a good answer, but the risk was visible. That is context rot in miniature: not the absence of knowledge, but the gradual corruption of the working surface where reasoning happens.

This connects directly to the essay’s argument. The best agent is not the one who remembers everything. The best agent is the one who knows what to preserve, what to ignore, what to compress, and what to challenge. The experiment supports that view. Retrieval alone was not enough. Classification alone was not enough. A context governor helped, but it needs to become more sophisticated.

## Future Work: Toward Stronger Context Governance

The next step would be to improve the context governor so that it does not rely only on relevance score, stale-memory penalty, document count, and character budget. A stronger version should include diversity control, source reliability, freshness metadata, contradiction detection, and topic consistency. For example, once the classifier predicts `sci.space` with high confidence, the governor could require stronger justification before allowing `rec.autos` or `talk.politics.misc` documents into the active context. This would reduce accidental contamination.

Another improvement would be chunking. Instead of allowing or rejecting whole documents, the system should split long documents into smaller evidence units. This would solve the problem where useful `sci.space` documents were rejected because they were too long. In production RAG systems, this is critical. The relevant answer is often buried in one paragraph of a long document. The agent should not have to choose between swallowing the whole document or discarding it entirely.

A third improvement would be the ability to track evidence attribution and contradiction. The current agent selects documents, but it does not explicitly say which claims are supported by which snippets. A more advanced version should maintain a structured evidence table: confirmed facts, uncertain facts, rejected facts, and source references. This would make the agent more auditable and less likely to reuse stale assumptions.

A fourth direction would be replacing the template-based answer generator with an actual LLM, but only after the context-governance layer is strengthened. That order matters. Adding an LLM too early might make the system sound smarter while masking the same context problems. The correct architecture is not “LLM plus everything.” It is “governed context first, LLM second.”

Finally, the evaluation should be expanded. The current experiment measured classifier accuracy and dominant working-context accuracy. Future tests should include deliberate adversarial context: highly similar but wrong documents, outdated facts, contradictory evidence, and multi-turn topic drift. That would make the experiment closer to real context rot, where the dangerous context is not random noise but plausible, semantically similar, and wrong for this moment.

### Final Interpretation

The experiment succeeded because it made context rot visible. The system performed well overall, but the outputs showed the exact type of subtle degradation that matters in real AI agents. The classifier was strong, the retrieval was useful, and context pruning reduced noise. However, the working context was not perfectly clean. Irrelevant evidence slipped through, and some relevant evidence was rejected because of simple budgeting rules.

That is the practitioner’s lesson: context rot is not solved by one component. It requires an architecture. The agent needs routing, retrieval, pruning, freshness awareness, chunking, evidence ranking, state management, and evaluation under noisy conditions. In this experiment, the agent behaved like a capable analyst who had started organizing the desk but still needed a better filing system. It knew the topic. It found relevant material. It ignored much of the noise. But it still lets a few wrong papers sit beside the right ones.

For a production AI agent, that is the difference between a demo and a reliable system.

## The Deeper Lesson

Context rot reveals a deeper truth about AI agents: intelligence is not enough. A strong model inside a weak context architecture will still fail. The model may reason well locally, but reason over the wrong working set globally. This is the same lesson distributed systems taught software engineers decades ago. Reliability comes from state management, boundaries, observability, invalidation, and recovery — not from trusting a powerful component to infer everything correctly.

For advanced practitioners, the path forward is clear. Stop treating context as a passive container. Treat it as an actively managed substrate. Design context lifecycles. Separate state from history. Separate evidence from hypotheses. Separate active memory from archived memory. Make contradiction explicit. Make freshness visible. Make authority rankable. Make summaries operational rather than decorative.

Longer prompts, larger models, or more retrieval do not solve context rot. Those may help, but they do not remove the underlying failure mode. The real solution is disciplined context engineering.

In the end, the best agents will not be the ones who remember the most. They will be the ones who know what to forget, what to preserve, what to challenge, and what to bring forward at exactly the moment it matters.

Have you seen context rot in RAG, coding agents, or troubleshooting agents? Share your failure case and mitigation strategy below.

## References

**\[1\] Context as a Tool: Context Management for Long-Horizon SWE-Agents**, Shukai Liu, Jian Yang, Bo Jiang, Yizhi Li, Jinyang Guo, Xianglong Liu, Bryan Dai, propose context management as an explicit callable tool for software-engineering agents and report a 57.6% solved rate on SWE-Bench-Verified under bounded context budgets.

## [Context as a Tool: Context Management for Long-Horizon SWE-Agents](https://arxiv.org/abs/2512.22087?source=post_page-----ae14616c0a88---------------------------------------)

### Agents based on large language models have recently shown strong potential in real-world software engineering (SWE)…

arxiv.org

**\[2\] Evaluating Long-Context Reasoning in LLM-Based WebAgents**, Andy Chung, Yichi Zhang, Kaixiang Lin, Aditya Rawal, Qiaozi Gao, Joyce Chai, directly supports the context-rot argument by showing WebAgent success rates dropping from roughly 40–50% to below 10% under long, noisy interaction histories.

## [Evaluating Long-Context Reasoning in LLM-Based WebAgents](https://arxiv.org/abs/2512.04307?source=post_page-----ae14616c0a88---------------------------------------)

### As large language model (LLM)-based agents become increasingly integrated into daily digital interactions, their…

arxiv.org

**\[3\] Long-Context LLMs Meet RAG: Overcoming Challenges for Long Inputs in RAG**, Bowen Jin, Jinsung Yoon, Jiawei Han, Sercan O. Arik, shows that adding more retrieved passages can first help and then hurt, especially when hard negatives pollute the context.

## [Long-Context LLMs Meet RAG: Overcoming Challenges for Long Inputs in RAG](https://arxiv.org/abs/2410.05983?source=post_page-----ae14616c0a88---------------------------------------)

### Retrieval-augmented generation (RAG) empowers large language models (LLMs) to utilize external knowledge sources. The…

arxiv.org

**\[4\] A Survey of Context Engineering for Large Language Models**, by Lingrui Mei et al., provides the broader taxonomy that underlies the essay’s claim that prompt engineering is being replaced by context retrieval, processing, management, memory, tools, and multi-agent orchestration.

## [A Survey of Context Engineering for Large Language Models](https://arxiv.org/abs/2507.13334?source=post_page-----ae14616c0a88---------------------------------------)

### The performance of Large Language Models (LLMs) is fundamentally determined by the contextual information provided…

arxiv.org

**\[5\] Lost in the Middle: How Language Models Use Long Context**, by Nelson F. Liu, Kevin Lin, John Hewitt, Ashwin Paranjape, Michele Bevilacqua, Fabio Petroni, and Percy Liang, is foundational for understanding why relevant information can be ignored in long prompts; code and data are available.

## [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172?source=post_page-----ae14616c0a88---------------------------------------)

### While recent language models can take long contexts as input, relatively little is known about how well…

arxiv.org

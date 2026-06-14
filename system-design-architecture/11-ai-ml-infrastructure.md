---
type: System Design
title: "AI/ML Infrastructure: Patterns for Production LLM Systems"
description: "LLMs generate text probabilistically — they predict the next token based on training data patterns. They have **no concept of truth**. This leads to hallucinations when:"
timestamp: 2026-06-14T00:00:00Z
---

# AI/ML Infrastructure: Patterns for Production LLM Systems

> **Source**: [22 Scenario-Based System Design Questions](../articles/medium/22-design-interview-questions/01-22-scenario-based-system-design-questions.md) — Scenarios #17, #18, #19  
> **Taxonomy Reference**: §12 AI Applications, §4.1 Data & Analytics  
> **Azure Mapping**: See [Azure Service Mapping](07-azure-service-mapping.md)

---

## Table of Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [`ai-01`](#ai-01-rag-architecture--stopping-ai-hallucinations) | AI Chatbot Gives Wrong Answers | RAG, chunking, grounding, validation |
| [`ai-02`](#ai-02-llm-cost-optimization) | AI Platform Becomes Very Expensive | Model routing, semantic caching, prompt compression |
| [`ai-03`](#ai-03-vector-search-performance) | AI Search Feels Too Slow | ANN indexing, hybrid search, latency budgeting |

---

## ai-01: RAG Architecture — Stopping AI Hallucinations

### The Problem

LLMs generate text probabilistically — they predict the next token based on training data patterns. They have **no concept of truth**. This leads to hallucinations when:

1. **Training data is outdated** — model cutoff predates recent events
2. **Context window limitations** — relevant facts fall outside even 128K token windows
3. **Poor retrieval** — RAG retrieves irrelevant/outdated documents
4. **Over-confidence** — model presents speculation as fact

### Solution: Retrieval-Augmented Generation (RAG)

Ground the LLM's response in **retrieved documents** rather than training data alone.

```mermaid
flowchart LR
    Q[User Question] --> E[Embedding Model]
    E --> V[(Vector DB)]
    V --> R[Retrieved Chunks]
    R --> P[Prompt: Context + Question]
    P --> L[LLM]
    L --> G[Grounded Answer]
    G --> VAL{Validation}
    VAL -->|Pass| U[User]
    VAL -->|Fail| F[Fallback: "Insufficient info"]
```

### 1. Chunking Strategy

How documents are split dramatically affects retrieval quality:

| Strategy | Best For | Example |
|:---|:---|:---|
| Fixed-size (512 tokens) | General docs | Split by paragraphs |
| Semantic chunking | Technical docs | Split at section boundaries |
| Overlapping sliding window | FAQ-style | 256-token chunks, 64-token overlap |
| Hierarchical | Long documents | Chunk → Summary → Document |

### 2. Prompt Engineering to Reduce Hallucination

```
System: Answer questions SOLELY based on the provided context. If the context 
doesn't contain enough information, say "I don't have enough information to 
answer that question." Do NOT speculate.

Context: {retrieved_chunks}

Instructions:
- Cite the specific source document for each claim
- If multiple sources conflict, note the discrepancy
- Use direct quotes when possible
- Mark confidence level: [High/Medium/Low]
```

### 3. Guardrails and Validation

Before returning an answer, validate:

```python
def validate_answer(question, context_chunks, generated_answer):
    claims = extract_claims(generated_answer)
    for claim in claims:
        if not any(claim_supported(claim, chunk) for chunk in context_chunks):
            return fallback_response(f"Unverified claim: {claim}")
    return generated_answer
```

### Grounding Spectrum

```
Pure LLM (no RAG)    RAG + Prompting    RAG + Validation    Human-in-loop
[Most hallucinations] ←────────────────────────────────→ [Fewest hallucinations]
[Cheapest]            ←────────────────────────────────→ [Most expensive]
```

> **Azure Mapping**: Azure OpenAI Service (LLM hosting), Azure AI Search (vector/hybrid search), Azure Cosmos DB for MongoDB vCore (native vector support), Azure AI Content Safety (guardrails/hallucination detection).

---

## ai-02: LLM Cost Optimization

### The Problem

LLM costs are driven by **token count** (input + output tokens). Seemingly small design choices explode costs:

```
One GPT-4 call: 4,000 input + 500 output tokens
  = (4000 × $0.03/1K) + (500 × $0.06/1K)
  = $0.12 + $0.03 = $0.15 per call

At scale: 100K users/day × 5 queries × $0.15 = $75,000/day = $2.25M/month 💸
```

### Solution Architecture

**Layer 1 — Model Router**

Route each request to the cheapest model that can handle it:

```python
class ModelRouter:
    def route(self, request):
        if request.task_type == TaskType.CLASSIFICATION:
            return ModelConfig(model="gpt-4o-mini", max_tokens=50)   # Tiny
        if request.task_type == TaskType.SUMMARIZATION:
            return ModelConfig(model="gpt-4o-mini", max_tokens=200)  # Mid-tier
        if request.task_type == TaskType.COMPLEX_REASONING:
            cached = self.semantic_cache.lookup(request.prompt)
            if cached: return ModelConfig(model="CACHE_HIT", cost=0)
            return ModelConfig(model="gpt-4o", max_tokens=500)       # Only if needed
```

**Layer 2 — Semantic Cache**

Cache LLM responses by **semantic similarity**, not exact string match. For FAQ/support bots, this can reduce costs by **60-80%**. "How do I reset my password?" and "I forgot my password, help!" both hit the same cached response.

**Layer 3 — Context Window Optimization**

| Optimization | Impact |
|:---|:---|
| Compress system prompt | 2000 → 300 tokens |
| Summarize old conversation messages | Keep only recent verbatim |
| Truncate retrieved documents | Most relevant passages only |

**Layer 4 — Prompt Compression**

```
BEFORE (~200 tokens):
"You are an expert customer support assistant for ACME Corp, a leading 
provider of cloud-based widget management solutions. Your role is to help 
customers with technical issues, billing questions, account management..."

AFTER (~50 tokens → 4x cheaper):
"ACME support bot. Rules: Answer from KB only. No speculation → escalate. 
Hours: M-F 9-5 EST."
```

### Cost Reduction Impact

| Technique | Cost Reduction | Quality Impact |
|:---|:---|:---|
| Model routing | 40-60% | None (right model for right task) |
| Semantic caching | 60-80% (FAQ bots) | None (identical semantics) |
| Context optimization | 20-30% | Minimal |
| Prompt compression | 10-30% | None (lossless compression) |

> **Azure Mapping**: Azure OpenAI Service with provisioned throughput for predictable pricing, Azure AI Search for semantic caching, Azure Cosmos DB (vCore) for vector cache storage, Azure API Management for rate limiting and quota enforcement.

---

## ai-03: Vector Search Performance

### The Problem

Semantic search involves multiple steps, each adding latency:

| Component | Latency |
|:---|:---|
| Embedding generation | 100-300ms |
| Vector similarity search (10M vectors) | 50-200ms |
| Optional reranking (cross-encoder) | 100-500ms |
| LLM response generation | 500-3000ms |
| **Total** | **1.2-4.5 seconds** 😞 |

Traditional keyword search: ~10-50ms.

### Solution Architecture

**Layer 1 — Approximate Nearest Neighbor (ANN) with Index Tuning**

Exact KNN on 10M vectors is O(N) — too slow. ANN sacrifices a small amount of recall for massive speed gains:

| Algorithm | Speed | Recall | Memory | Best For |
|:---|:---|:---|:---|:---|
| **HNSW** | Very Fast | ~98% | High | Low-dim (≤ 384), in-memory |
| **IVF + PQ** | Fast | ~95% | Low | High-dim (≥ 768), disk-backed |
| **DiskANN** | Medium | ~99% | Very Low | Billion-scale, SSD-based |

**Layer 2 — Hybrid Search (Sparse + Dense)**

Combine fast keyword search (BM25, ~5ms) with semantic vector search (~100ms). Use **Reciprocal Rank Fusion (RRF)** to merge rankings. Show keyword results immediately, refine with semantic results.

**Layer 3 — Streaming for Perceived Performance**

Don't wait for everything. Return results progressively:

```
t=0ms:    Keyword results (fast first paint)
t=100ms:  Semantic results refine rankings
t=500ms:  LLM-powered summary (if needed)
```

**Layer 4 — Embedding Model Selection**

Smaller models = faster embeddings with acceptable quality trade-off:

| Model | Dimension | Speed (sent/sec) | Use Case |
|:---|:---|:---|:---|
| `all-MiniLM-L6-v2` | 384 | 14,000 | Real-time search |
| `bge-small-en` | 384 | 10,000 | Balanced |
| `text-embedding-3-small` | 512 | 5,000 | OpenAI ecosystem |
| `text-embedding-3-large` | 3072 | 1,000 | Offline/batch only |

### Latency Budget (Target: < 700ms)

| Component | Target | Optimization |
|:---|:---|:---|
| Embedding generation | < 50ms | Smaller model, GPU, batching |
| Vector search | < 30ms | HNSW, ef_search tuning |
| Reranking | < 100ms | Only rerank top-20, not top-100 |
| LLM generation | < 500ms | Streaming, short outputs |

### ANN Trade-Off

```
High Recall (99%+)          Balanced (95-98%)          High Speed (90-95%)
[Exact KNN / DiskANN]  ←──  [HNSW / IVF+PQ]  ──→  [Quantized + Pruned]
[Slowest, most accurate]    [Best for production]      [Fastest, acceptable quality]
```

> **Azure Mapping**: Azure AI Search with vector search (HNSW indexing), Azure Kubernetes Service with GPU nodes for self-hosted vector DBs, Azure OpenAI `text-embedding-3-small` for balanced speed/quality.

---

## Cross-Cutting AI Concerns

### The AI Infrastructure Stack

```
┌──────────────────────────────────────────┐
│            AI INFRASTRUCTURE              │
├──────────────┬───────────────────────────┤
│  RAG Layer   │ Chunking, retrieval,      │
│              │ grounding, validation      │
│  Cost Layer  │ Model routing, semantic   │
│              │ cache, prompt compression  │
│  Speed Layer │ ANN indexing, hybrid       │
│              │ search, streaming results  │
│  Safety Layer│ Guardrails, content safety, │
│              │ human-in-loop escalation    │
└──────────────┴───────────────────────────┘
```

### Key Takeaways

1. **Ground LLMs in retrieved documents** — never trust training data alone
2. **Route to the right model** — GPT-4 for reasoning, GPT-4o-mini for classification
3. **Cache semantically** — same-meaning questions shouldn't cost twice
4. **ANN, not exact KNN** — 95% recall at 100x speed is the right trade-off
5. **Stream results progressively** — perceived speed > actual speed

> **Taxonomy Reference**: §12 AI Applications, §4.1 Data & Analytics  
> **Related**: [Databases & Query Performance](01-databases-query-performance.md) | [Caching Architecture](03-caching-architecture.md) | [Stream Processing](09-stream-processing-flink.md)

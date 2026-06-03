# Vector Database Architecture

> **Taxonomy Reference**: §4.4 AI / ML Architecture

## Overview

Vector databases are purpose-built systems for **storing, indexing, and querying high-dimensional vector embeddings** — the numerical representations of unstructured data (text, images, audio) produced by ML models. They enable similarity search, recommendation, and retrieval-augmented generation (RAG) at scale.

## Table of Contents

- [Core Concepts](#core-concepts)
- [Architecture Diagram](#architecture-diagram)
- [Embedding Pipeline](#embedding-pipeline)
- [Similarity Metrics](#similarity-metrics)
- [ANN Algorithms](#ann-algorithms)
- [Vector Database Comparison](#vector-database-comparison)
- [RAG Architecture](#rag-architecture)
- [Hybrid Search](#hybrid-search)
- [Decision Framework](#decision-framework)
- [Related Patterns](#related-patterns)

## Core Concepts

| Concept | Description |
|---------|-------------|
| **Embedding** | A dense vector (e.g., 768-dim or 1536-dim) representing semantic meaning |
| **Similarity Search** | Finding vectors closest to a query vector in high-dimensional space |
| **k-NN (k-Nearest Neighbors)** | Exact search: find k closest vectors |
| **ANN (Approximate Nearest Neighbor)** | Approximate search: trade a small accuracy loss for huge speed gains |
| **Index** | Data structure enabling fast similarity search (HNSW, IVF, etc.) |
| **Namespace / Collection** | Logical grouping of vectors (like a table in SQL) |

### What Are Embeddings?

```
Text: "The cat sat on the mat"
        ↓ Embedding Model (e.g., BERT, Ada, Cohere)
Vector: [0.023, -0.451, 0.782, ..., -0.113]  ← 1536 dimensions

Similar texts → nearby vectors in vector space
"The feline rested on the rug" → close to "The cat sat on the mat"
"Quantum physics is fascinating" → far from "The cat sat on the mat"
```

## Architecture Diagram

```mermaid
graph TB
    subgraph "Vector Database Architecture"
        subgraph "Data Ingestion"
            TEXT[Text<br/>Documents]
            IMG[Images]
            AUDIO[Audio]
            TEXT --> EMBED[Embedding<br/>Model<br/>BERT / Ada / Cohere]
            IMG --> EMBED
            AUDIO --> EMBED
        end

        subgraph "Vector Database"
            subgraph "Index Layer"
                HNSW[HNSW Graph]
                IVF[IVF<br/>Inverted File]
                PQ[Product<br/>Quantization]
                DISK[Disk-Based<br/>Index]
            end

            subgraph "Storage Layer"
                VECTORS[(Vector<br/>Store)]
                METADATA[(Metadata<br/>Store)]
                FULLTEXT[(Full-Text<br/>Index)]
            end

            subgraph "Query Engine"
                SEARCH[Similarity<br/>Search]
                HYBRID[Hybrid<br/>Search]
                FILTER[Metadata<br/>Filtering]
                SEARCH --> VECTORS
                HYBRID --> VECTORS
                HYBRID --> FULLTEXT
                FILTER --> METADATA
            end

            EMBED --> HNSW
            EMBED --> IVF
            HNSW --> VECTORS
            IVF --> VECTORS
        end

        subgraph "Application Layer"
            RAG[RAG<br/>Retrieval]
            RECOMMEND[Recommendation<br/>Engine]
            SEMANTIC[Semantic<br/>Search]
            ANOMALY[Anomaly<br/>Detection]
            SEARCH --> RAG
            HYBRID --> SEMANTIC
            SEARCH --> RECOMMEND
            SEARCH --> ANOMALY
        end
    end

    style EMBED fill:#ff6b6b,color:#fff
    style VECTORS fill:#4ecdc4,color:#fff
    style SEARCH fill:#45b7d1,color:#fff
```

## Embedding Pipeline

```mermaid
graph LR
    subgraph "Embedding Generation Pipeline"
        RAW[Raw Content] --> CHUNK[Text<br/>Chunking]
        CHUNK --> MODEL[Embedding<br/>Model]
        MODEL --> VECTOR[(Vector DB)]

        CHUNK --> CHUNK_META[Chunk<br/>Metadata]
        CHUNK_META --> VECTOR

        MODEL --> DIM[Embedding Dim<br/>384 / 768 / 1536]
    end

    style RAW fill:#ff6b6b,color:#fff
    style MODEL fill:#4ecdc4,color:#fff
    style VECTOR fill:#45b7d1,color:#fff
```

### Chunking Strategies

| Strategy | How It Works | Best For |
|----------|-------------|----------|
| **Fixed-Size** | Split by character/token count | Simple, predictable |
| **Recursive** | Split by paragraph → sentence → word | Natural text boundaries |
| **Semantic** | Split at semantic boundaries using sentence embeddings | Maintaining meaning |
| **Sliding Window** | Overlapping chunks | Context preservation |
| **Document-Aware** | Respect document structure (headers, sections) | Structured docs |

### Embedding Models

| Model | Dimensions | Max Tokens | Cost | Best For |
|-------|-----------|------------|------|----------|
| **OpenAI text-embedding-3-small** | 512/1536 | 8191 | $0.02/1M tokens | General purpose |
| **OpenAI text-embedding-3-large** | 256/1024/3072 | 8191 | $0.13/1M tokens | High accuracy |
| **Cohere Embed v3** | 1024 | 512 | Varies | Multilingual |
| **BGE-M3 (BAAI)** | 1024 | 8192 | Free (OSS) | Multilingual, dense+sparse |
| **E5-mistral-7b-instruct** | 4096 | 32768 | Free (OSS) | Long context, high quality |
| **Jina embeddings v2** | 768 | 8192 | Free (OSS) | 8K context, multilingual |

## Similarity Metrics

| Metric | Formula | Range | Best For |
|--------|---------|-------|----------|
| **Cosine Similarity** | `cos(θ) = A·B / (‖A‖‖B‖)` | [−1, 1] | Text embeddings (default) |
| **Euclidean Distance (L2)** | `√Σ(Aᵢ−Bᵢ)²` | [0, ∞) | When magnitude matters |
| **Dot Product** | `Σ AᵢBᵢ` | (−∞, ∞) | Proxy for cosine (normalized vectors) |
| **Manhattan Distance (L1)** | `Σ |Aᵢ−Bᵢ|` | [0, ∞) | Sparse vectors, robustness |

> **Rule of thumb**: If using normalized embeddings (``‖v‖ = 1``), cosine similarity and dot product are equivalent. Most embedding models produce normalized vectors.

## ANN Algorithms

### Algorithm Landscape

```mermaid
graph TB
    subgraph "ANN Algorithm Family Tree"
        A[ANN Algorithms]

        A --> TREE[Tree-Based]
        TREE --> ANNOY[Annoy<br/>Random Projection<br/>Trees]

        A --> HASH[Hash-Based]
        HASH --> LSH[LSH<br/>Locality-Sensitive<br/>Hashing]

        A --> GRAPH[Graph-Based]
        GRAPH --> HNSW_G[HNSW<br/>Hierarchical<br/>Navigable Small World]

        A --> QUANT[Quantization-Based]
        QUANT --> IVF[IVF<br/>Inverted File]
        QUANT --> PQ_G[Product<br/>Quantization]
        QUANT --> SCANN[ScaNN<br/>Google]

        A --> CLUSTER[Clustering-Based]
        CLUSTER --> FAISS_IVF[FAISS IVF]
    end

    style HNSW_G fill:#4ecdc4,color:#fff
    style IVF fill:#45b7d1,color:#fff
```

### Algorithm Comparison

| Algorithm | Speed (QPS) | Recall | Memory | Build Time | Best For |
|-----------|------------|--------|--------|------------|----------|
| **HNSW** | Very High | 95-99% | High | Medium | Most use cases (default choice) |
| **IVF + PQ** | High | 90-97% | Low | High | Memory-constrained |
| **DiskANN** | Medium | 95-99% | Very Low (disk) | Very High | Billion-scale, cost-sensitive |
| **Annoy** | Medium | 90-95% | Medium | Low | Read-only, static datasets |
| **ScaNN** | Very High | 97-99% | High | High | Google-scale, max recall |
| **LSH** | High | 80-90% | Medium | Low | Simple, predictable recall |

## Vector Database Comparison

| Database | Type | ANN Algorithm | Strengths | Best For |
|----------|------|--------------|-----------|----------|
| **Pinecone** | Managed Cloud | Custom (pod-based) | Zero-ops, serverless | Teams wanting no infra management |
| **Weaviate** | OSS / Cloud | HNSW + PQ | Hybrid search, GraphQL, modular | Semantic search + keyword |
| **Qdrant** | OSS / Cloud | HNSW | Rust-based, fast, rich filtering | Performance + filtering |
| **Milvus** | OSS / Cloud | HNSW, IVF, DiskANN | Billion-scale, cloud-native | Large-scale production |
| **Chroma** | OSS | HNSW | Simple, Pythonic, lightweight | Prototyping, small projects |
| **pgvector** | PostgreSQL Extension | IVF, HNSW | No new infra, SQL-native | Existing PostgreSQL users |
| **Redis Stack** | OSS / Cloud | HNSW | Sub-ms latency, caching | Low-latency, real-time |
| **Elasticsearch** | OSS / Cloud | HNSW | Full-text + vector + analytics | Unified search platform |

## RAG Architecture

```mermaid
graph TB
    subgraph "Retrieval-Augmented Generation (RAG)"
        subgraph "Indexing (Offline)"
            DOCS[Documents] --> CHUNK[Chunking]
            CHUNK --> EMBED[Embed]
            EMBED --> VECTORDB[(Vector DB)]
        end

        subgraph "Retrieval + Generation (Online)"
            QUERY[User Query] --> Q_EMBED[Embed Query]
            Q_EMBED --> RETRIEVE[Retrieve Top-K<br/>from Vector DB]
            VECTORDB --> RETRIEVE
            RETRIEVE --> CONTEXT[Build Context<br/>from Chunks]
            QUERY --> PROMPT[Construct<br/>Prompt]
            CONTEXT --> PROMPT
            PROMPT --> LLM[LLM<br/>Generation]
            LLM --> ANSWER[Answer +<br/>Citations]
        end
    end

    style VECTORDB fill:#ff6b6b,color:#fff
    style LLM fill:#4ecdc4,color:#fff
    style ANSWER fill:#45b7d1,color:#fff
```

### RAG Pipeline Code (Conceptual)

```python
# 1. Indexing
documents = load_documents("knowledge_base/")
chunks = recursive_text_splitter(documents, chunk_size=512, overlap=50)
embeddings = embedding_model.encode(chunks)
vector_db.insert(chunks, embeddings, metadata)

# 2. Retrieval + Generation
def rag_query(user_query: str, k: int = 5) -> str:
    query_embedding = embedding_model.encode(user_query)
    retrieved = vector_db.search(query_embedding, top_k=k)

    context = "\n\n".join([r.text for r in retrieved])
    prompt = f"""Answer based on the context below.
    If unsure, say "I don't know."

    Context:
    {context}

    Question: {user_query}
    Answer:"""

    return llm.generate(prompt)
```

## Hybrid Search

Combining vector (semantic) and keyword (lexical) search for best results:

```python
# Hybrid search: combine sparse (BM25) + dense (vector) scores
def hybrid_search(query: str, alpha: float = 0.7):
    # Alpha controls vector vs keyword weight
    vector_results = vector_db.search(query_embedding, top_k=50)
    keyword_results = text_index.search(query, top_k=50)

    # Reciprocal Rank Fusion (RRF) or weighted sum
    combined = reciprocal_rank_fusion(
        vector_results,
        keyword_results,
        k=60  # RRF constant
    )

    return combined[:10]
```

| Search Type | Strengths | Weaknesses |
|------------|-----------|------------|
| **Vector (Dense)** | Semantic understanding, synonyms, multilingual | Misses exact matches, brand names |
| **Keyword (Sparse)** | Exact matches, entities, acronyms | Misses semantic similarity |
| **Hybrid** | Best of both | Higher latency, complexity |

## Decision Framework

```mermaid
graph TD
    Q1{Scale of vectors?} -->|< 1M| Q2{Existing PostgreSQL?}
    Q1 -->|1M - 100M| Q3{Need managed?}
    Q1 -->|> 100M| MILVUS[Milvus /<br/>Pinecone]

    Q2 -->|Yes| PGVECTOR[pgvector]
    Q2 -->|No| CHROMA[Chroma /<br/>Qdrant]

    Q3 -->|Yes| PINECONE[Pinecone /<br/>Weaviate Cloud]
    Q3 -->|No| QDRANT[Qdrant /<br/>Weaviate OSS]

    Q4{Need hybrid search?} -->|Yes| ES[Elasticsearch /<br/>Weaviate]
    Q4 -->|No| QDRANT2[Qdrant /<br/>Pinecone]

    style PGVECTOR fill:#4ecdc4,color:#fff
    style PINECONE fill:#45b7d1,color:#fff
    style MILVUS fill:#ff6b6b,color:#fff
```

## Related Patterns

- [Machine Learning Pipeline Architecture](01-machine-learning-pipeline-architecture.md) — Embedding generation pipeline
- [Model Inference Architecture](05-model-inference-architecture.md) — Embedding model serving
- [Feature Store Architecture](03-feature-store-architecture.md) — Storing vector features
- [MLOps Architecture](02-mlops-architecture.md) — Monitoring embedding quality and drift

> **Azure Implementation**: See [Azure AI Search](https://learn.microsoft.com/en-us/azure/search/) (hybrid search with vector + keyword), [Azure Cosmos DB for PostgreSQL](https://learn.microsoft.com/en-us/azure/cosmos-db/postgresql/) (pgvector), and [Azure Cache for Redis Enterprise](../../../architecture-azure/data/redis/) (Redis Stack with vector search).

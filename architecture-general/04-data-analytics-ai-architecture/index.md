# 4. Data, Analytics & AI Architecture

This section covers data management, analytics platforms, and AI/ML architectures.

## Subsections

### 4.0 Data Architecture Fundamentals
- [ACID Properties](data-architecture-fundamentals/acid-properties.md) - Transaction guarantees
- [BASE Properties](data-architecture-fundamentals/base-properties.md) - Distributed availability approach
- [CAP Theorem](data-architecture-fundamentals/cap-theorem.md) - Distributed systems trade-offs

### 4.0.1 Database Performance & Caching
- [PostgreSQL Performance & Caching Strategies](database-performance/postgres-performance-caching.md) - Modern PostgreSQL features and caching decisions
- [Database Caching Patterns](database-performance/database-caching-patterns.md) - General caching strategies and patterns

### 4.1 Data Architecture
- [OLTP Architecture](01-data-architecture/01-oltp-architecture.md) - Transaction processing systems with ACID guarantees
- [OLAP Architecture](01-data-architecture/02-olap-architecture.md) - Analytical processing and dimensional modeling
- [Polyglot Persistence](01-data-architecture/03-polyglot-persistence.md) - Multi-database strategies for heterogeneous workloads
- [Data Virtualization](01-data-architecture/04-data-virtualization.md) - Abstracted data access across disparate sources

### 4.2 Analytics Architecture
- [Data Warehouse Architecture](02-analytics-architecture/01-data-warehouse-architecture.md) - Dimensional modeling, ETL/ELT, Kimball/Inmon
- [Data Lake Architecture](02-analytics-architecture/02-data-lake-architecture.md) - Schema-on-read, medallion architecture, governance
- [Lakehouse Architecture](02-analytics-architecture/03-lakehouse-architecture.md) - Unified lake and warehouse with ACID on data lakes
- [Lambda Architecture](02-analytics-architecture/04-lambda-architecture.md) - Batch + speed layer pattern for big data
- [Kappa Architecture](02-analytics-architecture/05-kappa-architecture.md) - Stream-first design with event log as source of truth

### 4.3 Streaming & Real-Time Architecture
- [Real-Time Analytics Architecture](03-streaming-architecture/01-real-time-analytics-architecture.md) - Windowing, watermarks, exactly-once semantics
- [Stream Processing Architecture](03-streaming-architecture/02-stream-processing-architecture.md) - Stream processors, topologies, state management
- [Change Data Capture (CDC)](03-streaming-architecture/03-change-data-capture.md) - Database change propagation in real time
- [Apache Flink Architecture](03-streaming-architecture/04-apache-flink-architecture.md) - Comprehensive guide to Flink use cases, sources/sinks, and production topologies

### 4.4 AI / ML Architecture
- [Machine Learning Pipeline Architecture](04-ai-ml-architecture/01-machine-learning-pipeline-architecture.md) - End-to-end ML pipelines from data to deployment
- [MLOps Architecture](04-ai-ml-architecture/02-mlops-architecture.md) - ML operations, CI/CD/CT, lifecycle management
- [Feature Store Architecture](04-ai-ml-architecture/03-feature-store-architecture.md) - Feature engineering, serving, and registry
- [Model Training Architecture](04-ai-ml-architecture/04-model-training-architecture.md) - Distributed training, hyperparameter tuning, AutoML
- [Model Inference Architecture](04-ai-ml-architecture/05-model-inference-architecture.md) - Model serving, deployment strategies, optimization
- [Vector Database Architecture](04-ai-ml-architecture/06-vector-database-architecture.md) - Embeddings, similarity search, ANN algorithms

## Related

- [Architecture Taxonomy Reference](../10-practicality-taxonomy/architecture_taxonomy_reference.md)

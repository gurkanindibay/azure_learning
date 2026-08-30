---
type: System Design Case
title: "Design A Web Crawler"
description: "Design a massively scalable, distributed web crawler (like Googlebot) featuring priority and politeness-aware URL Frontiers, DNS caching, duplicate content detection via hashing, robots.txt parsing, and spider trap mitigation."
tags: [system-design, distributed-systems, web-crawler, url-frontier, politeness, bloom-filter, search-engine, simhash]
timestamp: 2026-08-22T00:00:00Z
---

# Design A Web Crawler

> **Source**: *System Design Interview – An Insider's Guide: Volume 1* by Alex Xu  
> **ByteByteGo Chapter**: 10  
> **Topic**: Distributed Web Crawling, URL Frontier Architecture, Politeness & Priority Scheduling, Spider Trap Defenses

---

## 1. Understand the Problem and Establish Design Scope

A web crawler (spider/robot) systematically discovers, fetches, and parses billions of web pages across the public internet for search engine indexing, archival, and data mining.

```mermaid
flowchart LR
    SEEDS["Seed URLs"] --> FRONTIER["URL Frontier"]
    FRONTIER --> DOWNLOAD["HTML Downloader"]
    DOWNLOAD --> PARSER["Content Parser & Validator"]
    PARSER --> EXTRACT["Link Extractor"]
    EXTRACT --> FILTER["URL Filter & Bloom Check"]
    FILTER -->|New Discovered URLs| FRONTIER
```

---

### Interview Clarification & Scope

> **Candidate:** What is the primary purpose of this web crawler?  
> **Interviewer:** **Search engine indexing**.
>
> **Candidate:** What is the target crawling volume?  
> **Interviewer:** **1 billion web pages per month**.
>
> **Candidate:** What content types are crawled and stored?  
> **Interviewer:** **HTML pages only** (images and media files are excluded). Store crawled pages for **5 years**.
>
> **Candidate:** How should duplicate content and polite server access be handled?  
> **Interviewer:** Must detect and ignore duplicate pages (near-duplicate hashing) and adhere strictly to `robots.txt` and domain rate limits (**Politeness**).

---

### Back-of-the-Envelope Estimation

| Metric / Dimension | Calculation | Estimated Value |
|:---|:---|:---|
| **Monthly Crawled Pages** | Given | $1{,}000{,}000{,}000\text{ pages/month}$ |
| **Average Crawl QPS** | $\frac{10^9}{30\text{ days} \times 86{,}400\text{ sec}}$ | $\approx \mathbf{400\text{ pages/sec}}$ |
| **Peak Crawl QPS** | $2 \times \text{Average QPS}$ | $\approx \mathbf{800\text{ pages/sec}}$ |
| **Average HTML Page Size** | Text + markup | $\approx 500\text{ KB/page}$ |
| **Monthly Storage** | $1\text{B pages} \times 500\text{ KB}$ | $\approx \mathbf{500\text{ TB/month}}$ |
| **5-Year Storage Capacity** | $500\text{ TB/month} \times 60\text{ months}$ | $\approx \mathbf{30\text{ PB}}$ |

---

## 2. High-Level Architecture & Crawling Pipeline

```mermaid
flowchart TD
    SEEDS["Seed URLs<br/>(Wikipedia, Yahoo, Curated Directory)"] --> UF["URL Frontier<br/>(Priority & Politeness Queues)"]
    
    UF -->|Fetch Next URL| DL["HTML Downloader Worker Fleet"]
    DL <--> DNS["DNS Cache Resolver"]
    DL <--> ROBOTS["Robots.txt Cache"]
    
    DL --> PARSER["Content Parser & Sanitizer"]
    
    PARSER --> SEEN_DOC{"Content Seen?<br/>(SimHash / MD5)"}
    SEEN_DOC -->|Duplicate -> Ignore| DROP1["Drop Page"]
    SEEN_DOC -->|New Content| STORE_DOC[("Doc Storage / S3<br/>(30 PB Raw HTML)")]
    
    STORE_DOC --> EXTRACT["Link Extractor"]
    EXTRACT --> FILTER["URL Filter<br/>(Bad Extensions, Denylist)"]
    
    FILTER --> SEEN_URL{"URL Seen?<br/>(Bloom Filter)"}
    SEEN_URL -->|Already Crawled| DROP2["Drop URL"]
    SEEN_URL -->|New URL| UF
```

---

## 3. Design Deep Dive

### 1. The URL Frontier (Mercator Crawling Model)

A robust crawler must balance two competing constraints:
1. **Politeness**: Never bombard a single web host with concurrent requests (prevents accidental DoS).
2. **Priority / Freshness**: Prioritize high-quality domains (PageRank) and frequently updated news portals.

```mermaid
flowchart TD
    subgraph PriorityRouting["1. Priority Stage (Prioritizer)"]
        IN_URL["Incoming Discovered URLs"] --> PRIORITIZER["URL Prioritizer<br/>(PageRank / Traffic / Quality)"]
        PRIORITIZER --> FQ1["Front Queue 1 (High Priority)"]
        PRIORITIZER --> FQ2["Front Queue 2 (Medium Priority)"]
        PRIORITIZER --> FQ3["Front Queue 3 (Low Priority)"]
        FQ1 & FQ2 & FQ3 --> F_SEL["Front Queue Selector"]
    end

    subgraph PolitenessRouting["2. Politeness Stage (Domain Queues)"]
        F_SEL --> B_MAP["Host-to-Queue Mapper<br/>(hash(host_name) -> Queue ID)"]
        B_MAP --> BQ1["Back Queue 1 (wikipedia.org)"]
        B_MAP --> BQ2["Back Queue 2 (nytimes.com)"]
        B_MAP --> BQ3["Back Queue 3 (github.com)"]
        
        BQ1 & BQ2 & BQ3 --> B_SEL["Politeness Queue Selector<br/>(Enforces delay timer per host)"]
        B_SEL --> WORKERS["Download Worker Threads"]
    end
```

#### Politeness Selector Logic
- Each back queue corresponds to a single web host/domain.
- A worker thread processes a queue, downloads a page, and enforces a mandatory delay (e.g., $500\text{ ms}$) before fetching the next URL from the same host queue.

---

### 2. Duplicate Detection: URLs vs. Content

```mermaid
flowchart LR
    subgraph URLDedup["URL Deduplication"]
        U["Extracted URL"] --> BF["Bloom Filter in RAM<br/>(Fast 99.99% Membership Check)"]
        BF -->|Not Seen| DB_U[("URL Database")]
    end

    subgraph ContentDedup["Content Deduplication"]
        HTML["Parsed HTML"] --> HASH["SimHash / 64-bit Fingerprint"]
        HASH --> HAMMING{"Hamming Distance <= 3 bits?"}
        HAMMING -->|Yes: Near-Duplicate| SKIP["Skip Storing"]
        HAMMING -->|No: Novel Content| STORE["Store in Object Storage"]
    end
```

- **Bloom Filter for URLs**: Eliminates disk lookups for billions of visited URLs with minimal RAM.
- **SimHash for Content**: Detects near-identical web pages (e.g., pages with only changing timestamp footers or ads) by measuring Hamming distance between 64-bit feature vectors.

---

### 3. HTML Downloader Optimizations

```mermaid
flowchart TD
    subgraph DownloaderOptimizations["Downloader Acceleration"]
        DNS_C["<b>1. Local DNS Cache</b><br/>Avoids 10–50 ms DNS roundtrips via in-memory IP map."]
        GEO_D["<b>2. Geographic Crawl Workers</b><br/>Deploy crawler nodes in US, EU, and Asia close to target servers."]
        TIMEOUT["<b>3. Short Socket Timeouts</b><br/>Set 5–10s read timeouts to avoid hanging on slow/dead servers."]
        ROBOT_C["<b>4. Robots.txt Local Cache</b><br/>Cache host crawling rules with 24h TTL."]
    end
```

---

### 4. Spider Traps & Edge Case Defense

```mermaid
mindmap
  root((Crawler Defenses))
    Spider Traps
      Infinite URL loops: /a/b/a/b/a/b
      Max URL depth limit: 20 levels
      Max URL string length: 512 bytes
    Malformed HTML
      Defensive HTML parsers (Jsoup / Beautiful Soup)
      Payload byte limit: 10 MB cap
    Politeness Compliance
      Strict adherence to robots.txt
      User-Agent string with contact email
    Server Throttling
      Back-off on HTTP 429 & 503 errors
```

---

## 4. Architectural Summary

| Subsystem | Core Technical Choice | Scaling Benefit |
|:---|:---|:---|
| **URL Frontier** | 2-Stage Front/Back Queues (Mercator) | Decouples PageRank priority scheduling from domain politeness rate-limiting. |
| **URL Deduplication** | Distributed Bloom Filter Cluster | Memory-efficient visited URL filtering across billions of URLs. |
| **Content Deduplication**| SimHash Fingerprinting | Filters out near-duplicate pages without byte-by-byte comparisons. |
| **DNS Resolution** | In-Memory Asynchronous DNS Cache | Eliminates repetitive DNS latency on the critical download path. |
| **Storage Architecture** | S3 / Distributed Object Store | Highly cost-effective $30\text{ PB}$ durable archival storage. |

---

## References

1. Mercator: A Scalable, Extensible Web Crawler (Heydon & Najork): https://www.researchgate.net/publication/220875323_Mercator_A_scalable_extensible_web_crawler
2. SimHash: Detecting Near-Duplicates for Web Crawling (Manku et al. Google): https://dl.acm.org/doi/10.1145/1242572.1242592
3. The Robots Exclusion Protocol: https://www.robotstxt.org/

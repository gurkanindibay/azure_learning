---
type: Article
title: "Our RAG Got Better When We Fixed Chunking, Not Embeddings"
description: "Why swapping embedding models repeatedly failed to improve RAG accuracy, and how switching from naive character chunking to structure-aware paragraph splitting boosted retrieval from 61% to 89%."
source: "https://medium.com/@kp9810113/our-rag-got-better-when-we-fixed-chunking-not-embeddings-59a9a941d3a6"
author: "The Concurrent Mind"
published: 2026-08-09
timestamp: 2026-08-22T00:00:00Z
---

# Our RAG Got Better When We Fixed Chunking, Not Embeddings

> **Source**: [Medium — The Concurrent Mind](https://medium.com/@kp9810113/our-rag-got-better-when-we-fixed-chunking-not-embeddings-59a9a941d3a6)  
> **Key Takeaways**: [37. RAG Chunking vs. Embeddings — Key Takeaways](../../system-design-architecture/ai-ml-infrastructure/37-ai-key-takeaways.md)  
> **Dictionary**: [Structure-Aware Chunking](../../reference-dictionary/ai-ml-llm.md#structure-aware-chunking), [Semantic Chunking](../../reference-dictionary/ai-ml-llm.md#semantic-chunking), [Chunk Inspection Audit](../../reference-dictionary/ai-ml-llm.md#chunk-inspection-audit)

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*nC6XF1clTgRbhe-tUV3Oyg.png)

Three weeks ago I sat in a war room with four engineers, staring at a Slack thread titled *RAG Is Trash Again*, and every single person in that thread wanted to swap the embedding model. Again. That was the third time in two months.

I remember thinking, what if the problem was never the model.

If you have ever shipped a retrieval system that answers questions beautifully in the demo and falls apart the moment a real user asks something slightly off script, you already know this feeling. You blame the embeddings first. Everyone does.

It feels technical, and swapping a model line in code feels like progress even when it changes nothing.

We swapped models three separate times. A well known OpenAI embedding, then a fine tuned open source model, then a hosted alternative from another provider.

Retrieval accuracy barely moved. It sat somewhere around sixty percent no matter what vector math we threw at it.

---

## The Question Nobody Asked

While the team argued about similarity thresholds, I pulled up twenty of our worst failing queries and manually read the actual chunks being retrieved. Not the scores. The raw text, sentence by sentence.

What I found was almost funny in a bitter way, the kind of laugh you let out when the mistake has been sitting in front of you the entire time.

A policy document about refund eligibility got sliced right between the condition and the consequence.

The model was never confused about meaning. It never had the meaning in front of it to begin with.

We were feeding half a thought into an expensive similarity search and wondering why the answers felt hollow and disconnected from the source material.

Here is roughly what our original chunking looked like:

```python
def chunk_text(text: str, size: int = 512) -> list[str]:
    chunks = []
    for i in range(0, len(text), size):
        chunks.append(text[i:i + size])
    return chunks
```

Clean, simple, and quietly wrecking every document we fed it. It cuts by character count with zero awareness of sentences, headers, or ideas. A window of five hundred and twelve characters does not know it just severed a legal clause in half.

```text
Original doc:
[Refund policy: customers are eligible for a
 refund if the product was returned within
 thirty days of purchase and unused.]

Naive chunk 1: "Refund policy: customers are eligible for a"
Naive chunk 2: "refund if the product was returned within"
Naive chunk 3: "thirty days of purchase and unused."
```

Three fragments, zero complete ideas, and a retrieval model asked to find meaning inside the wreckage.

---

## What We Changed

We stopped chunking by character count and started chunking by structure, using paragraphs and headers as the natural unit of truth, with a small overlap so context does not get orphaned at the edges.

```python
def chunk_by_paragraph(text: str, overlap: int = 50) -> list[str]:
    paras = text.split("\n\n")
    chunks = []
    buffer = ""
    for p in paras:
        if len(buffer) + len(p) < 800:
            buffer += p + " "
        else:
            chunks.append(buffer.strip())
            buffer = buffer[-overlap:] + p + " "
    if buffer:
        chunks.append(buffer.strip())
    return chunks
```

Nothing clever, nothing academic. We simply respected the shape the original writer gave the document instead of slicing it like a loaf of bread with a ruler in place of a knife.

---

## What Semantic Chunking Actually Broke

Before we landed on paragraph aware chunking, we tried something more sophisticated first, splitting the text wherever the meaning between two neighboring sentences drifted apart, measured by embedding distance. On paper it sounded like the correct academic answer.

In practice it made things worse before it made things better. Our documents came from scanned files converted to plain text, and sentence boundaries were often unreliable, with stray line breaks and broken punctuation.

The semantic splitter reacted to that noise and created far more chunks than before, each one thinner and less useful than the last.

We had to add a floor and a ceiling around chunk size just to keep it sane, and only after that tuning did the simpler paragraph based approach quietly outperform it.

The fancier method was not wrong, it just needed cleaner input than we had, and that humbled us more than any embedding benchmark ever did.

---

## The Numbers That Made The Room Go Quiet

We ran the same evaluation set of two hundred real user queries against both pipelines, same embedding model, same retriever, only the chunking changed.

These are our own measurements from our own system, not a published benchmark, but they told a story loud enough to end the argument in that room:

| Metric | Character Chunking | Structure-Aware Chunking |
|:---|---:|---:|
| **Retrieval Accuracy** | 61% | **89%** |
| **Answer Relevance (Human Rated)** | 6.2 / 10 | **8.7 / 10** |
| **Average Chunks Needed per Query** | 6 | **3** |

Same embedding model. Same vector database. Same everything except how we cut the text before it ever touched a vector.

---

## The Lesson That Actually Stuck

The sting was that this was never exotic. We spent weeks chasing a smarter brain while handing it torn pages instead of whole ones, and no amount of intelligence fixes a sentence that was never allowed to finish.

I think about that Slack thread often now, the one demanding another model swap, and how close we came to spending another sprint chasing the wrong fix.

The real answer was slower and less glamorous: reading actual text with actual eyes instead of trusting a similarity score to tell the whole truth.

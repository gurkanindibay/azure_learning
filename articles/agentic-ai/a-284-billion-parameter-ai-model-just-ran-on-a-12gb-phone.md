---
type: Article
title: "A 284 Billion Parameter AI Model Just Ran on a 12GB Phone"
description: "How BigMoeOnEdge ran a 284B parameter MoE model on a 12GB RAM mobile device using demand-paged flash weight streaming rather than model compression."
source: "https://medium.com/@kanishks772/a-284-billion-parameter-ai-model-just-ran-on-a-12gb-phone-ae8abaa402e6"
author: "The Latency Gambler"
published: 2026-08-17
timestamp: 2026-08-23T00:00:00Z
---

# A 284 Billion Parameter AI Model Just Ran on a 12GB Phone

> **Source**: [Medium — The Latency Gambler](https://medium.com/@kanishks772/a-284-billion-parameter-ai-model-just-ran-on-a-12gb-phone-ae8abaa402e6)  
> **Key Takeaways**: [38. On-Device MoE Inference & Flash Weight Streaming — Key Takeaways](../../system-design-architecture/ai-ml-infrastructure/38-ai-key-takeaways.md)  
> **Dictionary**: [MoE (Mixture of Experts)](../../reference-dictionary/ai-ml-llm.md#moe), [Demand Paging for MoE Weights](../../reference-dictionary/ai-ml-llm.md#demand-paging-moe-weights), [Read-Compute Overlapping (Inference)](../../reference-dictionary/ai-ml-llm.md#read-compute-overlapping-inference)

DeepSeek V4 Flash has 284 billion parameters and takes up about 91 gigabytes on disk. A phone with 12 gigabytes of RAM has no business running it — that model is roughly seven times larger than the memory available to hold it. An open-source project called BigMoeOnEdge did it anyway, CPU only, with output byte-identical to running the model fully loaded in memory. The trick isn’t compression. It’s rethinking what actually needs to be in RAM in the first place.

---

## The Gap MoE Architecture Leaves Open

Mixture-of-Experts (MoE) models are built from many small sub-networks, called experts, spread across each layer. For any single token, a router picks only a handful of those experts to actually run — the rest sit unused for that step. That’s what makes MoE models efficient to compute: a 284-billion-parameter model might only touch a few billion parameters per token.

The problem is that traditional inference still loads the entire model into memory anyway, because you don’t know in advance which experts any given token will need. All that architectural efficiency in compute doesn’t translate into savings on memory, which is exactly the resource a phone doesn’t have to spare.

---

## What BigMoeOnEdge Actually Changes

The project’s fix is architectural, not a shortcut. It keeps only the small, always-needed part of the model resident in RAM — attention layers, shared components, the router itself — and leaves every expert on disk. When a layer’s router picks the experts a token needs, the engine reads exactly those weight slices from flash storage at that moment, runs the computation, and moves on. Nothing is approximated or dropped: the output is byte-identical to running the same model fully loaded, because it’s the same weights and the same math, just fetched right when they’re needed instead of held the whole time.

```text
Traditional MoE inference                 BigMoeOnEdge on-device inference

Load entire model into RAM                Load small resident core into RAM
  - every expert, every layer                - attention, router, shared layers
  - requires RAM ≥ model size                       │
         │                                          ▼
         ▼                                For each token, at each layer:
 Run all layers from RAM                   router picks the needed experts
                                                     │
                                                     ▼
                                           read only those expert weights
                                           from flash, just in time
                                                     │
                                                     ▼
                                           optional: cache hot experts,
                                           overlap reads with compute
```

A simplified version of that per-layer decision looks like this:

```python
# Conceptual illustration of the approach, not the project's literal source
def on_layer_eval(layer, token_state, flash_storage, cache):
    needed_experts = layer.router.select_experts(token_state)
    for expert_id in needed_experts:
        if expert_id not in cache:
            cache[expert_id] = flash_storage.read(layer.id, expert_id)
    weights = [cache[e] for e in needed_experts]
    return layer.compute(token_state, weights)
```

---

## Built on Top of, Not Instead of

The other notable choice is what the project didn’t do: fork `llama.cpp`. It’s built entirely against `llama.cpp`’s public evaluation API, hooking the moment each layer selects its experts rather than replacing any of the underlying engine. That means every quantization format, tokenizer, and chat template `llama.cpp` already supports works automatically, with no separate maintenance. Supporting a new MoE model architecture is a registry entry, not a rewrite.

There’s one narrow exception: an optional overlap mode, which lets expert reads happen while the previous computation is still running, needed a small hook into `llama.cpp`’s CPU kernel that the public API doesn’t expose. That piece lives as a self-contained, roughly 25-line addition on a separate branch, does nothing when it isn’t turned on, and is meant to be deleted the moment upstream `llama.cpp` exposes the same capability natively.

---

## The Honest Number

DeepSeek V4 Flash, the 284-billion-parameter model, runs at well under one token per second on a 12GB phone in the project’s own demo — flash storage bandwidth is now the bottleneck, not compute. That’s a feasibility result, not a usable chat experience. Smaller MoE models fare much better in the same framework, since fewer and smaller expert reads are needed per token, putting them at genuinely workable speeds on the same hardware. The 284B run is best read as a proof that the ceiling exists, not a recommendation to try to chat with it.

---

## What Actually Shifted

The interesting part isn’t the specific speed number. It’s that the limiting question for how large a model you can run locally quietly changed from “can you fit it in RAM” to “how fast can your storage stream the parts you actually need.” RAM capacity on a phone barely moves generation over generation. Flash storage bandwidth moves faster, and it’s a problem hardware trends are already chipping away at — which makes this less a party trick and more an early look at where the actual ceiling for on-device inference is heading.

---

## Source Reference

- GitHub Repository: [Helldez/BigMoeOnEdge](https://github.com/Helldez/BigMoeOnEdge)

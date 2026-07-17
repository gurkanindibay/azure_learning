---
type: Reference
title: "Media Processing & Async Pipelines"
description: "Splitting video at **keyframe (Group of Pictures) boundaries** for clean cuts. Chunks cut at keyframes can be decoded independently; chunks cut mid-GOP produce artifacts."
timestamp: 2026-06-14T00:00:00Z
---

# Media Processing & Async Pipelines

> **Domain**: Video processing, adaptive streaming, parallel work distribution, and encoding infrastructure.
> **Parent**: [Reference Dictionary](index.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| GOP-Aligned Chunking | [`#gop-aligned-chunking`](#gop-aligned-chunking) |
| Transcoding | [`#transcoding`](#transcoding) |
| DASH / HLS | [`#dash-hls`](#dash-hls) |
| Fan-Out / Fan-In | [`#fan-out-fan-in`](#fan-out-fan-in) |
| Progressive Availability | [`#progressive-availability`](#progressive-availability) |
| Work Stealing | [`#work-stealing`](#work-stealing) |
| Two-Pass Encoding | [`#two-pass-encoding`](#two-pass-encoding) |
| Embarrassingly Parallel | [`#embarrassingly-parallel`](#embarrassingly-parallel) |
| Buffer-based Bitrate Adaptation | [`#buffer-based-bitrate-adaptation`](#buffer-based-bitrate-adaptation) |
| Quality Ladder | [`#quality-ladder`](#quality-ladder) |

---

## GOP-Aligned Chunking

Splitting video at **keyframe (Group of Pictures) boundaries** for clean cuts. Chunks cut at keyframes can be decoded independently; chunks cut mid-GOP produce artifacts.

> **Key insight**: Chunk boundaries must align with keyframes. Closed GOP = each GOP is self-contained.

**Also see**: [DASH/HLS](#dash-hls), [Transcoding](#transcoding)

---

## Transcoding

Converting video **between formats, resolutions, and bitrates**. A single source video may produce 5+ output renditions (1080p, 720p, 480p, 360p, 240p) for adaptive streaming.

| Technique | Detail |
|:---|:---|
| **Per-title encoding** | Optimize parameters per video — simpler video = lower bitrate |
| **Two-pass encoding** | First pass analyzes complexity; second pass encodes optimally |
| **Hardware encoding** | GPU/ASIC — 10-50× faster than CPU encoding |

**Also see**: [DASH/HLS](#dash-hls), [Two-Pass Encoding](#two-pass-encoding)

---

## DASH / HLS

**Adaptive bitrate streaming** protocols. The player detects network conditions and switches between quality levels seamlessly.

| Protocol | Origin |
|:---|:---|
| **DASH** | MPEG standard — codec-agnostic |
| **HLS** | Apple — widely supported on iOS/macOS |

> Both use manifests that describe available resolutions, bitrates, and chunk URLs.

**Also see**: [Transcoding](#transcoding), [GOP-Aligned Chunking](#gop-aligned-chunking)

---

## Fan-Out / Fan-In

Split large work into **independent units** → process in parallel → aggregate results. Classic pattern for media processing, batch jobs, and map-reduce workloads.

```
1 large job → Fan-Out → 1000 chunks → process in parallel → Fan-In → 1 result
```

**Also see**: [Embarrassingly Parallel](#embarrassingly-parallel), [Work Stealing](#work-stealing)

---

## Progressive Availability

Release the **lowest resolution first**, upgrade quality as higher resolutions complete. The user sees something immediately; quality improves over seconds.

**Also see**: [DASH/HLS](#dash-hls), [Fan-Out/Fan-In](#fan-out-fan-in)

---

## Work Stealing

**Fast workers pull more work** from a shared queue instead of waiting for slow workers. Prevents stragglers from blocking overall progress. More efficient than round-robin distribution when task durations vary.

**Also see**: [Fan-Out/Fan-In](#fan-out-fan-in)

---

## Two-Pass Encoding

**First pass** analyzes video complexity frame-by-frame. **Second pass** encodes with optimal bit allocation based on the analysis. Produces better quality at the same bitrate — at the cost of encoding time.

**Also see**: [Transcoding](#transcoding)

---

## Embarrassingly Parallel

Work decomposable into **fully independent units** with no dependencies. Each chunk can be processed without any coordination. Ideal for fan-out/fan-in, media processing, and batch compute.

**Also see**: [Fan-Out/Fan-In](#fan-out-fan-in)

---

## Buffer-based Bitrate Adaptation

An **adaptive bitrate (ABR) algorithm** that selects the next video chunk's quality based on the **playback buffer depth** rather than throughput estimation alone. Unlike throughput-only ABR, which guesses wrong under rapid network fluctuations, buffer-based adaptation watches how many seconds of video are queued and only steps down when the buffer is genuinely at risk of running dry.

> **Key insight**: Throughput is a point-in-time measurement that does not capture the buffer's ability to absorb short-term variance. Monitoring buffer health cuts rebuffering sharply compared to throughput-only adaptation (Netflix/Stanford, SIGCOMM 2014).

### Key Characteristics
- **Buffer-aware**: Tracks playback buffer depth (seconds) in addition to measured throughput
- **Cautious start**: Begins at a conservative bitrate and climbs as the buffer fills
- **Late downgrade**: Only steps down quality when the buffer actually runs low, not on every throughput dip
- **Smooth transitions**: Avoids quality oscillation by using hysteresis in the decision threshold

### When to Use
- Video streaming over variable network conditions (Wi-Fi, mobile, congested home networks)
- Any adaptive streaming pipeline where rebuffering is worse than a temporary quality drop
- Combined with per-title encoding ladders for maximum efficiency per content type

### When NOT to Use
- Live/low-latency streaming where buffer sizes are necessarily small and throughput is the dominant signal
- Fixed-bitrate delivery where adaptation is not possible (legacy broadcast)
- Non-streaming workloads where buffer depth has no meaning

### Also see
- [DASH/HLS](#dash-hls) · [Quality Ladder](#quality-ladder) · [Transcoding](#transcoding)

---

## Quality Ladder

A **pre-encoded set of bitrate/resolution pairs** for a single piece of content, enabling adaptive bitrate streaming. Each rung represents a different quality level — from low-bitrate audio-only (~235 kbps) up to 4K (~15 Mbps). The player climbs or descends the ladder based on network conditions and buffer health.

> **Key insight**: Per-title encoding builds a custom ladder for each piece of content. A flat-color cartoon needs far fewer bits per rung than grainy handheld action, so each title gets its own optimized ladder rather than a one-size-fits-all set of renditions.

### Key Characteristics
- **Per-title optimization**: Each title's ladder is tuned to its visual complexity — simpler content achieves the same perceived quality at lower bitrates
- **Multiple renditions**: Typically 5-12 quality levels spanning audio-only through 4K HDR
- **Codec-aware**: More efficient codecs (AV1, HEVC) reduce the bitrate needed per rung, making the same ladder cheaper to deliver
- **Chunk-aligned**: Each rung's video is split into a few-second chunks that can be switched independently

### When to Use
- Any adaptive streaming pipeline (VOD, live with delay)
- Content catalogs with diverse visual complexity where per-title optimization saves significant bandwidth
- Delivery over constrained or variable networks where quality tradeoffs are necessary

### When NOT to Use
- Fixed-quality delivery where adaptation is not needed
- Extremely latency-sensitive live streaming where per-title encoding is too slow
- When storage cost of multiple renditions exceeds the bandwidth savings

### Also see
- [DASH/HLS](#dash-hls) · [Buffer-based Bitrate Adaptation](#buffer-based-bitrate-adaptation) · [Transcoding](#transcoding) · [GOP-Aligned Chunking](#gop-aligned-chunking)

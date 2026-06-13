# Media Processing & Async Pipelines

> **Domain**: Video processing, adaptive streaming, parallel work distribution, and encoding infrastructure.
> **Parent**: [Reference Dictionary](README.md)

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

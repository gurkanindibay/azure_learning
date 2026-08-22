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
| Adaptive Bitrate Streaming (ABR) | [`#adaptive-bitrate-streaming-abr`](#adaptive-bitrate-streaming-abr) |
| HLS (HTTP Live Streaming) | [`#hls-http-live-streaming`](#hls-http-live-streaming) |
| MPEG-DASH | [`#mpeg-dash`](#mpeg-dash) |
| Transcoding DAG Model | [`#transcoding-dag-model`](#transcoding-dag-model) |
| Selective Forwarding Unit (SFU) | [`#selective-forwarding-unit-sfu`](#selective-forwarding-unit-sfu) |

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

## Adaptive Bitrate Streaming (ABR)

A **video delivery technique** where the source video is encoded at multiple bitrates and resolutions, and the player dynamically switches between quality levels based on the viewer's available bandwidth and device capabilities. Prevents buffering by degrading quality rather than stopping playback.

### Key Characteristics
- **Multiple renditions**: a single source produces 1080p, 720p, 480p, 360p, 240p variants
- **Client-side decision**: the player monitors buffer level and download speed to choose the next chunk's quality
- **Chunked delivery**: video is split into small segments (2-10 seconds); quality can change at chunk boundaries
- **ABR ladder**: the set of available bitrate-resolution pairs, optimized per-title or per-genre

### When to Use
- Video streaming over variable network conditions (Netflix, YouTube)
- Live streaming where real-time adaptation is essential
- Any video delivery where users are on heterogeneous connections (mobile, WiFi, wired)

### When NOT to Use
- When all viewers have guaranteed, stable bandwidth (e.g., internal corporate streaming)
- For short clips where encoding overhead exceeds the benefit
- When storage cost for multiple renditions is prohibitive

### Also see
- [DASH / HLS](#dash-hls) · [Transcoding](#transcoding) · [Quality Ladder](#quality-ladder) · [Buffer-based Bitrate Adaptation](#buffer-based-bitrate-adaptation)

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

---

## HLS (HTTP Live Streaming)

An **HTTP-based adaptive bitrate streaming communications protocol** developed by Apple. It breaks overall video streams into a sequence of small HTTP-based file downloads (historically MPEG-2 Transport Streams `.ts`, now also fragmented MP4 `.m4s`), each download loading one short chunk of an overall potentially unbounded transport stream. A master `.m3u8` playlist coordinates available bitrate streams and chunk locations.

### Key Characteristics
- **Manifest format**: Extended M3U playlist (`.m3u8`) with hierarchical master/variant structure
- **Chunk format**: MPEG-2 TS or Fragmented MP4 (fMP4) chunks, typically 2–6 seconds in length
- **Universal Apple support**: Required by iOS App Store guidelines for video exceeding 3 minutes or 5 MB
- **Standard HTTP transport**: Traversable across firewalls and cacheable on existing standard CDN edge servers

### When to Use
- Video on Demand (VOD) and Live streaming targeting iOS, macOS, Safari, and cross-platform web players (via hls.js)
- Edge-cached video distribution leveraging commoditized CDN web infrastructure
- Secure streaming requiring AES-128 chunk encryption or FairPlay DRM

### When NOT to Use
- Ultra-low latency requirements under 1 second (such as live bidirectional interaction; prefer WebRTC) without Low-Latency HLS (LL-HLS) tuning
- Environments strictly requiring non-segmented, continuous socket streams

### Also see
- [Adaptive Bitrate Streaming (ABR)](#adaptive-bitrate-streaming-abr) · [MPEG-DASH](#mpeg-dash) · [Quality Ladder](#quality-ladder) · [GOP-Aligned Chunking](#gop-aligned-chunking)

---

## MPEG-DASH

An **international standard adaptive bitrate streaming protocol** (ISO/IEC 23009-1) that enables high-quality streaming of media content over the Internet delivered from conventional HTTP web servers. Unlike proprietary protocols, DASH is codec-agnostic and uses an XML-formatted Media Presentation Description (`.mpd`) manifest.

### Key Characteristics
- **Codec agnostic**: Works seamlessly with H.264, H.265 (HEVC), VP9, AV1, and AAC/Opus audio
- **Manifest format**: XML-based Media Presentation Description (`.mpd`) containing Period, AdaptationSet, and Representation elements
- **Container format**: Segmented ISO Base Media File Format (fragmented MP4) and WebM
- **DRM interoperability**: Supports Common Encryption (CENC) allowing a single set of media files to decrypt under Widevine, PlayReady, or FairPlay

### When to Use
- Standardized cross-platform video delivery on Android, Smart TVs, game consoles, and modern desktop browsers (via dash.js)
- Multi-DRM production environments where storing separate encrypted asset copies per platform is cost-prohibitive
- Advanced subtitle, multi-language audio, and dynamic ad-insertion (DAI) workflows

### When NOT to Use
- Pure native iOS/Safari environments where native Safari lacks DASH playback without JavaScript MSE polyfills
- Low-complexity architectures where a single HLS pipeline satisfies all client requirements

### Also see
- [HLS (HTTP Live Streaming)](#hls-http-live-streaming) · [Adaptive Bitrate Streaming (ABR)](#adaptive-bitrate-streaming-abr) · [Transcoding](#transcoding)

---

## Transcoding DAG Model

A **modular pipeline execution architecture** that structures video ingestion and processing as a Directed Acyclic Graph (DAG). Rather than treating video processing as a monolithic linear task, the DAG splits source video at GOP keyframe boundaries into independent chunks and parallelizes sequential transformations across distributed workers.

### Key Characteristics
- **Graph-based task decomposition**: Stages include demuxing, video splitting, parallel multi-resolution encoding, audio extraction, watermarking, thumbnail generation, and manifest merging
- **Fine-grained parallelism**: Unblocks horizontal scaling across spot/preemptible worker clusters
- **Fault containment**: Failure in encoding a single 6-second segment at 1080p triggers a retry of only that graph node rather than restarting the entire hour-long video
- **Resource specialization**: CPU-intensive audio filtering and GPU-accelerated video rendering execute on dedicated, right-sized compute nodes

### When to Use
- Large-scale video platforms (YouTube, TikTok, Netflix) processing millions of user uploads daily
- Complex post-processing pipelines requiring conditional execution (e.g., AI moderation, automated captions, multi-codec rendering)
- Cloud cost optimization allowing aggressive use of ephemeral GPU instances

### When NOT to Use
- Simple, low-volume video hosting where a single FFmpeg command suffices
- Real-time video conferencing where frame-by-frame latency budgets rule out batch chunking

### Also see
- [Transcoding](#transcoding) · [GOP-Aligned Chunking](#gop-aligned-chunking) · [Fan-Out / Fan-In](#fan-out-fan-in) · [Embarrassingly Parallel](#embarrassingly-parallel)

---

## Selective Forwarding Unit (SFU)

A **WebRTC media server architecture** where each participant sends their media stream to a central server, which selectively forwards it to other participants — without decoding or mixing. Unlike MCU (Multipoint Control Unit), the SFU does not transcode; it routes packets. This is the architecture behind Discord (2.5M+ concurrent voice users) and many modern video conferencing systems.

### Key Characteristics
- **Packet routing, not mixing**: the SFU forwards encoded packets; it does not decode or re-encode media
- **Per-receiver bitrate adaptation**: sends different quality levels (simulcast) to participants based on their available bandwidth
- **Lower CPU cost than MCU**: no transcoding means the server can handle many more concurrent streams
- **End-to-end encryption compatible**: the SFU can forward encrypted packets it cannot read (E2EE with insertable streams)

### When to Use
- Group video/voice calls with >3 participants where peer-to-peer mesh would overwhelm each client's uplink
- Large-scale real-time audio rooms (Discord stages, Twitter Spaces, Clubhouse)
- Systems where server CPU cost must scale sub-linearly with participant count

### When NOT to Use
- 1:1 calls where direct P2P mesh has lower latency and zero server cost
- Legacy endpoints (PSTN, SIP) that cannot decode multiple incoming streams — requires an MCU to mix into a single stream
- Ultra-low-bandwidth clients that cannot receive multiple incoming streams

### Also see
- [Adaptive Bitrate Streaming (ABR)](#adaptive-bitrate-streaming-abr) · [HLS (HTTP Live Streaming)](#hls-http-live-streaming)


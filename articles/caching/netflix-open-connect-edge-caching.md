---
type: Article
title: "How Netflix Handles 260 Million Concurrent Streams Without Buffering"
source: "https://medium.com/beyond-localhost/how-netflix-handles-260-million-concurrent-streams-without-buffering-cbbaad6c81ca"
author: "The Speedcraft Lab"
published: 2026-07-10
created: 2026-07-17
description: "How Netflix pre-positions content at the ISP edge and uses buffer-aware adaptive bitrate streaming to serve 260M+ households without buffering — most of the hard problem is solved before you press play."
tags:
  - caching
  - cdn
  - streaming
  - edge-computing
  - adaptive-bitrate
---

# How Netflix Handles 260 Million Concurrent Streams Without Buffering

> **Source**: [Medium — Beyond Localhost](https://medium.com/beyond-localhost/how-netflix-handles-260-million-concurrent-streams-without-buffering-cbbaad6c81ca)

## Most of the hard problem is solved before you press play

A few weeks ago my Wi-Fi dipped in the middle of an episode. The picture went soft for about ten seconds, then quietly sharpened again. No spinner. No stall.

That small moment sits at the end of a long chain, and almost none of that chain runs when you press play. Netflix passed 260 million member households in early 2024 and has kept growing past 300 million since. On one night in November 2024, 65 million streams ran at the same time for a single boxing match.

How Netflix handles that kind of load in 2026 is mostly decided hours before the request ever leaves your house. That is the whole story, and it changed how I think about caching.

## Why the Obvious Design Falls Over

The design most of us would sketch first looks reasonable. Store the video files in a few big data centres, put a commercial CDN in front, and let the caches fill up as people watch.

Do the maths and it falls over fast.

Sixty-five million streams at an average of about 5 Mbps works out to over 300 terabits per second. No cluster of central servers pushes that across the public internet. The transit bills alone would sink you, and the peering links would choke long before your machines did. Sandvine, the firm that measures this sort of thing, has repeatedly found Netflix carrying a double-digit share of all downstream traffic on the internet.

The on-demand cache has a quieter failure too. Think about a premiere. When a new season drops at midnight, a pull-through CDN holds none of it yet. Millions of requests arrive in the same minute, every one a cache miss, and all of them run back to the origin at once.

So the naive design buffers hardest at the exact moment the most people are watching. Netflix got around this by inverting the problem, twice.

## The First Mechanism — The Movie Is Already Down the Street

Netflix built its own CDN and called it Open Connect. The unusual part is physical. It ships real servers, called Open Connect Appliances, into ISP data centres and internet exchange points, free of charge to ISPs that qualify. By Netflix's own published count, that footprint had passed 17,000 servers across 158 countries by 2021.

ISPs take the boxes because every byte served from inside their own network is a byte they don't pay to haul across transit links. Both sides save money, which is why the arrangement has lasted.

Each appliance holds the slice of the catalogue its region is most likely to watch. And the boxes are filled ahead of time. Every night, during a quiet-hours fill window, Netflix predicts tomorrow's regional demand and copies the right titles onto the right appliances. Friday's premiere is sitting on a server inside your ISP's building on Thursday night.

Now picture the diagram. Two arrows leave your living room. A skinny one goes the long way, to AWS, where Netflix runs everything except the video itself. Login, browsing, recommendations, DRM and the steering service that picks your appliance all live there. What comes back is a small manifest of URLs.

The fat arrow is the video, and it travels a few miles at most, from the appliance sitting inside your ISP's network. By Netflix's own account, effectively all of its video traffic comes from Open Connect. The movie never comes from the cloud.

That split is deliberate. Netflix finished moving everything to AWS back in 2016, then chose to keep its heaviest workload out of the cloud, on hardware it designs itself. The control plane lives where flexibility is cheap. The data plane lives where the bytes are.

And the premiere stampede? It lands on thousands of already-warm caches at once, each one serving its own neighbourhood. There is no single origin left to overwhelm.

## The Second Mechanism — Your TV Renegotiates Quality as You Watch

Pre-positioning fixes the internet. It does nothing for your house. The crowded Wi-Fi, the microwave, the sibling in a ranked match — that mess belongs to the client.

Every title is encoded ahead of time into a ladder of quality levels, from roughly 235 kbps at the bottom up to around 15 Mbps for 4K. Since Netflix's per-title encoding work, that ladder is also built per piece of content. A flat-colour cartoon needs far fewer bits than grainy handheld action, so each gets its own ladder.

The video is cut into chunks a few seconds long. Your player downloads a chunk, checks its real throughput and how many seconds of video are sitting in the buffer, then picks the bitrate for the next chunk. Research Netflix published with Stanford (SIGCOMM 2014) showed that watching the buffer, rather than only guessing at throughput, cuts rebuffering sharply.

So playback starts cautious, climbs within seconds, and steps down before the buffer runs dry when your bandwidth dips. You get a softer picture for a moment instead of a spinner. That was my Wi-Fi dip from the opening. The system was working exactly as designed.

There is a quieter third lever too. Netflix has spent years rolling out the AV1 codec across devices, because a more efficient codec means every rung of the ladder costs fewer bits. The same picture survives a worse connection.

Stack the two mechanisms and the shape becomes clear. Open Connect keeps the path from server to your router short and uncrowded. The adaptive player soaks up whatever is left in the last fifty feet. One removes the variance. The other absorbs the remainder.

## The Request Is the Last Step, Not the First

We are trained to treat a request as the start of the work. Request arrives, system responds.

Netflix's setup says the opposite. By the time you press play, the file was chosen last night, encoded into its own ladder months ago, and copied to a box down the street before you got home. Pressing play triggers almost nothing. A small API call, a manifest, then a short local transfer.

Most of the streaming problem is solved before a single byte reaches your home network. At this scale, reacting to demand is already too late.

## What This Looks Like at 1/1000th the Scale

You don't need 17,000 servers to borrow the principle. Move the work to before the request.

- **Launching a feature to 50,000 users?** Warm your CDN and caches at deploy time, so your first real users aren't the ones paying the cache-miss tax.
- **Running a read-heavy dashboard?** Compute the aggregates on a schedule and serve the stored result, rather than running the query on every request.
- **Building for flaky mobile networks?** Ship a quality ladder of your own. Smaller payloads, skeleton states, downgraded images. Degrade, never stall.

The pattern repeats each time. Predict, pre-position, then let the client adapt to whatever mess is left.

Push content close to the edge before demand arrives. If you are reacting to demand, you are already late.

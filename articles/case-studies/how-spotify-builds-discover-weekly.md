---
type: Article
title: "How Spotify Builds Your Discover Weekly Before You Even Wake Up"
source: "https://medium.com/@the_atomic_architect/how-spotify-builds-discover-weekly-recommendation-algorithms-4f976b8094a3"
author:
  - "[[The Atomic Architect]]"
published: 2026-08-23
created: 2026-08-27
description: "How Spotify's Discover Weekly recommendation engine works: Collaborative Filtering with matrix factorization, NLP-based cultural text analysis, deep audio convolutional neural networks, and offline batch taste-space distance computation."
tags:
  - "system-design"
  - "machine-learning"
  - "recommendation-systems"
  - "case-study"
  - "collaborative-filtering"
  - "batch-processing"
---

# How Spotify Builds Your Discover Weekly Before You Even Wake Up

Every Monday morning, before I’ve had coffee, before I’ve even fully opened my eyes most days, there’s a playlist sitting in my Spotify with thirty songs I’ve never heard, and somehow twenty-something of them are actually good.

Not “algorithm trying its best” good.

Genuinely, “how did you know” good.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*zlqzCUcW5GblxEHvRPsDlQ.png)

Songs that feel like they were pulled out of a version of my taste I hadn’t fully articulated to myself yet.

For years I just accepted this as a nice little Monday gift and moved on with my day.

Then one Sunday night, out of pure curiosity, I stayed up looking into how this actually gets built, and what I found genuinely rearranged how I think about the whole thing.

It’s not one clever trick.

It’s three almost completely unrelated systems, none of which know anything about “music” in the way a human does, running overnight, disagreeing with each other constantly, and somehow landing on something that feels uncannily personal by the time you wake up.

Let me walk you through what’s actually happening while you sleep.

---

## The Thing That’s Easy to Assume, and Why It’s Wrong

Here’s the assumption I carried around for years without ever examining it:

Somewhere, Spotify has a model that “understands” my taste, the way a friend who knows your music history might, and it just picks songs that fit.

That’s not really what’s happening.

And once you see the actual mechanism, the real version is honestly more interesting than the story I’d made up in my head.

There isn’t one model that understands you.

There are several systems, each one blind to almost everything the others know, each one contributing a completely different kind of signal.

And the actual magic, if you want to call it that, is in how those signals get combined and filtered down to thirty songs, not in any single system being cleverer than you’d expect.

---

## System One: The Crowd, Not the Song

The first and probably most important signal has almost nothing to do with what a song sounds like.

It’s built entirely from what other people did.

Specifically, which songs tend to show up on the same playlists as each other, across an enormous number of playlists made by real users for their own reasons, completely unrelated to any recommendation system.

Think about what a playlist actually represents, structurally.

Someone made a “late night drive” playlist, and by putting fifty songs into it, they’ve quietly encoded a huge amount of information:

These songs belong together in some human, contextual sense, even if a machine has no idea what “late night drive” actually means as a concept.

Multiply that by hundreds of millions of playlists, and you get an enormous web of co-occurrence.

Which songs keep showing up next to which other songs, across an almost unimaginable number of independent human decisions.

```text
playlist "late night drive":      [Song A, Song B, Song C, Song D]

playlist "study focus":           [Song B, Song E, Song F]

playlist "gym motivation":        [Song A, Song G, Song H]

playlist "sad songs 3am":         [Song C, Song D, Song I]

Song A and Song C never appear together directly.

But Song A co-occurs with B and D.
Song C co-occurs with D too.

A and C end up "close" to each other through shared neighbors,
even though no single playlist ever put them side by side.
```

That’s the rough shape of **collaborative filtering**.

And the specific technique that makes it computationally workable at this scale is something called **matrix factorization**.

You build a giant grid:

- Users or playlists down one side
- Songs across the top
- Every cell is essentially “does this song appear in this context?”

That grid is enormous and almost entirely empty.

Most songs never appear in most playlists.

But hidden inside the pattern of what *does* co-occur is a much smaller, denser set of latent factors.

Maybe a few hundred numbers per song.

They don’t correspond to anything human-readable like “genre” or “mood,” but they mathematically capture the same kinds of relationships those labels describe.

```text
Song A: [0.82, -0.31, 0.14, 0.55, ...]

Song C: [0.79, -0.28, 0.19, 0.51, ...]

These vectors are close together in that space,
purely because they kept showing up in similar company,
not because anyone tagged them as similar.
```

Two songs end up mathematically “close” simply because they travel in the same crowds.

The same way you can infer a lot about a person by who their friends are without ever meeting them directly.

Nothing in this system has ever “listened” to either song.

It’s pure social proof encoded as geometry.

---

## System Two: What the Internet Is Actually Saying

The second signal comes from somewhere that surprised me completely when I first read about it:

**Text.**

Not lyrics.

The actual written language people use when they talk about music anywhere on the internet.

- Music blogs
- Playlist titles
- Descriptions
- Articles
- Forums

Anywhere humans are writing words near the name of an artist or song.

The rough idea is **natural language processing** applied at massive scale.

Scanning huge amounts of text and tracking which artists and songs keep getting mentioned near each other, and which descriptive words repeatedly appear alongside them.

If a thousand different articles independently describe an artist using words like:

- atmospheric
- melancholic
- driving

that artist gradually accumulates a relationship with those ideas.

Not because anyone explicitly tagged them.

But because people keep talking about them the same way.

```text
"...their sound is atmospheric and driving, similar to Artist B..."

"...another melancholic, atmospheric release from Artist A..."

"...if you liked Artist B's last record,
   Artist A scratches the same itch..."

Pattern extracted:

Artist A and Artist B keep appearing near each other,
near similar descriptive language,
across many independent pieces of writing.
```

This matters because it catches something collaborative filtering struggles with: **new artists**.

A brand-new artist with little playlist history has almost no signal in System One.

There simply isn’t enough data yet.

But if music writers and listeners are already discussing that artist alongside established acts, text-based signals can place them into the recommendation ecosystem long before playlist behavior becomes meaningful.

---

## System Three: The Actual Audio

The third piece looks directly at the music itself:

- Tempo
- Key
- Energy
- Acoustic texture
- Patterns inside the raw waveform

Historically, Spotify has described using neural-network-based audio analysis (Convolutional Neural Networks operating on audio spectrograms) to extract characteristics directly from sound files without relying on human labels.

This system exists primarily to solve the **cold-start problem**.

A song uploaded yesterday may have:

- No playlist history
- No reviews
- No articles
- No listener behavior

Systems One and Two have almost nothing to work with.

The audio itself becomes the only available signal.

By comparing those audio characteristics with millions of existing songs, Spotify can still place the new track somewhere sensible in the broader recommendation ecosystem.

```text
DIAGRAM: Three systems, three different inputs

SYSTEM 1                 SYSTEM 2                 SYSTEM 3

Playlist co-occurrence   Text mentions            Raw audio features
(Millions of playlists)  (Blogs, articles,        (Tempo, key,
                          descriptions)            energy, texture)
        |                      |                       |
        v                      v                       v
        \______________________|______________________/
                               |
                               v
                  Combined into a single
                  "taste-space" position
                         for a song
```

Three completely different inputs:

1. One is **social behavior** (Collaborative Filtering).
2. One is **language** (Cultural NLP).
3. One is **signal processing** (Deep Audio CNNs).

None of them understands music the way humans do.

Yet together they often land surprisingly close to human intuition.

---

## And Then It Has to Figure Out Where You Are

None of those systems matter until Spotify can position **you** inside the same taste space.

Every interaction becomes a signal:

- Streams
- Replays
- Saves
- Playlist additions
- Skips

Those actions gradually create a profile representing your listening behavior.

Songs get coordinates.

You get coordinates.

And recommendation becomes a distance problem in high-dimensional vector space.

```text
your position: [0.71, -0.22, 0.38, ...]

candidate songs near you:

Song X   distance: 0.04  -> strong candidate
Song Y   distance: 0.09  -> strong candidate
Song Z   distance: 0.31  -> weaker candidate
```

The basic pipeline becomes surprisingly structured:

1. Find songs near your position that you haven’t already heard.
2. Remove songs that are *too* similar to things you already know (to maintain discovery vs. familiarity balance).
3. Rank and filter what’s left down to 30 tracks.
4. Build the playlist.

---

## Why Monday Morning, Specifically?

The timing isn’t arbitrary.

Once I understood the scale of what’s actually being calculated, it made complete sense why this can’t happen live every time you open the app.

Recomputing recommendation positions for hundreds of millions of users against a catalog containing tens of millions of songs is an enormous computational task.

The kind of work that’s far better suited to large scheduled batch jobs running across distributed infrastructure than real-time request processing.

Building Discover Weekly once per week turns a difficult real-time engineering problem into a manageable batch-processing problem:

- Run it overnight across distributed worker clusters.
- Generate the pre-computed recommendations.
- Ship them before people wake up on Monday.

That’s a very reasonable tradeoff between recommendation freshness and computational cost.

Monday isn’t special because of your listening habits; it’s special because the batch job has to finish sometime.

---

## The Part That Actually Changed How I Listen to It Now

Here’s what I keep coming back to:

Nothing in this entire chain has ever, at any point, “understood” a song emotionally the way a friend recommending music might.

There’s no system anywhere in this pipeline that knows a track is:

- sad
- nostalgic
- comforting
- perfect for 2am

at least not in the way a human understands those ideas.

It’s three enormous, mathematically blind systems:

1. One looking at crowd behavior.
2. One looking at written language.
3. One looking at sound waves.

And somehow, despite none of them truly understanding music, they agree often enough that the final result feels startlingly personal.

I used to think of that Monday playlist as the app “getting me.” Now I think of it as something stranger, and honestly, more impressive: millions of strangers building playlists, thousands of writers discussing artists online, and raw audio waveforms converted into vectors — all quietly combining overnight into thirty songs waiting for you before you’ve even had coffee.

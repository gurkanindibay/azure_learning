---
type: System Design
title: "Dockerfile Optimization — Key Takeaways"
description: "FROM node:20-slim"
timestamp: 2026-06-14T00:00:00Z
---

# 26. Dockerfile Optimization — Key Takeaways

> **Parent**: [System Design Interview Reference](../index.md)
> **Source**: [Junior Devs Write Dockerfiles. Senior Devs Write These 5 Layers That Cut Build Time by 70%](../../articles/medium/docker-file-art.md) — The Atomic Architect, May 2026
> **Purpose**: Extract practical Dockerfile optimization patterns — treating the Dockerfile as a cache strategy, ordering layers by change frequency, shrinking production images, and persisting dependency caches across builds.
> **Also see**: [Pragmatic System Design](system-design-interview/pragmatic-takeaways.md) (`prag-01`–`prag-08`), [Resilience Patterns](resilience/resilience-patterns.md)

---

## Contents

| ID | Problem | Key Concept |
|:---|:---|:---|
| [`docker-01`](#docker-01-order-by-change-frequency) | Source change reinstalls all dependencies | Put the manifest first, dependencies second, source last |
| [`docker-02`](#docker-02-use-a-real-dockerignore) | Huge build context sent to the daemon | Exclude `.git`, `node_modules`, build artifacts, and local secrets |
| [`docker-03`](#docker-03-multi-stage-builds) | Production image ships compilers and dev tools | Build in one stage, copy only runtime artifacts to a slim final stage |
| [`docker-04`](#docker-04-cache-mounts) | One dependency bump redownloads everything | Use BuildKit cache mounts for package-manager caches |
| [`docker-05`](#docker-05-pin-base-images-and-merge-run) | Moving tags and bloated bases kill cache and size | Pin by digest, use slim variants, and clean up in the same `RUN` |
| [`docker-06`](#docker-06-the-70-is-a-lie-measure-first) | Reordered layers but no speedup | Profile first; cache must persist somewhere to help |
| [`docker-07`](#docker-07-the-mental-model) | Dockerfile seen as setup script | Treat it as a cache strategy that happens to produce an image |
| [`docker-08`](#docker-08-the-monday-action-plan) | Don't know where to start | Pick the slowest build, profile, then apply layers 1–4 |

---

## docker-01: Order by Change Frequency

> **Source**: [Article §"Layer 1: Order by Change Frequency, Not by What Feels Natural"](../../articles/medium/docker-file-art.md#layer-1-order-by-change-frequency-not-by-what-feels-natural)

| | |
|:---|:---|
| **Problem** | `COPY . .` followed by `RUN npm install` invalidates the dependency layer on every source-code edit, reinstalling hundreds of packages for a one-line change. |
| **Root cause** | Layers are ordered by what feels logical to a human, not by how often inputs change. |

### The Rule

| Order | What to put | Why |
|:---|:---|:---|
| 1 | Base image, `WORKDIR`, system packages | Changes rarely |
| 2 | Manifest files (`package.json`, `go.mod`, `pom.xml`) | Changes when dependencies change |
| 3 | Dependency install (`npm ci`, `go mod download`, `mvn dependency:go-offline`) | Expensive; must stay cached |
| 4 | Source code | Changes constantly; keep it last |

### ❌ Wrong — everything copied before install

```dockerfile
FROM node:20-slim
WORKDIR /app
COPY . .
RUN npm install
CMD ["node", "server.js"]
```

### ✅ Correct — manifest first, source last

```dockerfile
FROM node:20-slim
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
CMD ["node", "server.js"]
```

> **Key insight**: If editing one source file reinstalls your dependencies, your layers are ordered wrong.

---

## docker-02: Use a Real `.dockerignore`

> **Source**: [Article §"Layer 2: A .dockerignore That Actually Does Its Job"](../../articles/medium/docker-file-art.md#layer-2-a-dockerignore-that-actually-does-its-job)

| | |
|:---|:---|
| **Problem** | Build context ships `.git/`, `node_modules/`, build artifacts, logs, and local `.env` files — slowing context upload and silently breaking the `COPY . .` cache. |
| **Root cause** | No `.dockerignore`, or one that doesn't exclude the files that change locally but don't belong in the image. |

### Example `.dockerignore`

```text
.git
node_modules
dist
build
coverage
*.log
.env
.env.*
Dockerfile
.dockerignore
README.md
**/*.test.js
```

### Why It Matters

| Win | Explanation |
|:---|:---|
| Faster context upload | Less data sent to the Docker daemon |
| Cache integrity | Local `node_modules` changes don't invalidate `COPY . .` |
| Smaller image | Accidental files never enter the image |

> **Key insight**: No `.dockerignore` is a bug, not an omission. If you wouldn't `git add` it, Docker shouldn't see it.

---

## docker-03: Multi-Stage Builds

> **Source**: [Article §"Layer 3: Multi-Stage Builds — Throw Away the Toolchain"](../../articles/medium/docker-file-art.md#layer-3-multi-stage-builds--throw-away-the-toolchain)

| | |
|:---|:---|
| **Problem** | Production image contains compilers, dev dependencies, and intermediate build files — shipping 1.2GB to run a 30MB binary. |
| **Root cause** | Single-stage builds mix the build environment with the runtime environment. |

### ❌ Wrong — one stage ships everything

```dockerfile
FROM node:20
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build
CMD ["node", "dist/server.js"]
```

### ✅ Correct — separate build and runtime stages

```dockerfile
# ---- build stage ----
FROM node:20 AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build && npm prune --production

# ---- runtime stage ----
FROM node:20-slim
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
CMD ["node", "dist/server.js"]
```

### Go Distroless Example

```dockerfile
FROM golang:1.22 AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /app/server .

FROM gcr.io/distroless/static-debian12
COPY --from=builder /app/server /server
ENTRYPOINT ["/server"]
```

> **Key insight**: Your production image should contain what runs, not what built it.

---

## docker-04: Cache Mounts

> **Source**: [Article §"Layer 4: Cache Mounts — Persist Caches the Layer Cache Can’t"](../../articles/medium/docker-file-art.md#layer-4-cache-mounts--persist-caches-the-layer-cache-cant)

| | |
|:---|:---|
| **Problem** | Bumping one dependency invalidates the entire `npm ci` layer, redownloading every package. |
| **Root cause** | The layer cache is the only caching mechanism considered; BuildKit cache mounts are ignored. |

### ✅ Correct — persistent package cache

```dockerfile
# syntax=docker/dockerfile:1
FROM node:20-slim
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci
```

### Ecosystem-Specific Mount Targets

| Ecosystem | Cache mount target |
|:---|:---|
| **Go** | `/go/pkg/mod`, `/root/.cache/go-build` |
| **Maven** | `/root/.m2` |
| **pip** | `/root/.cache/pip` |
| **npm** | `/root/.npm` |

> **Key insight**: The layer cache protects you from re-running steps. Cache mounts protect you from re-fetching data. You want both.

### CI Caveat

Cache mounts live on the build machine. In CI they only help if the runner persists BuildKit cache or you explicitly export/import with `--cache-to` / `--cache-from`.

---

## docker-05: Pin Base Images and Merge RUN

> **Source**: [Article §"Layer 5: Pin the Base Image and Stop Splitting RUN"](../../articles/medium/docker-file-art.md#layer-5-pin-the-base-image-and-stop-splitting-run)

| | |
|:---|:---|
| **Problem** | `FROM node:20` silently pulls a new image next month, invalidating cache; split `RUN` instructions leave deleted files baked into earlier layers. |
| **Root cause** | Moving tags and misunderstanding that layers are immutable. |

### Pin by Digest

```dockerfile
# ❌ Wrong — moving tag, bloated base
FROM node:20

# ✅ Correct — slim variant, pinned by digest
FROM node:20.11.1-slim@sha256:1c1...
```

### Merge RUN Instructions

```dockerfile
# ❌ Wrong — cleanup is too late
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

# ✅ Correct — create and clean in one layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*
```

> **Key insight**: Pin what you depend on, slim what you ship, and clean up in the same layer you made the mess.

---

## docker-06: The 70% Is a Lie — Measure First

> **Source**: [Article §"The 70% Is a Lie (When You Skip This Part)"](../../articles/medium/docker-file-art.md#the-70-is-a-lie-when-you-skip-this-part)

| | |
|:---|:---|
| **Problem** | Teams reorder layers but see no improvement, then conclude "caching doesn't work." |
| **Root cause** | Cache must persist somewhere to be useful. Stateless CI runners throw it away every build. |

### When Layer Ordering Fails to Help

| Scenario | Why it doesn't help | What to do instead |
|:---|:---|:---|
| Stateless CI runner | No warm layer cache to hit | Export cache with `--cache-to` / `--cache-from`, or persist BuildKit volume |
| Heavy compile dominates | Layer ordering doesn't speed up the compiler | Cache build-cache directories; parallelize stages |
| Slow deploy, not slow build | Bottleneck is image pull/push size | Multi-stage + slim base (Layers 3 and 5) |

> **Key insight**: Profile first. `docker build` with BuildKit prints timing for every step. Optimize the line that's actually costing you.

---

## docker-07: The Mental Model

> **Source**: [Article §"The Mental Model That Changes Everything"](../../articles/medium/docker-file-art.md#the-mental-model-that-changes-everything)

| Junior View | Senior View |
|:---|:---|
| A `Dockerfile` is a setup script | A `Dockerfile` is a cache strategy that happens to produce an image |

### The Question Behind Every Line

> How often does this change, and what does it cost to redo when it does?

### The Four Principles

| Principle | Practice |
|:---|:---|
| Stable things go up top | Order layers by change frequency |
| Don't ship what you don't need | `.dockerignore`, multi-stage builds |
| Persist what's expensive to fetch | Cache mounts |
| Pin what must not drift | Digest-pinned slim base images |

> **Key insight**: Senior engineers refuse to let the build do the same work twice. Once you see a `Dockerfile` that way, you'll never write `COPY . .` on line three again.

---

## docker-08: The Monday Action Plan

> **Source**: [Article §"Your Action Plan for Monday"](../../articles/medium/docker-file-art.md#your-action-plan-for-monday)

Don't refactor every `Dockerfile`. Pick the slowest one and apply these in order:

1. **Profile** — run the build twice, read BuildKit step timings, find the single slowest step.
2. **Layer 1** — move manifest copy and dependency install above `COPY . .`.
3. **Layer 2** — add a real `.dockerignore` with `node_modules` and `.git`.
4. **Layer 3** — split into a build stage and a slim runtime stage.
5. **Layer 4** — add cache mounts to dependency install, and confirm CI persists them.

> **Key insight**: Each change makes the build more honest about what work actually needs doing. That honesty — not cleverness — is the real line between a junior and a senior `Dockerfile`.

---

## Quick Reference Card

| ID | Decision | Answer |
|:---|:---|:---|
| `docker-01` | What order should layers be in? | Manifest → dependencies → source |
| `docker-02` | What belongs in `.dockerignore`? | Anything you wouldn't `git add` |
| `docker-03` | What ships to production? | Only runtime artifacts, not the build toolchain |
| `docker-04` | How do I survive dependency bumps? | BuildKit cache mounts |
| `docker-05` | How do I keep builds reproducible? | Pin base images by digest; merge related `RUN` commands |
| `docker-06` | Why didn't my optimization work? | Measure first; cache must persist in CI to help |
| `docker-07` | How should I think about a Dockerfile? | As a cache strategy, not a setup script |
| `docker-08` | Where do I start on Monday? | Profile the slowest build, then apply layers 1–4 |

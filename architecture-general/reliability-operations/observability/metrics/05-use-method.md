# The USE Method

## Table of Contents

- [Overview](#overview)
- [What is the USE Method?](#what-is-the-use-method)
- [The Three Metrics](#the-three-metrics)
  - [Utilization](#utilization)
  - [Saturation](#saturation)
  - [Errors](#errors)
- [USE Method Checklist](#use-method-checklist)
- [Implementation by Resource Type](#implementation-by-resource-type)
- [Dashboard Design](#dashboard-design)
- [Alerting Strategies](#alerting-strategies)
- [USE vs. RED vs. Golden Signals](#use-vs-red-vs-golden-signals)
- [Common Pitfalls](#common-pitfalls)
- [Tools and Examples](#tools-and-examples)

---

## Overview

The **USE Method** is a methodology for analyzing the performance of any system by examining **Utilization**, **Saturation**, and **Errors** of every resource. It was developed by **Brendan Gregg** (Netflix) and is particularly effective for analyzing system resources and infrastructure components.

```
┌─────────────────────────────────────────────────────────────────┐
│                       THE USE METHOD                             │
│                                                                  │
│           For every resource, check:                             │
│                                                                  │
│    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│    │ UTILIZATION  │  │  SATURATION  │  │    ERRORS    │        │
│    │              │  │              │  │              │        │
│    │  How busy    │  │  How much    │  │  How many    │        │
│    │  is it?      │  │  is queued?  │  │  failures?   │        │
│    │              │  │              │  │              │        │
│    │   (0-100%)   │  │  (queue/wait)│  │   (count)    │        │
│    └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                  │
│                  Applied to EVERY resource:                      │
│         CPU • Memory • Disk • Network • GPU • etc.              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

> "For every resource, check utilization, saturation, and errors."
> — Brendan Gregg

---

## What is the USE Method?

### Origin

Created by **Brendan Gregg**, senior performance architect at Netflix, the USE Method provides a systematic approach to identifying resource bottlenecks. It's based on queuing theory and years of performance engineering experience.

### Philosophy

The USE Method focuses on **resources** rather than requests:
- **Resources**: Physical or virtual system components (CPU, memory, disk, network)
- **Goal**: Identify bottlenecks and performance constraints quickly
- **Approach**: Systematic checklist applied to each resource type

### When to Use the USE Method

| Scenario | Applicability |
|----------|---------------|
| Performance troubleshooting | ✅ Excellent |
| Capacity planning | ✅ Excellent |
| Infrastructure monitoring | ✅ Excellent |
| Resource bottleneck identification | ✅ Excellent |
| Request-driven service monitoring | ⚠️ Use RED instead |
| User experience monitoring | ⚠️ Use Golden Signals |

---

## The Three Metrics

### Utilization

**Definition**: The percentage of time a resource is busy servicing work, or the percentage of resource capacity being used.

```
┌─────────────────────────────────────────────────────────────────┐
│                        UTILIZATION                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Definition:    Time busy / Total time × 100                     │
│                 OR                                               │
│                 Capacity used / Total capacity × 100             │
│                                                                  │
│  Range:         0% to 100%                                       │
│                                                                  │
│  Types:                                                          │
│  ══════                                                          │
│  • TIME-BASED: % of time resource is busy                        │
│    Example: CPU at 75% means busy 75% of measured interval       │
│                                                                  │
│  • CAPACITY-BASED: % of capacity in use                          │
│    Example: 12GB of 16GB memory = 75% utilization               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Utilization by Resource Type

| Resource | Utilization Metric | Calculation |
|----------|-------------------|-------------|
| CPU | % time busy | `(user + system + nice + irq) / total` |
| Memory | % capacity used | `used / total` |
| Disk I/O | % time busy | `await / service_time` or `%util` |
| Network | % bandwidth used | `bytes_transferred / max_bandwidth` |
| File descriptors | % in use | `open_fds / max_fds` |
| Connection pool | % connections used | `active / max_connections` |

#### Utilization Visualization

```
                    CPU Utilization Over Time
════════════════════════════════════════════════════════════════

  100% ─┤─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ DANGER ZONE
        │                                 ╭───────────
   90% ─┤                                ╱            ⚠️ High
        │                               ╱
   80% ─┤─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─╱─ ─ WARNING LINE
        │                            ╱
   70% ─┤                     ╭────╯
        │                    ╱
   60% ─┤               ╭───╯
        │              ╱
   50% ─┤─────────────╯
        │
   40% ─┤
        └─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬──► Time
            00:00 01:00 02:00 03:00 04:00 05:00 06:00 07:00

  Key Thresholds:
  • < 70%: Healthy headroom
  • 70-85%: Warning - plan for scaling
  • > 85%: Critical - performance degradation likely
```

#### Important: The Utilization Paradox

```
⚠️  High utilization doesn't always mean good!

At high utilization, queuing increases exponentially:

Utilization    Average Queue Length    Response Time Impact
────────────────────────────────────────────────────────────
    50%              1.0                   Baseline
    70%              2.3                   2x slower
    80%              4.0                   4x slower
    90%              9.0                   9x slower
    95%             19.0                  19x slower
    99%             99.0                  99x slower

This is why 70-80% utilization is often the practical limit!
```

---

### Saturation

**Definition**: The degree to which a resource has extra work queued that it can't service. Often represented by queue length or wait time.

```
┌─────────────────────────────────────────────────────────────────┐
│                        SATURATION                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Definition:    Amount of work waiting/queued                    │
│                                                                  │
│  Indicators:                                                     │
│  ═══════════                                                     │
│  • Queue length (number of waiting requests)                     │
│  • Wait time (time spent waiting for resource)                   │
│  • Overflows (work rejected due to full queues)                 │
│                                                                  │
│  Key insight:                                                    │
│  ════════════                                                    │
│  Saturation shows what utilization CANNOT:                       │
│  • A resource at 100% utilization with no queue = OK             │
│  • A resource at 100% utilization with long queue = PROBLEM      │
│                                                                  │
│  Non-zero saturation = resource bottleneck                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Saturation by Resource Type

| Resource | Saturation Metric | How to Measure |
|----------|-------------------|----------------|
| CPU | Run queue length | `vmstat r column`, load average |
| Memory | Swap activity | Pages swapped in/out, OOM events |
| Disk | I/O queue depth | `avgqu-sz` from iostat |
| Network | Dropped packets | Interface drops, TCP retransmits |
| Thread pool | Queued tasks | Pending work items |
| Connection pool | Waiting connections | Connection wait time |

#### Understanding Queue Behavior

```
                    Saturation: Queue Length Over Time
════════════════════════════════════════════════════════════════

Queue
Length
   │
  50─┤                                          ╭────── OVERFLOW
    │                                         ╱        (work rejected)
  40─┤                                       ╱
    │                                      ╱
  30─┤                                    ╱
    │                               ╭───╯
  20─┤                         ╭───╯
    │                    ╭────╯
  10─┤               ╭──╯
    │          ╭────╯
   0─┤─────────╯
    └───────┬───────┬───────┬───────┬───────┬───────┬──► Time

    │◄──────────────────────────────────────────────►│
    │  Utilization gradually increasing to 100%      │
    │                                                │
    │  Notice: Queue grows EXPONENTIALLY as         │
    │  utilization approaches 100%                   │

    Key: Even small increases in utilization near 100%
         cause massive queue growth!
```

#### CPU Saturation Example: Load Average

```
Load Average Interpretation:

┌─────────────────────────────────────────────────────────────────┐
│  System: 4-core CPU                                              │
│  Load Average: 1.00, 2.00, 4.00                                 │
│                │      │      │                                   │
│                │      │      └── 15-min average (long trend)    │
│                │      └── 5-min average (medium trend)          │
│                └── 1-min average (current state)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Interpretation for 4-core system:                              │
│  ═══════════════════════════════════                            │
│  Load 1.0  = 25% utilized, no saturation (1/4 cores busy)       │
│  Load 4.0  = 100% utilized, no saturation (all cores busy)      │
│  Load 8.0  = 100% utilized + 4 waiting (saturated!)             │
│  Load 16.0 = 100% utilized + 12 waiting (severely saturated!)   │
│                                                                  │
│  Rule of thumb: Load > number_of_cores = saturation             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### Errors

**Definition**: The count of error events for a resource, including both hardware and software errors.

```
┌─────────────────────────────────────────────────────────────────┐
│                          ERRORS                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Definition:    Count of error events                            │
│                                                                  │
│  Types:                                                          │
│  ══════                                                          │
│  • Hardware errors (ECC, disk failures, NIC errors)              │
│  • Software errors (timeouts, rejected connections)              │
│  • Resource exhaustion (OOM kills, file descriptor limits)       │
│  • Operational errors (misconfigurations)                        │
│                                                                  │
│  Why errors matter:                                              │
│  ═══════════════════                                             │
│  • May indicate failing hardware                                 │
│  • Can cause performance degradation (retries)                   │
│  • Often precede complete failures                               │
│  • Some "normal" errors mask real problems                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Errors by Resource Type

| Resource | Error Types | How to Check |
|----------|-------------|--------------|
| CPU | Machine check exceptions | `dmesg`, MCE logs |
| Memory | ECC errors, OOM kills | `dmesg`, `/var/log/messages` |
| Disk | Read/write errors, bad sectors | `smartctl`, `dmesg` |
| Network | CRC errors, drops, overruns | `ifconfig`, `netstat -i` |
| File system | I/O errors, corruption | `dmesg`, application logs |

#### Error Investigation Priority

```
                    Error Severity Matrix
════════════════════════════════════════════════════════════════

         │  Frequency
         │  Low              High
─────────┼──────────────────────────────────────
         │
Severity │  MONITOR          URGENT
High     │  ┌───────────┐    ┌───────────┐
         │  │ Hardware  │    │ Cascading │
         │  │ warnings  │    │ failures  │
         │  └───────────┘    └───────────┘
         │
         │  LOG              INVESTIGATE
Low      │  ┌───────────┐    ┌───────────┐
         │  │ Transient │    │ Pattern   │
         │  │ issues    │    │ indicates │
         │  └───────────┘    │ problem   │
         │                   └───────────┘
```

---

## USE Method Checklist

### Systematic Resource Analysis

Apply the USE Method by going through each resource type:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        USE METHOD CHECKLIST                                  │
├──────────────┬─────────────────────┬──────────────────┬─────────────────────┤
│   Resource   │    Utilization      │   Saturation     │      Errors         │
├──────────────┼─────────────────────┼──────────────────┼─────────────────────┤
│              │ Per-CPU: mpstat     │ Run queue:       │ Machine check       │
│     CPU      │ Overall: top, htop  │ vmstat r,        │ exceptions: dmesg   │
│              │ Metric: % busy      │ load average     │                     │
├──────────────┼─────────────────────┼──────────────────┼─────────────────────┤
│              │ free -m             │ Swap usage:      │ OOM kills:          │
│    Memory    │ /proc/meminfo       │ vmstat si/so,    │ dmesg,              │
│              │ Metric: % used      │ page scan rate   │ /var/log/messages   │
├──────────────┼─────────────────────┼──────────────────┼─────────────────────┤
│              │ iostat -x           │ Queue length:    │ Device errors:      │
│   Disk I/O   │ Metric: %util       │ iostat avgqu-sz  │ smartctl,           │
│              │                     │ await time       │ /var/log/messages   │
├──────────────┼─────────────────────┼──────────────────┼─────────────────────┤
│              │ sar -n DEV          │ Drops:           │ ifconfig errors:    │
│   Network    │ Metric: % bandwidth │ netstat -s,      │ CRC, frame,         │
│              │                     │ ss overflow      │ carrier errors      │
├──────────────┼─────────────────────┼──────────────────┼─────────────────────┤
│   Storage    │ df -h               │ N/A              │ fsck errors,        │
│   Capacity   │ Metric: % full      │ (capacity only)  │ quota exceeded      │
├──────────────┼─────────────────────┼──────────────────┼─────────────────────┤
│    File      │ /proc/sys/fs/       │ Waiting for FDs: │ "Too many open      │
│ Descriptors  │ file-nr             │ lsof count       │ files" errors       │
├──────────────┼─────────────────────┼──────────────────┼─────────────────────┤
│  Connection  │ active / max        │ Wait queue,      │ Connection refused, │
│    Pools     │ connections         │ timeout count    │ timeout errors      │
└──────────────┴─────────────────────┴──────────────────┴─────────────────────┘
```

### Linux Commands Quick Reference

```bash
# CPU
$ mpstat -P ALL 1          # Per-CPU utilization
$ uptime                   # Load average (saturation indicator)
$ vmstat 1                 # r column = run queue

# Memory
$ free -m                  # Memory utilization
$ vmstat 1                 # si/so = swap in/out (saturation)
$ dmesg | grep -i oom      # OOM errors

# Disk
$ iostat -xz 1             # Disk utilization and saturation
$ smartctl -a /dev/sda     # Disk errors

# Network
$ sar -n DEV 1             # Network utilization
$ netstat -s | grep -i drop # Network saturation/errors
$ ifconfig                 # Interface errors

# File Descriptors
$ cat /proc/sys/fs/file-nr # System-wide FD usage
$ lsof | wc -l             # Open files count
```

---

## Implementation by Resource Type

### CPU Analysis

```python
# Prometheus metrics for CPU USE

# Utilization: CPU usage percentage
cpu_utilization = (
    1 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) by (instance)
) * 100

# Saturation: Load average vs CPU count
cpu_saturation = (
    node_load1 / count(node_cpu_seconds_total{mode="idle"}) by (instance)
)
# Saturation > 1 means more work than CPUs available

# Errors: Check kernel logs for MCE
# (Usually requires log parsing rather than metrics)
```

### Memory Analysis

```python
# Prometheus metrics for Memory USE

# Utilization: Memory usage percentage
memory_utilization = (
    1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)
) * 100

# Saturation: Swap activity
memory_saturation_swap_in = rate(node_vmstat_pswpin[5m])
memory_saturation_swap_out = rate(node_vmstat_pswpout[5m])
# Any swap activity indicates memory pressure

# Saturation: Page scan rate
memory_saturation_scan = rate(node_vmstat_pgsteal_kswapd[5m])

# Errors: OOM kills
# Usually tracked via log aggregation or separate OOM exporter
```

### Disk I/O Analysis

```python
# Prometheus metrics for Disk USE

# Utilization: % time disk is busy
disk_utilization = rate(node_disk_io_time_seconds_total[5m]) * 100

# Saturation: Average queue size
disk_saturation = rate(node_disk_io_time_weighted_seconds_total[5m])
# Or: avgqu-sz from iostat

# Saturation: Await time (includes queue time)
disk_await = (
    rate(node_disk_read_time_seconds_total[5m]) + 
    rate(node_disk_write_time_seconds_total[5m])
) / (
    rate(node_disk_reads_completed_total[5m]) + 
    rate(node_disk_writes_completed_total[5m])
)

# Errors: I/O errors (if available from SMART)
# Usually requires smartctl or vendor-specific exporters
```

### Network Analysis

```python
# Prometheus metrics for Network USE

# Utilization: Bandwidth usage (% of max)
# Requires knowing interface speed
network_utilization_receive = (
    rate(node_network_receive_bytes_total[5m]) * 8 
    / node_network_speed_bytes * 100
)

network_utilization_transmit = (
    rate(node_network_transmit_bytes_total[5m]) * 8 
    / node_network_speed_bytes * 100
)

# Saturation: Dropped packets
network_saturation_drops = (
    rate(node_network_receive_drop_total[5m]) +
    rate(node_network_transmit_drop_total[5m])
)

# Errors: Interface errors
network_errors = (
    rate(node_network_receive_errs_total[5m]) +
    rate(node_network_transmit_errs_total[5m])
)
```

---

## Dashboard Design

### USE Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  HOST: prod-web-01    OS: Linux 5.4    UPTIME: 45 days    [Last 6h ▼]      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ═══════════════════════════════ CPU ═══════════════════════════════════   │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐    │
│  │ UTILIZATION        │  │ SATURATION         │  │ ERRORS             │    │
│  │   72.3%            │  │   Load: 3.2        │  │   0                │    │
│  │   [████████░░]     │  │   (4 cores)        │  │   ✅ None          │    │
│  │   ⚠️ Warning       │  │   ✅ OK (< 4)      │  │                    │    │
│  └────────────────────┘  └────────────────────┘  └────────────────────┘    │
│                                                                              │
│  ═══════════════════════════ MEMORY ════════════════════════════════════   │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐    │
│  │ UTILIZATION        │  │ SATURATION         │  │ ERRORS             │    │
│  │   85.7%            │  │   Swap: 0 B/s      │  │   0 OOM kills      │    │
│  │   [█████████░]     │  │   ✅ No swapping   │  │   ✅ None          │    │
│  │   ⚠️ High          │  │                    │  │                    │    │
│  └────────────────────┘  └────────────────────┘  └────────────────────┘    │
│                                                                              │
│  ════════════════════════════ DISK ═════════════════════════════════════   │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐    │
│  │ UTILIZATION        │  │ SATURATION         │  │ ERRORS             │    │
│  │   45.2%            │  │   Queue: 0.8       │  │   0                │    │
│  │   [████░░░░░░]     │  │   Await: 2.3ms     │  │   ✅ None          │    │
│  │   ✅ Healthy       │  │   ✅ OK            │  │                    │    │
│  └────────────────────┘  └────────────────────┘  └────────────────────┘    │
│                                                                              │
│  ═══════════════════════════ NETWORK ═══════════════════════════════════   │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐    │
│  │ UTILIZATION        │  │ SATURATION         │  │ ERRORS             │    │
│  │   23.1% (eth0)     │  │   Drops: 0/s       │  │   0                │    │
│  │   [██░░░░░░░░]     │  │   ✅ No drops      │  │   ✅ None          │    │
│  │   ✅ Healthy       │  │                    │  │                    │    │
│  └────────────────────┘  └────────────────────┘  └────────────────────┘    │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                    CPU UTILIZATION OVER TIME                           │ │
│  │  100%─┤─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─        │ │
│  │       │                              ╭──────────────                   │ │
│  │   80%─┤──────────────────────────────╯─────────────────  Warning      │ │
│  │       │                    ╭────────╯                                  │ │
│  │   60%─┤────────────────────╯───────────────────────────────────       │ │
│  │       │                                                                │ │
│  │   40%─┤                                                                │ │
│  │       └───────┬───────┬───────┬───────┬───────┬───────┬───────┬──    │ │
│  │             -6h     -5h     -4h     -3h     -2h     -1h      Now       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Alerting Strategies

### USE Alert Rules (Prometheus)

```yaml
groups:
  - name: use_method_alerts
    rules:
      # CPU UTILIZATION
      - alert: HighCPUUtilization
        expr: |
          100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 85
        for: 10m
        labels:
          severity: warning
          resource: cpu
          metric: utilization
        annotations:
          summary: "High CPU utilization on {{ $labels.instance }}"
          
      # CPU SATURATION
      - alert: CPUSaturation
        expr: |
          node_load1 > on(instance) count by(instance) (node_cpu_seconds_total{mode="idle"}) * 1.5
        for: 5m
        labels:
          severity: warning
          resource: cpu
          metric: saturation
        annotations:
          summary: "CPU saturated on {{ $labels.instance }} (load > 1.5x cores)"

      # MEMORY UTILIZATION
      - alert: HighMemoryUtilization
        expr: |
          (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100 > 90
        for: 5m
        labels:
          severity: warning
          resource: memory
          metric: utilization
        annotations:
          summary: "High memory utilization on {{ $labels.instance }}"
          
      # MEMORY SATURATION (Swapping)
      - alert: MemorySwapping
        expr: |
          rate(node_vmstat_pswpout[5m]) > 0
        for: 5m
        labels:
          severity: warning
          resource: memory
          metric: saturation
        annotations:
          summary: "Memory pressure causing swapping on {{ $labels.instance }}"

      # DISK UTILIZATION
      - alert: HighDiskUtilization
        expr: |
          rate(node_disk_io_time_seconds_total[5m]) * 100 > 90
        for: 10m
        labels:
          severity: warning
          resource: disk
          metric: utilization
        annotations:
          summary: "High disk I/O utilization on {{ $labels.instance }}"
          
      # DISK SATURATION
      - alert: DiskIOSaturation
        expr: |
          rate(node_disk_io_time_weighted_seconds_total[5m]) > 10
        for: 5m
        labels:
          severity: warning
          resource: disk
          metric: saturation
        annotations:
          summary: "Disk I/O queue saturation on {{ $labels.instance }}"

      # NETWORK SATURATION (Drops)
      - alert: NetworkDrops
        expr: |
          rate(node_network_receive_drop_total[5m]) + rate(node_network_transmit_drop_total[5m]) > 0
        for: 5m
        labels:
          severity: warning
          resource: network
          metric: saturation
        annotations:
          summary: "Network packet drops on {{ $labels.instance }}"
          
      # NETWORK ERRORS
      - alert: NetworkErrors
        expr: |
          rate(node_network_receive_errs_total[5m]) + rate(node_network_transmit_errs_total[5m]) > 0
        for: 5m
        labels:
          severity: warning
          resource: network
          metric: errors
        annotations:
          summary: "Network interface errors on {{ $labels.instance }}"
```

### Alert Thresholds Reference

| Resource | Metric | Warning | Critical |
|----------|--------|---------|----------|
| CPU | Utilization | > 70% (10m) | > 90% (5m) |
| CPU | Load Average | > 1.5x cores | > 2x cores |
| Memory | Utilization | > 85% | > 95% |
| Memory | Swap I/O | Any sustained | > 100 MB/s |
| Disk | Utilization | > 80% (10m) | > 95% (5m) |
| Disk | Queue Depth | > 5 | > 20 |
| Network | Utilization | > 70% | > 90% |
| Network | Drops/Errors | Any | > 100/s |

---

## USE vs. RED vs. Golden Signals

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    METHODOLOGY COMPARISON                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  USE METHOD              RED METHOD              GOLDEN SIGNALS              │
│  ══════════              ══════════              ══════════════              │
│  (Resources)             (Services)              (User-centric)              │
│                                                                              │
│  ┌─────────────┐                                                            │
│  │ Utilization │         ┌────────┐              ┌──────────┐               │
│  │             │         │  Rate  │◄────────────►│ Traffic  │               │
│  └─────────────┘         └────────┘              └──────────┘               │
│                                                                              │
│  ┌─────────────┐                                 ┌──────────┐               │
│  │ Saturation  │◄───────────────────────────────►│Saturation│               │
│  │             │                                 └──────────┘               │
│  └─────────────┘                                                            │
│                                                                              │
│  ┌─────────────┐         ┌────────┐              ┌──────────┐               │
│  │   Errors    │◄───────►│ Errors │◄────────────►│  Errors  │               │
│  └─────────────┘         └────────┘              └──────────┘               │
│                                                                              │
│                          ┌────────┐              ┌──────────┐               │
│                          │Duration│◄────────────►│ Latency  │               │
│                          └────────┘              └──────────┘               │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Best for:               Best for:               Best for:                  │
│  • Infrastructure        • Microservices         • End-to-end               │
│  • Resource analysis     • APIs                  • SLO definition           │
│  • Capacity planning     • Request-driven        • User experience          │
│  • Bottleneck finding      workloads               monitoring               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### When to Use Each

| Scenario | Recommended Method |
|----------|-------------------|
| "Why is my server slow?" | USE Method |
| "Why are API requests failing?" | RED Method |
| "What should our SLOs be?" | Golden Signals |
| "Do we need more servers?" | USE Method |
| "Is the service healthy?" | RED or Golden Signals |
| "What's causing the timeout?" | All three together |

---

## Common Pitfalls

### 1. Only Checking Utilization

```
❌ Bad: "CPU is at 50%, we're fine"
   Problem: Misses saturation and errors

✅ Good: Check all three metrics
   CPU: 50% util, 0 queue, 0 errors = Actually fine
   CPU: 50% util, 10 queue, errors = Problem!
```

### 2. Wrong Utilization Definition

```
❌ Bad: Using iostat %util as actual utilization
   Problem: SSDs can handle multiple parallel I/O; 
            100% doesn't mean saturated

✅ Good: Use saturation metrics (queue depth, await) 
   for storage performance
```

### 3. Ignoring Errors

```
❌ Bad: Focus only on utilization and saturation
   Problem: Errors might indicate failing hardware

✅ Good: Always check dmesg, logs for errors
   Even occasional errors can predict failures
```

### 4. Not Correlating Metrics

```
❌ Bad: Looking at each resource in isolation
   Problem: Misses interactions

✅ Good: Correlate metrics
   High disk await + high memory usage = 
   Memory pressure causing disk swapping
```

---

## Tools and Examples

### Command-Line Tools

```bash
# Comprehensive system check
$ vmstat 1 5       # CPU, memory, I/O
$ iostat -xz 1 5   # Disk I/O
$ sar -n DEV 1 5   # Network
$ mpstat -P ALL 1  # Per-CPU

# Quick USE check
$ uptime           # Load (CPU saturation)
$ free -m          # Memory
$ df -h            # Disk space
$ dmesg -T | tail  # Recent errors
```

### Prometheus Recording Rules

```yaml
groups:
  - name: use_method_recording
    rules:
      # CPU
      - record: use:cpu:utilization
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
        
      - record: use:cpu:saturation
        expr: node_load1 / on(instance) count by(instance) (node_cpu_seconds_total{mode="idle"})

      # Memory
      - record: use:memory:utilization
        expr: (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100
        
      - record: use:memory:saturation
        expr: rate(node_vmstat_pswpout[5m]) + rate(node_vmstat_pswpin[5m])

      # Disk
      - record: use:disk:utilization
        expr: rate(node_disk_io_time_seconds_total[5m]) * 100
        
      - record: use:disk:saturation
        expr: rate(node_disk_io_time_weighted_seconds_total[5m])
```

---

## Summary

| Metric | Question | Key Insight |
|--------|----------|-------------|
| **Utilization** | How busy is it? | Capacity usage |
| **Saturation** | How much is waiting? | Bottleneck indicator |
| **Errors** | What's failing? | Reliability issues |

### Key Takeaways

1. **Apply systematically** to every resource type
2. **Saturation is often more important** than utilization
3. **High utilization + high saturation = bottleneck**
4. **Don't ignore errors** - they predict failures
5. **Combine with RED** for complete system visibility

---

## Related Documentation

- [RED Method](04-red-method.md) - Request-focused monitoring
- [Golden Signals](03-golden-signals.md) - User-centric monitoring
- [MTTR/MTTF/MTBF](06-mttr-mttf-mtbf.md) - Reliability metrics

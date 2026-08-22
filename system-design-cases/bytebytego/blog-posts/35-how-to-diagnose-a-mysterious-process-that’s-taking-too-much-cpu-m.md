---
type: System Design Case
title: "How to diagnose a mysterious process that’s taking too much CPU, memory, IO, etc?"
description: "much CPU, memory, IO, etc? The diagram below illustrates helpful tools in a Linux system. - ‘vmstat’ - reports information about processes, memory, paging, block IO, traps, and CPU activity. - ‘ios..."
tags: [system-design]
timestamp: 2026-08-22T00:00:00Z
---

# How to diagnose a mysterious process that’s taking too much CPU, memory, IO, etc?

> **Source**: ByteByteGo — System Design compilation PDF

![How to diagnose a mysterious process that’s taking too much CPU, memory, IO, etc?](images/img-034.jpeg)

much CPU, memory, IO, etc? The diagram below illustrates helpful tools in a Linux system. - ‘vmstat’ - reports information about processes, memory, paging, block IO, traps, and CPU activity. - ‘iostat’ - reports CPU and input/output statistics of the system. - ‘netstat’ - displays statistical data related to IP, TCP, UDP, and ICMP protocols. - ‘lsof’ - lists open files of the current system. - ‘pidstat’ - monitors the utilization of system resources by all or specified processes, including CPU, memory, device IO, task switching, threads, etc.

---
type: Article
title: "The Five Levels: From Spicy Autocomplete to the Dark Factory"
description: "In my last post, I wrote about **technical deflation**. We're seeing the cost of code is dropping so fast that we need to change our tech debt payment plans. The smart teams are deferring payment o..."
timestamp: 2026-06-14T00:00:00Z
---

# The Five Levels: From Spicy Autocomplete to the Dark Factory

> **Author**: Dan Shapiro — Glowforge CEO, Wharton Research Fellow, Robot Turtles creator  
> **Source**: [Dan Shapiro's Blog](https://danshapiro.com)  
> **Date**: January 23, 2026  
> **Topics**: AI-assisted development, software engineering automation, technical deflation

---

## Introduction

In my last post, I wrote about **technical deflation**. We're seeing the cost of code is dropping so fast that we need to change our tech debt payment plans. The smart teams are deferring payment on human hours today to pay them back with cheaper AI hours tomorrow.

But how do you actually cash in on those cheap hours?

If you are just using ChatGPT to write your regex, you aren't really getting the benefits of deflation. You're just typing faster.

I've now seen dozens of companies struggling to put AI to work writing code, and each one has moved through five clear tiers of automation. That felt familiar, and I realized that the federal government had been there first — but for cars.

In 2013, the NHTSA created the five levels of driving automation[^1]. This was helpful, because while the highest level at the time was only level 2[^2], it let everyone have a common language for both where things were, and where things were going.

![NHTSA Five Levels of Driving Automation](images/nhtsa-five-levels-driving-automation.png)

---

## Level 0: Spicy Autocomplete

Level Zero is your parents' Volvo, maybe with an automatic transmission. Whether it's `vi` or Visual Studio, not a character hits the disk without your approval. You might use AI as a search engine on steroids or occasionally hit tab to accept a suggestion, but the code is unmistakably yours. This is manual labor in a deflationary world.

![Level 0 — Manual coding with occasional AI autocomplete suggestions](images/level-0-spicy-autocomplete.png)

---

## Level 1: Lanekeeping & Cruise Control

At Level 1, you've got lanekeeping and cruise control. You're writing the important stuff, but you offload specific, discrete tasks to your AI intern. *"Write a unit test for this."* *"Add a docstring."* You could be using anything from copy-paste ChatGPT to Copilot. You're seeing speedups, but your job is unchanged. You're still moving at the rate you type.

![Level 1 — Offloading discrete tasks to AI like unit tests and docstrings](images/level-1-lanekeeping-cruise-control.png)

---

## Level 2: Autopilot on the Highway

At Level 2, you've got Autopilot on the highway. As a coder, you feel free. You've got a junior buddy to hand off all your boring stuff to. This is where **90% of "AI-native" developers** are living right now. You are pairing with the AI like a colleague. You get into a flow state; you're more productive than you've ever been. You're not using chat, you're getting real mileage out of an AI-native coding tool.

> ⚠️ **But here is the danger**: Level 2, and every level after it, feels like you are done. But you are not done.

![Level 2 — Pairing with AI like a colleague in flow state](images/level-2-autopilot-highway.png)

---

## Level 3: Waymo with a Safety Driver

Level 3 is a Waymo with a safety driver. You're not a senior developer anymore; that's your AI's job. You are… **a manager**. You are the human in the loop. Your coding agent is always running multiple tabs. You spend your days reviewing code. So much code. Your life is diffs. For many people, this feels like things got worse.

And almost everyone tops out here.

![Level 3 — The developer becomes a manager reviewing AI-generated diffs](images/level-3-waymo-safety-driver.png)

---

## Level 4: The Robotaxi

Level 4 is a robotaxi, and while it's driving, you can do something else. You're not a developer. You're not a development manager either. You've now become that which you loathed: **you're a PM**[^3]. You write a spec. You argue with it about the spec. You craft skills (for Claude Code, because most folks at level 4 seem to find their way to Claude Code). You plan schedules. You review plans. Then you leave for 12 hours, and check to see if the tests pass.

> *I'm here.*

![Level 4 — The developer becomes a PM writing specs and reviewing plans](images/level-4-robotaxi-pm.png)

---

## Level 5: The Dark Factory

At level 5, it's not really a car any more. You're not really running anybody else's software any more. And your software process isn't really a software process any more. It's a **black box that turns specs into software**.

Why "Dark"? Maybe you've heard of the **Fanuc Dark Factory** — the robot factory staffed by robots. It's dark, because it's a place where humans are neither needed nor welcome.

I know a handful of people who are doing this. They're small teams, less than five people. And what they're doing is nearly unbelievable — and it will likely be our future.

---

## Summary Table

| Level | Metaphor | Your Role | Key Tool |
|:-----:|----------|-----------|----------|
| 0 | Spicy Autocomplete | Manual coder | Tab-completion |
| 1 | Lanekeeping & Cruise Control | Coder + AI intern | ChatGPT, Copilot |
| 2 | Autopilot on the Highway | AI pair programmer | AI-native coding tools |
| 3 | Waymo with Safety Driver | Code reviewer / Manager | Coding agents |
| 4 | Robotaxi | PM (spec writer) | Claude Code + skills |
| 5 | Dark Factory | Not needed | Black-box software generation |

---

## References

- [The Five Levels: from Spicy Autocomplete to the Dark Factory — Dan Shapiro's Blog](https://danshapiro.com)
- [NHTSA Levels of Driving Automation](https://www.nhtsa.gov/vehicle-safety/automated-vehicles-safety)

---

## Footnotes

[^1]: Actually they made four, which was really five because it was zero-based. Then they realized they had to add a fifth. Which was actually the sixth.
[^2]: The 2014 Mercedes-Benz S-Class Distronic Plus with Steering Assist. Who says AI companies have a monopoly on catchy names?
[^3]: Program manager? Project manager? Product manager? Yes.

---

*Thanks to Jesse Vincent, Justin Massa, Ramon Marc, Tenzin Wangdhen, and Noah Radford (who wrote this incredible piece) for reading drafts of this.*

# Junior Devs Use `Task.Run`. Senior Devs Use These 4 Async Patterns Instead

*Generated as a C#/.NET companion to HabibWahid's original Java/Spring article*

> **Original**: [Junior Devs Use @Async. Senior Devs Use These 4 Concurrency Patterns Instead](https://medium.com/@habibwahid/junior-devs-use-async-senior-devs-use-these-4-concurrency-patterns-instead) by HabibWahid
> **Companion to**: [Java/Spring Version](01-senior-java-concurrency-patterns.md)

---

`Task.Run(() => ...)` on every slow method? That's not performance — that's a thread pool waiting to starve. Here's what senior .NET devs do instead.

I once inherited an ASP.NET application that had `Task.Run` wrapped around 27 different service calls. The team was proud of it. *"Everything is async,"* they said. *"It's super responsive."*

It was responsive — right up until the holiday sale, when the thread pool hit exhaustion, request queuing spiked, and the health check endpoint started timing out. The load balancer marked the server as dead. Cascading failure, 503s everywhere. **No exceptions. No alerts. Just a dead app pool.**

The real problem wasn't the code — it was the mindset. The team had treated `Task.Run` like a performance button. Wrap anything slow and watch your response times drop. What they didn't understand is that **concurrency isn't a feature you sprinkle on. It's a system you design.**

Senior .NET developers don't reach for `Task.Run` first. They ask a harder question: *what is actually happening to this work once it leaves my request thread?*

---

## Why Junior Devs Default to `Task.Run`

It's an easy sell. Method taking too long? Wrap it in `Task.Run`, return immediately, and the endpoint latency drops. The Stack Overflow answer shows it in three lines. The code compiles. Ship it.

The problem is that `Task.Run` **hides complexity rather than solving it**. You've moved work off the request thread — but onto what? Onto the **shared thread pool**, which is also handling incoming ASP.NET requests. Under load, you're not offloading work — you're **competing with yourself**.

Senior devs don't avoid concurrency. They make it **explicit**. Every pattern below answers the question that `Task.Run` doesn't: *what happens when this fails, who manages these threads, and how do I know it actually ran?*

---

## The 4 Patterns Senior .NET Devs Use Instead

### Pattern 1: Don't Use `Task.Run` for I/O — Just `await` It, or Use a Job Library

The most dangerous thing about `Task.Run` isn't the method. It's that most devs use it for **I/O-bound work** when they should just be using `await` directly.

```csharp
// ❌ WRONG — Task.Run wrapping I/O calls steals ASP.NET's own thread pool
[HttpPost("orders")]
public async Task<IActionResult> CreateOrder(OrderRequest request)
{
    var order = await _orderRepository.SaveAsync(request);

    _ = Task.Run(() => _emailService.SendConfirmation(order));
    _ = Task.Run(() => _inventoryService.ReserveItems(order));

    return Ok(order);
}
```

Under load, `Task.Run` steals thread pool threads from ASP.NET itself. For I/O work, this is pure overhead — the thread sits idle waiting for the network anyway.

**What Senior .NET Devs Do Instead:**

```csharp
// ✅ SIMPLE — Use Hangfire. One NuGet package. One line per background job.
// install-package Hangfire

[HttpPost("orders")]
public IActionResult CreateOrder(OrderRequest request)
{
    var order = _orderRepository.Save(request);

    // One line each. Persisted to DB. Automatic retries. Built-in dashboard.
    BackgroundJob.Enqueue(() => _emailService.SendConfirmation(order.Id));
    BackgroundJob.Enqueue(() => _inventoryService.ReserveItems(order.Id));

    return Ok(order);
}
```

```csharp
// Startup.cs or Program.cs — 3 lines of config
builder.Services.AddHangfire(config =>
    config.UseSqlServerStorage(connectionString));
builder.Services.AddHangfireServer();
app.UseHangfireDashboard(); // Web UI at /hangfire
```

| Approach | Complexity | Persists on Crash? | Retries? | Dashboard? |
|----------|-----------|-------------------|----------|------------|
| `Task.Run` scattered everywhere | None | ❌ Jobs lost | ❌ | ❌ |
| `Channel<T>` + `BackgroundService` | High (100+ lines) | ❌ In-memory only | Manual | ❌ |
| **Hangfire** | **One-liner** | ✅ SQL/Redis | ✅ Built-in | ✅ Web UI |

> **The Rule**: `Task.Run` is for CPU-bound work only. If you're wrapping a database call, HTTP call, or file I/O — stop. Use `await` directly for the request path. Use Hangfire or Quartz.NET for background jobs. One package. No boilerplate.

---

### Pattern 2: `Task.WhenAll` for Parallel Work That Must Complete Together

Fire-and-forget is catastrophic when you need results from multiple calls before responding.

```csharp
// ❌ WRONG — Three independent calls, awaited one after another = 650ms
[HttpGet("dashboard/{userId}")]
public async Task<DashboardDTO> GetDashboard(Guid userId)
{
    var profile = await _profileService.GetProfileAsync(userId);      // 200ms
    var orders = await _orderService.GetRecentOrdersAsync(userId);    // 150ms
    var balance = await _billingService.GetBalanceAsync(userId);      // 300ms

    return new DashboardDTO(profile, orders, balance);
}
```

**What Senior .NET Devs Do Instead:**

```csharp
// ✅ CORRECT — Start all three, await all three. 300ms total.
[HttpGet("dashboard/{userId}")]
public async Task<DashboardDTO> GetDashboard(Guid userId)
{
    var profileTask = _profileService.GetProfileAsync(userId);
    var ordersTask = _orderService.GetRecentOrdersAsync(userId);
    var balanceTask = _billingService.GetBalanceAsync(userId);

    await Task.WhenAll(profileTask, ordersTask, balanceTask);

    return new DashboardDTO(
        await profileTask,
        await ordersTask,
        await balanceTask
    );
}
```

| Before | After | Improvement |
|--------|-------|-------------|
| 650ms | 300ms | **54% faster** |

That's it. No custom scheduler. No channels. Just start the tasks before you await them. This is the single highest-impact change most .NET codebases need.

> **The Rule**: Independent I/O calls? Start them all, then `await Task.WhenAll()`. Your users pay for every unnecessary sequential await.

---

### Pattern 3: Fire Side Effects AFTER `SaveChangesAsync`, Not Before

The most common `Task.Run` bug: email fires before the DB commit. Transaction rolls back. **Customer gets a confirmation for an order that doesn't exist.**

```csharp
// ❌ WRONG — Task.Run fires before SaveChangesAsync commits
[HttpPost("orders")]
public async Task<IActionResult> CreateOrder(OrderRequest request)
{
    var order = request.ToOrder();
    _dbContext.Orders.Add(order);

    _ = Task.Run(() => _emailService.SendConfirmationAsync(order)); // BEFORE commit!

    await _dbContext.SaveChangesAsync(); // If this fails, email was already sent
    return Ok(order);
}
```

**What Senior .NET Devs Do Instead:**

```csharp
// ✅ CORRECT — Save first. Fire after. That's the entire fix.
[HttpPost("orders")]
public async Task<IActionResult> CreateOrder(OrderRequest request)
{
    var order = request.ToOrder();
    _dbContext.Orders.Add(order);

    await _dbContext.SaveChangesAsync(); // COMMIT FIRST

    // Now — and ONLY now — fire side effects
    BackgroundJob.Enqueue(() => _emailService.SendConfirmation(order.Id));
    BackgroundJob.Enqueue(() => _inventoryService.ReserveItems(order.Id));

    return Ok(order);
}
```

That's the entire fix. **Commit first. Fire after.** No interceptor. No aggregate root base class. No domain event infrastructure.

```csharp
// ✅ IF you want cleaner separation — use MediatR (3 more lines)
// install-package MediatR
public record OrderCreatedEvent(Guid OrderId) : INotification;

[HttpPost("orders")]
public async Task<IActionResult> CreateOrder(OrderRequest request)
{
    var order = request.ToOrder();
    _dbContext.Orders.Add(order);
    await _dbContext.SaveChangesAsync();

    await _mediator.Publish(new OrderCreatedEvent(order.Id)); // After commit!
    return Ok(order);
}
```

| Complexity | Approach | When |
|:---|:---|:---|
| **Simplest** | `SaveChangesAsync()` → `BackgroundJob.Enqueue()` | Few side effects, one controller |
| **Cleaner** | MediatR `INotification` after save | Multiple handlers per event |
| **DDD** | `SaveChangesInterceptor` + Aggregate Roots | Complex domain model |

> **The Rule**: The fix is one line: **move `SaveChangesAsync` above your fire-and-forget code.** Save first, fire after.

---

### Pattern 4: Wrap Every Background Task in `try/catch` — Log the Failure

When fire-and-forget throws, the exception **vanishes**. No log. No alert. You discover it from a support ticket.

```csharp
// ❌ WRONG — Exception swallowed silently
_ = Task.Run(async () =>
{
    var user = await _userRepository.GetByIdAsync(userId);
    await _searchClient.IndexAsync(user); // Throws → swallowed → index broken
});
```

**What Senior .NET Devs Do Instead:**

```csharp
// ✅ SIMPLEST — One try/catch with logging. Every time.
[HttpPost("users/{userId}/sync")]
public IActionResult SyncUser(Guid userId)
{
    BackgroundJob.Enqueue(() => SyncUserSafeAsync(userId));
    return Accepted();
}

async Task SyncUserSafeAsync(Guid userId)
{
    try
    {
        var user = await _userRepository.GetByIdAsync(userId);
        await _searchClient.IndexAsync(user);
    }
    catch (Exception ex)
    {
        _logger.LogError(ex, "Search sync failed for {UserId}", userId);
    }
}
```

Want retries? Hangfire gives you that with an attribute — no extra code:

```csharp
// ✅ WITH RETRIES — One attribute. Free.
public class SearchIndexJob
{
    [AutomaticRetry(Attempts = 3, DelaysInSeconds = new[] { 10, 30, 60 })]
    public async Task SyncAsync(Guid userId)
    {
        var user = await _userRepository.GetByIdAsync(userId);
        await _searchClient.IndexAsync(user);
    }
}

// One-liner from controller
BackgroundJob.Enqueue<SearchIndexJob>(j => j.SyncAsync(userId));
```

| Approach | Lines of Code | Retries | Visibility |
|----------|:---:|:---:|:---|
| Raw `Task.Run` + silent failure | 2 | ❌ | ❌ |
| `try/catch` + log | 6 | ❌ | Logs |
| **Hangfire + `[AutomaticRetry]`** | **1 attribute** | ✅ | Dashboard + logs |

> **The Rule**: Every background task needs a `try/catch` with a log entry. If you use Hangfire, retries are one attribute away. Never let an async failure go unobserved.

---

## Java/Spring → .NET Pattern Mapping

| # | Pattern | Java/Spring | .NET (Simple) |
|---|---------|------------|---------------|
| 1 | Thread Ownership | `@Async("namedExecutor")` | Hangfire `BackgroundJob.Enqueue()` |
| 2 | Parallel Composition | `CompletableFuture.allOf()` | `Task.WhenAll()` |
| 3 | Post-Commit Dispatch | `@TransactionalEventListener(AFTER_COMMIT)` | `await SaveChangesAsync()` first, then fire |
| 4 | Error Observability | `AsyncUncaughtExceptionHandler` | `try/catch` in the background method |

---

## The Mental Model

| Dimension | Key Question | Simple Answer |
|:---|:---|:---|
| **Ownership** | Who owns this work? | Hangfire (persisted, retryable, visible) — not the thread pool |
| **Lifecycle** | When does it run? | After `SaveChangesAsync()` — never before |

---

## Your Action Plan for Tomorrow

1. **Remove `Task.Run` from I/O wrappers** → Just `await` the method directly
2. **Fix sequential awaits** → `var t = CallAsync(); await Task.WhenAll(t, other);`
3. **Move `SaveChangesAsync` above fire-and-forget** → Commit first, fire after
4. **Install Hangfire** → One package, 3 startup lines, free retries + dashboard

**.NET's `async/await` already gives you the concurrency model. You don't need to build more infrastructure — you just need to use it correctly.**

---

*Companion to [Junior Devs Use @Async. Senior Devs Use These 4 Concurrency Patterns Instead](01-senior-java-concurrency-patterns.md) by HabibWahid.*

> **Taxonomy Reference**: §2.1 Application Architecture Patterns (Concurrency & Threading), §8.2 Delivery & Runtime  
> **Related**: [.NET Multithreading Best Practices](../../../dotNet_multi_threading/12-Best-Practices.md) | [TAP Pattern](../../../dotNet_multi_threading/01-TAP-Pattern.md) | [Hangfire Docs](https://www.hangfire.io/)
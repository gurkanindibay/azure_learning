# .NET Asynchronous and Multithreading Programming Guide

Welcome to the .NET Asynchronous and Multithreading Programming study guide. This collection of documents will help you master concurrent programming in .NET.

## 📚 Documentation Structure

### Asynchronous Programming Patterns
1. **[TAP - Task-based Asynchronous Pattern](./01-TAP-Pattern.md)**
   - Modern async/await approach
   - Cancellation and progress reporting
   - Best practices for TAP

2. **[EAP - Event-based Asynchronous Pattern](./02-EAP-Pattern.md)**
   - Legacy event-based pattern
   - Converting EAP to TAP
   - When you'll encounter EAP

3. **[APM - Asynchronous Programming Model](./03-APM-Pattern.md)**
   - Oldest Begin/End pattern
   - Converting APM to TAP
   - Legacy code integration

### Multithreading Fundamentals
4. **[Multithreading Concepts](./04-Multithreading-Concepts.md)**
   - Thread vs Task
   - ThreadPool
   - Parallel programming basics

### Synchronization Primitives
5. **[Semaphore and SemaphoreSlim](./05-Semaphore.md)**
   - Throttling concurrent operations
   - Rate limiting
   - Resource pool management

6. **[Mutex](./06-Mutex.md)**
   - Cross-process synchronization
   - Single-instance applications
   - Named mutexes

7. **[Monitor and Lock](./07-Monitor-Lock.md)**
   - Critical section protection
   - Thread-safe operations
   - Monitor.TryEnter patterns

8. **[ReaderWriterLockSlim](./08-ReaderWriterLock.md)**
   - Read-heavy scenarios
   - Upgradeable locks
   - Performance optimization

9. **[Events (ManualReset & AutoReset)](./09-Events.md)**
   - Thread signaling
   - Producer-consumer patterns
   - Coordination scenarios

10. **[Barrier](./10-Barrier.md)**
    - Phase synchronization
    - Parallel algorithm coordination
    - Multi-stage processing

11. **[CountdownEvent](./11-CountdownEvent.md)**
    - Waiting for multiple operations
    - Dynamic task tracking
    - Batch processing

### Best Practices
12. **[Best Practices and Guidelines](./12-Best-Practices.md)**
    - Async/await patterns
    - Common pitfalls
    - Performance tips
    - Choosing the right primitive

## 🎯 Quick Reference

| Scenario | Recommended Approach | Document |
|----------|---------------------|----------|
| Async I/O operations | TAP (async/await) | [01-TAP-Pattern.md](./01-TAP-Pattern.md) |
| Protect critical section | `lock` statement | [07-Monitor-Lock.md](./07-Monitor-Lock.md) |
| Limit concurrent access | SemaphoreSlim | [05-Semaphore.md](./05-Semaphore.md) |
| Single app instance | Mutex | [06-Mutex.md](./06-Mutex.md) |
| Many reads, few writes | ReaderWriterLockSlim | [08-ReaderWriterLock.md](./08-ReaderWriterLock.md) |
| Signal between threads | ManualResetEvent | [09-Events.md](./09-Events.md) |
| Coordinate phases | Barrier | [10-Barrier.md](./10-Barrier.md) |
| Wait for multiple tasks | CountdownEvent | [11-CountdownEvent.md](./11-CountdownEvent.md) |

## 🚀 Getting Started

If you're new to async programming in .NET:
1. Start with [TAP Pattern](./01-TAP-Pattern.md)
2. Review [Multithreading Concepts](./04-Multithreading-Concepts.md)
3. Learn about [Monitor and Lock](./07-Monitor-Lock.md)
4. Read [Best Practices](./12-Best-Practices.md)

If you're dealing with legacy code:
1. [APM Pattern](./03-APM-Pattern.md) for Begin/End methods
2. [EAP Pattern](./02-EAP-Pattern.md) for event-based code

## 📖 Additional Resources

- [Microsoft Docs: Asynchronous Programming](https://docs.microsoft.com/en-us/dotnet/csharp/async)
- [Microsoft Docs: Threading](https://docs.microsoft.com/en-us/dotnet/standard/threading/)
- [Task-based Asynchronous Pattern (TAP)](https://docs.microsoft.com/en-us/dotnet/standard/asynchronous-programming-patterns/task-based-asynchronous-pattern-tap)
- [Threading in C# - Joseph Albahari](http://www.albahari.com/threading/)

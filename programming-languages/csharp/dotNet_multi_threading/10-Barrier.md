# Barrier

Synchronizes a group of threads at a specific point, useful for phased algorithms.

## Table of Contents
- [Overview](#overview)
- [Basic Usage](#basic-usage)
- [Post-Phase Action](#post-phase-action)
- [Use Cases](#use-cases)
- [Best Practices](#best-practices)

---

## Overview

A Barrier enables multiple threads to work cooperatively on an algorithm in parallel through multiple phases. Each thread signals when it reaches the barrier and waits until all participants reach it before continuing.

**Key Concepts:**
- **Participants**: Number of threads that must reach the barrier
- **Phase**: A synchronized step in the algorithm
- **SignalAndWait**: Thread signals arrival and waits for others
- **Post-Phase Action**: Optional callback after each phase completes

---

## Basic Usage

### Simple Phase Synchronization

```csharp
public class ParallelProcessor
{
    public void ProcessInPhases(int participantCount)
    {
        using (var barrier = new Barrier(participantCount))
        {
            var tasks = Enumerable.Range(0, participantCount).Select(i => Task.Run(() =>
            {
                for (int phase = 0; phase < 3; phase++)
                {
                    Console.WriteLine($"Task {i}: Phase {phase} starting");
                    Thread.Sleep(Random.Shared.Next(500, 1500));
                    Console.WriteLine($"Task {i}: Phase {phase} complete, waiting at barrier");
                    
                    barrier.SignalAndWait(); // Wait for all participants
                    
                    Console.WriteLine($"Task {i}: All tasks completed phase {phase}");
                }
            })).ToArray();
            
            Task.WaitAll(tasks);
        }
    }
}

// Usage: 4 parallel workers synchronized through 3 phases
var processor = new ParallelProcessor();
processor.ProcessInPhases(participantCount: 4);
```

### With Timeout

```csharp
public class TimedBarrier
{
    public void ProcessWithTimeout(int participantCount)
    {
        using (var barrier = new Barrier(participantCount))
        {
            var tasks = Enumerable.Range(0, participantCount).Select(i => Task.Run(() =>
            {
                try
                {
                    Console.WriteLine($"Task {i} working...");
                    Thread.Sleep(Random.Shared.Next(500, 2000));
                    
                    // Wait with timeout
                    if (barrier.SignalAndWait(TimeSpan.FromSeconds(5)))
                    {
                        Console.WriteLine($"Task {i} passed barrier");
                    }
                    else
                    {
                        Console.WriteLine($"Task {i} timed out at barrier");
                    }
                }
                catch (BarrierPostPhaseException ex)
                {
                    Console.WriteLine($"Task {i}: Post-phase action failed: {ex.Message}");
                }
            })).ToArray();
            
            Task.WaitAll(tasks);
        }
    }
}
```

---

## Post-Phase Action

### Phase Callback

```csharp
public class PhaseReporter
{
    public void ProcessWithReporting(int participantCount)
    {
        var barrier = new Barrier(participantCount, (b) =>
        {
            // This runs after all participants reach the barrier
            Console.WriteLine($"=== Phase {b.CurrentPhaseNumber} completed by all {b.ParticipantCount} participants ===");
        });
        
        using (barrier)
        {
            var tasks = Enumerable.Range(0, participantCount).Select(i => Task.Run(() =>
            {
                for (int phase = 0; phase < 3; phase++)
                {
                    Console.WriteLine($"Task {i}: Working on phase {phase}");
                    Thread.Sleep(Random.Shared.Next(500, 1000));
                    
                    barrier.SignalAndWait();
                }
            })).ToArray();
            
            Task.WaitAll(tasks);
        }
    }
}

// Output shows synchronized phases:
// Task 0: Working on phase 0
// Task 1: Working on phase 0
// Task 2: Working on phase 0
// === Phase 0 completed by all 3 participants ===
// Task 0: Working on phase 1
// ...
```

### Data Aggregation Between Phases

```csharp
public class DataAggregator
{
    public void AggregateResults(int participantCount)
    {
        var results = new List<int>();
        var lockObj = new object();
        
        var barrier = new Barrier(participantCount, (b) =>
        {
            // Aggregate results after each phase
            lock (lockObj)
            {
                var sum = results.Sum();
                var avg = results.Average();
                Console.WriteLine($"Phase {b.CurrentPhaseNumber}: Sum={sum}, Avg={avg:F2}");
                results.Clear();
            }
        });
        
        using (barrier)
        {
            var tasks = Enumerable.Range(0, participantCount).Select(taskId => Task.Run(() =>
            {
                for (int phase = 0; phase < 3; phase++)
                {
                    // Do work
                    int result = Random.Shared.Next(1, 100);
                    
                    lock (lockObj)
                    {
                        results.Add(result);
                    }
                    
                    Console.WriteLine($"Task {taskId}: Phase {phase}, Result={result}");
                    
                    barrier.SignalAndWait(); // Results aggregated here
                }
            })).ToArray();
            
            Task.WaitAll(tasks);
        }
    }
}
```

---

## Use Cases

### 1. Parallel Matrix Operations

```csharp
public class MatrixProcessor
{
    public void ProcessMatrixInPhases(int[,] matrix, int workerCount)
    {
        int rows = matrix.GetLength(0);
        int cols = matrix.GetLength(1);
        int rowsPerWorker = rows / workerCount;
        
        using (var barrier = new Barrier(workerCount, (b) =>
        {
            Console.WriteLine($"Phase {b.CurrentPhaseNumber + 1} complete");
        }))
        {
            var tasks = Enumerable.Range(0, workerCount).Select(workerId => Task.Run(() =>
            {
                int startRow = workerId * rowsPerWorker;
                int endRow = (workerId == workerCount - 1) ? rows : startRow + rowsPerWorker;
                
                // Phase 1: Normalize rows
                Console.WriteLine($"Worker {workerId}: Normalizing rows {startRow}-{endRow}");
                for (int i = startRow; i < endRow; i++)
                {
                    for (int j = 0; j < cols; j++)
                    {
                        matrix[i, j] = matrix[i, j] * 2;
                    }
                }
                barrier.SignalAndWait();
                
                // Phase 2: Apply transformation
                Console.WriteLine($"Worker {workerId}: Transforming rows {startRow}-{endRow}");
                for (int i = startRow; i < endRow; i++)
                {
                    for (int j = 0; j < cols; j++)
                    {
                        matrix[i, j] = matrix[i, j] + 10;
                    }
                }
                barrier.SignalAndWait();
                
                // Phase 3: Validate
                Console.WriteLine($"Worker {workerId}: Validating rows {startRow}-{endRow}");
                for (int i = startRow; i < endRow; i++)
                {
                    for (int j = 0; j < cols; j++)
                    {
                        if (matrix[i, j] < 0)
                        {
                            Console.WriteLine($"Worker {workerId}: Invalid value at [{i},{j}]");
                        }
                    }
                }
                barrier.SignalAndWait();
            })).ToArray();
            
            Task.WaitAll(tasks);
        }
        
        Console.WriteLine("Matrix processing complete");
    }
}

// Usage
var matrix = new int[100, 100];
// Initialize matrix...
var processor = new MatrixProcessor();
processor.ProcessMatrixInPhases(matrix, workerCount: 4);
```

### 2. Simulation Steps

```csharp
public class SimulationEngine
{
    private List<Agent> _agents;
    private Barrier _barrier;
    
    public class Agent
    {
        public int Id { get; set; }
        public double X { get; set; }
        public double Y { get; set; }
        
        public void UpdatePosition()
        {
            X += Random.Shared.NextDouble() - 0.5;
            Y += Random.Shared.NextDouble() - 0.5;
        }
        
        public void DetectCollisions(List<Agent> otherAgents)
        {
            // Collision detection logic
            Thread.Sleep(10); // Simulate work
        }
        
        public void React()
        {
            // React to environment
            Thread.Sleep(10);
        }
    }
    
    public void RunSimulation(int agentCount, int steps)
    {
        _agents = Enumerable.Range(0, agentCount)
            .Select(i => new Agent { Id = i, X = i, Y = i })
            .ToList();
        
        _barrier = new Barrier(agentCount, (b) =>
        {
            Console.WriteLine($"Step {b.CurrentPhaseNumber + 1} synchronized");
        });
        
        try
        {
            var tasks = _agents.Select(agent => Task.Run(() =>
            {
                for (int step = 0; step < steps; step++)
                {
                    // Phase 1: Update positions
                    agent.UpdatePosition();
                    _barrier.SignalAndWait();
                    
                    // Phase 2: Detect collisions (needs all positions updated)
                    agent.DetectCollisions(_agents);
                    _barrier.SignalAndWait();
                    
                    // Phase 3: React to environment
                    agent.React();
                    _barrier.SignalAndWait();
                }
            })).ToArray();
            
            Task.WaitAll(tasks);
        }
        finally
        {
            _barrier.Dispose();
        }
        
        Console.WriteLine("Simulation complete");
    }
}

// Usage
var simulation = new SimulationEngine();
simulation.RunSimulation(agentCount: 10, steps: 5);
```

### 3. Data Processing Pipeline

```csharp
public class PipelineProcessor
{
    public class DataBatch
    {
        public List<string> Data { get; set; } = new List<string>();
    }
    
    public void ProcessPipeline(List<DataBatch> batches)
    {
        int batchCount = batches.Count;
        
        using (var barrier = new Barrier(batchCount, (b) =>
        {
            Console.WriteLine($"Pipeline stage {b.CurrentPhaseNumber + 1} complete for all batches");
        }))
        {
            var tasks = batches.Select((batch, index) => Task.Run(() =>
            {
                // Stage 1: Extract
                Console.WriteLine($"Batch {index}: Extracting data");
                Thread.Sleep(Random.Shared.Next(500, 1000));
                var extracted = batch.Data.Select(d => d.ToUpper()).ToList();
                barrier.SignalAndWait();
                
                // Stage 2: Transform
                Console.WriteLine($"Batch {index}: Transforming data");
                Thread.Sleep(Random.Shared.Next(500, 1000));
                var transformed = extracted.Select(d => $"[{d}]").ToList();
                barrier.SignalAndWait();
                
                // Stage 3: Load
                Console.WriteLine($"Batch {index}: Loading data");
                Thread.Sleep(Random.Shared.Next(500, 1000));
                // Save transformed data
                barrier.SignalAndWait();
                
                Console.WriteLine($"Batch {index}: Complete");
            })).ToArray();
            
            Task.WaitAll(tasks);
        }
    }
}

// Usage
var batches = Enumerable.Range(0, 4).Select(i => new PipelineProcessor.DataBatch
{
    Data = Enumerable.Range(0, 10).Select(j => $"Item{i}-{j}").ToList()
}).ToList();

var processor = new PipelineProcessor();
processor.ProcessPipeline(batches);
```

### 4. Game Frame Synchronization

```csharp
public class GameEngine
{
    private Barrier _frameBarrier;
    private bool _running = true;
    
    public void RunGame(int playerCount)
    {
        _frameBarrier = new Barrier(playerCount + 1, (b) => // +1 for render thread
        {
            Console.WriteLine($"Frame {b.CurrentPhaseNumber} complete");
        });
        
        try
        {
            // Player threads
            var playerTasks = Enumerable.Range(0, playerCount).Select(playerId => Task.Run(() =>
            {
                int frame = 0;
                while (_running && frame < 10)
                {
                    // Update player state
                    Console.WriteLine($"Player {playerId}: Processing frame {frame}");
                    Thread.Sleep(Random.Shared.Next(50, 150));
                    
                    _frameBarrier.SignalAndWait(); // Wait for all players and render
                    frame++;
                }
            })).ToArray();
            
            // Render thread
            var renderTask = Task.Run(() =>
            {
                int frame = 0;
                while (_running && frame < 10)
                {
                    _frameBarrier.SignalAndWait(); // Wait for all players
                    
                    // Render frame with all player states updated
                    Console.WriteLine($"=== Rendering frame {frame} ===");
                    Thread.Sleep(50);
                    frame++;
                }
            });
            
            Task.WaitAll(playerTasks.Concat(new[] { renderTask }).ToArray());
        }
        finally
        {
            _frameBarrier.Dispose();
        }
    }
    
    public void Stop()
    {
        _running = false;
    }
}

// Usage
var game = new GameEngine();
game.RunGame(playerCount: 4);
```

---

## Best Practices

### 1. Dispose Barrier

```csharp
// ✅ Good - using statement
using (var barrier = new Barrier(participantCount))
{
    // Use barrier
}

// ✅ Good - explicit disposal
var barrier = new Barrier(participantCount);
try
{
    // Use barrier
}
finally
{
    barrier.Dispose();
}
```

### 2. Handle Post-Phase Exceptions

```csharp
var barrier = new Barrier(participantCount, (b) =>
{
    try
    {
        // Post-phase action
        PerformAggregation();
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Post-phase error: {ex.Message}");
        throw; // Will be wrapped in BarrierPostPhaseException
    }
});

// In participant threads
try
{
    barrier.SignalAndWait();
}
catch (BarrierPostPhaseException ex)
{
    Console.WriteLine($"Barrier post-phase failed: {ex.InnerException?.Message}");
}
```

### 3. Use Timeout for Safety

```csharp
// ✅ Good - with timeout
if (!barrier.SignalAndWait(TimeSpan.FromSeconds(30)))
{
    Console.WriteLine("Barrier timeout - possible deadlock");
    // Handle timeout
}

// ⚠️ Risky - infinite wait
barrier.SignalAndWait(); // Could block forever if participant fails
```

### 4. Add/Remove Participants Carefully

```csharp
// Add participant
barrier.AddParticipant();

Task.Run(() =>
{
    try
    {
        for (int i = 0; i < phaseCount; i++)
        {
            DoWork();
            barrier.SignalAndWait();
        }
    }
    finally
    {
        // Remove participant when done
        barrier.RemoveParticipant();
    }
});
```

### 5. Avoid Long Operations in Post-Phase Action

```csharp
// ❌ Bad - Long operation blocks all participants
var barrier = new Barrier(count, (b) =>
{
    Thread.Sleep(5000); // All threads wait!
    ExpensiveOperation();
});

// ✅ Good - Quick operations only
var barrier = new Barrier(count, (b) =>
{
    Console.WriteLine($"Phase {b.CurrentPhaseNumber} done");
    phaseCounter++;
});
```

### 6. Consider Parallel.For for Simple Cases

```csharp
// ❌ Don't use Barrier for this
using (var barrier = new Barrier(workerCount))
{
    Parallel.For(0, workerCount, i =>
    {
        ProcessItem(i);
        barrier.SignalAndWait(); // Unnecessary complexity
    });
}

// ✅ Better - Parallel.For handles synchronization
Parallel.For(0, workerCount, i =>
{
    ProcessItem(i);
});
```

---

## Barrier vs Other Synchronization

| Feature | Barrier | CountdownEvent | ManualResetEvent |
|---------|---------|----------------|------------------|
| Multiple Phases | ✅ Yes | ❌ No | ❌ No |
| All Wait | ✅ Yes | 1 waits | All wait |
| Reusable | ✅ Yes | ❌ No | ✅ Yes |
| Phase Action | ✅ Yes | ❌ No | ❌ No |
| Dynamic Participants | ✅ Yes | ✅ Yes | N/A |

---

## Summary

- **Barrier**: Synchronizes multiple threads across multiple phases
- Each phase waits for all participants to reach the barrier
- Optional post-phase action after each phase completes
- Perfect for parallel algorithms with distinct stages
- Always dispose when done
- Use timeouts to avoid deadlocks

**Next:** [CountdownEvent](./11-CountdownEvent.md) | **Previous:** [Events (ManualReset & AutoReset)](./09-Events.md) | **Back to:** [README](./README.md)

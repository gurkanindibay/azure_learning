# Observability Techniques

## 1. Distributed Tracing

### What is Distributed Tracing?

Distributed tracing tracks requests as they flow through multiple services in a distributed system, creating a complete picture of the request journey.

### Core Concepts

#### Trace Context
The propagated information that connects spans across service boundaries:

```
Trace ID: 32-character hex string (identifies entire request)
Span ID: 16-character hex string (identifies current operation)
Parent Span ID: 16-character hex string (identifies caller)
Trace Flags: Sampling decision, debug flag
```

#### Span Structure

```json
{
  "traceId": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "spanId": "1234567890abcdef",
  "parentSpanId": "fedcba0987654321",
  "name": "ProcessPayment",
  "startTime": "2025-12-10T14:23:45.123Z",
  "endTime": "2025-12-10T14:23:45.456Z",
  "duration": 333,
  "status": "OK",
  "attributes": {
    "http.method": "POST",
    "http.url": "/api/payments",
    "http.status_code": 200,
    "user.id": "user-12345",
    "payment.amount": 150.00,
    "payment.currency": "USD"
  },
  "events": [
    {
      "timestamp": "2025-12-10T14:23:45.200Z",
      "name": "payment.validation.complete",
      "attributes": {"valid": true}
    }
  ]
}
```

### Implementation Patterns

#### Manual Instrumentation

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def process_order(order_id):
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)
        
        # Do work
        validate_order(order_id)
        charge_payment(order_id)
        update_inventory(order_id)
        
        span.add_event("order.processed")
        return True
```

#### Automatic Instrumentation

```python
# Many frameworks provide auto-instrumentation
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

FlaskInstrumentor().instrument()
RequestsInstrumentor().instrument()
```

### Context Propagation

#### W3C Trace Context (HTTP Headers)

```
traceparent: 00-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6-1234567890abcdef-01
tracestate: vendor1=value1,vendor2=value2
```

#### Implementation

```javascript
// Outgoing request
const axios = require('axios');
const { trace, context } = require('@opentelemetry/api');

const span = trace.getActiveSpan();
const carrier = {};

// Inject trace context into headers
propagation.inject(context.active(), carrier);

await axios.post('https://api.example.com/users', data, {
  headers: carrier
});
```

```javascript
// Incoming request
const express = require('express');
const { propagation, context } = require('@opentelemetry/api');

app.use((req, res, next) => {
  // Extract trace context from headers
  const ctx = propagation.extract(context.active(), req.headers);
  
  context.with(ctx, () => {
    next();
  });
});
```

### Advanced Tracing Techniques

#### Baggage
Key-value pairs propagated with trace context for cross-cutting concerns:

```python
from opentelemetry import baggage

# Set baggage
ctx = baggage.set_baggage("user.tier", "premium")

# Get baggage
user_tier = baggage.get_baggage("user.tier")
```

#### Span Links
Connect related but independent traces:

```python
span = tracer.start_span(
    "batch_process",
    links=[
        trace.Link(trace_context_1),
        trace.Link(trace_context_2)
    ]
)
```

## 2. Correlation Techniques

### Correlation IDs

A unique identifier that follows a request through the entire system.

#### Implementation Strategy

```csharp
public class CorrelationIdMiddleware
{
    private const string CorrelationIdHeader = "X-Correlation-ID";
    
    public async Task InvokeAsync(HttpContext context)
    {
        var correlationId = context.Request.Headers[CorrelationIdHeader]
            .FirstOrDefault() ?? Guid.NewGuid().ToString();
        
        context.Items["CorrelationId"] = correlationId;
        context.Response.Headers.Add(CorrelationIdHeader, correlationId);
        
        using (LogContext.PushProperty("CorrelationId", correlationId))
        {
            await _next(context);
        }
    }
}
```

### Log Correlation

#### Structured Logging with Correlation

```json
{
  "timestamp": "2025-12-10T14:23:45.123Z",
  "level": "INFO",
  "service": "order-service",
  "correlationId": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "traceId": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "spanId": "1234567890abcdef",
  "userId": "user-12345",
  "orderId": "order-67890",
  "message": "Order created successfully"
}
```

### Cross-Service Correlation

```
Client Request
    ↓ (correlation-id: abc123)
API Gateway
    ↓ (correlation-id: abc123, span-id: span1)
Order Service → Logs with correlation-id + span-id
    ↓ (correlation-id: abc123, span-id: span2)
Payment Service → Logs with correlation-id + span-id
    ↓ (correlation-id: abc123, span-id: span3)
Inventory Service → Logs with correlation-id + span-id
```

## 3. Sampling Techniques

### Why Sampling?

At scale, collecting 100% of traces is expensive and often unnecessary. Sampling reduces data volume while maintaining observability.

### Sampling Strategies

#### Head-Based Sampling (Decision at Trace Start)

**1. Deterministic/Probability Sampling**
```python
# Sample 10% of all traces
sampler = TraceIdRatioBased(0.1)
```

**2. Rate Limiting Sampling**
```python
# Sample max 100 traces per second
sampler = RateLimitingSampler(100)
```

**3. Parent-Based Sampling**
```python
# Follow parent's sampling decision
sampler = ParentBased(root=TraceIdRatioBased(0.1))
```

#### Tail-Based Sampling (Decision After Trace Completion)

Examine complete traces before deciding to keep them.

**Criteria:**
- Keep all error traces
- Keep slow traces (>1s duration)
- Sample 1% of successful fast traces
- Keep traces with specific attributes

```python
# Pseudo-code
def should_sample(trace):
    if trace.has_errors():
        return True
    if trace.duration > 1000:  # 1 second
        return True
    if trace.has_attribute("vip.user"):
        return True
    return random.random() < 0.01  # 1% of remaining
```

#### Adaptive Sampling

Dynamically adjust sampling rates based on traffic:

```python
class AdaptiveSampler:
    def __init__(self, target_rate=100):
        self.target_rate = target_rate  # traces per second
        self.current_rate = 0
        self.sample_probability = 1.0
    
    def should_sample(self):
        if self.current_rate < self.target_rate:
            return True
        
        # Adjust probability to maintain target rate
        self.sample_probability = self.target_rate / self.current_rate
        return random.random() < self.sample_probability
```

### Sampling Best Practices

1. **Always sample errors**: Keep 100% of failed requests
2. **Sample by latency**: Keep slow requests for performance analysis
3. **Use consistent IDs**: Same trace ID = same sampling decision
4. **Consider costs**: Balance data volume with observability needs
5. **Monitor sample rates**: Ensure sufficient data for analysis

## 4. Aggregation Techniques

### Metrics Aggregation

#### Time-Based Aggregation

```
Raw data points → 1-minute aggregation → 1-hour aggregation → 1-day aggregation

Example:
10:00:01 - 5 requests
10:00:15 - 8 requests     →  10:00-10:01: 150 requests  →  10:00-11:00: 9,000 requests
10:00:30 - 12 requests
...
```

#### Aggregation Functions

**Count**: Total number of events
```
sum(http_requests_total)
```

**Rate**: Events per time unit
```
rate(http_requests_total[5m])  # requests/second over 5 minutes
```

**Percentiles**: Distribution analysis
```
histogram_quantile(0.95, http_request_duration_seconds_bucket)
```

**Average**: Mean value
```
avg(cpu_usage_percent)
```

#### Pre-aggregation vs. Post-aggregation

**Pre-aggregation**: Aggregate at source
- Lower storage costs
- Faster queries
- Less flexibility

**Post-aggregation**: Aggregate at query time
- Higher storage costs
- Slower queries
- More flexibility

### Log Aggregation

#### Pattern-Based Aggregation

Group similar log messages:

```
Original logs:
- "User 123 logged in"
- "User 456 logged in"
- "User 789 logged in"

Aggregated:
- Pattern: "User * logged in" (count: 3, users: [123, 456, 789])
```

#### Time-Window Aggregation

```python
# Count errors per service per minute
SELECT 
    service,
    COUNT(*) as error_count,
    DATE_TRUNC('minute', timestamp) as window
FROM logs
WHERE level = 'ERROR'
GROUP BY service, window
```

### Trace Aggregation

#### Service Dependency Mapping

Aggregate spans to build service graphs:

```
Order Service
  ↓ calls (avg: 50ms, p95: 80ms, errors: 0.1%)
Payment Service
  ↓ calls (avg: 30ms, p95: 60ms, errors: 0.05%)
Database
```

#### Operation Performance

Aggregate by operation name:

```sql
SELECT 
    operation_name,
    COUNT(*) as total_calls,
    AVG(duration) as avg_duration,
    PERCENTILE(duration, 95) as p95_duration,
    SUM(CASE WHEN status = 'ERROR' THEN 1 ELSE 0 END) / COUNT(*) as error_rate
FROM spans
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY operation_name
```

## 5. Anomaly Detection

### Statistical Methods

#### Standard Deviation

```python
def detect_anomaly(value, mean, std_dev, threshold=3):
    """Z-score method"""
    z_score = abs(value - mean) / std_dev
    return z_score > threshold
```

#### Moving Average

```python
def detect_anomaly(current, history, window=10, threshold=2.0):
    """Compare to moving average"""
    moving_avg = sum(history[-window:]) / window
    deviation = abs(current - moving_avg) / moving_avg
    return deviation > threshold
```

### Machine Learning Methods

#### Isolation Forest

```python
from sklearn.ensemble import IsolationForest

# Train model on normal behavior
model = IsolationForest(contamination=0.01)
model.fit(normal_metrics)

# Detect anomalies
prediction = model.predict(new_metric)
# -1 = anomaly, 1 = normal
```

#### Time Series Forecasting

```python
# Predict expected value
expected = forecast_model.predict(timestamp)

# Compare actual to expected
if abs(actual - expected) > threshold:
    alert("Anomaly detected")
```

## 6. Cardinality Management

### What is Cardinality?

The number of unique values for a dimension or combination of dimensions.

**High cardinality**: user_id, request_id, timestamp
**Low cardinality**: environment (prod/staging), region (us-east/eu-west)

### Problems with High Cardinality

- Exponential storage growth
- Slow query performance
- Increased costs

### Techniques to Manage Cardinality

#### 1. Dimension Reduction

```
❌ High cardinality:
metric{user_id="12345", request_id="abc123", endpoint="/api/users/12345"}

✅ Lower cardinality:
metric{endpoint="/api/users/:id"}
```

#### 2. Sampling

Only emit metrics for sampled requests.

#### 3. Bucketing

```
❌ response_time{value="123ms"}
❌ response_time{value="124ms"}

✅ response_time{bucket="100-200ms"}
```

#### 4. Exemplars

Keep aggregated metrics + link to example traces:

```
http_request_duration_bucket{le="0.5"} 1000 # {trace_id="abc123"}
```

## 7. Real-Time Stream Processing

### Architecture Pattern

```
Events → Collection → Stream Processing → Storage → Analysis
          (Agents)    (Kafka/Kinesis)      (Time-series DB)
```

### Processing Techniques

#### Windowing

**Tumbling Window**: Fixed, non-overlapping intervals
```
[0-5s] [5-10s] [10-15s]
```

**Sliding Window**: Overlapping intervals
```
[0-5s]
  [2-7s]
    [4-9s]
```

**Session Window**: Based on inactivity
```
[events...] <gap> [events...] <gap> [events...]
```

#### Stateful Processing

```python
# Count requests per user (stateful)
user_counts = {}

for event in stream:
    user_id = event['user_id']
    user_counts[user_id] = user_counts.get(user_id, 0) + 1
    
    if user_counts[user_id] > 1000:  # Rate limit
        alert(f"High request rate for {user_id}")
```

## 8. Synthetic Monitoring

### Active Monitoring

Proactively test system behavior with synthetic requests.

#### Techniques

**1. Health Check Endpoints**
```python
@app.route('/health')
def health_check():
    return {
        "status": "healthy",
        "database": check_database(),
        "cache": check_cache(),
        "dependencies": check_dependencies()
    }
```

**2. Synthetic Transactions**
```python
# Simulate user journey every 5 minutes
def synthetic_test():
    # 1. Load homepage
    response = requests.get('https://example.com')
    assert response.status_code == 200
    
    # 2. Login
    response = requests.post('https://example.com/login', 
                            json={'username': 'test', 'password': 'test'})
    assert response.status_code == 200
    
    # 3. Purchase flow
    response = requests.post('https://example.com/checkout')
    assert response.status_code == 200
```

**3. Canary Tests**
Deploy to small subset and monitor before full rollout.

## 9. Service Level Objectives (SLO)

### SLI (Service Level Indicator)

Quantitative measure of service quality:

```
Availability SLI = (successful requests) / (total requests)
Latency SLI = (requests < 300ms) / (total requests)
```

### SLO (Service Level Objective)

Target value for SLI:

```
Availability SLO: 99.9% (3 nines)
Latency SLO: 95% of requests < 300ms
```

### Error Budget

Acceptable amount of failure:

```
SLO: 99.9% availability
Error Budget: 0.1% = 43 minutes downtime per month

Error Budget Remaining = Error Budget - Actual Errors
```

### Implementation

```python
# Calculate error budget burn rate
def calculate_burn_rate(error_rate, slo_target, time_window):
    """
    error_rate: current error rate (e.g., 0.002 = 0.2%)
    slo_target: SLO target (e.g., 0.999 = 99.9%)
    time_window: measurement window in hours
    """
    error_budget = 1 - slo_target
    burn_rate = error_rate / error_budget
    
    # burn_rate > 1 means burning faster than sustainable
    return burn_rate
```

## 10. Context Enrichment

### Automatic Enrichment

Add contextual information to telemetry data automatically:

```python
def enrich_span(span, context):
    """Add contextual attributes to span"""
    span.set_attribute("user.id", context.user_id)
    span.set_attribute("user.tier", context.user_tier)
    span.set_attribute("tenant.id", context.tenant_id)
    span.set_attribute("deployment.version", os.getenv("VERSION"))
    span.set_attribute("deployment.region", os.getenv("REGION"))
    span.set_attribute("kubernetes.pod", os.getenv("HOSTNAME"))
```

### Resource Attributes

Metadata about the service itself:

```python
from opentelemetry.sdk.resources import Resource

resource = Resource.create({
    "service.name": "payment-service",
    "service.version": "2.4.1",
    "service.namespace": "production",
    "deployment.environment": "prod",
    "cloud.provider": "azure",
    "cloud.region": "eastus",
    "container.name": "payment-service-pod-abc123"
})
```

## Summary

Effective observability relies on multiple techniques working together:

- **Distributed tracing** for request flow visibility
- **Correlation** for connecting data across services
- **Sampling** for managing data volume
- **Aggregation** for efficient storage and analysis
- **Anomaly detection** for proactive issue identification
- **Cardinality management** for cost control
- **Stream processing** for real-time insights
- **SLOs** for quality measurement
- **Context enrichment** for better analysis

The key is selecting and combining techniques appropriate for your system's scale, complexity, and requirements.

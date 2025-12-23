# Observability Best Practices

## 1. Instrumentation Best Practices

### Use OpenTelemetry

**Always start with OpenTelemetry** for vendor-neutral instrumentation.

```python
# ✅ Good: Use OpenTelemetry
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

# ❌ Avoid: Vendor-specific SDKs (unless necessary)
import datadog_sdk  # locks you into DataDog
```

**Benefits:**
- No vendor lock-in
- Single instrumentation, multiple backends
- Industry standard
- Rich ecosystem

---

### Instrument at Strategic Points

**Key areas to instrument:**

1. **Service boundaries** (HTTP requests, gRPC calls)
2. **Database operations**
3. **External API calls**
4. **Message queue operations**
5. **Business-critical operations**
6. **Error paths**

```python
# Example: Instrument critical operations
@tracer.start_as_current_span("process_payment")
def process_payment(user_id, amount):
    span = trace.get_current_span()
    span.set_attribute("user.id", user_id)
    span.set_attribute("payment.amount", amount)
    
    try:
        # Business logic
        result = charge_payment(amount)
        span.set_attribute("payment.status", "success")
        return result
    except PaymentError as e:
        span.set_status(Status(StatusCode.ERROR))
        span.record_exception(e)
        raise
```

---

### Use Automatic Instrumentation When Possible

Most frameworks and libraries support auto-instrumentation.

```python
# Python: Auto-instrument common libraries
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

FlaskInstrumentor().instrument()
RequestsInstrumentor().instrument()
SQLAlchemyInstrumentor().instrument()
```

```javascript
// Node.js: Auto-instrument
const { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');
const { registerInstrumentations } = require('@opentelemetry/instrumentation');
const { HttpInstrumentation } = require('@opentelemetry/instrumentation-http');
const { ExpressInstrumentation } = require('@opentelemetry/instrumentation-express');

registerInstrumentations({
  instrumentations: [
    new HttpInstrumentation(),
    new ExpressInstrumentation(),
  ],
});
```

---

### Keep Instrumentation DRY (Don't Repeat Yourself)

Create reusable instrumentation helpers:

```python
# instrumentation_helpers.py
from functools import wraps
from opentelemetry import trace

def traced_function(operation_name=None):
    """Decorator for automatic span creation"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            span_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            with tracer.start_as_current_span(span_name) as span:
                # Add function arguments as attributes
                span.set_attributes({
                    f"arg.{i}": str(arg) for i, arg in enumerate(args)
                })
                return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@traced_function("calculate_total")
def calculate_order_total(order_id, items):
    # Business logic
    pass
```

---

## 2. Logging Best Practices

### Use Structured Logging

**Always use structured (JSON) logging** instead of plain text.

```python
# ❌ Bad: Unstructured logging
logger.info(f"User {user_id} placed order {order_id} for ${amount}")

# ✅ Good: Structured logging
logger.info("Order placed", extra={
    "event": "order.placed",
    "user_id": user_id,
    "order_id": order_id,
    "amount": amount,
    "currency": "USD"
})
```

**Output:**
```json
{
  "timestamp": "2025-12-10T14:23:45.123Z",
  "level": "INFO",
  "message": "Order placed",
  "event": "order.placed",
  "user_id": "user-12345",
  "order_id": "order-67890",
  "amount": 150.00,
  "currency": "USD",
  "trace_id": "a1b2c3d4e5f6g7h8",
  "span_id": "1234567890ab"
}
```

---

### Include Correlation IDs

Always include trace/correlation IDs in logs.

```python
import logging
from opentelemetry import trace

class TraceContextFilter(logging.Filter):
    """Add trace context to all log records"""
    def filter(self, record):
        span = trace.get_current_span()
        if span:
            ctx = span.get_span_context()
            record.trace_id = format(ctx.trace_id, '032x')
            record.span_id = format(ctx.span_id, '016x')
        else:
            record.trace_id = None
            record.span_id = None
        return True

# Configure logger
logger = logging.getLogger(__name__)
logger.addFilter(TraceContextFilter())
```

---

### Use Appropriate Log Levels

```python
# TRACE/DEBUG: Detailed diagnostic (verbose)
logger.debug("Cache lookup", extra={"key": cache_key, "hit": True})

# INFO: Important business events
logger.info("User registered", extra={"user_id": user_id})

# WARN: Potential issues (recoverable)
logger.warning("API rate limit approaching", extra={"usage": 95})

# ERROR: Errors requiring attention
logger.error("Payment failed", extra={"error": str(e)}, exc_info=True)

# CRITICAL/FATAL: Severe errors
logger.critical("Database connection lost", exc_info=True)
```

**Guidelines:**
- **DEBUG**: Development only, not production
- **INFO**: Normal business operations
- **WARN**: Unusual but handled situations
- **ERROR**: Failures requiring investigation
- **CRITICAL**: Service impacting issues

---

### Don't Log Sensitive Data

```python
# ❌ Bad: Logging sensitive data
logger.info("Payment processed", extra={
    "credit_card": "4532-1234-5678-9010",  # PII
    "password": user.password,              # Credentials
    "ssn": user.ssn                         # PII
})

# ✅ Good: Mask or omit sensitive data
logger.info("Payment processed", extra={
    "payment_method": "credit_card",
    "last_four": "9010",
    "user_id": user.id  # Use IDs, not PII
})
```

---

### Set Log Retention Policies

```yaml
# Example retention policy
development:
  retention: 7 days
  
staging:
  retention: 30 days
  
production:
  retention: 90 days
  hot_tier: 7 days   # Fast access
  warm_tier: 30 days # Standard access
  cold_tier: 90 days # Archive
```

---

## 3. Metrics Best Practices

### Choose the Right Metric Type

```python
from prometheus_client import Counter, Gauge, Histogram, Summary

# Counter: Monotonically increasing (total requests, total errors)
requests_total = Counter('http_requests_total', 
                        'Total HTTP requests',
                        ['method', 'endpoint', 'status'])

# Gauge: Point-in-time value (current memory, queue length)
memory_usage = Gauge('memory_usage_bytes', 
                    'Current memory usage')

# Histogram: Distribution (response time, request size)
request_duration = Histogram('http_request_duration_seconds',
                            'HTTP request duration',
                            ['method', 'endpoint'])

# Summary: Pre-calculated quantiles
request_size = Summary('http_request_size_bytes',
                      'HTTP request size',
                      ['method'])
```

---

### Use Consistent Naming Conventions

**Prometheus naming conventions:**
- Use `snake_case`
- Include unit suffix (`_seconds`, `_bytes`, `_total`)
- Start with namespace (`myapp_`)
- Be descriptive

```python
# ✅ Good naming
myapp_http_requests_total
myapp_http_request_duration_seconds
myapp_database_connections_active
myapp_queue_messages_processed_total

# ❌ Bad naming
requests          # Too generic
requestCount      # Wrong case
time              # No unit
http_req_dur      # Unclear abbreviation
```

---

### Keep Cardinality Under Control

```python
# ❌ Bad: High cardinality (unbounded labels)
requests_total.labels(
    method='GET',
    endpoint='/api/users/12345',  # User ID in label!
    user_id='12345'                # Another high-cardinality label
).inc()

# ✅ Good: Low cardinality (bounded labels)
requests_total.labels(
    method='GET',
    endpoint='/api/users/:id',    # Parameterized
    status='200'
).inc()
```

**Rule of thumb:**
- Keep total cardinality under 10,000 per metric
- Use high-cardinality data in traces, not metrics

---

### Monitor the Four Golden Signals

For every service, track:

1. **Latency**: Request duration
2. **Traffic**: Request rate
3. **Errors**: Error rate
4. **Saturation**: Resource utilization

```python
# Latency
request_duration = Histogram('http_request_duration_seconds', ...)

# Traffic
request_count = Counter('http_requests_total', ...)

# Errors
error_count = Counter('http_requests_errors_total', ...)

# Saturation
cpu_usage = Gauge('cpu_usage_percent', ...)
memory_usage = Gauge('memory_usage_bytes', ...)
```

---

### Use RED Method for Services

**Rate, Errors, Duration** - Essential metrics for request-driven services:

```promql
# Rate: Requests per second
rate(http_requests_total[5m])

# Errors: Error percentage
sum(rate(http_requests_total{status=~"5.."}[5m])) /
sum(rate(http_requests_total[5m]))

# Duration: Response time (p50, p95, p99)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

---

## 4. Distributed Tracing Best Practices

### Always Propagate Context

Ensure trace context is propagated across all service boundaries.

```python
import requests
from opentelemetry import trace
from opentelemetry.propagate import inject

# Create outgoing request with trace context
headers = {}
inject(headers)  # Inject trace context into headers

response = requests.get('https://api.example.com/users', headers=headers)
```

---

### Add Meaningful Span Attributes

```python
with tracer.start_as_current_span("database_query") as span:
    # ✅ Good: Rich, meaningful attributes
    span.set_attributes({
        "db.system": "postgresql",
        "db.name": "users_db",
        "db.statement": "SELECT * FROM users WHERE id = ?",
        "db.operation": "SELECT",
        "db.rows_affected": 1,
        "user.id": user_id,
    })
    
    # ❌ Bad: Sparse attributes
    span.set_attribute("query", "select")  # Too generic
```

**Follow semantic conventions:**
https://opentelemetry.io/docs/specs/semconv/

---

### Record Exceptions in Spans

```python
with tracer.start_as_current_span("process_payment") as span:
    try:
        charge_payment()
    except Exception as e:
        span.set_status(Status(StatusCode.ERROR, str(e)))
        span.record_exception(e)  # Record full exception
        raise
```

---

### Use Sampling Strategically

```python
from opentelemetry.sdk.trace.sampling import (
    ParentBasedTraceIdRatioBased,
    ALWAYS_ON,
    TraceIdRatioBased
)

# Sample 10% of successful requests, 100% of errors
class SmartSampler:
    def should_sample(self, context, trace_id, name, kind, attributes, links):
        # Always sample if parent sampled
        parent_context = trace.get_current_span(context).get_span_context()
        if parent_context.is_valid and parent_context.trace_flags.sampled:
            return ALWAYS_ON
        
        # Sample all errors
        if attributes and attributes.get("error"):
            return ALWAYS_ON
        
        # Sample 10% of others
        return TraceIdRatioBased(0.1).should_sample(
            context, trace_id, name, kind, attributes, links
        )
```

---

### Keep Span Count Reasonable

```python
# ❌ Bad: Too many spans (excessive overhead)
for item in items:  # Might be 10,000 items
    with tracer.start_as_current_span(f"process_item_{item.id}"):
        process(item)

# ✅ Good: Batch processing
with tracer.start_as_current_span("process_items") as span:
    span.set_attribute("item.count", len(items))
    for item in items:
        process(item)
```

---

## 5. Alerting Best Practices

### Alert on Symptoms, Not Causes

```yaml
# ❌ Bad: Alert on causes (too noisy)
alert: HighCPU
expr: cpu_usage > 80

# ✅ Good: Alert on symptoms (user impact)
alert: HighErrorRate
expr: |
  sum(rate(http_requests_total{status=~"5.."}[5m])) /
  sum(rate(http_requests_total[5m])) > 0.01
annotations:
  summary: "Error rate > 1%"
  impact: "Users experiencing failures"
```

---

### Use SLOs for Alerting

Define Service Level Objectives and alert on violations.

```yaml
# SLO: 99.9% availability
alert: SLOViolation
expr: |
  sum(rate(http_requests_total{status=~"5.."}[30m])) /
  sum(rate(http_requests_total[30m])) > 0.001
for: 5m
labels:
  severity: critical
annotations:
  summary: "SLO violation: availability < 99.9%"
  runbook: "https://wiki/runbooks/availability-slo"
```

---

### Include Context in Alerts

```yaml
alert: HighErrorRate
annotations:
  summary: "High error rate in {{ $labels.service }}"
  description: |
    Error rate: {{ $value | humanizePercentage }}
    Service: {{ $labels.service }}
    Environment: {{ $labels.environment }}
  dashboard: "https://grafana/d/service-{{ $labels.service }}"
  logs: "https://loki/?query={service='{{ $labels.service }}'}"
  runbook: "https://wiki/runbooks/high-error-rate"
```

---

### Avoid Alert Fatigue

```python
# Use proper thresholds and durations
alert: DiskSpaceWarning
expr: disk_usage_percent > 80
for: 30m  # Must persist for 30 minutes

# Group related alerts
alert: ServiceDown
expr: up{job="my-service"} == 0
for: 5m
labels:
  severity: critical
  service: my-service
  team: platform
```

---

## 6. Performance and Cost Optimization

### Sample Intelligently

```python
# Keep 100% of errors, 1% of success
class ErrorAwareSampler:
    def should_sample(self, trace):
        if trace.has_errors:
            return True
        return random.random() < 0.01
```

---

### Use Aggregation for High-Volume Metrics

```python
# ❌ Bad: Record every event (millions per second)
for event in events:
    metric.observe(event.duration)

# ✅ Good: Pre-aggregate
bucket_counts = defaultdict(int)
for event in events:
    bucket = get_bucket(event.duration)
    bucket_counts[bucket] += 1

for bucket, count in bucket_counts.items():
    metric.observe(bucket, count)
```

---

### Set Data Retention Policies

```yaml
# Tiered retention
metrics:
  high_resolution: 7 days      # 10s granularity
  medium_resolution: 30 days   # 1m granularity
  low_resolution: 365 days     # 1h granularity

logs:
  hot: 7 days                  # Fast SSD
  warm: 30 days                # Standard storage
  cold: 90 days                # Archive (S3)

traces:
  sampled: 30 days
  errors_only: 90 days
```

---

### Minimize Instrumentation Overhead

```python
# ✅ Lazy attribute computation
with tracer.start_as_current_span("process") as span:
    result = expensive_operation()
    
    # Only compute if span is recording
    if span.is_recording():
        span.set_attribute("result.size", len(result))
```

---

## 7. Security Best Practices

### Sanitize Sensitive Data

```python
def sanitize_headers(headers):
    """Remove sensitive headers from traces/logs"""
    sensitive_headers = ['authorization', 'cookie', 'x-api-key']
    return {
        k: '***REDACTED***' if k.lower() in sensitive_headers else v
        for k, v in headers.items()
    }

with tracer.start_as_current_span("http_request") as span:
    span.set_attribute("http.headers", sanitize_headers(request.headers))
```

---

### Control Access to Observability Data

```yaml
# RBAC for observability tools
roles:
  - name: developer
    permissions:
      - read:metrics
      - read:logs
      - read:traces
  
  - name: sre
    permissions:
      - read:*
      - write:alerts
      - admin:dashboards
  
  - name: security
    permissions:
      - read:audit_logs
      - read:security_metrics
```

---

### Encrypt Data in Transit and at Rest

```yaml
# Encrypt telemetry data
collectors:
  receivers:
    otlp:
      protocols:
        grpc:
          tls:
            cert_file: /certs/cert.pem
            key_file: /certs/key.pem
  
  exporters:
    otlp:
      endpoint: https://backend:4317
      tls:
        insecure: false
        ca_file: /certs/ca.pem
```

---

## 8. Operational Best Practices

### Document Your Observability

Create and maintain:
1. **Runbooks** for common alerts
2. **Dashboard catalog** with descriptions
3. **Metrics dictionary** explaining each metric
4. **Trace attributes conventions**

```markdown
# Runbook: High Error Rate

## Symptoms
- Alert: HighErrorRate
- Error rate > 1%

## Investigation
1. Check error logs: `{service="api"} |= "ERROR"`
2. View traces: Filter by `status=ERROR`
3. Check recent deployments
4. Review dependency health

## Mitigation
1. Rollback if recent deployment
2. Scale up if resource constrained
3. Check dependent services

## Prevention
- Add more integration tests
- Implement circuit breakers
```

---

### Use Infrastructure as Code

```terraform
# Terraform: Provision observability stack
resource "helm_release" "prometheus" {
  name       = "prometheus"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "kube-prometheus-stack"
  
  values = [
    file("${path.module}/prometheus-values.yaml")
  ]
}

resource "grafana_dashboard" "service_dashboard" {
  config_json = file("${path.module}/dashboards/service.json")
}
```

---

### Test Your Observability

```python
# Test that instrumentation works
def test_tracing():
    with tracer.start_as_current_span("test_span") as span:
        span.set_attribute("test", "value")
        
    # Verify span was created
    spans = exporter.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].attributes["test"] == "value"

# Test alerts
def test_alert_fires():
    # Simulate high error rate
    for _ in range(100):
        error_counter.inc()
    
    # Wait for alert evaluation
    time.sleep(60)
    
    # Verify alert fired
    alerts = alertmanager.get_alerts()
    assert any(a.name == "HighErrorRate" for a in alerts)
```

---

### Monitor Your Monitoring

**Monitor the observability stack itself:**
- Collector health and performance
- Data ingestion rates
- Storage usage
- Query performance
- Alert delivery

```promql
# Metrics for observability stack
otel_collector_receiver_accepted_spans
otel_collector_processor_dropped_spans
prometheus_tsdb_storage_blocks_bytes
grafana_api_response_time_seconds
```

---

## 9. Team and Process Best Practices

### Establish Observability Champions

Designate team members to:
- Maintain observability standards
- Review instrumentation in PRs
- Train new team members
- Improve dashboards and alerts

---

### Include Observability in Definition of Done

```markdown
## Definition of Done Checklist

- [ ] Code reviewed and approved
- [ ] Tests passing (unit, integration)
- [ ] **Instrumentation added (metrics, logs, traces)**
- [ ] **Dashboard updated if needed**
- [ ] **Alerts configured if needed**
- [ ] **Runbook updated**
- [ ] Documentation updated
- [ ] Deployed to staging
```

---

### Review Dashboards and Alerts Regularly

```markdown
# Quarterly Review Checklist

- [ ] Remove unused dashboards
- [ ] Archive obsolete alerts
- [ ] Update alert thresholds based on actual behavior
- [ ] Verify runbooks are current
- [ ] Check alert notification routing
- [ ] Review data retention costs
```

---

### Foster a Blameless Culture

When incidents occur:
1. Focus on learning, not blaming
2. Document in postmortems
3. Improve observability based on gaps
4. Share learnings across teams

---

## 10. Common Antipatterns to Avoid

### ❌ Logging Everything

```python
# Too much logging (noisy, expensive)
for i in range(10000):
    logger.debug(f"Processing item {i}")  # Don't do this
```

### ❌ High-Cardinality Metrics

```python
# Unbounded label values
requests.labels(user_id=user_id).inc()  # DON'T
```

### ❌ Alert on Everything

```yaml
# Too sensitive
alert: CPUHigh
expr: cpu > 50%  # Too low threshold
for: 10s         # Too short duration
```

### ❌ No Context in Logs

```python
# Useless log
logger.error("Failed")  # No context!

# Better
logger.error("Payment processing failed", extra={
    "user_id": user_id,
    "order_id": order_id,
    "error": str(e)
})
```

### ❌ Not Testing Observability

```python
# No verification that instrumentation works
# Add tests for spans, metrics, logs
```

---

## Summary Checklist

### ✅ Instrumentation
- [ ] Use OpenTelemetry
- [ ] Auto-instrument where possible
- [ ] Propagate context across boundaries
- [ ] Add meaningful attributes

### ✅ Logging
- [ ] Use structured logging (JSON)
- [ ] Include correlation IDs
- [ ] Use appropriate log levels
- [ ] Don't log sensitive data

### ✅ Metrics
- [ ] Choose correct metric types
- [ ] Use consistent naming
- [ ] Control cardinality
- [ ] Monitor golden signals

### ✅ Tracing
- [ ] Propagate trace context
- [ ] Add span attributes
- [ ] Record exceptions
- [ ] Sample intelligently

### ✅ Alerting
- [ ] Alert on symptoms
- [ ] Use SLOs
- [ ] Include context
- [ ] Avoid alert fatigue

### ✅ Cost & Performance
- [ ] Implement sampling
- [ ] Set retention policies
- [ ] Minimize overhead

### ✅ Security
- [ ] Sanitize sensitive data
- [ ] Control access
- [ ] Encrypt data

### ✅ Operations
- [ ] Document everything
- [ ] Use IaC
- [ ] Test observability
- [ ] Monitor the monitoring

### ✅ Culture
- [ ] Establish champions
- [ ] Include in DoD
- [ ] Regular reviews
- [ ] Blameless postmortems

---

Following these best practices will help you build a robust, cost-effective, and maintainable observability solution that provides genuine insights into your system's behavior.

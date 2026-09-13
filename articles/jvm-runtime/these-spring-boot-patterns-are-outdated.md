---
type: Article
title: "These Spring Boot Patterns Are Outdated"
source: "https://medium.com/javarevisited/these-spring-boot-patterns-are-outdated-eacb34065736"
author:
  - "Umesh Kumar Yadav"
published: 2026-09-09
created: 2026-09-13
description: "Spring Boot evolution from 2.x to 3.x and toward 4.x has deprecated or replaced foundational idioms. A practical guide to modernizing field injection, configuration, transactions, logging, security, HTTP clients, Jakarta namespaces, and concurrency."
tags:
  - "clippings"
  - "spring-boot"
  - "java"
  - "jvm"
  - "software-architecture"
  - "microservices"
  - "migration"
---

# These Spring Boot Patterns Are Outdated

> **Author**: [Umesh Kumar Yadav](https://medium.com/@umeshkumaryadav)  
> **Published**: September 09, 2026  
> **Source**: [Medium / Javarevisited](https://medium.com/javarevisited/these-spring-boot-patterns-are-outdated-eacb34065736)  
> **Domain**: Spring Boot 3.x/4.x Migration, Dependency Injection, Proxy Architecture, Virtual Threads, JPA Optimization  
> **Related Takeaways**: [65. Modern Spring Boot Architecture & Migration Patterns — Key Takeaways](../../system-design-architecture/jvm-runtime/65-jvm-key-takeaways.md)  

---

![Spring Boot Modernization](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*XQyuYSOx0iofJjvdzRUT3A.png)

**Spring Boot has evolved rapidly. Some practices that were considered “best practice” a few years ago are now deprecated, discouraged, or completely removed.**

If you maintain an older Spring Boot application, there is a good chance your codebase contains patterns that are no longer recommended.

The migration from Spring Boot 2.x to 3.x — and eventually toward 4.x — is not just about changing a version number. Several APIs, configuration patterns, and ecosystem conventions have changed significantly.

Here are some of the most important ones to know.

---

## 1. Stop Using @Autowired Field Injection

For years, this was probably the most common way to inject dependencies:

```java
@Service
public class OrderService {

    @Autowired
    private OrderRepository orderRepo;
    @Autowired
    private PaymentGateway paymentGateway;
}
```

It works, but **constructor injection is the preferred approach**.

### Use constructor injection instead

```java
@Service
public class OrderService {

    private final OrderRepository orderRepo;
    private final PaymentGateway paymentGateway;

    public OrderService(
            OrderRepository orderRepo,
            PaymentGateway paymentGateway) {
        this.orderRepo = orderRepo;
        this.paymentGateway = paymentGateway;
    }
}
```

And if you use Lombok:

```java
@Service
@RequiredArgsConstructor
public class OrderService {

    private final OrderRepository orderRepo;
    private final PaymentGateway paymentGateway;
}
```

### Why is field injection problematic?

There are several reasons:

- Dependencies cannot be `final`.
- Dependencies are hidden from the class constructor.
- Unit testing becomes more difficult (requires reflection or Spring context).
- The class becomes more tightly coupled to the Spring container.
- A class can be instantiated with missing dependencies at runtime.
- Adding more injected fields can make a class grow without making the design problem obvious.

Constructor injection makes dependencies explicit. If a constructor starts requiring ten different dependencies, that’s also a useful architectural signal: **the class may be doing too much.**

---

## 2. Don’t Use @Value for Large Configuration Objects

`@Value` is still useful for injecting a single configuration value:

```java
@Value("${my.service.host}")
private String host;

@Value("${my.service.port}")
private int port;
```

But imagine a service with ten or twenty related configuration properties. Scattering them across individual fields quickly becomes difficult to maintain.

### Prefer @ConfigurationProperties

```java
@Configuration
@ConfigurationProperties(prefix = "my.service")
@Validated
public class MyServiceProperties {

    @NotBlank
    private String host;
    @Min(1)
    @Max(65535)
    private int port;
    @NotNull
    private Duration timeout;

    // Getters and setters (or immutable record)
}
```

This gives you:

- Type-safe configuration binding
- Bean validation (JSR-380)
- Grouped, cohesive configuration
- IDE metadata and autocomplete
- Cleaner configuration management

Instead of having configuration scattered throughout your application, you get a dedicated configuration object.

---

## 3. @Transactional Is Powerful — and Easy to Misuse

`@Transactional` looks simple:

```java
@Transactional
public void processOrder() {
    // ...
}
```

But there are several traps developers should understand.

### Pitfall #1: Using transactions carelessly for read-only operations

If a method only reads data, consider whether a read-only transaction is appropriate:

```java
@Transactional(readOnly = true)
public Order getOrder(Long id) {
    return orderRepository.findById(id)
            .orElseThrow();
}
```

This communicates intent and can allow the underlying persistence infrastructure (e.g., Hibernate dirty checking suppression, replica routing) to optimize accordingly.

### Pitfall #2: Calling transactional methods internally (Proxy Bypass)

Consider:

```java
public void methodA() {
    methodB();
}

@Transactional
public void methodB() {
    // ...
}
```

Spring’s proxy-based AOP does not intercept a self-invocation in the same way as an external call through the Spring proxy. As a result, the transactional behavior you expect will not be applied. This is one of those bugs that can look completely normal during code review.

### Pitfall #3: Putting @Transactional on private methods

Spring’s standard proxy mechanism cannot intercept a private method in the normal proxy-based transaction model:

```java
@Transactional
private void updateDatabase() {
    // Will NOT participate in a transaction!
}
```

Place transactional boundaries on methods that can actually be intercepted (public methods called from external beans).

### Pitfall #4: Catching exceptions and accidentally committing

Consider:

```java
@Transactional
public void process() {
    try {
        // database operations
    } catch (Exception e) {
        // exception swallowed
    }
}
```

If the exception is caught and the transactional method completes normally, the transaction will commit. The application may therefore persist partial or invalid data even though the business operation failed.

### Pitfall #5: Understand rollback rules

Do not assume every exception automatically triggers rollback. By default, Spring only rolls back for unchecked exceptions (`RuntimeException` and `Error`).

If your business logic throws checked exceptions and depends on rollback, configure the transaction accordingly:

```java
@Transactional(rollbackFor = Exception.class)
public void process() throws Exception {
    // ...
}
```

The rollback policy should reflect the application’s exception model rather than being copied blindly.

### Pitfall #6: Don’t casually use REQUIRES_NEW

`REQUIRES_NEW` suspends the current transaction and starts another transaction. That can be useful in specific cases (e.g., writing an independent audit log entry), but it also introduces additional transactional complexity, consumes two database connections simultaneously, and can result in partial commits.

Use it because the business semantics genuinely require an independent transaction — not simply because it seems safer.

---

## 4. System.out.println() Doesn't Belong in Production Logging

We’ve all used:

```java
System.out.println("User logged in");
```

It’s fine for algorithm challenges or quick experiments. But it is not a production logging solution.

`System.out.println()` lacks:

- Log levels (DEBUG, INFO, WARN, ERROR)
- Structured configuration and outputs (JSON, masking)
- Timestamps
- Thread and MDC contextual information
- Integration with Spring Boot’s logging infrastructure (Logback/Log4j2)
- Proper production log management and shipping

Instead, use SLF4J:

```java
@Slf4j
public class MyService {
    public void login(Long userId, String ip) {
        log.info("User {} logged in from {}", userId, ip);
    }
}
```

### Prefer parameterized logging

Use:

```java
log.info("User {} logged in", userId);
```

rather than:

```java
log.info("User " + userId + " logged in");
```

Parameterized logging avoids unnecessary string concatenation and heap allocations when the corresponding log level is disabled.

---

## 5. WebSecurityConfigurerAdapter Is Gone

This is one of the major Spring Security changes. Older applications often contain:

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig extends WebSecurityConfigurerAdapter {

    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http.authorizeRequests()
            .antMatchers("/public/**").permitAll()
            .anyRequest().authenticated();
    }
}
```

`WebSecurityConfigurerAdapter` was deprecated in Spring Security 5.7 and completely removed in Spring Security 6.0.

The modern approach is to define a `SecurityFilterChain` bean:

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.authorizeHttpRequests(auth -> auth
            .requestMatchers("/public/**").permitAll()
            .anyRequest().authenticated()
        );
        return http.build();
    }
}
```

Notice the API changes as well:

```text
authorizeRequests()       → authorizeHttpRequests()
antMatchers()             → requestMatchers()
```

If you’re upgrading an older Spring Security application, this is one of the first areas you’ll encounter.

---

## 6. RestTemplate Is Entering the Legacy Zone

`RestTemplate` has been one of the standard ways to make HTTP calls from Spring applications for years. But the Spring ecosystem is moving toward newer HTTP client APIs.

The recommended modern alternative for synchronous HTTP calls is:

### RestClient

```java
RestClient restClient = RestClient.create();

User user = restClient.get()
        .uri("https://api.example.com/users/{id}", 1)
        .retrieve()
        .body(User.class);
```

The API provides a modern fluent programming model while remaining synchronous.

For reactive applications and streaming scenarios, **WebClient** remains the appropriate choice.

> **Important architectural takeaway**: Don’t introduce reactive programming merely because it is newer. Choose the HTTP client based on the application’s actual concurrency and I/O requirements.

---

## 7. WebMvcConfigurerAdapter Is Unnecessary

Older Spring MVC applications often contained:

```java
public class WebConfig extends WebMvcConfigurerAdapter {
}
```

This adapter was deprecated because Java 8 introduced default interface methods. Today, simply implement `WebMvcConfigurer`:

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    // Override only the methods you need
}
```

### Be careful with @EnableWebMvc

In a typical Spring Boot application, adding:

```java
@EnableWebMvc
```

can disable Spring Boot’s MVC auto-configuration. That can unexpectedly break:

- Static resource handling
- Default message converters
- Formatters
- Other auto-configured MVC behaviors

Do not add `@EnableWebMvc` unless you genuinely need to take total control of MVC configuration.

---

## 8. javax.* → jakarta.* Namespace Migration

One of the biggest ecosystem-level changes arrived with Spring Boot 3. The Java EE namespace moved from `javax.*` to `jakarta.*`:

```text
javax.servlet     → jakarta.servlet
javax.persistence → jakarta.persistence
javax.validation  → jakarta.validation
javax.annotation  → jakarta.annotation
javax.transaction → jakarta.transaction
javax.mail        → jakarta.mail
```

This isn’t just a cosmetic import change. Your third-party dependencies also need to be compatible with the Jakarta EE ecosystem; otherwise, you will encounter classpath and runtime compatibility problems.

For large codebases, automated refactoring tools such as OpenRewrite can help automate this migration.

---

## 9. JUnit 4 Patterns Are Giving Way to JUnit 5

Older Spring tests often look like:

```java
@RunWith(SpringRunner.class)
@SpringBootTest
public class UserServiceTest {
}
```

With JUnit 5, the Spring extension integration is built into `@SpringBootTest`, so you simply write:

```java
@SpringBootTest
class UserServiceTest {
}
```

Classes and methods no longer require `public` visibility, reducing boilerplate across the test suite.

---

## 10. spring.factories → AutoConfiguration.imports

If you’ve created a custom Spring Boot starter, this migration matters.

Older automatic configuration registration used:

```text
META-INF/spring.factories
```

Modern Spring Boot uses:

```text
META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
```

This migration began in Spring Boot 2.7 and is required in Spring Boot 3.x+ for custom starters.

---

## 11. Use ProblemDetail for Standardized Error Responses

Many older applications return custom maps from exception handlers:

```java
return Map.of("error", "Something went wrong");
```

Spring 6 and Spring Boot 3 introduced support for **ProblemDetail**, based on RFC 7807.

This gives APIs a standardized structure for representing errors and makes error responses easier for clients to consume consistently:

```json
{
  "type": "https://api.example.com/errors/not-found",
  "title": "Resource Not Found",
  "status": 404,
  "detail": "Order 12345 was not found",
  "instance": "/orders/12345"
}
```

Instead of every service inventing its own error-response format, applications expose a predictable contract across distributed systems and microservices.

---

## 12. Watch Out for the JPA N+1 Problem

This isn’t a deprecated API, but it remains one of the most common performance killers in Spring/JPA applications.

Suppose you load a list of orders and iterate over each order’s items:

```sql
SELECT * FROM orders;
SELECT * FROM items WHERE order_id = 1;
SELECT * FROM items WHERE order_id = 2;
SELECT * FROM items WHERE order_id = 3;
-- ... N additional round-trips!
```

One query becomes many. That’s the classic **N+1 query problem**.

### Solution 1: JOIN FETCH

```java
@Query("""
    SELECT o
    FROM Order o
    JOIN FETCH o.items
""")
List<Order> findOrdersWithItems();
```

### Solution 2: @EntityGraph

```java
@EntityGraph(attributePaths = "items")
List<Order> findAll();
```

### Solution 3: Hibernate @BatchSize

Batching child collection loads across batches (e.g., `@BatchSize(size = 25)`) reduces the round trips from $N$ to $\lceil N / 25 \rceil$.

> **Key takeaway**: Never assume `LAZY` loading automatically means efficient database access. Always inspect and test the SQL generated by your ORM.

---

## 13. Virtual Threads Change the Concurrency Conversation

Spring Boot 3.2+ supports Java 21 virtual threads, enabled with a single property:

```properties
spring.threads.virtual.enabled=true
```

This allows traditional Spring MVC applications on Tomcat to handle tens of thousands of concurrent I/O requests without adopting reactive programming.

> **Architectural principle**: *You don’t need WebFlux simply because your application has high concurrency.*

For many workloads, **Spring MVC + virtual threads** provides a significantly simpler imperative programming model, clearer stack traces, and easier debugging. Reserve reactive programming for genuine streaming pipelines.

---

## The Bigger Architectural Lesson

The most interesting part of Spring Boot’s evolution isn’t any individual deprecated API. It’s the architectural direction of the ecosystem:

Spring is systematically eliminating patterns that:

- Hide dependencies
- Create unnecessary boilerplate
- Depend heavily on runtime reflection and framework-specific magic
- Complicate testing
- Scatter configuration
- Encourage accidental complexity

Technical debt doesn’t always look like broken code. Sometimes it looks like perfectly working code using an idiom that the framework and industry have outgrown.

---

## A Practical Upgrade Checklist

When preparing an older Spring Boot codebase for modernization:

1. Replace field injection with constructor injection.
2. Group related configuration using `@ConfigurationProperties`.
3. Audit all `@Transactional` methods for self-invocation, visibility, and rollback rules.
4. Replace production `System.out.println()` with parameterized SLF4J logging.
5. Replace `WebSecurityConfigurerAdapter` with `SecurityFilterChain` beans.
6. Migrate `antMatchers()` to `requestMatchers()`.
7. Evaluate migrating `RestTemplate` to `RestClient`.
8. Replace `WebMvcConfigurerAdapter` with `WebMvcConfigurer` and audit `@EnableWebMvc`.
9. Migrate `javax.*` imports to `jakarta.*`.
10. Modernize JUnit 4 test runners to JUnit 5 `@SpringBootTest`.
11. Migrate custom starter `spring.factories` to `AutoConfiguration.imports`.
12. Adopt `ProblemDetail` (RFC 7807) for REST API error responses.
13. Audit JPA relationships for N+1 queries using `JOIN FETCH` or `@EntityGraph`.
14. Evaluate virtual threads (`spring.threads.virtual.enabled=true`) for I/O-bound services.

---

## Final Thought

The goal is not to blindly rewrite working code every time a new version appears.

Instead, understand **why** an API was replaced, what architectural benefit the new approach provides, and how modern idioms reduce cognitive load and operational risk.

**The best legacy code isn’t code that never changes. It’s code that can cleanly evolve when the ecosystem around it does.**
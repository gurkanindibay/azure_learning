---
type: Article
title: "Defensive Coding Approach"
description: "Fifteen practical defensive coding techniques for writing resilient, secure, and maintainable software — covering input validation, assertions, fail-safe mechanisms, immutable data structures, and dependency management."
timestamp: 2026-06-25T00:00:00Z
---

> **Source**: [Sophia Dizon on Medium](https://medium.com/@sophiadizon/defensive-coding-approach-43bf3f3c007d) · Published 2024-01-02

# Defensive Coding Approach

**a.k.a *Defensive Programming***, essentially writing a code with the assumption that it would somehow fail

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*7621Q0uls9dtPXzFGo0T0Q.jpeg)

The approach would seem weird but in software engineering it is possible that there are some instances that are not handled and could result to a bug or an issue. For example, an unverified user accesses a page meant for authenticated individuals.

![](https://miro.medium.com/v2/resize:fit:1100/format:webp/1*LE39v_RoUxlYWdkjbj-OqA.png)

There are a lot of possible actions that a system user could do in your application. Therefore, having this approach in mind would help in lessening potential issues

> Prevention is better than cure (Desiderius Erasmus — 1500)

Here are some ideas and best practices for implementing defensive coding:

## 01 Input Validation

Ensure that you validate all user inputs and they meet the expected criteria. You can use regex or specific validation functions for data types. Don’t forget to sanitize and escape characters to prevent injection attacks

## 02 Error Handling

You can implement a comprehensive error-handling throughout your code. If the flow is not expected throw an exception. You can implement try-catch blocks to gracefully handle exceptions.

Log errors with sufficient details for debugging.

## 03 Boundary Checks

Check list/arrays and string bounds to prevent buffer overflows. Always validate indices and pointers before accessing arrays or objects.

## 04 Assertions

If your plaform have assertion mechanism you can use it to check for conditions that should always be true during development. You can enable assertions during testing and development and **disable** those in production.

## 05 Default Values

Always provide default values for variables, especially when dealing with user inputs or external data. You should avoid relying on implicit assumptions about default behavior.

## 06 Secure Coding Practices

Apply secure coding practices to prevent vulnerabilities like SQL injection, cross-site scripting, etc. Use parameterized queries for database interactions.

## 07 Code Reviews

If your team have an established coding standards/guidelines, make sure to follow-it. Thorough code reviews are important to catch potential issues and ensure adherence to coding standards, it also lessens potential technical debt.

This practice encourages a culture of constructive criticism and learning

## 08 Logging and Monitoring

Implement robust logging mechanism to record relevant information during normal operation and errors. You can set up monitoring application to detect and respond to unexpected behavior. Remember in Production environment we can only rely on logs (and without logs it is difficult to know what went wrong!)

There are tools like Real User Monitoring Apps that could help monitor your users but ofcourse there are some data privacy concerns but these tools would help you understand what your users are trying to accomplish

## 09 Immutable Data Structures

Use immutable data structures where possible to reduce the risk of unintended modifications.

For example favor *const* or *readonly* declarations for variables. With this you enhance the predictability and maintainability of your code, making it less prone to unintended modifications and easier to reason about. This is particularly important in scenarios where multiple parts of the codebase may interact with the same data.

## 10 Documentation

Clearly document your code, including assumptions, constraints, and potential issues. Provide inline comments for complex logic or non-trivial algorithms. It would be helpful for other developers to easily grasp the context/purpose of the code

## 11 Dependency Management

Keep the dependencies up-to-date to leverage bug fixes and security patches. Regularly audit and assess third-party libraries for security vulnerabilities.

## 12 Unit Testing

Write unit tests to cover different scenarios and edge cases. You can use test-driven development (TDD) approach to ensure code correctness from the start. This would add additional development efforts but if you are implementing complex processes with a lots of scenarios, TDD is beneficial

## 13 Graceful Degradation

Design your systems to gracefully degrade in the face of errors or partial failures. You can provide fallback mechanisms to handle unexpected situations, simplest example would be adding CSS vendor prefixes

## 14 Fail-Safe Mechanisms

Fail-safe mechanisms are designed to ensure that critical operations or transactions are completed even in the presence of errors or failures.

For example, an **unexpected error** was encountered when processing records in batch, instead of ending the entire process you can perhaps create a processing status for each record and set the record processing status to FAILED then proceed with other records in Pending state.

## 15 Continuous Improvement

Regularly revisit and improve your code based on feedback, evolving requirements, and lessons learned from incidents.

## —

**That’s All! Happy Coding!**
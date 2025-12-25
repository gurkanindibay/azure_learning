# 11. Architectural Qualities (Non-Functional)

This section covers non-functional requirements that apply across all architecture types. The quality attributes are compiled from multiple industry standards and frameworks:

- **ISO/IEC 25010** - Software Product Quality Model
- **SEI (Software Engineering Institute)** - Software Architecture in Practice
- **NETAS/Microsoft** - Design Fundamentals Quality Attributes

---

## Quality Attributes by Category

### 1. Functional Suitability *(ISO)*

Degree to which a product or system provides functions that meet stated and implied needs when used under specified conditions.

- **Functional Completeness** - Degree to which the set of functions covers all the specified tasks and user objectives
- **Functional Correctness** - Degree to which a product or system provides the correct results with the needed degree of precision
- **Functional Appropriateness** - Degree to which the functions facilitate the accomplishment of specified tasks and objectives

---

### 2. Performance Efficiency *(ISO, SEI, NETAS)*

Performance relative to the amount of resources used under stated conditions.

- **Time Behaviour** - Degree to which the response and processing times and throughput rates meet requirements
- **Resource Utilization** - Degree to which the amounts and types of resources used meet requirements
- **Capacity** - Degree to which the maximum limits of a product or system parameter meet requirements (e.g., number of concurrent users, transaction throughput, database size)

---

### 3. Compatibility *(ISO)*

Degree to which a product, system or component can exchange information with other products, systems or components, and/or perform its required functions while sharing the same hardware or software environment.

- **Co-existence** - Degree to which a product can perform its required functions efficiently while sharing a common environment and resources with other products
- **Interoperability** - Degree to which two or more systems, products or components can exchange information and use the information that has been exchanged

---

### 4. Usability *(ISO, SEI, NETAS)*

Degree to which a product or system can be used by specified users to achieve specified goals with effectiveness, efficiency and satisfaction in a specified context of use.

- **Appropriateness Recognizability** - Degree to which users can recognize whether a product or system is appropriate for their needs
- **Learnability** - Degree to which users can achieve specified goals of learning to use the product or system
- **Predictability** - Property to forecast the consequences of a user action given the current state of the system
- **Operability** - Degree to which a product or system has attributes that make it easy to operate and control
- **User Error Protection** - Degree to which a system protects users against making errors
- **User Interface Aesthetics** - Degree to which a user interface enables pleasing and satisfying interaction for the user
- **Accessibility** - Degree to which a product or system can be used by people with the widest range of characteristics and capabilities

---

### 5. Reliability *(ISO, SEI, NETAS)*

Degree to which a system, product or component performs specified functions under specified conditions for a specified period of time.

- **Maturity** - Degree to which a system meets needs for reliability under normal operation
- **Availability** - Degree to which a system is operational and accessible when required for use
- **Fault Tolerance** - Degree to which a system operates as intended despite the presence of hardware or software faults
- **Recoverability** - Degree to which a product or system can recover data and re-establish desired state after an interruption or failure
- **Self-Sustainability** - A system is self-sustaining if it can maintain itself by independent effort

---

### 6. Security *(ISO, SEI, NETAS)*

Degree to which a product or system protects information and data so that persons or other products or systems have the degree of data access appropriate to their types and levels of authorization.

- **Confidentiality** - Degree to which data are accessible only to those authorized to have access
- **Integrity** - Degree to which a system prevents unauthorized access to, or modification of, computer programs or data
- **Non-repudiation** - Degree to which actions or events can be proven to have taken place, so that they cannot be repudiated later
- **Accountability** - Degree to which the actions of an entity can be traced uniquely to the entity
- **Authenticity** - Degree to which the identity of a subject or resource can be proved to be the one claimed

---

### 7. Safety *(SEI)*

Software's ability to avoid entering states that cause or lead to damage, injury, or loss of life to actors in the software's environment, and to recover and limit the damage when it does enter into bad states.

> **Note:** Safety is not the same as reliability. A system can be reliable (consistent with its specification) but still unsafe (for example, when the specification ignores conditions leading to unsafe action). Tactics for safety overlap with those for availability - both comprise tactics to prevent failures and to detect and recover from failures.

---

### 8. Maintainability *(ISO, NETAS)*

Degree of effectiveness and efficiency with which a product or system can be modified by the intended maintainers.

- **Modularity** - Degree to which a system is composed of discrete components such that a change to one component has minimal impact on other components
- **Reusability** - Degree to which an asset can be used in more than one system, or in building other assets
- **Analysability** - Degree of effectiveness and efficiency with which it is possible to assess the impact of an intended change or diagnose deficiencies
- **Modifiability** - Degree to which a product or system can be effectively and efficiently modified without introducing defects or degrading existing product quality
- **Testability** - Degree of effectiveness and efficiency with which test criteria can be established and tests can be performed

---

### 9. Portability *(ISO, SEI)*

Degree of effectiveness and efficiency with which a system, product or component can be transferred from one hardware, software or other operational or usage environment to another.

- **Adaptability** - Degree to which a product or system can effectively and efficiently be adapted for different or evolving hardware, software or other operational environments
- **Installability** - Degree of effectiveness and efficiency with which a product or system can be successfully installed and/or uninstalled in a specified environment
- **Replaceability** - Degree to which a product can replace another specified software product for the same purpose in the same environment

---

### 10. Scalability *(SEI, NETAS)*

Ability of a system to either handle increases in load without impact on the performance of the system, or the ability to be readily enlarged.

---

### 11. Deployability *(SEI, NETAS)*

Concerned with how an executable arrives at a host platform and how it is subsequently invoked.

**Key considerations:**
- How does it arrive at its host (push vs. pull updates)?
- How is it integrated into an existing system?

---

### 12. Manageability *(NETAS)*

Defines how easy it is for system administrators to manage the application through sufficient and useful instrumentation exposed for monitoring, debugging, and performance tuning.

- **Upgradability** - Capability of being improved in functionality by the addition or replacement of components
- **Configurability** - Defines how the system can be configured

---

### 13. Observability

Ability to understand the internal state of a system by examining its external outputs. Observability goes beyond monitoring by enabling deep insights into system behavior.

**Three Pillars of Observability:**
- **Metrics** - Numerical measurements collected over time (e.g., CPU usage, request latency, error rates)
- **Logs** - Timestamped records of discrete events that occurred within a system
- **Traces** - Records of requests as they flow through distributed system components

**Key capabilities:**
- Root cause analysis
- Performance profiling
- Anomaly detection
- Distributed tracing across microservices

---

### 14. Monitorability *(SEI, NETAS)*

Ability of operations staff to monitor the system while it is executing.

**Items to monitor:**
- Queue lengths
- Average transaction processing time
- Health of various components
- Potential problems and visibility to operators
- Corrective action capabilities

> **Note:** Monitorability is a subset of Observability, focused on predefined metrics and alerts.

---

### 15. Supportability *(NETAS)*

Ability of the system to provide information helpful for identifying and resolving issues when it fails to work correctly.

---

### 15. Sensibility *(NETAS)*

Quality related to data accuracy and correctness.

- **Accuracy** - Closeness of a measured value to a standard or known value
- **Precision** - Closeness of two or more measurements to each other (independent of accuracy)
- **Correctness** - Algorithm is correct with respect to a specification

---

### 16. Mobility *(SEI, NETAS)*

Deals with the problems of movement and affordances of a platform.

**Considerations:**
- Size and type of display
- Type of input devices
- Availability and volume of bandwidth
- Battery life

---

### 17. Variability *(SEI)*

Ability of a core asset to adapt to usages in different product contexts that are within the product line scope.

---

### 18. Development Distributability *(SEI, NETAS)*

Quality of designing software to support distributed software development.

> **Key principle:** The system should be designed so that coordination among globally distributed teams is minimized - both for code and data model.

---

### 19. Conceptual Integrity *(NETAS - Design Quality)*

Defines the consistency and coherence of the overall design.

**Includes:**
- Way components or modules are designed
- Coding style
- Variable naming conventions

---

### 21. Additional Quality Considerations

- **Compliance & Regulatory** - Meeting legal and industry requirements
- **Sustainability (Green IT)** - Environmental impact considerations
- **Extensibility** - Ability to add new features without significant rework

---

## Quality Attributes Summary by Source

| Category | ISO/IEC 25010 | SEI | NETAS |
|----------|---------------|-----|-------|
| Functional Suitability | ✓ | | |
| Performance Efficiency | ✓ | ✓ | ✓ |
| Compatibility | ✓ | ✓ | ✓ |
| Usability | ✓ | ✓ | ✓ |
| Reliability | ✓ | | ✓ |
| Security | ✓ | ✓ | ✓ |
| Safety | | ✓ | |
| Maintainability | ✓ | ✓ | ✓ |
| Portability | ✓ | ✓ | |
| Scalability | | ✓ | ✓ |
| Deployability | | ✓ | ✓ |
| Manageability | | | ✓ |
| Observability | | | |
| Monitorability | | ✓ | ✓ |
| Supportability | | | ✓ |
| Sensibility | | | ✓ |
| Mobility | | ✓ | ✓ |
| Variability | | ✓ | |
| Dev. Distributability | | ✓ | ✓ |
| Conceptual Integrity | | | ✓ |

---

## Cross-Cutting Concerns

These qualities influence decisions across all architecture layers:

- **Conceptual** → How capabilities are structured
- **Logical** → How components are designed
- **Physical** → How technologies are selected
- **Runtime** → How systems are operated

---

## References

- ISO/IEC 25010:2011 - Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE)
- Software Architecture in Practice, 3rd Edition (SEI)
- Microsoft Design Fundamentals Quality Attributes
- Wikipedia - List of System Quality Attributes

---

## Related

- [Architecture Taxonomy Reference](../10-practicality-taxonomy/architecture_taxonomy_reference.md)
- [Reliability Patterns](../07-reliability-performance-operations/reliability-performance-operations-patterns.md)

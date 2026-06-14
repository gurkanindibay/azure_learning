# 11. Architectural Qualities (Non-Functional)

This section covers non-functional requirements that apply across all architecture types. The quality attributes are compiled from multiple industry standards and frameworks:

- **ISO/IEC 25010** - Software Product Quality Model
- **SEI (Software Engineering Institute)** - Software Architecture in Practice
- **NETAS/Microsoft** - Design Fundamentals Quality Attributes

---

## Quality Attributes by Category

### 1. Functional Suitability *(ISO)*

> **Also known as:** Functionality, Feature Completeness, Functional Adequacy

Degree to which a product or system provides functions that meet stated and implied needs when used under specified conditions.

- **Functional Completeness** *(aka Feature Coverage)* - Degree to which the set of functions covers all the specified tasks and user objectives
- **Functional Correctness** *(aka Accuracy)* - Degree to which a product or system provides the correct results with the needed degree of precision
- **Functional Appropriateness** *(aka Suitability)* - Degree to which the functions facilitate the accomplishment of specified tasks and objectives

---

### 2. Performance Efficiency *(ISO, SEI, NETAS)*

> **Also known as:** Performance, Efficiency, Speed, Responsiveness

Performance relative to the amount of resources used under stated conditions.

- **Time Behaviour** *(aka Latency, Response Time, Throughput)* - Degree to which the response and processing times and throughput rates meet requirements
- **Resource Utilization** *(aka Resource Efficiency)* - Degree to which the amounts and types of resources used meet requirements
- **Capacity** *(aka Load Capacity, Throughput Capacity)* - Degree to which the maximum limits of a product or system parameter meet requirements (e.g., number of concurrent users, transaction throughput, database size)

---

### 3. Compatibility *(ISO)*

> **Also known as:** Interchangeability, Integration Capability

Degree to which a product, system or component can exchange information with other products, systems or components, and/or perform its required functions while sharing the same hardware or software environment.

- **Co-existence** *(aka Cohabitation, Resource Sharing)* - Degree to which a product can perform its required functions efficiently while sharing a common environment and resources with other products
- **Interoperability** *(aka Integration, Interconnectivity, API Compatibility)* - Degree to which two or more systems, products or components can exchange information and use the information that has been exchanged

---

### 4. Usability *(ISO, SEI, NETAS)*

> **Also known as:** User Experience (UX), Ease of Use, User-Friendliness, Ergonomics

Degree to which a product or system can be used by specified users to achieve specified goals with effectiveness, efficiency and satisfaction in a specified context of use.

- **Appropriateness Recognizability** *(aka Discoverability, Self-Descriptiveness)* - Degree to which users can recognize whether a product or system is appropriate for their needs
- **Learnability** *(aka Ease of Learning, Intuitiveness)* - Degree to which users can achieve specified goals of learning to use the product or system
- **Predictability** *(aka Consistency, Expected Behavior)* - Property to forecast the consequences of a user action given the current state of the system
- **Operability** *(aka Controllability, Ease of Operation)* - Degree to which a product or system has attributes that make it easy to operate and control
- **User Error Protection** *(aka Error Prevention, Fault Tolerance for Users)* - Degree to which a system protects users against making errors
- **User Interface Aesthetics** *(aka Visual Design, Look and Feel)* - Degree to which a user interface enables pleasing and satisfying interaction for the user
- **Accessibility** *(aka Inclusive Design, A11y, Universal Design)* - Degree to which a product or system can be used by people with the widest range of characteristics and capabilities

---

### 5. Reliability *(ISO, SEI, NETAS)*

> **Also known as:** Dependability, Resilience, Robustness, Stability

Degree to which a system, product or component performs specified functions under specified conditions for a specified period of time.

- **Maturity** *(aka Stability, Production-Readiness)* - Degree to which a system meets needs for reliability under normal operation
- **Availability** *(aka Uptime, High Availability - HA)* - Degree to which a system is operational and accessible when required for use
- **Fault Tolerance** *(aka Resilience, Robustness, Graceful Degradation)* - Degree to which a system operates as intended despite the presence of hardware or software faults
- **Recoverability** *(aka Disaster Recovery - DR, Business Continuity, Restore Capability)* - Degree to which a product or system can recover data and re-establish desired state after an interruption or failure
- **Self-Sustainability** *(aka Self-Healing, Autonomic Computing)* - A system is self-sustaining if it can maintain itself by independent effort

---

### 6. Security *(ISO, SEI, NETAS)*

> **Also known as:** Information Security, InfoSec, Cybersecurity, Data Protection

Degree to which a product or system protects information and data so that persons or other products or systems have the degree of data access appropriate to their types and levels of authorization.

- **Confidentiality** *(CIA Triad - C, Privacy, Data Secrecy)* - Degree to which data are accessible only to those authorized to have access
- **Integrity** *(CIA Triad - I, Data Integrity, Tamper-Proofing)* - Degree to which a system prevents unauthorized access to, or modification of, computer programs or data
- **Non-repudiation** *(aka Undeniability, Proof of Action)* - Degree to which actions or events can be proven to have taken place, so that they cannot be repudiated later
- **Accountability** *(aka Auditability, Traceability)* - Degree to which the actions of an entity can be traced uniquely to the entity
- **Authenticity** *(aka Authentication, Identity Verification)* - Degree to which the identity of a subject or resource can be proved to be the one claimed

---

### 7. Safety *(SEI)*

> **Also known as:** System Safety, Hazard Avoidance, Risk Mitigation, Harm Prevention

Software's ability to avoid entering states that cause or lead to damage, injury, or loss of life to actors in the software's environment, and to recover and limit the damage when it does enter into bad states.

> **Note:** Safety is not the same as reliability. A system can be reliable (consistent with its specification) but still unsafe (for example, when the specification ignores conditions leading to unsafe action). Tactics for safety overlap with those for availability - both comprise tactics to prevent failures and to detect and recover from failures.

---

### 8. Maintainability *(ISO, NETAS)*

> **Also known as:** Serviceability, Supportability, Evolvability, Technical Debt Management

Degree of effectiveness and efficiency with which a product or system can be modified by the intended maintainers.

- **Modularity** *(aka Loose Coupling, Separation of Concerns, Componentization)* - Degree to which a system is composed of discrete components such that a change to one component has minimal impact on other components
- **Reusability** *(aka DRY - Don't Repeat Yourself, Component Reuse)* - Degree to which an asset can be used in more than one system, or in building other assets
- **Analysability** *(aka Understandability, Comprehensibility, Code Readability)* - Degree of effectiveness and efficiency with which it is possible to assess the impact of an intended change or diagnose deficiencies
- **Modifiability** *(aka Changeability, Flexibility, Adaptability)* - Degree to which a product or system can be effectively and efficiently modified without introducing defects or degrading existing product quality
- **Testability** *(aka Verifiability, Test Coverage Capability)* - Degree of effectiveness and efficiency with which test criteria can be established and tests can be performed

---

### 9. Portability *(ISO, SEI)*

> **Also known as:** Platform Independence, Cross-Platform Compatibility, Transferability

Degree of effectiveness and efficiency with which a system, product or component can be transferred from one hardware, software or other operational or usage environment to another.

- **Adaptability** *(aka Flexibility, Environmental Flexibility, Multi-Platform Support)* - Degree to which a product or system can effectively and efficiently be adapted for different or evolving hardware, software or other operational environments
- **Installability** *(aka Ease of Installation, Deployment Simplicity)* - Degree of effectiveness and efficiency with which a product or system can be successfully installed and/or uninstalled in a specified environment
- **Replaceability** *(aka Substitutability, Interchangeability, Vendor Independence)* - Degree to which a product can replace another specified software product for the same purpose in the same environment

---

### 10. Scalability *(SEI, NETAS)*

> **Also known as:** Elasticity (Cloud), Extensibility, Growth Capacity, Load Handling

Ability of a system to either handle increases in load without impact on the performance of the system, or the ability to be readily enlarged.

**Types:**
- **Horizontal Scalability** *(aka Scale-Out)* - Adding more instances/nodes
- **Vertical Scalability** *(aka Scale-Up)* - Adding more resources to existing instances

---

### 11. Deployability *(SEI, NETAS)*

> **Also known as:** Release Management, Continuous Deployment (CD), Delivery Capability

Concerned with how an executable arrives at a host platform and how it is subsequently invoked.

**Key considerations:**
- How does it arrive at its host (push vs. pull updates)?
- How is it integrated into an existing system?

---

### 12. Manageability *(NETAS)*

> **Also known as:** Administrability, Operability, Operations Friendliness, DevOps Readiness

Defines how easy it is for system administrators to manage the application through sufficient and useful instrumentation exposed for monitoring, debugging, and performance tuning.

- **Upgradability** *(aka Updateability, Patch Management)* - Capability of being improved in functionality by the addition or replacement of components
- **Configurability** *(aka Customizability, Parameterization)* - Defines how the system can be configured

---

### 13. Observability

> **Also known as:** System Visibility, Telemetry, Insights, Introspection

Ability to understand the internal state of a system by examining its external outputs. Observability goes beyond monitoring by enabling deep insights into system behavior.

**Three Pillars of Observability:**
- **Metrics** *(aka KPIs, Measurements, Telemetry Data)* - Numerical measurements collected over time (e.g., CPU usage, request latency, error rates)
- **Logs** *(aka Event Logs, Audit Trails, Application Logs)* - Timestamped records of discrete events that occurred within a system
- **Traces** *(aka Distributed Tracing, Request Tracing, Spans)* - Records of requests as they flow through distributed system components

**Key capabilities:**
- Root cause analysis
- Performance profiling
- Anomaly detection
- Distributed tracing across microservices

---

### 14. Monitorability *(SEI, NETAS)*

> **Also known as:** Monitoring Capability, Health Monitoring, System Monitoring, Watchability

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

> **Also known as:** Serviceability, Diagnosability, Troubleshootability, Help Desk Friendliness

Ability of the system to provide information helpful for identifying and resolving issues when it fails to work correctly.

---

### 16. Sensibility *(NETAS)*

> **Also known as:** Data Quality, Information Quality, Data Fidelity

Quality related to data accuracy and correctness.

- **Accuracy** *(aka Exactness, Truthfulness)* - Closeness of a measured value to a standard or known value
- **Precision** *(aka Repeatability, Consistency)* - Closeness of two or more measurements to each other (independent of accuracy)
- **Correctness** *(aka Validity, Algorithmic Correctness)* - Algorithm is correct with respect to a specification

---

### 17. Mobility *(SEI, NETAS)*

> **Also known as:** Mobile Readiness, Mobile-First, Responsive Design, Cross-Device Compatibility

Deals with the problems of movement and affordances of a platform.

**Considerations:**
- Size and type of display
- Type of input devices
- Availability and volume of bandwidth
- Battery life

---

### 18. Variability *(SEI)*

> **Also known as:** Customizability, Configurability, Product Line Flexibility, Feature Toggling

Ability of a core asset to adapt to usages in different product contexts that are within the product line scope.

---

### 19. Development Distributability *(SEI, NETAS)*

> **Also known as:** Team Scalability, Distributed Development Support, Conway's Law Alignment

Quality of designing software to support distributed software development.

> **Key principle:** The system should be designed so that coordination among globally distributed teams is minimized - both for code and data model.

---

### 20. Conceptual Integrity *(NETAS - Design Quality)*
> **Also known as:** Architectural Consistency, Design Coherence, Uniformity, Single Vision
Defines the consistency and coherence of the overall design.

**Includes:**
- Way components or modules are designed
- Coding style
- Variable naming conventions

---

### 21. Additional Quality Considerations

- **Compliance & Regulatory** *(aka Governance, Legal Compliance, Audit Readiness)* - Meeting legal and industry requirements
- **Sustainability (Green IT)** *(aka Environmental Efficiency, Carbon Footprint, Energy Efficiency)* - Environmental impact considerations
- **Extensibility** *(aka Pluggability, Open for Extension, Plugin Architecture)* - Ability to add new features without significant rework

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

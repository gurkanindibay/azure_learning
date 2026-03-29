# Azure API Management — Policy Inheritance and `<base />` Element

## Table of Contents

- [1. Overview](#1-overview)
- [2. Default Policy Execution Order](#2-default-policy-execution-order)
- [3. Purpose of the `<base />` Element](#3-purpose-of-the-base--element)
  - [Definition](#definition)
- [4. Example of Inherited Policies](#4-example-of-inherited-policies)
- [5. Operation-Level Policy Using `<base />`](#5-operation-level-policy-using-base-)
- [6. Final Execution Order](#6-final-execution-order)
- [7. Visual Representation](#7-visual-representation)
- [8. Key Takeaways](#8-key-takeaways)

## 1. Overview

Azure API Management (APIM) allows policies to be defined at multiple scopes:

*   Global
*   Product
*   API
*   Operation

Policies at lower scopes automatically inherit policies defined at higher scopes unless explicitly overridden.

The `<base />` element gives you precise control over the order and location of inherited policy execution.

## 2. Default Policy Execution Order

By default, APIM merges policies in this order:

> Global → Product → API → Operation

If the operation policy does not contain `<base />`, all inherited policies are inserted at the beginning of the inbound pipeline.

## 3. Purpose of the `<base />` Element

The `<base />` element:

*   Inherits all policies defined at higher scopes.
*   Injects them at the exact position where `<base />` is placed.
*   Enables deterministic ordering between custom (local) policies and inherited ones.

### Definition

> "<base /> inherits parent policies and inserts them at the element's position."

## 4. Example of Inherited Policies

### Global Policy
```xml
<policies>
  <inbound>
    <set-header name="X-Global" exists-action="override">
      <value>GlobalPolicy</value>
    </set-header>
  </inbound>
</policies>
```

### Product Policy
```xml
<policies>
  <inbound>
    <set-header name="X-Product" exists-action="override">
      <value>PremiumProductPolicy</value>
    </set-header>
  </inbound>
</policies>
```

### API Policy
```xml
<policies>
  <inbound>
    <set-header name="X-API" exists-action="override">
      <value>OrdersApiPolicy</value>
    </set-header>
  </inbound>
</policies>
```

## 5. Operation-Level Policy Using `<base />`

```xml
<policies>
  <inbound>

    <!-- Operation policy BEFORE inherited content -->
    <log-to-eventhub>Operation: Before base</log-to-eventhub>

    <!-- Inherited policies injected here -->
    <base />

    <!-- Operation policy AFTER inherited content -->
    <set-header name="X-Operation" exists-action="override">
      <value>OperationPolicy</value>
    </set-header>

  </inbound>
</policies>
```

## 6. Final Execution Order

1.  **Operation policy (before `<base />`)**
    *   `log-to-eventhub: Operation: Before base`

2.  **Inherited policies inserted via `<base />`**

    *Order:*
    *   Global policy
    *   Product policy
    *   API policy

    *Injected sequence:*
    ```text
    set-header X-Global = GlobalPolicy
    set-header X-Product = PremiumProductPolicy
    set-header X-API    = OrdersApiPolicy
    ```

3.  **Operation policy (after `<base />`)**
    *   `set-header X-Operation = OperationPolicy`

## 7. Visual Representation

```text
Operation Policy (before <base />)
         ↓
----- <base /> -----
1. Global Policy
2. Product Policy
3. API Policy
--------------------
         ↓
Operation Policy (after <base />)
```

## 8. Key Takeaways

*   `<base />` is used to override the default inheritance placement.
*   Without `<base />`, inherited policies always run first.
*   With `<base />`, inherited policies run exactly where you place the tag.
*   It provides full control over policy ordering in complex APIM designs.
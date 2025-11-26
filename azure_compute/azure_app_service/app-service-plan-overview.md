# Azure App Service Plan Overview

## Table of Contents

- [What is an App Service Plan?](#what-is-an-app-service-plan)
- [Key Concepts](#key-concepts)
- [Common Misconceptions](#common-misconceptions)
- [App Service Plan vs Other Azure Concepts](#app-service-plan-vs-other-azure-concepts)
- [How App Service Plans Work](#how-app-service-plans-work)
- [Multiple Apps in One Plan](#multiple-apps-in-one-plan)
- [Pricing Tiers](#pricing-tiers)
- [Creating an App Service Plan](#creating-an-app-service-plan)
- [Exam Tips](#exam-tips)
- [References](#references)

## What is an App Service Plan?

**An App Service Plan defines a set of compute resources for a web app to run.**

In App Service (Web Apps, API Apps, or Mobile Apps), an app **always runs in an App Service plan**. In addition, Azure Functions also has the option of running in an App Service plan.

These compute resources are analogous to the **server farm** in conventional web hosting. One or more apps can be configured to run on the same computing resources (or in the same App Service plan).

### Definition

An App Service Plan specifies:

- **Region** (e.g., West US, East US, West Europe)
- **Number of VM instances** (scale out)
- **Size of VM instances** (Small, Medium, Large)
- **Pricing tier** (Free, Shared, Basic, Standard, Premium, Isolated)

```bash
# Create an App Service Plan
az appservice plan create \
  --name myAppServicePlan \
  --resource-group myResourceGroup \
  --location eastus \
  --sku S1 \
  --number-of-workers 2
```

## Key Concepts

### Compute Resources

When you create an App Service plan in a region (e.g., West Europe), a set of compute resources is created for that plan in that region. Whatever apps you put into this App Service plan run on these compute resources as defined by the App Service plan.

Each App Service plan defines:

| Resource | Description |
|----------|-------------|
| **Operating System** | Windows or Linux |
| **Region** | Geographic location of resources |
| **Number of VM instances** | How many machines run your apps |
| **Size of VM instances** | CPU, Memory, Storage |
| **Pricing Tier** | Features and capabilities |

### The Server Farm Analogy

Think of an App Service Plan like a **traditional server farm**:

```
Traditional Hosting              Azure App Service
─────────────────────────────────────────────────
Physical Servers        →        App Service Plan
Server Capacity         →        SKU/Pricing Tier
Multiple Websites       →        Multiple Web Apps
Server Resources        →        Compute Resources
```

## Common Misconceptions

### ❌ What an App Service Plan is NOT

| Misconception | Reality |
|---------------|---------|
| **An isolated physical environment including network available to your applications and no other Azure customer** | This describes an **App Service Environment (ASE)**, not an App Service Plan. ASE is a premium, isolated deployment of App Service. |
| **A container running inside a VM** | This describes a container deployment model. An App Service Plan is a set of compute resources, not a container. |
| **A serverless environment in which App Services and Functions can run** | This describes the **Azure Functions Consumption Plan**. App Service Plans are dedicated compute, not serverless. |

### ✅ What an App Service Plan IS

> **Correct Definition:** A set of compute resources for a web app to run.

## App Service Plan vs Other Azure Concepts

### App Service Plan vs App Service Environment (ASE)

| Feature | App Service Plan | App Service Environment |
|---------|------------------|------------------------|
| **Definition** | Set of compute resources | Isolated, dedicated environment |
| **Network Isolation** | Shared infrastructure | Complete network isolation |
| **VNet** | Optional VNet integration | Runs entirely in your VNet |
| **Other Customers** | Shared underlying infrastructure | No other Azure customers |
| **Use Case** | Standard web hosting | High security/compliance needs |
| **Pricing** | Pay for plan tier | Pay for ASE + plan tier |

### App Service Plan vs Azure Functions Hosting

| Hosting Option | Description | Scaling |
|----------------|-------------|---------|
| **Consumption Plan** | Serverless, pay-per-execution | Automatic, event-driven |
| **Premium Plan** | Pre-warmed instances, VNet | Automatic with limits |
| **App Service Plan** | Dedicated compute resources | Manual or auto-scale rules |

```bash
# Functions on Consumption Plan (serverless)
az functionapp create \
  --consumption-plan-location eastus

# Functions on App Service Plan (dedicated)
az functionapp create \
  --plan myAppServicePlan
```

## How App Service Plans Work

### Resource Allocation

```
┌─────────────────────────────────────────────────────┐
│              App Service Plan (S2)                  │
│                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  Instance 1 │  │  Instance 2 │  │  Instance 3 │ │
│  │   2 cores   │  │   2 cores   │  │   2 cores   │ │
│  │  3.5 GB RAM │  │  3.5 GB RAM │  │  3.5 GB RAM │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
│                                                     │
│  Apps running on these instances:                   │
│  • Web App 1                                        │
│  • Web App 2                                        │
│  • API App                                          │
│  • Function App (Dedicated)                         │
└─────────────────────────────────────────────────────┘
```

### Scaling

App Service provides two options for scaling: **Scale Up** (vertical) and **Scale Out** (horizontal).

#### Scale Up (Vertical Scaling)

**Scale Up** means changing the pricing tier to get more CPU, memory, disk space, or additional features like deployment slots, custom domains, certificates, etc.

| Aspect | Description |
|--------|-------------|
| **What it does** | Moves to the next higher App Service Plan tier |
| **Example** | Going from S1 Standard plan to S2 Standard plan |
| **Resources affected** | CPU, memory, disk, features |
| **Downtime** | Minimal to none (cold start may occur) |

```bash
# Scale up from B1 to S1
az appservice plan update \
  --name myAppServicePlan \
  --resource-group myResourceGroup \
  --sku S1
```

#### Scale Out (Horizontal Scaling)

**Scale Out** means increasing the number of VM instances that run your app. The number of instances you can scale out to depends on your pricing tier.

| Aspect | Description |
|--------|-------------|
| **What it does** | Increases the number of VM instances that run your app |
| **How it works** | Adds more identical VMs running your app |
| **Load balancing** | Traffic is automatically distributed across instances |
| **Limits** | Depends on pricing tier (see table below) |

**Scale Out Limits by Pricing Tier:**

| Pricing Tier | Maximum Instances |
|--------------|-------------------|
| Free | 1 (no scale out) |
| Shared | 1 (no scale out) |
| Basic | 3 |
| Standard | 10 |
| Premium v2/v3 | 30 |
| Isolated (ASE) | 100 |

```bash
# Scale out to 5 instances
az appservice plan update \
  --name myAppServicePlan \
  --resource-group myResourceGroup \
  --number-of-workers 5
```

#### Scale Up vs Scale Out Comparison

| Aspect | Scale Up | Scale Out |
|--------|----------|-----------|
| **Direction** | Vertical | Horizontal |
| **What changes** | VM size/tier | Number of VMs |
| **Resources** | More CPU/RAM per instance | More instances |
| **Limit** | Tier capacity | 30 instances (100 in Isolated) |
| **Cost impact** | Higher tier = higher cost | More instances = multiplied cost |
| **Use case** | Need more power per request | Need to handle more concurrent requests |

#### Autoscale

For Standard tier and above, you can configure **autoscale rules** to automatically scale out based on metrics:

```bash
# Create autoscale setting
az monitor autoscale create \
  --resource-group myResourceGroup \
  --resource myAppServicePlan \
  --resource-type Microsoft.Web/serverfarms \
  --name myAutoscaleSetting \
  --min-count 2 \
  --max-count 10 \
  --count 2

# Add a scale-out rule based on CPU
az monitor autoscale rule create \
  --resource-group myResourceGroup \
  --autoscale-name myAutoscaleSetting \
  --condition "CpuPercentage > 70 avg 5m" \
  --scale out 1
```

---

### Practice Question: Scale Up vs Scale Out

**Question:**

Azure App Service has options to scale up and scale out. What does **scaling out** an app do?

**Options:**

A) Moves to the next higher App Service Plan, such as going from S1 Standard plan to S2 Standard plan.

B) Adds additional running versions of your app to the same instance.

C) Increases the number of VM instances that run your app. ✅

D) Deploys another instance of your app to a different region to ensure better performance for global customers.

---

**Correct Answer: C) Increases the number of VM instances that run your app.**

---

**Explanation:**

**Scale out** increases the number of VM instances that run your app. You can scale out to as many as **30 instances**, depending on your pricing tier. App Service Environments in the **Isolated tier** further increases your scale-out count to **100 instances**.

| Option | Why Correct/Incorrect |
|--------|----------------------|
| **A) Moves to the next higher App Service Plan** | ❌ Incorrect - This describes **Scale Up** (vertical scaling), not Scale Out |
| **B) Adds additional running versions to the same instance** | ❌ Incorrect - Scale Out adds more instances, not multiple versions on one instance |
| **C) Increases the number of VM instances** | ✅ **Correct** - Scale Out adds more VM instances to handle load |
| **D) Deploys to a different region** | ❌ Incorrect - This describes multi-region deployment, not Scale Out |

**Visual Representation:**

```
Scale Up (Vertical):
┌─────────────────┐        ┌─────────────────────┐
│  Instance (S1)  │   →    │   Instance (S2)     │
│  1 core, 1.75GB │        │   2 cores, 3.5GB    │
└─────────────────┘        └─────────────────────┘
     Same number of instances, but bigger

Scale Out (Horizontal):
┌─────────────────┐        ┌─────────┐ ┌─────────┐ ┌─────────┐
│  Instance (S1)  │   →    │ Inst 1  │ │ Inst 2  │ │ Inst 3  │
│  1 core, 1.75GB │        │   S1    │ │   S1    │ │   S1    │
└─────────────────┘        └─────────┘ └─────────┘ └─────────┘
     Same size instances, but more of them
```

**Reference:** [Scale up an app in Azure App Service](https://docs.microsoft.com/en-us/azure/app-service/manage-scale-up)

---

## Multiple Apps in One Plan

One of the key benefits of App Service Plans is the ability to run **multiple apps** on the same compute resources:

### Benefits

- **Cost Optimization:** Share resources across apps
- **Simplified Management:** Single plan to manage
- **Resource Sharing:** All apps use the same pool of resources

### Considerations

- All apps share CPU, memory, and storage
- One app consuming too many resources affects others
- All apps must be in the same region

### Example: Multiple Apps in One Plan

```bash
# Create one App Service Plan
az appservice plan create \
  --name sharedPlan \
  --resource-group myResourceGroup \
  --sku S2

# Create multiple apps using the same plan
az webapp create --name frontend-app --plan sharedPlan --resource-group myResourceGroup
az webapp create --name backend-api --plan sharedPlan --resource-group myResourceGroup
az webapp create --name admin-portal --plan sharedPlan --resource-group myResourceGroup

# All three apps share the same compute resources
```

### Apps Per Plan Limits

| Tier | Maximum Apps |
|------|--------------|
| Free | 10 |
| Shared | 100 |
| Basic | Unlimited |
| Standard | Unlimited |
| Premium | Unlimited |
| Isolated | Unlimited |

## Pricing Tiers

App Service Plans come in different pricing tiers:

| Tier | Target | Key Features |
|------|--------|--------------|
| **Free (F1)** | Dev/Test | Shared compute, 60 CPU min/day |
| **Shared (D1)** | Dev/Test | Shared compute, custom domains |
| **Basic (B1-B3)** | Low traffic | Dedicated compute, SSL, manual scale |
| **Standard (S1-S3)** | Production | Auto-scale, slots, VNet, backups |
| **Premium (P1v3-P3v3)** | Enterprise | Private endpoints, more slots, scale |
| **Isolated (I1v2-I3v2)** | High security | ASE, complete isolation |

> For detailed information on pricing tiers, see [App Service Pricing Tiers](./app-service-pricing-tiers.md)

## Creating an App Service Plan

### Azure CLI

```bash
# Basic creation
az appservice plan create \
  --name myAppServicePlan \
  --resource-group myResourceGroup \
  --location eastus \
  --sku S1

# With specific options
az appservice plan create \
  --name myAppServicePlan \
  --resource-group myResourceGroup \
  --location eastus \
  --sku P1v3 \
  --number-of-workers 3 \
  --is-linux
```

### Azure Portal

1. Navigate to **Create a resource**
2. Search for **App Service Plan**
3. Configure:
   - Subscription
   - Resource Group
   - Name
   - Operating System
   - Region
   - Pricing Tier
4. Click **Create**

### ARM Template

```json
{
  "type": "Microsoft.Web/serverfarms",
  "apiVersion": "2022-03-01",
  "name": "myAppServicePlan",
  "location": "[resourceGroup().location]",
  "sku": {
    "name": "S1",
    "tier": "Standard",
    "capacity": 2
  },
  "kind": "app",
  "properties": {
    "reserved": false
  }
}
```

## Exam Tips

### Key Points to Remember

1. **App Service Plan = Set of Compute Resources**
   - This is the correct definition for exam questions

2. **Not an Isolated Environment**
   - That's App Service Environment (ASE)
   - ASE runs in the Isolated tier

3. **Not Serverless**
   - Serverless is the Consumption Plan for Azure Functions
   - App Service Plans are dedicated resources

4. **Not a Container**
   - Containers can run ON an App Service Plan
   - But the plan itself is not a container

5. **Multiple Apps Can Share One Plan**
   - Cost optimization strategy
   - All apps share the same resources

### Common Exam Question Format

**Question:** What is an App Service Plan?

| Option | Correct? | Explanation |
|--------|----------|-------------|
| An isolated physical environment including network | ❌ | This is ASE |
| A container running inside a VM | ❌ | This is a container model |
| A serverless environment | ❌ | This is Consumption Plan |
| **A set of compute resources for a web app to run** | ✅ | Correct definition |

## References

- [App Service plan overview - Microsoft Docs](https://docs.microsoft.com/en-us/azure/app-service/overview-hosting-plans)
- [Scale up an app in Azure App Service](https://docs.microsoft.com/en-us/azure/app-service/manage-scale-up)
- [App Service Environment overview](https://docs.microsoft.com/en-us/azure/app-service/environment/overview)
- [Azure Functions hosting options](https://docs.microsoft.com/en-us/azure/azure-functions/functions-scale)

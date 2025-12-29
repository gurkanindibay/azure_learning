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
- [Kudu Service](#kudu-service)
- [App Settings and Environment Configuration](#app-settings-and-environment-configuration)
- [Moving Web Apps Between Regions](#moving-web-apps-between-regions)
  - [Moving Web Apps Between Resource Groups](#moving-web-apps-between-resource-groups)
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

### Deployment Slots and VM Instances

**Key Concept**: When you create an app in App Service, it runs on **all** the VM instances configured in the App Service plan. If multiple apps are in the same App Service plan, they all share the same VM instances. Similarly, if you have **multiple deployment slots** for an app, all deployment slots also run on the **same VM instances**.

This means:
- The App Service Plan is the **scale unit** of App Service apps
- If the plan is configured to run 5 VM instances, **all apps** in the plan run on **all 5 instances**
- If the plan is configured for autoscaling, **all apps** in the plan are scaled out together

### Practice Question: VM Instance Count with Multiple Apps and Slots

**Question:**

You have five applications installed on a single App Service Plan. Each application has two deployment slots - production and staging. You have scaled the plan out to three instances. How many VMs are running to support this?

**Options:**

A) Three ✅

B) One

C) Five

D) Ten

---

**Correct Answer: A) Three**

---

**Explanation:**

| Factor | Count |
|--------|-------|
| Applications | 5 |
| Deployment slots per app | 2 (production + staging) |
| Total deployment slots | 10 (5 apps × 2 slots) |
| App Service Plan instances | **3** |
| **VMs Running** | **3** |

**Why the answer is 3 (not 10, 5, or 1):**

1. **All apps in the same App Service Plan share the same VM instances**
2. **All deployment slots also run on the same VM instances**
3. The number of VMs is determined **only** by the App Service Plan's scale-out setting (3 instances)
4. Adding more apps or slots does NOT increase the number of VMs

**Visual Representation:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    App Service Plan (3 Instances)                   │
├─────────────────────┬─────────────────────┬─────────────────────────┤
│     Instance 1      │     Instance 2      │      Instance 3         │
│                     │                     │                         │
│  Running on this VM:│  Running on this VM:│   Running on this VM:   │
│  • App1-Production  │  • App1-Production  │   • App1-Production     │
│  • App1-Staging     │  • App1-Staging     │   • App1-Staging        │
│  • App2-Production  │  • App2-Production  │   • App2-Production     │
│  • App2-Staging     │  • App2-Staging     │   • App2-Staging        │
│  • App3-Production  │  • App3-Production  │   • App3-Production     │
│  • App3-Staging     │  • App3-Staging     │   • App3-Staging        │
│  • App4-Production  │  • App4-Production  │   • App4-Production     │
│  • App4-Staging     │  • App4-Staging     │   • App4-Staging        │
│  • App5-Production  │  • App5-Production  │   • App5-Production     │
│  • App5-Staging     │  • App5-Staging     │   • App5-Staging        │
└─────────────────────┴─────────────────────┴─────────────────────────┘
                        All 10 slots run on ALL 3 VMs
```

**Why Other Answers Are Wrong:**

| Answer | Why Incorrect |
|--------|---------------|
| **One** | Would only be true if you didn't scale out at all (single instance) |
| **Five** | Incorrectly assumes one VM per application |
| **Ten** | Incorrectly assumes one VM per deployment slot |

**Key Takeaway:**

The **App Service Plan** determines the number of VM instances. Apps and slots are workloads that run **on** these instances - they don't create additional VMs. Scaling out the plan increases VMs; adding apps or slots utilizes existing VMs.

**Reference:** [App Service plan overview - Microsoft Docs](https://docs.microsoft.com/en-us/azure/app-service/overview-hosting-plans)

---

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

## Kudu Service

**Kudu** is the engine behind a number of features in Azure App Service related to **source control based deployment** and other deployment methods like **Dropbox and OneDrive sync**.

### Accessing Kudu

The Kudu console URL varies based on your App Service tier:

| App Service Tier | Kudu URL Format |
|------------------|-----------------|
| **Standard Tiers** (Free, Shared, Basic, Standard, Premium) | `https://<app-name>.scm.azurewebsites.net` |
| **Isolated Tier** (App Service Environment) | `https://<app-name>.scm.<ase-name>.p.azurewebsites.net` |

### Examples

```
# Standard tier app named "mywebapp"
https://mywebapp.scm.azurewebsites.net

# Isolated tier app named "mywebapp" in ASE named "myase"
https://mywebapp.scm.myase.p.azurewebsites.net
```

### Kudu Features

Kudu provides several useful features for managing your App Service:

| Feature | Description |
|---------|-------------|
| **Debug Console** | Access command prompt or PowerShell in the browser |
| **Process Explorer** | View and manage running processes |
| **Environment Variables** | View all environment variables |
| **Log Stream** | Real-time log viewing |
| **Deployment Triggers** | Webhooks for CI/CD integration |
| **File Browser** | Browse and edit files in your app |
| **REST API** | Programmatic access to Kudu functionality |

### Reference

- [Kudu service overview - Microsoft Docs](https://docs.microsoft.com/en-us/azure/app-service/resources-kudu)

## App Settings and Environment Configuration

### ASP.NET Core Environment Variables

Azure App Service allows you to configure application settings that are exposed as environment variables to your application. For ASP.NET Core applications, the `ASPNETCORE_ENVIRONMENT` setting is particularly important for controlling application behavior.

### Environment Modes

| Environment | Description | Use Case |
|-------------|-------------|----------|
| **Development** | Enables detailed error pages, debugging features | Local development, troubleshooting |
| **Staging** | Similar to production but for testing | Pre-production testing |
| **Production** | Optimized for performance, minimal error details | Live production apps (default) |

### Default Behavior

If the `ASPNETCORE_ENVIRONMENT` variable is **not set**, it defaults to **Production**, which:
- Disables detailed error pages
- Disables most debugging features
- Shows generic error messages to users
- Optimizes for performance and security

### Enabling Detailed Errors for Debugging

To see detailed error information when your app throws a 500 server error, set:

```
ASPNETCORE_ENVIRONMENT=Development
```

**Azure CLI:**
```bash
az webapp config appsettings set \
  --name myWebApp \
  --resource-group myResourceGroup \
  --settings ASPNETCORE_ENVIRONMENT=Development
```

**Azure Portal:**
1. Navigate to your App Service
2. Go to **Configuration** > **Application settings**
3. Add new setting: `ASPNETCORE_ENVIRONMENT` = `Development`
4. Click **Save**

### ⚠️ Security Warning

> **Never use Development environment in production!** The development environment exposes sensitive information like stack traces, configuration details, and internal paths that could be exploited by attackers.

### Practice Question: Debugging 500 Errors

**Question:**

Your Azure Web App is currently throwing a 500 server error when viewed. You'd like to see more detail on the error. In order to accomplish this, what app setting do you need to set, and to what value?

**Options:**

A) `LOGGING="DEBUG"`

B) `ENVIRONMENT="Development"`

C) `DEBUG="TRUE"`

D) `ASPNETCORE_ENVIRONMENT="Development"` ✅

---

**Correct Answer: D) `ASPNETCORE_ENVIRONMENT="Development"`**

---

**Explanation:**

The `ASPNETCORE_ENVIRONMENT` setting controls the runtime environment for ASP.NET Core applications. Setting it to `Development` enables detailed error pages and debugging features that help diagnose issues.

| Option | Why Correct/Incorrect |
|--------|----------------------|
| **A) `LOGGING="DEBUG"`** | ❌ Incorrect - This is not a recognized ASP.NET Core environment setting |
| **B) `ENVIRONMENT="Development"`** | ❌ Incorrect - The correct variable name is `ASPNETCORE_ENVIRONMENT`, not `ENVIRONMENT` |
| **C) `DEBUG="TRUE"`** | ❌ Incorrect - This is not the correct setting for enabling detailed errors |
| **D) `ASPNETCORE_ENVIRONMENT="Development"`** | ✅ **Correct** - This enables the development environment which shows detailed error information |

**Key Points:**
- If the environment isn't set, it defaults to **Production**
- Production mode disables most debugging features for security
- Development mode should only be used temporarily for troubleshooting

**Reference:** [Access environment variables - Microsoft Docs](https://docs.microsoft.com/en-us/azure/app-service/configure-language-dotnetcore?pivots=platform-windows#access-environment-variables)

---

## Moving Web Apps Between Regions

### Regional Constraints

**Important:** You **cannot change an App Service Plan's region** after it has been created. The region in which your app runs is the region of the App Service Plan it's in.

### Moving Apps Between Plans

You can move an app to another App Service Plan, but with limitations:

| Requirement | Description |
|-------------|-------------|
| **Same Resource Group** | Source and target plans must be in the same resource group |
| **Same Region** | Source and target plans must be in the same geographical region |

### Options for Running an App in a Different Region

If you want to run your app in a different region, you have these alternatives:

| Option | Description | Use Case |
|--------|-------------|----------|
| **App Cloning** | Clone your app to a new or existing App Service Plan in any region | Best for quick migration with existing configuration |
| **Redeploy from Scratch** | Create a new app in the target region and deploy your code | Best when you want a fresh start or don't need to preserve settings |

### App Cloning

Cloning copies your app to a new or existing App Service Plan in any region. The clone includes:
- App settings
- Connection strings
- Deployment slots (optional)
- Custom domains (optional)

```bash
# Clone an app to a new region
az webapp create \
  --name myapp-eastus \
  --resource-group myResourceGroup-EastUS \
  --plan myAppServicePlan-EastUS \
  --source-web-app /subscriptions/{sub-id}/resourceGroups/myResourceGroup/providers/Microsoft.Web/sites/myapp
```

### Practice Question: Moving a Web App to a New Region

**Question:**

You have created a web app called TestWebApp in the West US region. After creating it, you decide you'd rather this web app run in the East US region. How do you move a Web App to a new region?

**Options:**

A) It can only be done in PowerShell or CLI

B) In the Azure Portal, open the Web App, and choose the Move menu at the top of the Overview screen

C) You cannot. If you want to move an app between regions, you must clone the app, or redeploy the app from scratch. ✅

D) You can't move the web app, but you can move the App Service Plan it runs in which has the same effect.

---

**Correct Answer: C) You cannot. If you want to move an app between regions, you must clone the app, or redeploy the app from scratch.**

---

**Explanation:**

You can move an app to another App Service plan, but **only** if the source plan and the target plan are in the **same resource group and geographical region**. The region in which your app runs is the region of the App Service plan it's in. However, **you cannot change an App Service plan's region**.

| Option | Why Correct/Incorrect |
|--------|----------------------|
| **A) It can only be done in PowerShell or CLI** | ❌ Incorrect - Moving between regions is not possible regardless of the tool used |
| **B) Use the Move menu in Azure Portal** | ❌ Incorrect - The Move option is for moving between resource groups/subscriptions, not regions |
| **C) Clone or redeploy** | ✅ **Correct** - These are the only two options for running an app in a different region |
| **D) Move the App Service Plan** | ❌ Incorrect - You cannot change an App Service Plan's region either |

**Key Takeaway:**

The App Service Plan's region is immutable. If you need your app in a different region, you must either:
1. **Clone** the app to a new App Service Plan in the target region
2. **Redeploy** the app from scratch in the target region

**Reference:** [Manage an App Service plan - Microsoft Docs](https://docs.microsoft.com/en-us/azure/app-service/app-service-plan-manage)

---

### Moving Web Apps Between Resource Groups

**Important:** When you move a web app between resource groups, the App Service Plan's location does NOT change, but the Azure Policy assignments change based on the new resource group.

#### What Happens When You Move a Web App

| Aspect | Behavior | Example |
|--------|----------|---------|
| **App Service Plan Location** | ✅ **Remains the same** | WebApp1 in West Europe stays in West Europe even after moving |
| **App Service Plan** | ✅ **Does not move** | The App Service Plan itself is not moved to the new resource group |
| **Azure Policy** | ⚠️ **Changes** | Policy from the new resource group applies; policy from the old resource group no longer applies |
| **Resource Group** | ✅ **Changes** | The web app is now part of the new resource group |

#### Practice Question: Moving Between Resource Groups

**Question:**

You have an Azure subscription named Subscription1. Subscription1 contains the following resource groups:

| Resource Group | Location | Azure Policy |
|----------------|----------|--------------|
| RG1 | West Europe | Policy1 |
| RG2 | North Europe | Policy2 |

RG1 has a web app named WebApp1. WebApp1 is located in West Europe.

You move WebApp1 to RG2.

**What is the effect of the move?**

**Options:**

A) The App Service plan for WebApp1 moves to North Europe. Policy1 applies to WebApp1.

B) The App Service plan for WebApp1 remains in West Europe. Policy1 applies to WebApp1.

C) The App Service plan for WebApp1 remains in West Europe. Policy2 applies to WebApp1. ✅

D) The App Service plan for WebApp1 moves to North Europe. Policy2 applies to WebApp1.

---

**Correct Answer: C) The App Service plan for WebApp1 remains in West Europe. Policy2 applies to WebApp1.**

---

**Explanation:**

| Option | Why Correct/Incorrect |
|--------|----------------------|
| **A) Plan moves to North Europe, Policy1 applies** | ❌ Incorrect - The App Service plan location does NOT change, and Policy1 (from RG1) no longer applies after the move |
| **B) Plan stays in West Europe, Policy1 applies** | ❌ Incorrect - While the plan location is correct, Policy1 (associated with RG1) no longer applies after moving to RG2 |
| **C) Plan stays in West Europe, Policy2 applies** | ✅ **Correct** - The App Service plan remains in its original region (West Europe), and Policy2 (from RG2) now applies |
| **D) Plan moves to North Europe, Policy2 applies** | ❌ Incorrect - The App Service plan location does NOT change, even though Policy2 is correct |

**Key Takeaways:**

1. **App Service Plan Region is Immutable**
   - The region in which your app runs is the region of the App Service plan it's in
   - You cannot change an App Service plan's region
   - Moving a web app to a different resource group does NOT change the App Service plan's location

2. **Azure Policy Follows the Resource Group**
   - When you move a web app to a new resource group, the Azure Policies of the **new resource group** apply
   - Policies from the old resource group no longer apply

3. **Alternative for Different Regions**
   - If you want to run your app in a different region, use **app cloning**
   - Cloning creates a copy of your app in a new or existing App Service plan in any region

**Remember for Exams:**
- Moving between resource groups = Azure Policy changes, but App Service Plan location stays the same
- Moving between regions = Not possible; must use cloning or redeployment

---

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

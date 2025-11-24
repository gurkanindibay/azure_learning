# Azure Identity Concepts: SP, SAMI, UAMI, and Certificate Renewal Flow

## 1. Introduction
This document explains the foundational Azure identity concepts required for securing applications and services:
- **Service Principal (SP)**
- **System-Assigned Managed Identity (SAMI)**
- **User-Assigned Managed Identity (UAMI)**
- **Certificate lifecycle and renewal flow**

Diagrams are included in ASCII format.

---

## 2. Service Principal (SP)
A **Service Principal** is the **identity** an application or service uses to authenticate against Azure Active Directory.

### Key Characteristics
- Represents an application or workload.
- Requires **credentials** (client secret or certificate).
- Azure AD issues access tokens to SPs.
- RBAC roles must be assigned to the SP to determine permissions.

### Why Service Principals Are Needed
RBAC determines **what** an identity can do, but not **who** the identity is. The SP provides the identity; RBAC provides the permissions.

### Authentication with SP
- SP authenticates using secret or certificate.
- Azure AD verifies credentials.
- Azure AD issues a token for accessing Azure resources.

```
[App] --(secret/certificate)--> [Azure AD] --(token)--> [Resource]
```

---

## 3. Managed Identities Overview
Managed Identities (MI) are **Service Principals managed by Azure**. They provide the same identity constructs but automate the credential lifecycle.

Types:
- **System-Assigned Managed Identity (SAMI)**
- **User-Assigned Managed Identity (UAMI)**

Azure automatically:
- Generates and stores the certificate.
- Rotates the credential regularly.
- Issues tokens via local endpoints (IMDS/MSI).

You never create or handle secrets or certificates.

---

## 4. System-Assigned Managed Identity (SAMI)
A SAMI is created and tied to a specific Azure resource.

### Characteristics
- Lifecycle bound to the resource.
- Cannot be shared between services.
- Automatically created and deleted.

### Use Case
Ideal when only **one service** needs a managed identity.

```
[VM/App Service]
     |
     |--(Identity auto-created)
     V
[System-Assigned MI]
```

---

## 5. User-Assigned Managed Identity (UAMI)
A UAMI is an independent Azure resource and can be assigned to **multiple** services.

### Characteristics
- Acts as a shared identity.
- Useful for scaling, multi-instance, multi-region, or cross-service access.
- Still a Service Principal, but fully Azure-managed.

### Why UAMI Is Managed
Azure manages:
- Creation of the underlying SP
- Credential generation
- Credential rotation
- Secure storage

### Use Case Example
Multiple App Services, Functions, and Container Apps sharing the same identity for accessing Key Vault.

```
[App Service A] ----\
[App Service B] ----- > [UAMI]
[Function App] ------/
      |
      V
[Key Vault / Storage / SQL]
```

---

## 6. Use Case Scenarios: Choosing UAMI vs SAMI

### UAMI over SAMI
- Use when multiple resources (App Services, Functions, VMs, Containers) need the same identity to access shared secrets or APIs.
- Prefer for multi-region deployments that must start new instances with identical permissions without reconfiguring identities.
- Choose when you need to pre-provision the identity separately (e.g., during IAM reviews or policy enforcement) and attach it to workloads later.
- Ideal when you want to separate resource lifecycle from identity lifecycle, enabling identity reuse even if individual services are deleted.

### SAMI over UAMI
- Use when a single resource requires access and you want the simplest setup with Azure handling the identity from creation to cleanup.
- Prefer when you do not want to manage another Azure resource (the identity) and you can accept the identity being deleted when the host resource is deleted.
- Choose for short-lived or disposable workloads where creating a dedicated identity per resource matches the workload lifecycle and reduces scope for cross-service permissions.
- Ideal when you want to avoid assigning multiple resources the same permissions unintentionally; each resource gets isolated credentials.

## 7. Certificate Lifecycle and Renewal Flow
Service Principals (including Managed Identities) rely on **certificate-based credentials**.

For SPs:
- You create and manage certificates.
- You handle rotation.

For Managed Identities:
- Azure generates and rotates certificates **automatically**.

### Certificate Authentication Flow
```
[App]
   |
   | 1. Signs request with private key
   V
[Azure AD]
   |
   | 2. Verifies signature using SP public key
   V
[Azure AD issues access token]
```

### Certificate Renewal Flow (Managed Identity)

```
           (Azure Internal Operation)
                  +-----------+
                  | Azure AD  |
                  +-----------+
                         |
                 1. Generate new certificate
                         |
                 2. Update Service Principal
                         |
    +----------------------------------------------+
    | Azure Resource (VM, App Service, Function)    |
    +----------------------------------------------+
                         |
                 3. MSI/IMDS endpoint receives
                    updated identity metadata
                         |
                 4. App continues requesting tokens
                    (no code changes required)
```

### Certificate Renewal Flow (Service Principal via Certificate)
```
You: Generate new certificate
You: Upload new certificate to App Registration
You: Update hosted service to use new certificate
You: Restart/redeploy application
```

### Key Difference
**SP:** You manage everything.
**MI:** Azure manages everything.

---

## 8. Summary Table

| Feature | Service Principal | SAMI | UAMI |
|--------|-------------------|------|------|
| Identity Type | Application identity | Managed SP | Managed SP |
| Credential Type | Secret/Cert (manual) | Cert (Azure-managed) | Cert (Azure-managed) |
| Credential Rotation | Manual | Automatic | Automatic |
| Resource Lifecycle | Independent | Tied to single service | Independent, reusable |
| Multi-resource use | Yes | No | Yes |
| Best For | CI/CD, custom auth | Single-resource workloads | Shared identity scenarios |

---

## 9. Final Notes
- Service Principal is the **foundation** identity.
- Managed Identities are **Service Principals with automated credential lifecycle**.
- UAMI is ideal for multi-service, multi-region, and zero-downtime deployments.
- Certificate rotation is fully handled by Azure for Managed Identities.

---

## 10. Central Managed Identity Certificate Renewal Service
Azure uses an internal, centralized Managed Identity control plane to automatically handle certificate lifecycle for all Managed Identities (SAMI and UAMI).

### 10.1 How It Works
A distributed Azure-internal service manages:
- Certificate generation
- Certificate rotation
- Public key updates in Entra ID
- Secure distribution of new credentials to MSI/IMDS endpoints on compute resources

### 10.2 High-Level Flow
```
[Azure Managed Identity Control Plane]
        |
        | 1. Generate new certificate
        v
[Entra ID - Service Principal]
        |
        | 2. Update public key metadata
        v
[Azure Compute Resource (VM / App Service / Function)]
        |
        | 3. MSI agent fetches updated identity metadata
        v
[MSI Endpoint continues issuing tokens seamlessly]
```

### 10.3 Why This Exists
The centralized MI control plane ensures:
- Zero-downtime certificate rotation
- Secure handling of private keys
- Consistent identity state across regions
- Compliance with security and operational standards
- Fully automated lifecycle with no developer involvement

This automated system is **exclusive to Managed Identities**. Service Principals using secrets or certificates still require **manual credential rotation**.

## 11. Discover the managed identities authentication flow

### 11.1 How a system-assigned managed identity works with an Azure virtual machine
1. Azure Resource Manager receives a request to enable the system-assigned managed identity on a virtual machine.
2. Azure Resource Manager creates a service principal in Microsoft Entra ID for the identity of the virtual machine. The service principal is created in the Microsoft Entra tenant that's trusted by the subscription.
3. Azure Resource Manager configures the identity on the virtual machine by updating the Azure Instance Metadata Service identity endpoint with the service principal client ID and certificate.
4. After the virtual machine has an identity, use the service principal information to grant the virtual machine access to Azure resources. To call Azure Resource Manager, use role-based access control in Microsoft Entra ID to assign the appropriate role to the virtual machine service principal. To call Key Vault, grant your code access to the specific secret or key in Key Vault.
5. Your code that's running on the virtual machine can request a token from the Azure Instance Metadata service endpoint, accessible only from within the virtual machine: http://169.254.169.254/metadata/identity/oauth2/token
6. A call is made to Microsoft Entra ID to request an access token (as specified in step 5) by using the client ID and certificate configured in step 3. Microsoft Entra ID returns a JSON Web Token (JWT) access token.
7. Your code sends the access token on a call to a service that supports Microsoft Entra authentication.

### 11.2 How a user-assigned managed identity works with an Azure virtual machine
1. Azure Resource Manager receives a request to create a user-assigned managed identity.
2. Azure Resource Manager creates a service principal in Microsoft Entra ID for the user-assigned managed identity. The service principal is created in the Microsoft Entra tenant that's trusted by the subscription.
3. Azure Resource Manager receives a request to configure the user-assigned managed identity on a virtual machine and updates the Azure Instance Metadata Service identity endpoint with the user-assigned managed identity service principal client ID and certificate.
4. After the user-assigned managed identity is created, use the service principal information to grant the identity access to Azure resources. To call Azure Resource Manager, use role-based access control in Microsoft Entra ID to assign the appropriate role to the service principal of the user-assigned identity. To call Key Vault, grant your code access to the specific secret or key in Key Vault.
   
        Note: You can also do this step before step 3.
5. Your code that's running on the virtual machine can request a token from the Azure Instance Metadata Service identity endpoint, accessible only from within the virtual machine: http://169.254.169.254/metadata/identity/oauth2/token
6. A call is made to Microsoft Entra ID to request an access token (as specified in step 5) by using the client ID and certificate configured in step 3. Microsoft Entra ID returns a JSON Web Token (JWT) access token.
7. Your code sends the access token on a call to a service that supports Microsoft Entra authentication.

---

End of Document


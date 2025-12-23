# Azure Storage - Learning Path

This folder contains comprehensive documentation about Azure Storage services, organized in a logical learning sequence from foundational concepts to advanced features.

## 📚 Learning Path

Follow these documents in order for the best learning experience:

### 1. [Storage Redundancy Options](./01-azure-storage-redundancy-options.md)
**Foundation: Durability & Availability**

Start here to understand how Azure Storage protects your data through various redundancy options.

- LRS (Locally Redundant Storage)
- ZRS (Zone-Redundant Storage)
- GRS (Geo-Redundant Storage)
- GZRS (Geo-Zone-Redundant Storage)
- Comparison of durability and availability guarantees
- Cost vs. resilience trade-offs

---

### 2. [Secure Access to Azure Storage](./02-azure-storage-secure-access.md)
**Foundation: Security & Authentication**

Learn how to securely access and authorize operations on Azure Storage.

- Authentication methods (Shared Key, SAS, Entra ID)
- Shared Access Signature (SAS) types
  - Account SAS
  - Service SAS
  - User Delegation SAS (most secure)
- RBAC roles for storage access
- Security best practices
- Exam-focused scenarios and decision matrices

---

### 3. [Blob Storage API](./03-azure-blob-storage-api.md)
**Core Skills: Working with Blobs**

Master the Azure Blob Storage API and learn how to interact with blobs programmatically.

- Blob client types and blob types
- Working with blob metadata and properties
- Blob leases for concurrency control
- Complete code examples (C#, Python, Azure CLI)
- Blob snapshots and versioning
- Advanced blob operations
- Common patterns and best practices

---

### 4. [Storage Access Tiers & Rehydration](./04-azure-storage-access-tiers-rehydration.md)
**Cost Optimization: Managing Storage Costs**

Optimize storage costs by understanding and implementing access tiers.

- Storage account types comparison
- Access tiers: Hot, Cool, Cold, Archive
- Archive tier rehydration strategies
  - Standard priority (up to 15 hours)
  - High priority (under 1 hour)
- Tier comparison and use cases
- Cost vs. performance trade-offs
- Best practices for tier selection

---

### 5. [Storage Lifecycle Policies](./05-azure-storage-lifecycle-policies.md)
**Automation: Policy-Based Management**

Automate tier transitions and blob deletion using lifecycle management policies.

- Policy structure and syntax
- Filter strategies (prefix, blob index tags)
- Actions: tier transitions and deletions
- Complete examples for common scenarios
- Bulk tier transitions within storage accounts
- Best practices and common mistakes
- When to use lifecycle policies vs. manual management

---

### 6. [Storage Data Protection](./06-azure-storage-data-protection.md)
**Advanced: Backup & Recovery**

Implement comprehensive data protection and disaster recovery strategies.

- Point-in-Time Restore
- Soft delete (blobs and containers)
- Blob versioning
- Change feed for audit and compliance
- Immutable storage (WORM)
  - Time-based retention policies
  - Legal holds
- Blob index tags for organization
- Feature comparison and when to use each

---

### 7. [Azure Files Overview](./07-azure-files-overview.md)
**Alternative Service: Managed File Shares**

Explore Azure Files as an alternative to Blob Storage for file share scenarios.

- Fully managed file shares in the cloud
- Protocols: SMB and NFS
- Cross-platform support (Windows, Linux, macOS)
- Mounting Azure file shares
- Use cases and scenarios
- Azure Files vs Azure Blob Storage comparison
- Hybrid cloud scenarios with Azure File Sync

---

## 🎯 Quick Reference

### By Topic

- **Getting Started**: Start with documents 1-2
- **Development**: Focus on document 3
- **Cost Management**: Study documents 4-5
- **Data Protection**: Review document 6
- **File Shares**: Explore document 7

### By Exam Preparation

If you're preparing for Azure certifications:
- **AZ-204**: All documents, with emphasis on 2, 3, 5
- **AZ-104**: Documents 1, 2, 4, 6
- **AZ-305**: All documents for architectural decisions

---

## 🔑 Key Concepts Summary

| Concept | Document | Priority |
|---------|----------|----------|
| Data Redundancy | 01 | ⭐⭐⭐ |
| Authentication & Authorization | 02 | ⭐⭐⭐ |
| Blob Operations | 03 | ⭐⭐⭐ |
| Access Tiers | 04 | ⭐⭐ |
| Lifecycle Automation | 05 | ⭐⭐ |
| Data Protection | 06 | ⭐⭐ |
| File Shares | 07 | ⭐ |

---

## 💡 Learning Tips

1. **Sequential Learning**: Follow the numbered order for comprehensive understanding
2. **Hands-On Practice**: Each document includes code examples - try them in your Azure subscription
3. **Exam Focus**: Pay special attention to sections marked with "Exam Question" or "Key Exam Points"
4. **Cross-References**: Documents reference each other - use links to deepen understanding
5. **Real-World Scenarios**: Focus on use cases and decision matrices to understand when to use each feature

---

## 📖 Additional Resources

- [Official Azure Storage Documentation](https://learn.microsoft.com/en-us/azure/storage/)
- [Azure Storage Best Practices](https://learn.microsoft.com/en-us/azure/storage/common/storage-introduction)
- [Azure Storage Pricing Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)

---

**Last Updated**: December 10, 2025

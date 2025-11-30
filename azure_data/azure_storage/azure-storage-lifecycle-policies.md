# Azure Storage Lifecycle Policies
## Table of Contents

- [Overview](#overview)
- [Policy Structure](#policy-structure)
  - [Basic Policy Schema](#basic-policy-schema)
- [Filters](#filters)
  - [prefixMatch Filter](#prefixmatch-filter)
    - [Syntax](#syntax)
    - [Examples](#examples)
  - [blobIndexMatch Filter](#blobindexmatch-filter)
  - [Combining Filters](#combining-filters)
- [Actions](#actions)
  - [Tier Actions](#tier-actions)
  - [Delete Actions](#delete-actions)
  - [Action Conditions](#action-conditions)
- [Blob Types](#blob-types)
- [Complete Examples](#complete-examples)
  - [Example 1: Comprehensive Tiering Strategy](#example-1-comprehensive-tiering-strategy)
  - [Example 2: Access-Based Lifecycle](#example-2-access-based-lifecycle)
  - [Example 3: Multi-Container Policy](#example-3-multi-container-policy)
- [Best Practices](#best-practices)
- [Common Mistakes to Avoid](#common-mistakes-to-avoid)
- [Bulk Tier Transitions Within Same Storage Account](#bulk-tier-transitions-within-same-storage-account)
  - [✅ Correct Approach: Lifecycle Management Policy](#-correct-approach-lifecycle-management-policy)
  - [❌ Incorrect Approaches for Bulk Tier Transitions](#-incorrect-approaches-for-bulk-tier-transitions)
  - [Key Insight: Tiers vs Containers](#key-insight-tiers-vs-containers)
- [Key Takeaway: prefixMatch Structure](#key-takeaway-prefixmatch-structure)
- [References](#references)


## Overview

Azure Blob Storage lifecycle management offers a rule-based policy that you can use to transition blob data to appropriate access tiers or expire data at the end of the data lifecycle. Lifecycle policies help you:

- Transition blobs to cooler storage tiers (hot to cool, hot to archive, or cool to archive) to optimize for performance and cost
- Delete blobs at the end of their lifecycles
- Define rule-based conditions to run once per day at the storage account level
- Apply rules to containers or a subset of blobs using name prefixes or blob index tags as filters

## Policy Structure

A lifecycle management policy is a collection of rules in a JSON document. Each rule definition includes:

- **Filter Set**: Limits rule actions to a certain set of objects within a container or objects' names
- **Action Set**: Applies the tiering or deletion actions to the filtered set of objects

### Basic Policy Schema

```json
{
  "rules": [
    {
      "enabled": true,
      "name": "ruleName",
      "type": "Lifecycle",
      "definition": {
        "actions": {
          "baseBlob": {
            "tierToCool": {
              "daysAfterModificationGreaterThan": 30
            },
            "tierToArchive": {
              "daysAfterModificationGreaterThan": 90
            },
            "delete": {
              "daysAfterModificationGreaterThan": 365
            }
          },
          "snapshot": {
            "delete": {
              "daysAfterCreationGreaterThan": 90
            }
          }
        },
        "filters": {
          "blobTypes": ["blockBlob"],
          "prefixMatch": ["container1/prefix1"]
        }
      }
    }
  ]
}
```

## Filters

### prefixMatch Filter

The `prefixMatch` filter is an array of strings for prefixes to be matched. Each prefix string defines a container and/or blob name prefix.

**Important**: The first element of the prefix string must be a **container name**.

#### Syntax

```json
"prefixMatch": [
  "containerName/blobPrefix",
  "containerName/folderPath/blobPrefix"
]
```

#### Examples

**Example 1: Target specific container with prefix**
```json
{
  "rules": [
    {
      "enabled": true,
      "name": "moveLogsToArchive",
      "type": "Lifecycle",
      "definition": {
        "actions": {
          "baseBlob": {
            "tierToArchive": {
              "daysAfterModificationGreaterThan": 180
            }
          }
        },
        "filters": {
          "blobTypes": ["blockBlob"],
          "prefixMatch": [
            "logs/application",
            "logs/system"
          ]
        }
      }
    }
  ]
}
```

In this example:
- Container name: `logs`
- Blob prefixes: `application` and `system`
- All blobs in the `logs` container starting with `application` or `system` will be moved to archive tier after 180 days

**Example 2: Multiple containers**
```json
{
  "rules": [
    {
      "enabled": true,
      "name": "deleteOldBackups",
      "type": "Lifecycle",
      "definition": {
        "actions": {
          "baseBlob": {
            "delete": {
              "daysAfterModificationGreaterThan": 365
            }
          }
        },
        "filters": {
          "blobTypes": ["blockBlob"],
          "prefixMatch": [
            "backups-2023/",
            "backups-2024/"
          ]
        }
      }
    }
  ]
}
```

**Example 3: Entire container without prefix**
```json
{
  "rules": [
    {
      "enabled": true,
      "name": "coolOldImages",
      "type": "Lifecycle",
      "definition": {
        "actions": {
          "baseBlob": {
            "tierToCool": {
              "daysAfterModificationGreaterThan": 30
            }
          }
        },
        "filters": {
          "blobTypes": ["blockBlob"],
          "prefixMatch": ["images"]
        }
      }
    }
  ]
}
```

This targets all blobs in the `images` container.

### blobIndexMatch Filter

Use blob index tags to filter blobs based on key-value pairs.

```json
{
  "rules": [
    {
      "enabled": true,
      "name": "archiveByTag",
      "type": "Lifecycle",
      "definition": {
        "actions": {
          "baseBlob": {
            "tierToArchive": {
              "daysAfterModificationGreaterThan": 0
            }
          }
        },
        "filters": {
          "blobTypes": ["blockBlob"],
          "blobIndexMatch": [
            {
              "name": "Project",
              "op": "==",
              "value": "Contoso"
            },
            {
              "name": "Status",
              "op": "==",
              "value": "Completed"
            }
          ]
        }
      }
    }
  ]
}
```

### Combining Filters

You can combine `prefixMatch` and `blobIndexMatch` filters:

```json
{
  "rules": [
    {
      "enabled": true,
      "name": "combinedFilters",
      "type": "Lifecycle",
      "definition": {
        "actions": {
          "baseBlob": {
            "delete": {
              "daysAfterModificationGreaterThan": 90
            }
          }
        },
        "filters": {
          "blobTypes": ["blockBlob"],
          "prefixMatch": ["logs/"],
          "blobIndexMatch": [
            {
              "name": "Priority",
              "op": "==",
              "value": "Low"
            }
          ]
        }
      }
    }
  ]
}
```

## Actions

### Tier Actions

- **tierToCool**: Move blobs to cool tier
- **tierToArchive**: Move blobs to archive tier
- **tierToCold**: Move blobs to cold tier

### Delete Actions

- **delete**: Delete blobs

### Action Conditions

- `daysAfterModificationGreaterThan`: Days since last modification
- `daysAfterCreationGreaterThan`: Days since blob creation
- `daysAfterLastAccessTimeGreaterThan`: Days since last access (requires access tracking)
- `daysAfterLastTierChangeGreaterThan`: Days since last tier change

## Blob Types

Lifecycle policies can target:
- **blockBlob**: Standard block blobs optimized for general-purpose storage. Composed of blocks that can be managed individually, supporting efficient parallel uploads. Ideal for documents, images, videos, and backups. Support all access tiers (hot, cool, cold, archive). Maximum size: ~190.7 TiB.
- **appendBlob**: Append blobs optimized for append-only operations like logging. Once written, blocks cannot be updated or deleted, only appended. Ideal for log files, audit trails, and continuous data streams. Do NOT support tiering to cool, cold, or archive tiers (hot tier only). Maximum size: ~195 GiB.

## Complete Examples

### Example 1: Comprehensive Tiering Strategy

```json
{
  "rules": [
    {
      "enabled": true,
      "name": "tieringStrategy",
      "type": "Lifecycle",
      "definition": {
        "actions": {
          "baseBlob": {
            "tierToCool": {
              "daysAfterModificationGreaterThan": 30
            },
            "tierToArchive": {
              "daysAfterModificationGreaterThan": 90
            },
            "delete": {
              "daysAfterModificationGreaterThan": 730
            }
          },
          "snapshot": {
            "tierToCool": {
              "daysAfterCreationGreaterThan": 7
            },
            "tierToArchive": {
              "daysAfterCreationGreaterThan": 30
            },
            "delete": {
              "daysAfterCreationGreaterThan": 365
            }
          }
        },
        "filters": {
          "blobTypes": ["blockBlob"],
          "prefixMatch": ["data/archive"]
        }
      }
    }
  ]
}
```

### Example 2: Access-Based Lifecycle

```json
{
  "rules": [
    {
      "enabled": true,
      "name": "accessBasedTiering",
      "type": "Lifecycle",
      "definition": {
        "actions": {
          "baseBlob": {
            "enableAutoTierToHotFromCool": {
              "daysAfterLastAccessTimeGreaterThan": 30
            },
            "tierToCool": {
              "daysAfterLastAccessTimeGreaterThan": 90
            },
            "tierToArchive": {
              "daysAfterLastAccessTimeGreaterThan": 180
            }
          }
        },
        "filters": {
          "blobTypes": ["blockBlob"],
          "prefixMatch": ["media/videos"]
        }
      }
    }
  ]
}
```

### Example 3: Multi-Container Policy

```json
{
  "rules": [
    {
      "enabled": true,
      "name": "coolTemporaryFiles",
      "type": "Lifecycle",
      "definition": {
        "actions": {
          "baseBlob": {
            "delete": {
              "daysAfterModificationGreaterThan": 7
            }
          }
        },
        "filters": {
          "blobTypes": ["blockBlob"],
          "prefixMatch": [
            "temp/uploads",
            "temp/processing",
            "cache/images"
          ]
        }
      }
    },
    {
      "enabled": true,
      "name": "archiveReports",
      "type": "Lifecycle",
      "definition": {
        "actions": {
          "baseBlob": {
            "tierToArchive": {
              "daysAfterModificationGreaterThan": 365
            }
          }
        },
        "filters": {
          "blobTypes": ["blockBlob"],
          "prefixMatch": [
            "reports/annual",
            "reports/quarterly"
          ]
        }
      }
    }
  ]
}
```

## Best Practices

1. **Start with the container name**: Always begin your `prefixMatch` strings with the container name
2. **Use specific prefixes**: Be as specific as possible to avoid unintended matches
3. **Test policies carefully**: Start with a small subset of data to verify behavior
4. **Monitor costs**: Track storage costs to ensure policies are optimizing expenses
5. **Consider access patterns**: Use access-based tracking for frequently accessed data
6. **Version blobs**: Enable versioning for important data before implementing delete policies
7. **Use blob index tags**: For complex filtering logic, blob index tags provide more flexibility
8. **Plan tier transitions**: Ensure blobs meet minimum storage duration requirements for each tier
9. **Review regularly**: Periodically review and adjust policies based on changing requirements

## Common Mistakes to Avoid

1. ❌ Starting `prefixMatch` with a blob name instead of container name
2. ❌ Not considering minimum storage duration fees for cool and archive tiers
3. ❌ Implementing delete policies without proper backups
4. ❌ Forgetting to enable access time tracking when using access-based conditions
5. ❌ Overlapping rules that conflict with each other
6. ❌ Not testing policies in a non-production environment first

## Bulk Tier Transitions Within Same Storage Account

When you need to transition blobs between access tiers (e.g., from hot to cool) within the same storage account, lifecycle management policies are the most efficient approach.

### ✅ Correct Approach: Lifecycle Management Policy

Lifecycle management policies can automatically transition blobs between tiers within the same account based on specified conditions. The tier change operation occurs **server-side without requiring data transfer**, making it the most efficient approach for bulk tier changes.

**Example: Immediate tier transition using `daysAfterModificationGreaterThan: 0`**
```json
{
  "rules": [
    {
      "enabled": true,
      "name": "transitionHotToCool",
      "type": "Lifecycle",
      "definition": {
        "actions": {
          "baseBlob": {
            "tierToCool": {
              "daysAfterModificationGreaterThan": 0
            }
          }
        },
        "filters": {
          "blobTypes": ["blockBlob"],
          "prefixMatch": ["mycontainer/"]
        }
      }
    }
  ]
}
```

**Key Benefits:**
- Server-side operation - no data transfer required
- Changes the tier of existing blobs in place
- Cost-efficient for bulk operations
- No data duplication

### ❌ Incorrect Approaches for Bulk Tier Transitions

| Approach | Why It's Wrong |
|----------|----------------|
| **Copy Blob API with x-ms-access-tier header** | Creates a **new blob copy** rather than changing the tier of the existing blob. Results in duplicate blobs and unnecessary storage costs. |
| **AzCopy with --block-blob-tier parameter** | Creates **new copies** of the blobs rather than changing the tier of existing blobs in place. Results in data duplication and increased costs. |
| **Azure Data Factory to move blobs** | Incorrectly assumes tiers are separate containers. Access tiers are **properties of blobs**, not separate containers. Involves unnecessary data movement. |

### Key Insight: Tiers vs Containers

Access tiers (hot, cool, cold, archive) are **blob-level properties**, not separate storage locations or containers. When you change a blob's tier:
- The blob stays in the same container
- Only the tier metadata property changes
- No physical data movement occurs (except for archive rehydration)
- The blob URL remains the same

## Key Takeaway: prefixMatch Structure

**The first element of the prefix string must be a container name**, followed by optional blob name prefixes.

✅ Correct:
```json
"prefixMatch": ["mycontainer/folder/prefix"]
```

❌ Incorrect:
```json
"prefixMatch": ["mystorageaccount/mycontainer/prefix"]  // Don't include account name
"prefixMatch": ["blobname.txt"]  // Must start with container
```

## References

- [Optimize costs by automatically managing the data lifecycle](https://learn.microsoft.com/en-us/azure/storage/blobs/lifecycle-management-overview)
- [Configure a lifecycle management policy](https://learn.microsoft.com/en-us/azure/storage/blobs/lifecycle-management-policy-configure)
- [Blob storage lifecycle policies - Training](https://learn.microsoft.com/en-us/training/modules/configure-blob-storage-lifecycle-management-policy/)

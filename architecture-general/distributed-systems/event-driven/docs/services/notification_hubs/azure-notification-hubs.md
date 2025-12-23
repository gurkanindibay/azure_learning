# Azure Notification Hubs

## Overview

Azure Notification Hubs is a massively scalable push notification engine that enables you to send push notifications to any platform (iOS, Android, Windows, etc.) from any backend (cloud or on-premises).

## Firebase Cloud Messaging (FCM) Integration

### FCM Legacy vs FCM v1

Google is deprecating FCM Legacy HTTP API. Azure Notification Hubs supports migration to the new FCM v1 API.

### FCM v1 Authentication Configuration

| Authentication Method | Supported | Notes |
|----------------------|-----------|-------|
| **Private Key, Project ID, and Client Email from service account JSON** | ✅ Required for FCM v1 | FCM v1 requires authentication using service account credentials obtained from Firebase Console |
| OAuth 2.0 client credentials | ❌ Not directly used | While FCM v1 uses OAuth 2.0 internally, the configuration requires service account JSON credentials, not direct OAuth 2.0 client credentials |
| Server key from Firebase Console | ❌ Legacy only | Server key is associated with the legacy FCM implementation; FCM v1 requires service account JSON credentials instead |
| API Key from Firebase project | ❌ Legacy only | API Key authentication is used for the legacy FCM/GCM integration, not for FCM v1 |

### Configuring FCM v1 in Azure Notification Hubs

To configure FCM v1 authentication:

1. Go to the **Firebase Console**
2. Navigate to **Project Settings** > **Service Accounts**
3. Generate a new private key (downloads a JSON file)
4. Extract the following from the service account JSON file:
   - **Private Key**
   - **Project ID**
   - **Client Email**
5. Configure these credentials in Azure Notification Hubs for FCM v1 integration

### Migration from FCM Legacy to FCM v1

When migrating from FCM Legacy HTTP to FCM v1:

- **Do**: Use service account JSON credentials (Private Key, Project ID, Client Email)
- **Don't**: Continue using Server keys or API keys (these are for legacy integration only)

## Key Concepts

- **Namespace**: A container for one or more notification hubs
- **Notification Hub**: A multi-platform push notification resource
- **Registration**: Associates a device's Platform Notification Service (PNS) handle with tags
- **Installation**: An enhanced registration that includes push-related properties
- **Tags**: Used to route notifications to the correct set of registered devices

## Use Cases

- Send push notifications to mobile apps across multiple platforms
- Broadcast notifications to millions of devices
- Personalized notifications using tags and templates
- Silent push notifications for background data sync

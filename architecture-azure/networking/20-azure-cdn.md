# Azure CDN (Content Delivery Network)

## Overview

**Layer/scope:** Global content delivery network for caching and accelerating static content.

**Purpose:** Caches static content at edge locations worldwide to reduce latency and offload origin servers. Also provides **HTTPS support for custom domains** on Azure Blob Storage static websites.

## Key Features

- Global network of edge servers (Points of Presence - POPs)
- Content caching with configurable TTL and cache rules
- **HTTPS termination for custom domains** (critical for static websites in Blob Storage)
- Custom domain support with free managed certificates
- Compression and optimization
- Geo-filtering and token authentication
- Integration with Azure Blob Storage, App Service, and custom origins
- Query string caching behavior
- Cache purging and pre-loading

## Typical Topology

CDN sits between end users and origin servers (Blob Storage, App Service, custom servers), caching content at edge locations closest to users.

## Why Use It as a Proxy

Use Azure CDN when you need to:
- **Enable HTTPS on custom domains for Azure Blob Storage static websites** (Blob Storage doesn't natively support HTTPS with custom domains)
- Accelerate static content delivery globally
- Reduce load on origin servers
- Improve performance for geographically distributed users

## Azure CDN vs Azure Front Door

| Feature | Azure CDN | Azure Front Door |
|---------|-----------|------------------|
| **Primary Purpose** | Content caching/delivery | Global load balancing + WAF |
| **HTTPS Custom Domains** | ✅ Yes | ✅ Yes |
| **Static Website Hosting** | ✅ Recommended | ⚠️ Works but overkill |
| **WAF** | ❌ No (Standard) / ✅ Yes (Premium from Edgio) | ✅ Yes |
| **Dynamic Content** | ⚠️ Limited | ✅ Full support |
| **Load Balancing** | ❌ No | ✅ Yes |
| **Cost** | Lower | Higher |

**Key Insight for Exams:**
> Azure Blob Storage does **NOT** natively support HTTPS with custom domains for static websites. You must use **Azure CDN** (recommended) or Azure Front Door to enable HTTPS on custom domains.

## When to Use Azure CDN

| Scenario | Use CDN? | Alternative |
|----------|----------|-------------|
| Static website with custom domain + HTTPS | ✅ **Yes** | Front Door (overkill) |
| Serving images/videos globally | ✅ **Yes** | - |
| API acceleration | ⚠️ Maybe | Front Door preferred |
| WAF protection needed | ❌ No | Front Door or App Gateway |
| Dynamic web application | ❌ No | Front Door |

## Pricing Tiers

### Azure CDN from Microsoft (Standard)

**Pricing Components**:
- **No base fee**: Pay only for data transfer
- **Outbound data transfer** (Zone 1 - North America, Europe):
  - First 10 TB: ~$0.081/GB
  - 10-50 TB: ~$0.075/GB
  - 50-150 TB: ~$0.053/GB
  - 150+ TB: Volume pricing
- **HTTPS custom domain**: Free (managed certificates included)

**Features**:
- ✅ Global edge network
- ✅ Free managed SSL certificates for custom domains
- ✅ Compression (gzip, brotli)
- ✅ Geo-filtering
- ✅ Query string caching
- ✅ Core analytics
- ❌ No WAF
- ❌ No real-time analytics

**Best For**: Simple static content delivery, enabling HTTPS on Blob Storage static websites

### Azure CDN from Edgio (Premium)

**Pricing Components**:
- **Outbound data transfer**: ~$0.17/GB (varies by region)
- **HTTP requests**: ~$0.0075 per 10,000 requests

**Features**:
- ✅ All Standard features
- ✅ Real-time analytics
- ✅ Advanced rules engine
- ✅ Token authentication
- ✅ Mobile device detection
- ✅ Customizable cache behaviors

**Best For**: Advanced caching scenarios requiring real-time analytics

**Cost Example (Microsoft Standard)**:
```
Setup: Static website with 100 GB/month data transfer, custom HTTPS domain
- Data transfer: 100 × $0.081 = $8.10/month
- HTTPS custom domain: Free
Total: ~$8.10/month
```

**Key Point for Static Websites:**
> Azure CDN is the **most cost-effective solution** for enabling HTTPS on custom domains for Azure Blob Storage static websites. It costs significantly less than Front Door (~$8/month vs ~$50+/month) for simple static content scenarios.

## Caching Rules Configuration

Azure CDN provides flexible caching rules to control how content is cached at edge locations (POPs). Understanding these configurations is critical for optimizing content delivery performance.

### Caching Behavior Options

| Caching Behavior | Description | Use Case |
|-----------------|-------------|----------|
| **Override** | CDN caches content regardless of origin server's cache headers | When you want CDN to control caching completely, ignoring origin directives |
| **Set if missing** | CDN caches only if origin doesn't provide cache headers | When you want to respect origin cache settings but provide defaults |
| **Bypass cache** | CDN doesn't cache content at all | For dynamic content that changes frequently or user-specific data |

### Cache Expiration Duration

- Defines how long content stays in the CDN cache before requesting a fresh copy from origin
- Common values: seconds, minutes, hours, or days
- Example: 1 hour, 1 day, 7 days
- **Best Practice**: Match expiration to content update frequency

### Query String Caching Behavior

Query string caching is crucial for content that varies based on URL parameters (e.g., video quality, image size, user preferences).

| Query String Behavior | Description | Example Impact |
|----------------------|-------------|----------------|
| **Cache every unique URL** | Each unique URL (including query parameters) is cached separately | `video.mp4?quality=1` and `video.mp4?quality=2` are cached as different objects |
| **Ignore query strings** | All URLs with different query strings are treated as the same cached object | `video.mp4?quality=1` and `video.mp4?quality=2` serve the same cached content |
| **Bypass caching for query strings** | URLs with query strings are never cached | All parameterized requests go directly to origin |

## Real-World Example: Video-on-Demand Streaming

**Scenario**: Azure App Service hosting video-on-demand with CDN, where videos have quality parameters.

**URL Pattern**: `http://www.contoso.com/content.mp4?quality=1`

**Requirements**:
- Content expires after 1 hour
- Different quality versions must be cached separately
- Deliver to closest regional POP node

**Correct Configuration**:
```
✅ Caching behavior: Override
✅ Cache expiration duration: 1 hour
✅ Query string caching behavior: Cache every unique URL
```

**Why This Works**:
- **Override**: Forces CDN to cache content for exactly 1 hour, regardless of origin headers
- **1 hour expiration**: Meets the requirement for content freshness
- **Cache every unique URL**: Each quality variant (`quality=1`, `quality=2`, etc.) is cached separately at each POP, ensuring optimal delivery of the requested quality to users

**Common Mistakes**:

❌ **Ignore query strings** - Would serve the same video quality to all users regardless of their request
```
Caching behavior: Override
Cache expiration duration: 1 hour
Query string caching behavior: Ignore query strings  ⬅️ WRONG
```
*Problem*: All quality variants would share the same cached object, breaking quality selection.

❌ **Bypass cache** - Defeats the purpose of using CDN
```
Caching behavior: Bypass cache  ⬅️ WRONG
Cache expiration duration: 1 day
Query string caching behavior: Bypass caching for query strings
```
*Problem*: No caching occurs, forcing all requests to origin server.

❌ **Set if missing with too short duration**
```
Caching behavior: Set if missing  ⬅️ WRONG FOR THIS SCENARIO
Cache expiration duration: 1 second  ⬅️ WRONG
Query string caching behavior: Ignore query strings  ⬅️ WRONG
```
*Problem*: Multiple issues - doesn't override origin headers, 1 second is too short, and query strings are ignored.

## Key Takeaways for CDN Caching

1. **Use "Override" behavior** when you need strict control over cache duration
2. **Use "Cache every unique URL"** when query parameters indicate different content variants
3. **Match cache duration** to your content update frequency and freshness requirements
4. **Consider bandwidth costs** - longer cache durations reduce origin requests but may serve stale content
5. **Test query string behavior** - incorrect configuration can break parameterized content delivery

## Common Use Cases

1. **Static Website HTTPS**: Enable HTTPS for Azure Blob Storage static websites with custom domains
2. **Media Streaming**: Cache video/audio content with quality variants
3. **Image Optimization**: Serve optimized images from edge locations
4. **Software Distribution**: Cache downloadable files (installers, updates)
5. **API Acceleration**: Cache API responses for read-heavy workloads
6. **Global Content Delivery**: Serve content to users worldwide with low latency

## Architecture Patterns

### Pattern 1: Static Website with Custom HTTPS Domain
```
Internet → Azure CDN → Azure Blob Storage (Static Website)
Cost: ~$5-20/month
```
**Note**: This is the recommended pattern for enabling HTTPS on custom domains for Azure Blob Storage static websites.

### Pattern 2: Media Delivery Platform
```
Internet → Azure CDN → Azure Media Services
```

### Pattern 3: Global Web Application
```
Internet → Azure CDN → 
  ├─> Static content: Cached at edge
  └─> Dynamic content: Origin fetch
```

### Pattern 4: Multi-Origin CDN
```
Internet → Azure CDN → 
  ├─> Images: Blob Storage
  ├─> Videos: Media Services
  └─> API: App Service
```

## Integration with Azure Services

### Azure Blob Storage

- **Primary use case**: Static website hosting with HTTPS custom domains
- Native integration for static websites
- Automatic origin configuration
- Free managed SSL certificates

**Setup Steps**:
1. Enable static website on Blob Storage
2. Create CDN profile and endpoint
3. Configure custom domain on CDN
4. Enable HTTPS with managed certificate

### Azure App Service

- Cache static content from App Service
- Reduce load on App Service instances
- Improve global performance
- Custom caching rules per content type

### Azure Media Services

- Streaming optimization
- Adaptive bitrate caching
- Live and on-demand video delivery
- DRM integration support

### Azure Front Door

- Use CDN for static content
- Front Door for dynamic content and WAF
- Complementary services for hybrid scenarios
- Cost optimization by using right tool for right job

## Compression and Optimization

### Compression

- **Automatic compression**: gzip, brotli
- **Supported file types**: HTML, CSS, JavaScript, JSON, XML, fonts, SVG
- **Minimum file size**: Typically 128 bytes
- **Bandwidth savings**: 60-80% for text-based content

**Best Practices**:
- Enable compression for all text-based content
- Pre-compress large files at origin for better performance
- Test compressed content for compatibility

### Image Optimization

- Automatic format conversion (WebP when supported)
- Resize and scale images
- Quality adjustment
- Progressive JPEG encoding

## Security Features

### HTTPS/TLS

- **Free managed certificates**: Automatic provisioning and renewal
- **Custom certificates**: Upload your own
- **TLS versions**: 1.0, 1.1, 1.2, 1.3
- **Force HTTPS**: Redirect HTTP to HTTPS

### Geo-Filtering

- Block or allow content by country/region
- Compliance with regional restrictions
- Content licensing requirements
- Prevent access from specific locations

### Token Authentication

- Time-limited access tokens
- Secure content delivery
- Prevent hotlinking
- Premium tier feature

### DDoS Protection

- Built-in DDoS protection at edge
- Absorb attacks at global scale
- Protect origin from traffic spikes
- Azure DDoS Protection integration

## Cache Management

### Cache Purge

Manually clear cached content:
- **Purge all**: Clear entire cache
- **Purge by path**: Clear specific files/folders
- **Purge by wildcard**: Clear patterns

**Use Cases**:
- Deploy new content version
- Fix incorrect cached content
- Remove sensitive content
- Force cache refresh

### Cache Pre-loading

Proactively load content to cache:
- Load frequently accessed content
- Prepare for traffic spikes
- Reduce origin load during events
- Improve initial user experience

### Cache Key Query String

Control how query strings affect caching:
- Include all parameters
- Include specific parameters
- Exclude all parameters

## Best Practices

1. **Use CDN for static content only** - don't cache user-specific data
2. **Configure appropriate cache durations** - balance freshness vs performance
3. **Enable compression** - significant bandwidth savings
4. **Use custom domains with HTTPS** - professional appearance, required for security
5. **Implement cache purge strategy** - for content updates
6. **Monitor cache hit ratio** - aim for >80% for static content
7. **Use query string caching correctly** - critical for parameterized content
8. **Test before production** - verify caching behavior matches expectations
9. **Configure origin timeouts** - prevent cascading failures
10. **Use geo-filtering** - comply with content licensing and regulations

## Cost Optimization Strategies

- ✅ Consolidate multiple origins under one CDN profile
- ✅ Use longer cache durations to reduce origin requests
- ✅ Enable compression to reduce data transfer
- ✅ Monitor and optimize cache hit ratio
- ✅ Use CDN instead of Front Door for static content (much cheaper)
- ✅ Pre-load content during off-peak hours
- ✅ Implement cache purge instead of short TTLs
- ✅ Use appropriate tier for requirements (Standard vs Premium)

## When to Choose Azure CDN

Choose Azure CDN when you need:
- ✅ **HTTPS for custom domains on Blob Storage static websites** (primary use case)
- ✅ Global content caching and delivery
- ✅ Reduce origin server load
- ✅ Improve performance for distributed users
- ✅ Cost-effective static content delivery
- ✅ Simple caching without complex routing

Don't choose Azure CDN when:
- ❌ You need WAF (use Front Door or Application Gateway)
- ❌ You need load balancing (use Front Door or Application Gateway)
- ❌ Content is highly dynamic (use Front Door)
- ❌ You need Layer 7 routing (use Front Door or Application Gateway)
- ❌ You need API management features (use APIM)

## Monitoring and Analytics

### Key Metrics

- **Cache hit ratio**: Percentage of requests served from cache
- **Bandwidth**: Data transfer volume
- **Request count**: Number of requests
- **Error rate**: HTTP errors (4xx, 5xx)
- **Origin latency**: Time to fetch from origin
- **Cache status**: Hit, miss, partial hit

### Core Analytics

- Traffic patterns by geography
- Popular content analysis
- Cache performance metrics
- Bandwidth usage trends
- Error analysis

### Real-Time Analytics (Premium)

- Live traffic monitoring
- Real-time alerts
- Detailed request logs
- Custom dashboards
- Advanced filtering

### Best Practices for Monitoring

1. Monitor cache hit ratio - target >80% for static content
2. Set alerts for error rate spikes
3. Track bandwidth trends for cost management
4. Analyze geographic distribution of users
5. Review most accessed content
6. Monitor origin health and latency

## Troubleshooting Common Issues

### Low Cache Hit Ratio

**Causes**:
- Cache duration too short
- Query strings not handled properly
- Cache-Control headers from origin overriding
- Content varies by cookies/headers

**Solutions**:
- Increase cache duration
- Configure query string caching correctly
- Use "Override" caching behavior
- Review vary headers from origin

### HTTPS Not Working

**Causes**:
- Certificate not provisioned yet (can take hours)
- DNS not configured correctly
- Custom domain not verified
- Certificate validation failed

**Solutions**:
- Wait for certificate provisioning
- Verify DNS CNAME record
- Complete domain verification
- Check domain ownership

### Origin Errors

**Causes**:
- Origin server down
- Origin overloaded
- Network issues
- Incorrect origin configuration

**Solutions**:
- Check origin server health
- Scale origin server
- Verify network connectivity
- Review origin configuration

### Stale Content

**Causes**:
- Cache not purged after update
- Cache duration too long
- Origin cache headers incorrect

**Solutions**:
- Purge cache manually
- Reduce cache duration
- Configure origin headers properly
- Implement versioning in URLs

## Security Considerations

1. **Always use HTTPS** - free managed certificates available
2. **Implement token authentication** for sensitive content (Premium)
3. **Use geo-filtering** for compliance requirements
4. **Secure origin** - restrict access to CDN only
5. **Monitor access logs** - detect unusual patterns
6. **Keep certificates updated** - managed certificates auto-renew
7. **Use custom error pages** - don't expose origin errors
8. **Implement rate limiting** at origin - protect from abuse
9. **Review cache rules** - don't cache sensitive data
10. **Regular security audits** - review configurations

## Comparison with Other Services

| Feature | Azure CDN | Azure Front Door | Azure Traffic Manager |
|---------|-----------|------------------|----------------------|
| **Primary Purpose** | Content caching | Global load balancing | DNS routing |
| **Layer** | Layer 7 | Layer 7 | DNS |
| **Caching** | ✅ Yes | ✅ Yes | ❌ No |
| **WAF** | ⚠️ Premium only | ✅ Yes | ❌ No |
| **Load Balancing** | ❌ No | ✅ Yes | ❌ No (DNS only) |
| **HTTPS Custom Domains** | ✅ Yes (Free) | ✅ Yes | ❌ N/A |
| **Cost (typical)** | ~$5-20/month | ~$50-1500/month | ~$3-10/month |
| **Best For** | Static content | Dynamic + static | DNS failover |

## References

- [Azure CDN documentation](https://learn.microsoft.com/en-us/azure/cdn/)
- [Azure CDN pricing](https://azure.microsoft.com/en-us/pricing/details/cdn/)
- [Use Azure CDN to access blobs with custom domains over HTTPS](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-https-custom-domain-cdn)
- [Host a static website in Azure Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-static-website)
- [Azure load balancing overview](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/load-balancing-overview)

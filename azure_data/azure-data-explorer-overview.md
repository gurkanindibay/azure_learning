# Azure Data Explorer (ADX) Overview

Azure Data Explorer (ADX) is a fully managed, high-performance big data analytics platform optimized for real-time analysis of large volumes of data streaming from applications, websites, IoT devices, and more.

## Key Characteristics

- **Interactive Analytics**: Powerful analytics service optimized for analyzing large volumes of data quickly and interactively
- **Petabyte Scale**: Supports storage and querying of structured and semi-structured data at petabyte scale
- **Low Latency**: Perform ad-hoc queries, aggregations, and visualizations over petabytes of data with minimal latency
- **Kusto Query Language (KQL)**: Uses KQL, a powerful query language designed for read-only requests to process data and return results

## Scaling Options

Azure Data Explorer supports multiple scaling approaches:

| Scaling Type | Description |
|--------------|-------------|
| **Manual Scaling** | Manually adjust cluster size based on workload requirements |
| **Built-in Autoscaling** | Automatic horizontal scaling based on predefined metrics |
| **Custom Autoscaling** | Define custom autoscaling rules based on specific metrics and thresholds |

## Use Cases

- **Log and Telemetry Analytics**: Real-time analysis of machine-generated data
- **IoT Analytics**: Processing streaming data from IoT devices
- **Time Series Analysis**: Analyzing time-stamped data patterns
- **Security Analytics**: Threat detection and security monitoring
- **Business Intelligence**: Interactive exploration of business data

## Data Types Supported

- **Structured Data**: Tabular data with defined schemas
- **Semi-structured Data**: JSON, logs, and other flexible formats
- **Unstructured Text Data**: Free-form text for analysis

## Integration with Azure Data Lake Storage Gen2

Processed and analyzed data can be offloaded to Azure Data Lake Storage Gen2 for:
- Long-term retention
- Cost-effective cold storage
- Integration with other analytics services

## When to Choose Azure Data Explorer

Choose Azure Data Explorer when you need:

✅ Interactive analytics over petabytes of data  
✅ Support for structured, semi-structured, and unstructured text data  
✅ Manual scaling, built-in autoscaling, and custom autoscaling options  
✅ Fast query response times with minimal latency  
✅ Integration with Azure Data Lake Storage Gen2 for long-term retention  

## References

- [Azure Data Explorer Overview](https://learn.microsoft.com/en-GB/azure/data-explorer/data-explorer-overview)
- [Azure Data Lake Analytics](https://azure.microsoft.com/en-us/products/data-lake-analytics)
- [Log Analytics Overview](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/log-analytics-overview)

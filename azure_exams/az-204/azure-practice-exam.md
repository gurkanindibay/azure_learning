A company uses Azure API Management to expose some of its services.

Each developer consuming APIs must use a single key to obtain access to various APIs without requiring approval from the API publisher.

You need to recommend a solution.

Which solution should you recommend?

Select only one answer.

Define a subscription with all APIs scope.

This answer is incorrect.

Define a subscription with product scope.

This answer is correct.

Restrict access based on caller IPs.


Restrict APIs based on client certificate.

This item tests the candidate's knowledge of Azure API Management subscriptions.

When creating a product, several APIs can be added to the product and a subscription can be associated with it. Access should not be granted to all APIs. Developer access should be granted regardless of the caller IP. A client certificate would require a policy to validate the certificate and specific logic to map the client to specific APIs.

Secure APIs by using subscriptions - Training | Microsoft Learn

Scope	Details
All APIs	Applies to every API accessible from the gateway
Single API	This scope applies to a single imported API and all of its endpoints
Product	A product is a collection of one or more APIs that you configure in API Management. You can assign APIs to more than one product. Products can have different access rules, usage quotas, and terms of use.

You manage the deployment of an Azure Container Registry named registry1 for a company.

You need to ensure that registry1 **** can be shared across multiple groups in the company, enabling group isolation.

What should you use?

Select only one answer.

artifact


tag


namespace

This answer is correct.

layer

This item tests the candidate’s knowledge of publishing an image to Azure Container Registry. A repository is a collection of container images or other artifacts in a registry that have the same name but different tags. A namespace enables the identification of related repositories and artifact ownership by using forward slash-delimited names. A tag for an image specifies its version. An artifact can be, for instance, a text file, a docker image, or a Helm chart stored in the registry with one or more tags. Container images consist of layers. Layers are used to avoid transferring redundant information and to skip build steps that have not changed.

------

You develop a web application hosted on the Web Apps feature of Microsoft Azure App Service.

You need to enable and configure Azure Web Service Local Cache with 1.5 GB.

Which two code segments should you use? Each correct answer presents part of the solution.

Select all answers that apply.

“WEBSITE_LOCAL_CACHE_OPTION”: “Always”

This answer is correct.

“WEBSITE_LOCAL_CACHE_SIZEINMB”: “1500”

This answer is correct.

“WEBSITE_LOCAL_CACHE_OPTION”: “Enable”

This answer is incorrect.

“WEBSITE_LOCAL_CACHE_SIZEINMB”: “1.5”

This item tests the candidate’s knowledge of configuring the settings of the Web Apps feature of Azure App Service.

By using WEBSITE_LOCAL_CACHE_OPTION = Always, local cache will be enabled. WEBSITE_LOCAL_CACHE_SIZEINMB will properly configure Local Cache with 1.5 GB of size. WEBSITE_LOCAL_CACHE_OPTION = Enable is not a valid value. 1.5 will not configure 1.5 GB for the local cache.

-----

You plan to develop an Azure App Service web app named app1 by using a Windows custom container.

You need to load a TLS/SSL certificate in application code.

Which app setting should you configure?

Select only one answer.

WEBSITE_LOAD_CERTIFICATES

This answer is correct.

WEBSITE_ROOT_CERTS_PATH

This answer is incorrect.

WEBSITE_CORS_ALLOWED_ORIGINS


WEBSITE_AUTH_TOKEN_CONTAINER_SASURL

This item tests the candidate’s knowledge of configuring app settings, which is part of creating Azure App Service Web Apps.

The WEBSITE_LOAD_CERTIFICATES app setting makes the specified certificates accessible to Windows or Linux custom containers as files. The WEBSITE_ROOT_CERTS_PATH app setting is read-only and does not allow comma-separated thumbprint values to be mentioned to the certificates and then be loaded in the code. The WEBSITE_AUTH_TOKEN_CONTAINER_SASURL app setting is used to instruct the auth module to store and load all encrypted tokens to the specified blob storage container. This setting is used for Azure Storage and cannot be used to load certificates inside a Windows custom container.


------

You manage an Azure App Service web app named app1. App1 uses a service plan based on the Basic pricing tier.

You need to create a deployment slot for app1.

What should you do first?

Select only one answer.

Scale out app1.


Scale up app1.

This answer is correct.

Configure automated deployment of app1 with Azure DevOps.


Configure automated deployment of app1 with GitHub.

This item tests the candidate’s knowledge of creating deployment slots, which ties directly to the pricing tier used by Azure App Service web apps. This is configured as part of the Azure App Service web app creation.

Deployment slots require at a minimum the Standard pricing tier, so to supply support for app1, it is necessary to scale it up. Scaling out app1 provisions more instances of app1, but it does not provide the ability to create its deployment slot. Automated deployment of app1 with Azure DevOps or GitHub is not a prerequisite of support for deployment slots, but it commonly is the reason for implementing them.

------

You create an Azure web app locally. The web app consists of a ZIP package.

You need to deploy the web app by using the Azure CLI. The deployment must reduce the likelihood of locked files.

What should you do?

Select only one answer.

Run az webapp deploy specifying –-clean true.

This answer is incorrect.

Run az webapp deploy specifying –-restart true.


Run az webapp deploy to a staging slot with auto swap on.

This answer is correct.

Run az webapp deploy by using a high value for the --timeout parameter.

This item tests the candidate's knowledge of deploying Azure Web Apps using the Azure CLI.

Using a production and staging slot with auto swap enabled reduces the likelihood of locked files. If –clean true is used, the target folder is cleaned, but this has no effect on the likelihood of locked files. It is good to restart the app after deployment. This, however, is the default behavior of a ZIP deployment and has no effect on the reduced likelihood of locked files during deployment. The --timeout parameter has no effect on the likelihood of locked files.

Deploy to App Service - Training | Microsoft Learn https://learn.microsoft.com/training/modules/introduction-to-azure-app-service/4-deploy-code-to-app-service?ns-enrollment-type=learningpath&ns-enrollment-id=learn.wwl.create-azure-app-service-web-apps

-----

You need to configure a web app to allow external requests from https://myapps.com.

Which Azure CLI command should you use?

Select only one answer.

az webapp cors add -g MyResourceGroup -n MyWebApp --allowed-origins https://myapps.com

This answer is correct.

az webapp identity add -g MyResourceGroup -n MyWebApp --allowed-origins https://myapps.com

This answer is incorrect.

az webapp traffic-routing set --distribution myapps=100 --name MyWebApp --resource-group MyResourceGroup


az webapp config access-restriction add -g MyResourceGroup -n MyWebApp --rule-name external --action Allow –ids myapps --priority 200

This item tests the candidate’s knowledge of configuring web app settings.

The code segment that includes the cors add will configure CORS to allow requests from  HYPERLINK "https://myapps.com" https://myapps.com. The code segment that includes identity add will add a managed identity to a web app. The code segment that includes traffic-routing-set will configure a traffic routing to a deployment slot named myapps. The code segment that includes access-restriction add will add an access restriction on a web app.

Control Azure services with the CLI - Training | Microsoft Learn https://learn.microsoft.com/training/modules/control-azure-services-with-cli/

-----

You are developing a Linux web app on Azure App Service.

You need to deploy the web app to the production environment based on the following requirements:

App changes must be validated in an environment identical to the production environment before moving the app to the production environment.
Downtime must be eliminated when the app is deployed to the production environment.
What should you use?

Select only one answer.

Deployment slots

This answer is correct.

Auto-scaling


Hybrid connection


App cloning

This item tests the candidate’s knowledge of when to use deployment slots. Deployment slots are live apps with unique host names, which allow swapping configuration and content between them. Auto-scaling is a feature that allows adding more capacity to an Azure Functions app hosting environment. This capacity can be added to an individual hosting environment (for example, scaling up or adding memory or CPU), or adding more hosts (scaling out). The scaling can be triggered based on a schedule or when breaching thresholds defined for certain metrics. Hybrid connections are available for consuming on-premises apps without needing to expose them to the internet. App cloning is a process to obtain an existing app and copy it to another destination, which can be a new app or a deployment slot, for example. However, this is not supported on Linux apps.

Explore staging environments - Training | Microsoft Learn

Discover App Service networking features - Training | Microsoft Learn

Examine Azure App Service plans - Training | Microsoft Learn

-----

A company has an App Service web app that requires a TLS/SSL certificate. The certificate will be used in other App Service apps. The certificate must be automatically renewed with the least management overhead.

You need to add the certificate.

What should you do?

Select only one answer.

Create a free App Service managed certificate.


Purchase an App Service certificate.

This answer is correct.

Upload a certificate from a third party.


Import a certificate from a Key Vault.

This answer is incorrect.
This item tests the candidate’s knowledge of configuring web app settings including SSL, API settings, and connection strings. Purchasing an App Service certificate automates the process of requesting, renewing, and synchronizing the certificate with the App Service apps that use them. Free App Service certificates offer basic functionalities and cannot be exported. Obtaining the certificate from a third party and uploading it to Azure App Service is also an option but lacks the automation and integration offered by the App Service certificates. It is recommended to store certificates in and retrieve them from a Key Vault, but if they are obtained from a third party, the renewal and synchronization with the App Service apps need to be automated in other ways.

-----

A company plans to implement a Microsoft Defender for Cloud solution.

The company has the following requirements:

Notifies when DNS domains are not deleted when a new Azure Functions app is deleted.
Use native alerting.
Minimize costs.
You need to select a hosting plan.

Which hosting plan should you use?

Select only one answer.

Consumption


Standard

This answer is correct.

Premium


Free

This item tests the candidate's knowledge about securing Azure Functions.

The Standard plan supports both custom domains and Microsoft Defender for Cloud, which can automatically alert on dangling DNS domains. The Consumption plan is incorrect because it does not support Microsoft Defender for Cloud. This can automatically alert on dangling DNS domains. The Premium plan supports custom domains and Microsoft Defender for Cloud, which can automatically alert on dangling DNS domains. This, however, is not the lowest cost option. The Free plan does not support custom domains, although it does support Microsoft Defender for Cloud, which can automatically alert on dangling DNS domains.

Overview of Defender for App Service to protect your Azure App Service web apps and APIs - Training | Microsoft Learn

----

A company plans to create an Azure Functions app.

You need to recommend a solution that meets the following requirements:

Executes multiple functions concurrently.
Performs aggregation on the results from the functions.
Avoids cold starts.
Minimizes costs.
Which two components should you recommend? Each correct answer presents part of the solution

Select all answers that apply.

The Consumption plan


The Premium plan

This answer is correct.

Fan-out/fan-in pattern

This answer is correct.

Function chaining pattern

This item tests the candidate’s knowledge of Azure Durable Functions and hosting plans.

The Premium plan avoids cold starts and offers unlimited execution duration. The fan-out/fan-in pattern enables multiple functions to be executed in parallel, waiting for all functions to finish. Often, some aggregation work is done on the results that are returned from the functions. The Consumption plan avoids paying for idle time but might face cold starts. Furthermore, each function run is limited to 10 minutes. The function chaining pattern is a sequence of functions that execute in a specific order. In this pattern, the output of one function is applied to the input of another function.

AZ-204: Implement Azure Functions - Training | Microsoft Learn

Fan-out/fan-in refers to the pattern of executing multiple functions concurrently and then performing some aggregation on the results

---- 

You are developing an Azure Functions app that will be deployed to a Consumption plan. The app consumes data from a database server that has limited throughput.

You need to use the functionAppScaleLimit property to control the number of instances of the app that will be created.

Which value should you use for the property setting?

Select only one answer.

0


10

This answer is correct.

null

This item tests the candidate’s knowledge of configuring an Azure Functions app. Imposing limits on the scaling out capacity of an Azure Functions app can help when the app connects to components that have limited throughput. The functionAppScaleLimit property lets you define the number of instances of the Azure Functions app that will be created. Therefore, setting it to a low value, such as 10, is appropriate in this scenario. Azure Functions apps in the Consumption plan can scale out and have 200 instances as a default. A value of 0 or null for the functionAppScaleLimit property means that an unrestricted number of instances of the Azure Functions app will be created.

----

You have an Azure subscription that contains an Azure Cosmos DB Core (SQL) API account. The account hosts two Azure Cosmos DB containers named Container1 and Container2.

You have an Azure Functions app named FunctionApp1.

You plan to create a function in FunctionApp1 that will process changes to Container1, and then write the results to Container2.

You need to ensure that the function reads the changes to Container1 immediately. The solution must minimize costs.

What should you do?

Select only one answer.

Configure FunctionApp1 to use the Consumption plan.


Configure FunctionApp1 to use the Premium plan.

This answer is incorrect.

Set the feedPollDelay parameter of the function to 0.

This answer is correct.

Set the feedPollDelay parameter of the function to -1.

The correct solution is to set the feedPollDelay parameter to 0, because this controls how frequently the Azure Functions change feed processor polls for new changes in the Cosmos DB container. By default, there is a delay (typically 5 seconds) between polls to balance responsiveness and cost. Setting it to 0 ensures the function reads changes from Container1 immediately, which meets the requirement without needing to upgrade the hosting plan. Configuring the function to use the Consumption or Premium plan does not directly affect how quickly change feed events are read. Setting feedPollDelay to -1 is invalid and would not achieve the desired result. Therefore, adjusting feedPollDelay to 0 is the most cost-effective solution.

Quickstart: Respond to database changes in Azure Cosmos DB using Azure Functions
Azure Cosmos DB trigger for Azure Functions 2.x and higher


----


You have an Azure Storage account container named container1.

You need to configure access to the container to meet the following requirements:

The shared access signature (SAS) token should be secured with Microsoft Entra ID credentials.
Role-based access control (RBAC) should be used.
The SAS token should support granting access to containers.
Which type of SAS should you use?

Select only one answer.

account


user delegation

This answer is correct.

service


stored access policy

This answer is incorrect.
This item tests the candidate’s knowledge of securing an Azure Storage account, which is part of developing solutions that use blob storage.

User delegation SAS fulfills all the requirements, including securing the SAS token with Microsoft Entra ID credentials, RBAC support, and granting access to containers. Azure Storage supports creating a new type of SAS at the level of the storage account. A service SAS delegates access to a resource in just one of the storage services (i.e., Blob, Queue, Table, or File). A stored access policy serves to group shared access signatures and to provide additional restrictions for signatures that are bound by the policy. The account, service, and stored access policy SAS types do not fulfill the requirement of securing the SAS token with Microsoft Entra ID credentials and RBAC support to manage permissions.

Store application data with Azure Blob storage - Training | Microsoft Learn

Secure your Azure Storage account - Training | Microsoft Learn

-----


You plan to use a shared access signature to protect access to services within a general-purpose v2 storage account.

You need to identify the type of service that you can protect by using the user delegation shared access signature.

Which service should you identify?

Select only one answer.

Blob

This answer is correct.

File


Queue


Table

This item tests the candidate’s knowledge of identifying the supported authorization method, which is the first step of implementing it.

The blob service is the only one that supports user delegation shared access signatures. The file service supports account and service shared access signatures. The queue service supports account and service shared access signatures. The table service supports account and service shared access signatures.

https://learn.microsoft.com/en-us/training/modules/implement-shared-access-signatures/2-shared-access-signatures-overview

---

You plan to use Microsoft Graph to retrieve a list of users in a Microsoft Entra ID tenant.

You need to optimize query results.

Which two query options should you use? Each correct answer presents part of the solution.

Select all answers that apply.

$filter

This answer is correct.

$count


$orderby


$select

This answer is correct.

$expand

This item tests the candidate's knowledge of Microsoft Graph query options.

The $filter query option must be used to limit the results returned. The $select query option limits the attributes projected from the result set, making the query more efficient. The $count query option is meant to retrieve the total count of matching resources. $expand query option is used to retrieve related resources.

Query Microsoft Graph by using REST - Training | Microsoft Learn

------

You manage an Azure App Service web app named app1. App1 is registered as a multi-tenant application in a Microsoft Entra ID tenant named tenant1.

You need to grant app1 the permission to access the Microsoft Graph API in tenant1.

Which service principal should you use?

Select only one answer.

legacy


system-assigned managed identity


application

This answer is correct.

user-assigned managed identity

This answer is incorrect.
This item tests the candidate’s knowledge of accessing user data from Microsoft Graph, which is part of implementing user authentication and authorization.

A Microsoft Entra ID application is defined by its one and only application object, which resides in the Microsoft Entra ID tenant where the application was registered (known as the application's home tenant). The application service principal is used to configure permission for app1 in tenant1 to access the Microsoft Graph API. The legacy service principal is a legacy app, which is an app created before app registrations were introduced or an app created through legacy experiences. Managed identities eliminate the need to manage credentials in code. A system-assigned managed identity is restricted to one per resource and is tied to the lifecycle of the resource. Managed identities for Azure resources eliminate the need to manage credentials in code. A user-assigned managed identity can be created and assigned to one or more instances of an Azure service. The legacy, system-assigned managed identity, and user-assigned managed identity cannot be used to assign permission for app1 in tenant1 to access the Microsoft Graph API.

Explore the Microsoft identity platform - Training | Microsoft Learn

Explore service principals - Training | Microsoft Learn

Identity Type	Can access Microsoft Graph with app permissions?	Why
Application (service principal)	✅ Yes	It supports OAuth2 app roles and consent
Legacy SP	❌ No	Old, unsupported model
System-assigned Managed Identity	❌ No	Not an application registration
User-assigned Managed Identity	❌ No	Not an application registration


💡 When can Managed Identities access Microsoft Graph?

Managed Identities can call Graph only in one case:

When using the Azure Instance Metadata Service (IMDS) token endpoint to fetch a Graph token within the same tenant.

However:

This is single-tenant only

No multi-tenant support

No app registration involved

No configurable Graph permissions

Permissions come from role assignments, not “API permissions”

This does NOT apply to your case because App1 is multi-tenant.

https://learn.microsoft.com/training/modules/explore-microsoft-identity-platform/3-app-service-principals
------

You have blobs in an Azure storage account.

You need to implement a stored access policy that will apply to shared access signatures generated for the blobs.

To which type of storage resource should you associate the policy?

Select only one answer.

the storage account

This answer is incorrect.

the blob service of the storage account


the container that is hosting blobs

This answer is correct.

each individual blob

This item tests the candidate’s knowledge of configuring stored access policy, which is part of implementing authorization.

The container that is hosting blobs is used for associating the corresponding stored access policies. The storage account can be associated with shared access signatures keys but not stored access policies. The blob service of the storage account can be associated with shared access signatures keys but not stored access policies. Each individual blob can be associated with shared access signatures keys but not stored access policies.


-----


You develop a multitenant web application named App1. You plan to register App1 with multiple Microsoft Entra ID tenants.

You need to identify the relationship between the application objects and security principals associated with App1.

Which relationship should you identify?

Select only one answer.

App1 will have multiple application objects and multiple service principals.


App1 will have multiple application objects and a single service principal.


App1 will have a single application object and multiple service principals.

This answer is correct.

App1 will have a single application object and a single service principal.

This item tests the candidate’s knowledge of configuring authentication of multitenant applications, which is a common scenario when implementing authentication.

App1 will have a single application object and multiple service principals. App1 will not have multiple application objects. multiple application objects and a single service principal., or a single service principal.

Explore service principals - Training | Microsoft Learn [text](https://learn.microsoft.com/training/modules/explore-microsoft-identity-platform/3-app-service-principals)

-----

You plan to create a key namespace hierarchy in Azure App Configuration.

You need to separate individual key names.

Which character should you use?

Select only one answer.

:

This answer is correct.

*


,


\

This item tests the candidate’s knowledge of configuring key namespace hierarchy of App Configuration, which is part of implementing secure cloud solutions.

The colon character (:) is used to separate names of individual keys when creating a namespace hierarchy in Azure App Configuration. The asterisk character (*) is one of reserved characters in Azure App Configuration, so it cannot be used to separate names of individual keys when creating a namespace hierarchy in Azure App Configuration. The comma character (,) is one of reserved characters in Azure App Configuration, so it cannot be used to separate names of individual keys when creating a namespace hierarchy in Azure App Configuration. The backslash character () is one of reserved characters in Azure App Configuration, so it cannot be used to separate names of individual keys when creating a namespace hierarchy in Azure App Configuration.


----


You need to generate a new version of a key stored in Azure Key Vault.

Which code segment should you use?

Select only one answer.

az keyvault key rotation-policy update -n mykey --vault-name mykeyvault --value path/to/policy.json


az keyvault key purge --name mykey

                      --vault-name mykeyvault


az keyvault key rotate --vault-name mykeyvault --name mykey

This answer is correct.

az keyvault key set-attributes --vault-name mykeyvault --name mykey –policy path/to/>policy.json

This item tests the candidate’s knowledge of setting key rotation by using the Azure CLI.

The Rotate operation will generate a new version of the key based on the key policy. The Rotation Policy operation updates the rotation policy of a key vault key. The Purge Deleted Key operation is applicable for soft-delete enabled vaults or HSMs. The Set Attributes operation changes specified attributes of a stored key.

Control Azure services with the CLI - Training | Microsoft Learn

----

You manage an Azure API Management instance.

You need to limit the maximum number of API calls allowed from a single source for a specific time interval.

What should you configure?

Select only one answer.

Product


Policy

This answer is correct.

Subscription

This answer is incorrect.

API

This item tests the candidate’s knowledge of polices in Azure API Management, which is part of implementing API Management.

API publishers can change API behavior through configuration using policies. Policies are a collection of statements that run sequentially on the request or response of an API. A product has one or more APIs, a usage quota, and the terms of use and cannot be used to restrict the number of API calls. Subscriptions are the most common way for API consumers to access APIs published through an API Management instance. API is a representation of a back-end API and needs to be configured with a policy to implement a rate limit.


-----


You plan to use Azure API Management for Hybrid and multicloud API management.

You need to create a self-hosted gateway for production.

Which container image tag should you use?

Select only one answer.

2.9.0

This answer is correct.

v3


latest

This answer is incorrect.

V3-preview

This item tests the candidate’s knowledge of self-hosted gateways in Azure API Management.

In production, the version must be pinned. The only way to achieve that is by using a tag that follows the convention {major}.{minor}.{patch}. The v3 tag will result in always running a major version with every new feature and patch. The latest tag is used for evaluating the self-hosted gateway. The V3-preview tag should be used to run the latest preview container image.


-----



A company is using Azure API Management to expose their APIs to external partners. The company wants to ensure that the APIs are accessible only to users authenticated with OAuth 2.0, and that usage quotas are enforced to prevent abuse.

You need to configure the API Management instance to meet the security and usage requirements.

Which two actions should you perform?

Select all answers that apply.

Configure a validate-jwt policy to authenticate incoming requests.

This answer is correct.

Deploy an Azure Application Gateway in front of the API Management instance.

This answer is incorrect.

Implement IP filtering by defining access restriction policies.


Set up a rate limit by key policy to enforce call quotas.

This answer is correct.
Configuring a validate-jwt policy is necessary to authenticate users with OAuth 2.0. Setting up a rate limit by key policy helps enforce usage quotas. IP filtering does not address the authentication and quota requirements. Deploying an Azure Application Gateway is not required for these specific needs.

Quickstart: Create a new Azure API Management instance by using the Azure CLI
Authentication and authorization to APIs in Azure API Management

-----

You have an Azure event hub.

You need to add partitions to the event hub.

Which code segment should you use?

Select only one answer.

az eventhubs eventhub consumer-group update --resource-group MyResourceGroupName --namespace-name MyNamespaceName --eventhub-name MyEventHubName --set partitioncount=12


az eventhubs eventhub consumer-group create --resource-group MyResourceGroupName --namespace-name MyNamespaceName --eventhub-name MyEventHubName --set partitioncount=12


az eventhubs eventhub update --resource-group MyResourceGroupName --namespace-name MyNamespaceName --name MyEventHubName --partition-count 12

This answer is correct.

az eventhubs eventhub create --resource-group MyResourceGroupName --namespace-name MyNamespaceName --name MyEventHubName --partition-count 12

This item tests the candidate’s knowledge of developing event-based solutions.

The code segment that includes az eventhubs eventhub update adds partitions to an existing event hub. The code segment that includes az eventhubs eventhub consumer-group update updates the event hub consumer group. The code segment that includes az eventhubs eventhub consumer-group create will create an event hub consumer group. The code segment that includes az eventhubs eventhub create --resource-group segment will create an event hub with partitions, not change an existing one

------



You manage an Azure event hub.

You need to ensure that multiple load-balanced instances of a .NET application (version 5.0) can be used to scale event processing.

Which event processor client should you use?

Select only one answer.

EventHubConsumerClient


EventProcessorHost


EventHubProducerClient

This answer is incorrect.

EventProcessorClient

This answer is correct.
This item tests the candidate’s knowledge of scaling event processing applications, which is part of developing event-based solutions.

EventProcessorClient balances the load between multiple instances of a program in newer .NET versions (version 5.0). EventHubConsumerClient balances the load between multiple instances of a program in Python and JavaScript. EventProcessorHost balances the load between multiple instances of a program in earlier .NET versions. The EventHubProducerClient class is used to send events to an event hub.

Explore Azure Event Hubs - Training | Microsoft Learn

Scale your processing application - Training | Microsoft Learn


-----

You develop the following code to read all published events for the first partition in Azure Event Hubs. (Line numbers are included for reference only.)

1  var connectionString = "<< CONNECTION STRING FOR THE EVENT HUBS NAMESPACE >>";

2  var eventHubName = "<< NAME OF THE EVENT HUB >>";

3  string consumerGroup = EventHubConsumerClient.DefaultConsumerGroupName;

4  await using (var consumer = new EventHubConsumerClient(consumerGroup, connectionString, eventHubName))

5  {

6

7

8    using var cancellationSource = new CancellationTokenSource();

9    cancellationSource.CancelAfter(TimeSpan.FromSeconds(45));

10   await foreach (PartitionEvent receivedEvent in consumer.ReadEventsFromPartitionAsync(partitionId,

11                  startingPosition, cancellationSource.Token))

12   {

13        // At this point, the loop will wait for events to be available in the partition. When an event is available, the loop will iterate with the event that was received.

15   }

16 }

You need to complete the code.

Which two actions should you perform? Each correct answer presents part of the solution.

Select all answers that apply.

Insert the following code segment at line 6:

EventPosition startingPosition = EventPosition.Earliest;

This answer is correct.

Insert the following code segment at line 6:

EventPosition startingPosition = EventPosition.Latest;

This answer is incorrect.

Insert the following code segment at line 7:

string partitionId = (await consumer.GetPartitionIdsAsync()).First();

This answer is correct.

Insert the following code segment at line 7:

int partitionId = (await consumer.GetPartitionIdsAsync()).First();

This answer is incorrect.
This item tests the candidate’s knowledge of reading events from Azure Event Hubs.

Inserting the code segment that includes startingPosition = EventPosition.Earliest at line 6 uses the earliest starting position, which is required to read all published events. Inserting the code segment that includes string partitionId = (await consumer.GetPartitionIdsAsync()).First(); at line 7 is required. The GetPartitionIdsAsync() method returns a string[]. The First() method will, therefore, return a string. The code segment at line 6 that uses startingPosition = EventPosition.Latest does not use the earliest starting position. The code segment at line 7 that includes int partitionId is incorrect because the GetPartitionIdsAsync() method returns a string[]. The First() method will, therefore, return a string, and not an int, as the return variable expects.

Perform common operations with the Event Hubs client library - Training | Microsoft Learn


-------


A company is using Azure Event Grid to process e-commerce order events. The system includes various event sources such as Azure Blob Storage, Azure Functions, and third-party services. The company wants to ensure that the event delivery mechanism is robust and can handle different failure scenarios with minimal loss.

You need to design an event delivery strategy that ensures high reliability, even when events result from 400 or 413 response codes.

What should you do?

Select only one answer.

Configure synchronous handshake validation for all event subscriptions to ensure immediate event delivery.


Decrease the event time-to-live (TTL) to the minimum value to expedite event processing.


Enable dead-lettering to capture events that are not delivered within the specified retry schedule.

This answer is correct.

Increase the maximum number of delivery attempts to the highest possible value to ensure all events are eventually delivered.

Enabling dead-lettering helps capture events that cannot be delivered within the specified retry schedule, ensuring no data is lost during temporary outages. Increasing the maximum number of delivery attempts does not guarantee delivery if the system is down and may lead to unnecessary delays. Synchronous handshake validation is related to subscription validation, not event delivery reliability. Decreasing the event TTL could result in valid events being dropped if the system is temporarily unavailable.

What is Azure Event Grid? - Training | Microsoft Learn

-----


A company is developing a multitenant application that will handle large volumes of events from various sources. The application must be capable of processing and analyzing these events in real-time.

You need to design an event ingestion service that provides data isolation and performance isolation to prevent noisy neighbor problems, while also considering the operational complexity and cost.

Which Event Hubs isolation model should you implement?

Select only one answer.

Dedicated namespace for each tenant

This answer is correct.

Shared namespace and event hubs for all tenants


Shared namespace with dedicated event hubs for each tenant


Trusted multitenancy with shared access signatures

The correct answer is 'Dedicated namespace for each tenant' because it provides the highest level of data and performance isolation, which is essential for preventing noisy neighbor problems in a multitenant application. 'Shared namespace with dedicated event hubs for each tenant' offers medium isolation and could still lead to noisy neighbor issues. 'Shared namespace and event hubs for all tenants' provides the lowest level of isolation and is not suitable for the given requirements. 'Trusted multitenancy with shared access signatures' is not an isolation model but a way to manage access within a shared environment.

Guidance for using Azure Event Hubs in a multitenant solution - Training | Microsoft Learn


-----



You create an Azure Service Bus topic with a default message time to live of 10 minutes.

You need to send messages to this topic with a time to live of 15 minutes. The solution must not affect other applications that are using the topic.

What should you recommend?

Select only one answer.

Change the topic’s default time to live to 15 minutes.


Change the specific message’s time to live to 15 minutes.

This answer is incorrect.

Create a new topic with a default time to live of 15 minutes. Send the messages to this topic.

This answer is correct.

Update the time to live for the queue containing the topic.

This question tests the candidate's knowledge of Azure Service Bus message expiration.

To avoid affecting existing applications, the time to live of the existing topic must not be changed. A new topic needs to be created. Changing the topic's default time to live will affect other applications. A message-level time to live cannot be higher than the topic's time to live. To avoid affecting existing applications, the time to live of the existing topic or queue must not be changed.

------



---
type: System Design Case
title: "URL Shortener"
description: "System design interview case for a global URL shortener with custom aliases and click analytics"
timestamp: 2026-07-15T00:00:00Z
---

# URL Shortener

Create a url shortener. Users should shorten their url's and use that shortener to access the link. Users can also create their own custom short url. Users could also see the access statistics 

How many users is being projected to use it?

Nearly 1 million url creation for each day is being projected to be created and in total 100 million access is being projected

Is there any projected peak hours determined?

It's a global service and mostly the non-working hours especially 20:00 22:00 is the peak hours related to e-shopping link usage

Is there any latency requirements related to time between creation of the link and the usage of it?
There is no hard metric for this requirement


----------------------------
Do short urls expire?
Depends on the configuration. Default configuration should allow 1 month expiration time. After 2 months of expiration the expired  urls can be used

Can anonymous users create and use the links ?

Both anonymous and non-anonymous users can create and use the link. However, to see the statistics the link creator should be logged in and identified

What's the acceptavle redirection latency?
The redirect should feel instanteneous so p99 < 10ms

What kind of analytics is needed here?
Total clicks per url and optionally per-day breakdowns. Referrer and geographic data would be a nice bonus but not required for MVP

Which http status code should be used for redirect?
Default to 301 (permanent) unless the user configures it as temporary then use 302

Do we need multi-region deployment?
User base is global hence we need low latency and high availability even if a whole region fails


Actors: 
Url creater
Url Clicker

Scenarios
1. User subscribe
2. Link creation
3. Url redirection
5. User Login
5. Statistics collection
6. Statistics visualisation 

Non functional requirements 
Each day 1 million url creation projected
24*60*60=86400 seconds
write = 1,000,000/86400 ~=  12 req/sn
read = 12*100 = 1200 req/sn

Peak times ~ 5 => write = 60 req/sn read = 6000 req/sn

statistics visualisation normally admins use 
User count = 1,000,000 => checks screen 3 times each day => 3,000,000 views 3,000,000/86400 ~ 36 req/sn

Redirect p99 < 10 ms 

Needs to be highly available Multiregion => Users should be directed to nearest region If there is an issue then again users should be redirected to nearest working region
218 trillion possible url

208,000,000 days required to finish the url pool so 8 chars is sufficient



Prioritization
1. Url redirection
2. Link creation
3. User login
4. User subscribe
5. Statistics collection
6. statistics visualisation

----------------------------------------------------------------------------

Core Entities

Url {
    id: auto increment  bigint => internal id
    public_id: uuid=> external id unique id 
    url_part char(8),
    original_url varchar(100)
    expiration_date date (default 30 days),
    user_region string (can be used as a part of shard key)
    user_id number(12,0)=> anonymous user =>0,
    idempotency_key varchar2(100)
    create_date datetime
}

Click_Stat{
    url_id bigint,
    url_part char(8),
    click_date datetime
}

---------------------------------------------------------------------------------


Storage requirements

Url  record size: 90 byte
Click stat record size: 40 byte

URL=> Nearly 50 million rows (30 days expiration + extended periods )=> 2.4 GB With replicas and indexes it can be up to ~*3 = 7 Gb
Stats=> 100mln clicks a day  * 40 bytes => 4 gb/day=> 105 gb month => Monthly archival => a backend process can be created daily stats and record in a seperate table => Deferred from this design review due to time constraints. With indexes and replicas it can be up to 315 gb/month

--------------------------------------------------------------------------------

Api design

We can use rest services 

All connections will be HTTPS

Endpoints => 
/v1/createUrl=>POST
Header: idempotency-key
Request: {
    user_id number (0 for anonymous user),
    ttl_day number
}

Response: {
    full_url (with short url),
    expiration_time
}
Return Codes: 
200=> success
500=> any system errors


/v1/createCustomUrl=>POST
Header: idempotency-key
Request: {
    user_id number (0 for anonymous user),
    custom_url
    ttl_day number
}

Response: {
    full_url (with short url),
    expiration_time
}
Return Codes: 
200=> success
409=> custom url collision
500=> any system errors


<main_url>/<short_uri>/=> 302 with original url => 404 if not found, 410 expired 
/v1/<short_uri>/statsList?startDate=<start_date>&finishDate=<finish_date>
Request{
    access_token: <jwt_token>

}

Response{
    day: string (yyyy-mm-dd)
    count: int
}
In statsList user can only see their own Url statistics. 
/v1//login=> POST
Request
{
    email: <user_name>
    password: <password>
}

Response:{
    access_token: <access_token>
}
/v1/subscribe =>POST
Request
{
    name: <name>
    surname: <surname>
    email: <email>
    password: <password>
}

Response
{

}
Retuen codes: 200 success 409 already subscribed, 500 system error



--------------------------------------------------------------------------------

High Level Design

Security: OIDC Connect+ OIDC with PKCE . Statics pages will be SPA. JWT tokens will be validated on API Gateway

Global CDN + load balancer- latency based routing(Cloudflare)
--Edge cache for popular redirects- Redirect is handled directly on edge then to increase count stats endpoint could be called from app server set
Regional API gateway=>  authentication, rate limiting, tls termination,input validation, load balancing
App Server Set 
Redis Cluster
Casandra/MongoDb

All application layers are stateless so we can scale horizontally. Since we are not using relational database database layer is also horizontally scalable

Casandra is my choice for database since it serves sufficiently in this scenario since there is no strict Consistency requirement like a payment system

We can use cache aside strategy to effectively use the cache. We can arrange the ttl with our needs accordingly if we can reserve sufficient memory for our redis cluster we can increase TTL to  increase the chance to memory hit

All apis should be async and nonblocking to prevent thread pool exhaustion

Unique url generation 
We will use 8 english characters to generate url. Url's will be created within the application servers and when we horizonrally scale each server. Therefore I will create a Snowflake like distributed Id generator which provides uniqueness across all servers globally. 

I will create a pool of unique url's and when a new url creation request comes, I will reserve and give the url at the request time. With this design I have an aim to lower the url generation request

A background service will work and prepare the unique urls and assure the uniqueness as well. In this service we can also manage the expiration. There will be a tombstone expiration mechanism we can reuse the urls as well (optional)

 After creation we need to check if the url exists already. While parallel url creation, it may cause a race condition. Since we are using Snowflake style url generation, we can assure all regions have seperate url pool therefore if we can assure that url is unique in a region then it is unique globally as well. We can give an id for each region to provide uniqueness accross all regions.

 For custom url's I will use the consistency level All which will provide a unique custom url on demand. In that case the custom url uniquness is assured in global level
 To avoid race conditions we can use Light Weight transactions (LWT) and statement like below. Custom uri's can be up to 50 chars

 ```SQL

 create table custom_url(
    url_part varchar2(100) primary key,
    user_id number,
    created_date datetime

 )
 INSERT INTO custom_url (url_part)
VALUES (<custom_uri> )
IF NOT EXISTS;

 We can use Write CL as all for custom url scenarion  and this assure the uniquness of url in this case 

We can have a RL of one as well. We may have stale data but since our main focus is performance, it is acceptable for us 

Idempotency
Inside /v1/createUrl we can get the idempotency key from the header so that in retry scenario if the url created we can return the created url. In custom url scenario, we fetch the url from db for the same user and return it


Statistics service

Statistics are collected using Kafka and written into Click_stat table. Each night a batch job can be executed and save the results inside a statistics summary table to serve the stats effectively for the long term



We can use kubernetes for orchestration so that we can use auto scale policies here to manage scalability

Inside Cloudflare we need to use a load balancing algorith which is Geo aware latency based and sensitive to regional failover. On the Api gateway before the App servers, we can use latency based health check performing load balancing 



Failure analysis: If response times increases we can prioritize url redirection to other scenarios. If we seperate url creation pods from redirection pods, in case of performance degradation we can throttle statistics login subscribe and even link creation for some time to open some space for redirection

In redirection most probably database will be the bottleneck. After getting some space to work, we can work on the db and address the issue. 

Since cassandra is highly available we don't need to use an additional sharding


Observability
Since p99<10ms for redirection, we need to use full-fledged tools line dynatrace to track and if it passes a threshold then we can create alarms
CDN and Redis Cache hit ratio 
cache miss and origin lookup latency
Redirect success and expired link rate 
Rate limit count
Code collusion retries and custom alias conflicts
Regional failover event
Click event publish failures and analytics lag
Hot key rate and cache stampede events


Expiration conflicts

For the links that is redirected with 301, there is a risk to stay in browsers and CDNs. It is safe not to reuse a shorturl after expiration. In that case we return 410 Gone after expiration
If reuse is a must then we need to use after a tombstone and cache lifecycle expiration period 
Mostly try to use 302 and 307 for most likely expiring links . Reserve 301 for permanent links



## Caching and hot keys

Both CDN and Redis will cache the uris. For the viral frequently accessed links, We will redirect the link on Cloudflare without accessing app servers.

If there is a cache miss on CDN then request will come to app server and if the uri exists then we will return from Redis otherwise we will update the cache (cache aside) and return 302 with the url
In this case after returning 302 Cloudflare cache will be updated. In this case Cloudflare should be configured to cache redirects

CDN expiretime < redis expire time < url expire time

Frequently accessed urls CSN and redis expire times can be converged to url expire time. In the future version we can create a popular links service to manage the TTL time of URLS both on Redis and CDN using the statistics stored

To avoid thundering herd for popular links, we can provide a background process to revalidate these links before they expire. Additionally, we can throttle and prevent accessing of additional requests to database when a cache expires and make them wait the first one to complete to avoid database fetch

When the link is deleted or expired, we will return 410 in this case 













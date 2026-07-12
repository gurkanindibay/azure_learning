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
208 billion possible url

208,000 days required to finish the url pool so 8 chars is sufficient



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
    expiration_date date (default 30 days),
    user_region string (can be used as a part of shard key)
    user_id number(12,0)=> anonymous user =>0
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

URL=> Nearly 50 million rows (30 days expiration + extended periods )=> 2.4 GB
Stats=> 100mln clicks a day  * 40 bytes => 4 gb/day=> 105 gb month => Monthly archival => a backend process can be created daily stats and record in a seperate table => Deferred from this design review due to time constraints.

--------------------------------------------------------------------------------

Api design

We can use rest services 

Endpoints => 
createUrl?ttlDay=180
<main_url>/<short_uri>/=> redirect to original url
/statsList?startDate=<start_date>&finishDate=<finish_date>
/login=> POST
/subscribe =>POST


--------------------------------------------------------------------------------

High Level Design

Security: OIDC Connect+ OIDC with PKCE . Statics pages will be SPA. JWT tokens will be validated on API Gateway

Global load balancer
Regional load balancer
API gateway=>  authentication, rate limiting, tls termination,input validation
Redis Cluster
App Server Set
Casandra/MongoDb

All application layers are stateless so we can scale horizontally. Since we are not using relational database database layer is also horizontally scalable

Casandra is my choice for database since it serves sufficiently in this scenario since there is no strict Consistency requirement like a payment system

We can use cache aside strategy to effectively use the cache. We can arrange the ttl with our needs accordingly if we can reserve sufficient memory for our redis cluster we can increase TTL to  increase the chance to memory hit

All apis should be async and nonblocking to prevent thread pool exhaustion

While creating the short url we can use a random string generator with 8 english characters. After creation we need to check if the url exists already. Since short usl already the key it will have a high performance

While calculating the statistics, if ~%2 error rate is acceptable we can use hyperloglog algorithm to calculate click counts

We can use kubernetes for orchestration so that we can use auto scale policies here to manage scalability

We can use round robin algorighm in Load balancer since the requests are short lived

Failure analysis: If response times increases we can prioritize url redirection to other scenarios. If we seperate url creation pods from redirection pods, in case of performance degradation we can throttle statistics login subscribe and even link creation for some time to open some space for redirection

In redirection most probably database will be the bottleneck. After getting some space to work, we can work on the db and address the issue. 

Since cassandra is highly available we don't need to use an additional sharding


Observability
Since p99<10ms for redirection, we need to use full-fledged tools line dynatrace to track and if it passes a threshold then we can create alarms













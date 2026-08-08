---
okf_version: "0.1"
type: concept
---

# How do we find nearby restaurants on Yelp?

> **Source**: ByteByteGo — System Design compilation PDF

![How do we find nearby restaurants on Yelp?](images/img-069.jpeg)

![How do we find nearby restaurants on Yelp?](images/img-070.jpeg)

![How do we find nearby restaurants on Yelp?](images/img-071.jpeg)

Here are some design details behind the scenes. There are two key services (see the diagram below): -

**Business Service**

- Add/delete/update restaurant information - Customers view restaurant details -

**Local-based Service**

(**LBS**) - Given a radius and location, return a list of nearby restaurants How are the restaurant locations stored in the database so that LBS can return nearby restaurants efficiently? Store the latitude and longitude of restaurants in the database? The query will be very inefficient when you need to calculate the distance between you and every restaurant. One way to speed up the search is using the **geohashalgorithm**. First, divide the planet into four quadrants along with the prime meridian and equator： - Latitude range [-90, 0] is represented by 0 - Latitude range [0, 90] is represented by 1 - Longitude range [-180, 0] is represented by 0 - Longitude range [0, 180] is represented by 1 Second, divide each grid into four smaller grids. Each grid can be represented by alternating between longitude bit and latitude bit. So when you want to search for the nearby restaurants in the red-highlighted block, you can write SQL like: SELECT * FROM geohash_index WHERE geohash LIKE `01%` Geohash has some limitations. There can be a lot of restaurants in one block (downtown New York), but none in another block (ocean). So there are other more complicated algorithms to optimize the process. Let me know if you are interested in the details.

One picture is worth more than a thousand words. Log4j from attack to prevention in one illustration. Credit GovCERT Link: https://www.govcert.ch/blog/zero-day-exploit-targeting-popular-java-libr ary-log4j/

How does a modern stock exchange achieve microsecond latency? The principal is:

**Do less on the critical path**

！ - Fewer tasks on the critical path - Less time on each task - Fewer network hops - Less disk usage For the stock exchange, the critical path is: - **start**: an order comes into the order manager - mandatory risk checks - the order gets matched and the execution is sent back - **end**: the execution comes out of the order manager Other non-critical tasks should be removed from the critical path. We put together a design as shown in the diagram:

- deploy all the components in a single giant server (no containers) - use shared memory as an event bus to communicate among the components, no hard disk - key components like Order Manager and Matching Engine are single-threaded on the critical path, and each pinned to a CPU so that there is **no context switch**and ​**nolocks** - the single-threaded application loop executes tasks one by one in sequence - other components listen on the event bus and react accordingly

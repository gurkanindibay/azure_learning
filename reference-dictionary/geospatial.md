---
type: Reference
title: "Geospatial & Spatial Indexing"
description: "Spatial indexing algorithms, space-filling curves, hierarchical grid systems, geospatial data structures, map tiling, geocoding, and location-based services (LBS)."
timestamp: 2026-08-22T00:00:00Z
---

# Geospatial & Spatial Indexing

> **Domain**: Spatial indexing algorithms, space-filling curves, hierarchical grid systems, geospatial data structures, map tiling, geocoding, distance calculations, and location-based services (LBS).
> **Parent**: [Reference Dictionary](index.md)

---

## Contents

| Term | Anchor |
|:---|:---|
| Spatial Index | [`#spatial-index`](#spatial-index) |
| Geohashing | [`#geohashing`](#geohashing) |
| Quadtree | [`#quadtree`](#quadtree) |
| Google S2 | [`#google-s2`](#google-s2) |
| Uber H3 | [`#uber-h3`](#uber-h3) |
| Hilbert Curve | [`#hilbert-curve`](#hilbert-curve) |
| R-Tree | [`#r-tree`](#r-tree) |
| K-D Tree | [`#k-d-tree`](#k-d-tree) |
| Map Tile Pyramid | [`#map-tile-pyramid`](#map-tile-pyramid) |
| Vector Tiles | [`#vector-tiles`](#vector-tiles) |
| Geocoding | [`#geocoding`](#geocoding) |
| Reverse Geocoding | [`#reverse-geocoding`](#reverse-geocoding) |
| Haversine Distance | [`#haversine-distance`](#haversine-distance) |
| Redis Geospatial | [`#redis-geospatial`](#redis-geospatial) |

---

## Spatial Index

A **specialized indexing data structure** designed to optimize spatial queries (e.g., nearest neighbors, range bounding box queries, point-in-polygon containment) across multidimensional geometric coordinates.

### Key Characteristics
- **Multidimensional mapping**: Bypasses the limitation of 1D B-Trees that cannot naturally sort $(x, y)$ coordinate pairs simultaneously
- **Hierarchical bounding**: Groups spatial objects into progressively larger bounding envelopes or discrete space-filling cells
- **Query primitives**: Point query (what is at location $P$), Range query (what is inside polygon/box $B$), K-Nearest Neighbors (find the $K$ closest entities to point $P$)
- **Core variants**: Grid Index (Geohash, Google S2, Uber H3), Tree Index (R-Tree, Quadtree, KD-Tree)

### When to Use
- Ride-hailing driver dispatch (Uber, Lyft), food delivery proximity search, and mapping applications
- Spatial filtering in GIS databases (PostGIS, SpatiaLite, Azure Cosmos DB Spatial)
- Location-based notification and geofence triggering

### When NOT to Use
- 1D scalar attributes (timestamps, IDs, prices) where standard B-Trees or Hash Indexes are faster and simpler
- Datasets with fewer than a few thousand points where in-memory brute-force distance calculation is cheaper than maintaining index trees

### Also see
- [Google S2](#google-s2) · [Uber H3](#uber-h3) · [Geohashing](#geohashing) · [R-Tree](#r-tree) · [Hilbert Curve](#hilbert-curve)

---

## Geohashing

<a id="geohash"></a>

A **geospatial indexing technique** that encodes a latitude/longitude coordinate pair into a short alphanumeric string (geohash) using base32 representation. Nearby locations share a common geohash prefix — the longer the shared prefix, the closer the points. Used for proximity searches, ride-matching, and location-based sharding.

### Key Characteristics
- **Hierarchical**: Truncating a geohash gives a larger bounding box (less precision, wider area; e.g., 6 chars $\approx$ 1.2km $\times$ 0.6km, 5 chars $\approx$ 4.9km $\times$ 4.9km)
- **Prefix-based proximity**: Points with the same prefix are spatially close (with edge-case exceptions at cell boundaries)
- **1D index for 2D space**: Enables standard database indexes (B-tree, key-value stores) for spatial queries using simple prefix scans (`WHERE geohash LIKE 'dr5r%'`)
- **Boundary edge cases**: Two points meters apart on either side of a grid boundary may have completely different geohashes; solved by querying the target cell plus its 8 adjacent neighbor cells

### When to Use
- Proximity queries: "find all drivers within 2 km of this rider" (Uber, Lyft)
- Location-based sharding: partition data by geohash prefix so nearby entities land on the same shard
- When a full spatial database (PostGIS) is overkill and approximate proximity is acceptable

### When NOT to Use
- When exact distance calculations are required — geohash is an approximation; use Haversine or PostGIS
- For point-in-polygon queries (geofencing) — use a spatial library with proper polygon support

### Also see
- [Quadtree](#quadtree) · [Google S2](#google-s2) · [Uber H3](#uber-h3) · [Haversine Distance](#haversine-distance) · [Sharding Key Selection](../system-design-architecture/15-interview-roadmap.md#sdi-11-sharding-key-selection)

---

## Quadtree

A **tree data structure** where each internal node has exactly four children, recursively subdividing a 2D space into quadrants (Northwest, Northeast, Southwest, Southeast). Used for spatial indexing, collision detection, and image compression. In system design, quadtrees enable efficient "find all points within a radius" queries without scanning the entire dataset.

### Key Characteristics
- **Recursive subdivision**: Each node represents a rectangular region; split into 4 quadrants when point capacity threshold is exceeded
- **Adaptive resolution / Sparse storage**: Dense areas (e.g., downtown Manhattan) get deeper trees with smaller cells; empty areas (e.g., ocean) stay shallow
- **$O(\log N)$ spatial queries**: Prunes irrelevant branches early during range and radius searches
- **In-memory representation**: Often held in server RAM for sub-millisecond search latencies (e.g., Yelp, Proximity Service)

### When to Use
- Ride-matching: find nearby drivers (Uber)
- Proximity search: find nearby restaurants or businesses (Yelp, Google Maps)
- Map rendering: determine which map tiles to load at a given zoom level
- Collision detection in games and physical simulations

### When NOT to Use
- When the dataset is small enough for brute-force distance calculations
- When the data is uniformly distributed — a grid-based spatial index (Geohash/S2) may be simpler
- When updates are highly frequent across many distributed nodes and the tree must be constantly rebalanced; consider grid-based indexing (Geohash, S2, H3) instead

### Also see
- [Geohashing](#geohashing) · [R-Tree](#r-tree) · [Spatial Index](#spatial-index)

---

## Google S2

A **hierarchical spherical spatial indexing library and geometry framework** developed by Google that projects the 3D spherical Earth onto the six faces of an enclosing cube and recursively subdivides each face into quadrilateral cells using the **Hilbert space-filling curve**. Every cell is uniquely identified by a compact 64-bit integer (`S2CellId`).

### Key Characteristics
- **Spherical projection**: Projects the sphere onto a cube, avoiding extreme polar distortion common in Mercator projections
- **Hilbert curve ordering**: Maps 2D spatial coordinates into a 1D sequence while maximizing spatial locality
- **30 Hierarchical Levels**: Level 0 is a full cube face (~85 million $\text{km}^2$), down to Level 30 (~1 $\text{cm}^2$ resolution)
- **Compact 64-bit Cell IDs**: Every cell on Earth at any subdivision level fits in a single 64-bit integer, enabling fast B-Tree indexing and range lookups in relational and NoSQL databases (`WHERE cell_id BETWEEN min_id AND max_id`)

### When to Use
- Global proximity queries, geofencing, and point-in-polygon tests (used by Google Maps, Uber, Pokémon GO)
- Spatial indexing in distributed databases where numeric range scans replace expensive 2D geometric intersection calculations
- Equal-area hierarchical spatial aggregation and spatial sharding

### When NOT to Use
- Flat local 2D planar CAD geometries where Euclidean $X, Y$ coordinates are sufficient
- Extremely simple localized lookups where standard Geohash string prefixes suffice

### Also see
- [Spatial Index](#spatial-index) · [Hilbert Curve](#hilbert-curve) · [Geohashing](#geohashing) · [Uber H3](#uber-h3) · [R-Tree](#r-tree)

---

## Uber H3

A **hexagonal hierarchical spatial index** developed by Uber that partitions the Earth's surface into regular hexagonal cells across 16 discrete resolution levels (from Resolution 0 with average area ~4.35 million $\text{km}^2$ down to Resolution 15 with average area ~0.9 $\text{m}^2$).

### Key Characteristics
- **Hexagonal grid symmetry**: Unlike squares (which have 4 edge neighbors at distance $d$ and 4 diagonal corner neighbors at distance $d\sqrt{2}$), every hexagon has exactly 6 adjacent neighbors all equidistant ($d$) from the center
- **Uniform neighbor expansion**: Finding all cells within radius $k$ requires simple equidistant ring traversals (k-ring), avoiding diagonal distortion
- **Hierarchical aperture 7**: Each coarser resolution hexagon decomposes approximately into 7 finer resolution hexagons
- **64-bit Integer representation**: Each hexagon index is encoded as a compact 64-bit integer (`H3Index`)

### When to Use
- Ride-hailing supply/demand aggregation and dynamic surge pricing calculation (Uber)
- Spatial machine learning, clustering, and hex-bin heatmap analytics
- Radius-based proximity dispatch and routing where uniform neighbor distance is required

### When NOT to Use
- Exact hierarchical nesting: hexagons cannot be subdivided into smaller hexagons with 100% exact mathematical boundaries (unlike S2 quadrilaterals or quadtrees)
- Planar Cartesian grids with rectangular pixel textures (use Map Tile Pyramid instead)

### Also see
- [Google S2](#google-s2) · [Geohashing](#geohashing) · [Spatial Index](#spatial-index)

---

## Hilbert Curve

A **continuous, fractal space-filling curve** that maps a multi-dimensional coordinate space into a 1-dimensional line while preserving spatial locality to a significantly higher degree than alternative ordering schemes (like the Z-order / Morton curve).

### Key Characteristics
- **Superior locality preservation**: Two points that are close together along the 1D Hilbert curve are almost guaranteed to be physically close in multi-dimensional space
- **Self-similar fractal geometry**: Rotates and reflects recursively across grid quadrants, eliminating long non-local jump discontinuities present in Z-order curves
- **Substrate for spatial indexing**: Forms the core ordering foundation for Google S2 cell IDs and high-performance multi-dimensional database clustering

### When to Use
- Transforming 2D/3D coordinates into 1D database keys for linear range scanning
- Multidimensional image processing and spatial data clustering
- Distributed database shard key generation to ensure geographically adjacent data points land on the same database partition

### When NOT to Use
- When coordinate conversion overhead must be ultra-minimal and simple bit-interleaving (Z-order curve) provides acceptable locality
- Flat unstructured categorical data

### Also see
- [Google S2](#google-s2) · [Spatial Index](#spatial-index) · [Geohashing](#geohashing)

---

## R-Tree

A **tree data structure designed for spatial access methods** that indexes multidimensional information (such as coordinates, geographic polygons, or bounding boxes) by grouping nearby geometric objects into Minimum Bounding Boxes (MBR) at hierarchical leaf and branch nodes.

### Key Characteristics
- **Balanced search tree**: Similar to a B-Tree, but nodes represent geometric Minimum Bounding Rectangles (MBRs) rather than 1D scalar ranges
- **Overlapping bounding boxes**: Bounding rectangles at the same tree depth may overlap, requiring search queries to potentially traverse multiple sub-branches
- **Dynamic insertion & splitting**: Employs heuristic split algorithms (Quadratic split, R* Tree re-insertion) to minimize bounding box area and overlap
- **Native database engine support**: Built into PostgreSQL (GiST indexes), SQLite (R*Tree module), and MySQL Spatial

### When to Use
- Indexing arbitrary geometric polygons, line strings, and bounding envelopes (e.g., real estate parcel boundaries, city limits)
- Complex geometric intersection and spatial containment queries in relational databases
- Computer-aided design (CAD) and GIS shapefile management

### When NOT to Use
- Millions of rapidly moving single-point objects (e.g., fleet tracking of delivery drivers) where frequent tree rebalancing and split overhead degrade write performance; prefer Geohash/S2 grid indexes
- Massive scale distributed NoSQL tables that require simple 1D partition key hashing

### Also see
- [Spatial Index](#spatial-index) · [Quadtree](#quadtree) · [Google S2](#google-s2) · [Geohashing](#geohashing)

---

## K-D Tree

A **k-dimensional binary search tree** used for organizing points in a $k$-dimensional space. At each tree depth level, the space is partitioned by a hyperplane perpendicular to one of the coordinate axes, cycling through dimensions (e.g., alternating between $X$ and $Y$ in 2D space).

### Key Characteristics
- **Binary space partitioning**: Every non-leaf node generates a splitting hyperplane dividing the point set into two halves
- **Dimension cycling**: Splits along dimension $d = \text{depth} \pmod k$
- **Efficient $K$-Nearest Neighbors (KNN)**: Enables $O(\log N)$ average-time nearest neighbor search and range queries by pruning sub-trees whose bounding box does not intersect the search sphere
- **Static vs Dynamic**: Well-suited for static datasets; point insertions/deletions require periodic rebalancing to prevent tree degradation

### When to Use
- Exact and approximate $K$-Nearest Neighbor (KNN) searches for 2D/3D spatial coordinates and low-dimensional feature vectors ($k < 20$)
- Point cloud processing (LiDAR), computer vision feature matching, and photon mapping

### When NOT to Use
- High-dimensional vector search ($k > 20$, such as 768-dim LLM embeddings) due to the "curse of dimensionality" where almost all branches must be searched; use HNSW (Hierarchical Navigable Small World) or IVF indexes instead
- Geospatial polygons or bounding boxes (use R-Tree instead)

### Also see
- [Spatial Index](#spatial-index) · [R-Tree](#r-tree) · [Quadtree](#quadtree)

---

## Map Tile Pyramid

A **hierarchical multi-resolution grid structure** used by digital mapping systems (Google Maps, OpenStreetMap, Mapbox) that projects the spherical surface of the Earth onto a flat 2D plane and recursively partitions it into a pyramid of square tiles (typically 256x256 or 512x512 pixels) across discrete zoom levels.

### Key Characteristics
- **Zoom level hierarchy**: Zoom Level 0 represents the entire Earth in a single tile ($1 \times 1 = 1$). Each increment in zoom level quadruples the tile count ($2^z \times 2^z$ tiles at zoom level $z$)
- **Web Mercator Projection (EPSG:3857)**: Standard conformal cylindrical map projection mapping global coordinates to a square bounding box
- **Tile coordinate addressing**: Each tile is addressed via an $(x, y, z)$ tuple or quadkey string
- **Aggressive CDN caching**: Immutable tile assets are cached indefinitely on edge CDNs, allowing millions of concurrent client pan/zoom operations without hitting backend database servers

### When to Use
- Interactive web and mobile map rendering engines
- Large-scale geospatial image and satellite imagery distribution
- Heatmap and tile overlay visualization layers

### When NOT to Use
- Polar scientific research stations requiring accurate spatial area measurements (where Mercator extreme area distortion near the poles is unacceptable)
- Offline embedded devices with strict storage limits unable to store multi-gigabyte tile pyramids

### Also see
- [Vector Tiles](#vector-tiles) · [Geocoding](#geocoding) · [CDN](../reference-dictionary/networking.md#cdn)

---

## Vector Tiles

A **modern geographic data packaging and delivery format** that packages raw vector map geometries (points, lines, polygons, road labels) into compact binary Protocol Buffer tiles (`.mvt` / `.pbf`) rather than pre-rendered raster bitmap images (PNG/JPEG).

### Key Characteristics
- **Client-side GPU rendering**: Client applications (via WebGL or Metal) render raw geometries and apply dynamic styling on the fly
- **Dynamic styling & theming**: Enables instant switching between light, dark, satellite, and custom brand themes without re-downloading map tiles
- **Compact size**: Vector tile payloads are typically 4–10x smaller than equivalent raster image tiles
- **Smooth vector scaling**: Supports smooth fractional zoom and 3D camera tilting/rotation without pixelation or blurry label artifacts

### When to Use
- Modern interactive web and mobile navigation apps (Google Maps, Apple Maps, Mapbox GL)
- Applications requiring dynamic, user-configurable map layers, runtime traffic coloring, or custom feature highlighting
- Low-bandwidth mobile mapping where bandwidth conservation is vital

### When NOT to Use
- Legacy client browsers lacking WebGL / GPU hardware acceleration
- Complex satellite and aerial photographic imagery (which are inherently raster data)

### Also see
- [Map Tile Pyramid](#map-tile-pyramid) · [Geocoding](#geocoding)

---

## Geocoding

The **computational process of converting human-readable textual addresses or landmark names** (e.g., "1600 Amphitheatre Parkway, Mountain View, CA") into geographic coordinates (Latitude: 37.422, Longitude: -122.084).

### Key Characteristics
- **Address parsing & normalization**: Tokenizes unstructured address strings, expanding abbreviations ("St" → "Street") and correcting misspellings
- **Spatial interpolation**: Uses road centerline databases and street address ranges to estimate the coordinate position along a street segment
- **Fuzzy matching**: Employs trie-based autocomplete and n-gram similarity scoring to match ambiguous or partial place queries
- **Cache-heavy architecture**: Frequently queried addresses and coordinate pairs are heavily cached in Redis/Memcached to reduce compute load

### When to Use
- Address autocompletion in e-commerce checkout and delivery apps
- Converting search queries (e.g., "coffee shops near Central Park") into spatial search origins
- Spatial tagging and location enrichment in business analytics

### When NOT to Use
- Direct point-to-point pathfinding when exact coordinate lat/long pairs are already available
- Low-latency real-time telemetry where converting every GPS ping into an address string causes unnecessary throughput bottlenecks

### Also see
- [Reverse Geocoding](#reverse-geocoding) · [Spatial Index](#spatial-index) · [Map Tile Pyramid](#map-tile-pyramid) · [Trie (Prefix Tree)](databases.md#trie-prefix-tree)

---

## Reverse Geocoding

The **process of converting geographic coordinate pairs (latitude and longitude)** into a human-readable street address, landmark name, or administrative boundary (neighborhood, city, country).

### Key Characteristics
- **Point-in-polygon containment**: Tests coordinate pings against administrative polygon boundaries (country, state, postal code)
- **Nearest road segment matching**: Snaps raw GPS points to the nearest road centerline to determine the street name and interpolated house number
- **Spatial index acceleration**: Queries spatial R-Trees or grid cells to restrict reverse lookup candidates to a small localized bounding box
- **GPS drift handling**: Uses map matching algorithms (Hidden Markov Models) to filter out noisy GPS telemetry

### When to Use
- Converting mobile GPS pings into rider pickup / driver dropoff street addresses in ride-hailing apps
- Tagging photos and user check-ins with recognizable place names
- Fleet tracking dashboards displaying readable vehicle locations

### When NOT to Use
- High-frequency GPS telemetry streams where only numeric coordinates are needed for route calculation
- Server-to-server spatial calculations where lat/long coordinates are sufficient

### Also see
- [Geocoding](#geocoding) · [Spatial Index](#spatial-index) · [R-Tree](#r-tree)

---

## Haversine Distance

A mathematical formula that calculates the **great-circle distance between two points on the surface of a sphere** given their longitudes and latitudes.

$$\Delta\sigma = 2 \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)}\right)$$
$$d = R \cdot \Delta\sigma$$

Where $\phi_1, \phi_2$ are latitudes, $\lambda_1, \lambda_2$ are longitudes (in radians), and $R$ is Earth's mean radius (~6,371 km).

### Key Characteristics
- **Spherical earth approximation**: Accurate to within ~0.5% for most everyday geographic distances
- **Trigonometric computation**: Involves multiple trigonometric operations ($\sin, \cos, \arcsin, \sqrt{}$), making it computationally heavier than Euclidean distance
- **Well-conditioned for small distances**: Avoids numerical cancellation errors for nearby points compared to the simpler Law of Cosines

### When to Use
- Calculating exact straight-line distance between two GPS coordinates (e.g., rider and driver)
- Radius filtering ("is distance $\le 5\text{ km}$?") after rough grid candidate selection
- Location-based distance sorting for search results

### When NOT to Use
- Driving distance/time routing (use graph pathfinding like Dijkstra/A* or contraction hierarchies over road networks)
- High-precision ellipsoidal geodesic surveys across thousands of kilometers (use Vincenty's formula)

### Also see
- [Spatial Index](#spatial-index) · [Geohashing](#geohashing) · [Redis Geospatial](#redis-geospatial)

---

## Redis Geospatial

Redis's built-in support for storing and querying geographic coordinates (longitude, latitude) with radius-based, distance-based, and bounding-box queries. Uses a Geohash-based encoding: coordinates are interleaved into a 52-bit integer, enabling sorted-set-style range queries.

### Key Characteristics
- **Geohash encoding**: Coordinates stored as 52-bit integers in a Sorted Set — GEO commands (`GEOADD`, `GEODIST`, `GEOSEARCH`) are thin wrappers over ZSET operations
- **Proximity queries**: `GEOSEARCH` (and legacy `GEORADIUS`) find members within a given circular radius or rectangular bounding box
- **Distance calculation**: `GEODIST` computes Haversine distance between two members
- **Sorted Set compatible**: All standard ZSET commands (`ZRANGE`, `ZREM`, `ZCARD`) work seamlessly on GEO keys

### When to Use
- Find nearest drivers, stores, or restaurants to a user's current location in real-time
- Geofencing: detect when a device enters or leaves a proximity radius
- Low-latency, high-throughput in-memory proximity lookup and rider-driver matching

### When NOT to Use
- Complex spatial queries (arbitrary polygon intersection, multi-polygon spatial joins — use PostGIS)
- High-precision coordinate storage (Geohash loses precision at extreme polar latitudes)
- When querying requires composite multi-attribute relational filtering (use a spatial relational database)

### Real-World Examples
- **Uber Eats restaurant search**: Stores restaurant locations in a GEO key — `GEOSEARCH` finds all restaurants within 3 km of a user in sub-millisecond time. Driver locations stored in a separate GEO key for nearest-driver matching.
- **Tinder proximity matching**: Stores user locations as GEO members — discovers potential matches within a configurable radius. ZSET compatibility ensures `ZREM` instantly purges users who log off.

### Also see
- [Geohashing](#geohashing) · [Spatial Index](#spatial-index) · [Haversine Distance](#haversine-distance) · [Redis Sorted Sets](../reference-dictionary/caching.md#redis-sorted-sets)

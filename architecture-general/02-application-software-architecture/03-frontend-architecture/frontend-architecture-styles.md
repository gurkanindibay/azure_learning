# Frontend Architecture Styles

## Table of Contents

- [Overview](#overview)
- [1. Single Page Application (SPA)](#1-single-page-application-spa)
- [2. Server-Side Rendering & Static Generation (SSR/SSG/ISR)](#2-server-side-rendering--static-generation-ssrssgisr)
- [3. Micro-Frontend Architecture](#3-micro-frontend-architecture)
- [Architecture Comparison](#architecture-comparison)
- [Decision Guide](#decision-guide)
- [References](#references)

---

## Overview

Frontend architecture styles define how user interfaces are structured, rendered, and delivered to users. Choosing the right frontend architecture impacts:

- **Performance** - Initial load time, interactivity, and perceived speed
- **SEO** - Search engine discoverability and indexing
- **User Experience** - Navigation, responsiveness, and offline capabilities
- **Developer Experience** - Development workflow, debugging, and deployment
- **Scalability** - Team organization and codebase growth

---

## 1. Single Page Application (SPA)

### Definition

A **Single Page Application (SPA)** is a web application that loads a single HTML page and dynamically updates content as the user interacts with the app, without full page reloads.

### Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SPA Architecture                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Initial Load                                                      │
│   ┌─────────┐         ┌─────────────────┐                          │
│   │ Browser │──GET───►│   Web Server    │                          │
│   │         │◄────────│  (Static Host)  │                          │
│   └─────────┘  HTML   └─────────────────┘                          │
│       │        + JS                                                 │
│       │        + CSS                                                │
│       ▼                                                             │
│   ┌─────────────────────────────────────────────────────────┐      │
│   │                JavaScript Application                    │      │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │      │
│   │  │ Router  │  │  State  │  │  Views  │  │  API    │    │      │
│   │  │         │  │ Manager │  │(Compon- │  │ Client  │    │      │
│   │  │         │  │         │  │  ents)  │  │         │    │      │
│   │  └─────────┘  └─────────┘  └─────────┘  └────┬────┘    │      │
│   └──────────────────────────────────────────────┼──────────┘      │
│                                                  │                  │
│   Subsequent Interactions                        │                  │
│   ┌─────────┐                              ┌─────▼─────┐            │
│   │ Browser │◄───────JSON─────────────────►│  REST/    │            │
│   │   DOM   │      (No page reload)        │  GraphQL  │            │
│   └─────────┘                              │    API    │            │
│                                            └───────────┘            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### SPA Lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SPA Request Lifecycle                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. Initial Page Load                                               │
│     Browser ──► Request index.html                                  │
│              ◄── Receive HTML shell + JS bundle                     │
│              ──► Download JS, CSS, assets                           │
│              ◄── Parse and execute JavaScript                       │
│              ──► API call for initial data                          │
│              ◄── Receive JSON data                                  │
│              ──► Render UI in browser (Client-Side Rendering)       │
│                                                                      │
│  2. Navigation (Route Change)                                       │
│     User clicks link ──► Router intercepts                          │
│                      ──► Update URL (History API)                   │
│                      ──► Fetch data if needed                       │
│                      ──► Re-render components                       │
│                      (No full page reload!)                         │
│                                                                      │
│  3. User Interaction                                                │
│     User action ──► Update local state                              │
│                 ──► API call (if needed)                            │
│                 ──► Update DOM (Virtual DOM diff)                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### SPA Frameworks

| Framework | Language | Key Features |
|-----------|----------|--------------|
| **React** | JavaScript/TypeScript | Virtual DOM, Component-based, Hooks |
| **Vue.js** | JavaScript/TypeScript | Reactive, Template-based, Easy learning curve |
| **Angular** | TypeScript | Full framework, Dependency Injection, RxJS |
| **Svelte** | JavaScript/TypeScript | Compile-time, No virtual DOM, Small bundles |
| **Solid** | JavaScript/TypeScript | Fine-grained reactivity, React-like syntax |

### State Management Patterns

```
┌─────────────────────────────────────────────────────────────────────┐
│                  SPA State Management Patterns                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. Component State (Local)                                         │
│     ┌─────────────┐                                                 │
│     │  Component  │  useState, reactive data                        │
│     │   State     │  Good for: UI state, form inputs                │
│     └─────────────┘                                                 │
│                                                                      │
│  2. Lifted State (Prop Drilling)                                    │
│     ┌─────────────┐                                                 │
│     │   Parent    │──state──┐                                       │
│     └─────────────┘         │                                       │
│           │                 ▼                                       │
│     ┌─────┴─────┐    ┌─────────────┐                               │
│     │   Child   │    │   Child     │  Props down, events up        │
│     └───────────┘    └─────────────┘                               │
│                                                                      │
│  3. Context / Provide-Inject                                        │
│     ┌─────────────┐                                                 │
│     │  Provider   │  React Context, Vue Provide/Inject              │
│     └──────┬──────┘  Good for: Theme, Auth, Localization            │
│            │                                                        │
│     ┌──────┴──────┐                                                 │
│     │  Consumer   │  Any nested component can access                │
│     └─────────────┘                                                 │
│                                                                      │
│  4. Global State Store                                              │
│     ┌─────────────────────────────────────────┐                    │
│     │              Store                       │                    │
│     │  ┌─────────┐  ┌─────────┐  ┌─────────┐ │                    │
│     │  │  State  │  │ Actions │  │Reducers │ │                    │
│     │  └─────────┘  └─────────┘  └─────────┘ │                    │
│     └─────────────────────────────────────────┘                    │
│     Redux, Vuex/Pinia, Zustand, MobX                               │
│     Good for: Complex app state, server cache                       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Routing in SPAs

```javascript
// Example: React Router
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/products" element={<Products />} />
        <Route path="/products/:id" element={<ProductDetail />} />
        <Route path="/checkout" element={<Checkout />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}
```

### Advantages

- ✅ Fluid, app-like user experience
- ✅ Fast navigation after initial load
- ✅ Rich interactivity and animations
- ✅ Reduced server load (static hosting)
- ✅ Works well with REST/GraphQL APIs
- ✅ Good for complex, interactive applications

### Disadvantages

- ❌ Poor SEO (content not in initial HTML)
- ❌ Slow initial load (large JS bundles)
- ❌ Blank screen until JS executes
- ❌ Requires JavaScript to function
- ❌ Memory management challenges
- ❌ Browser history/back button complexity

### When to Use

- Internal applications / dashboards
- Applications behind authentication
- Complex interactive applications
- Real-time collaborative tools
- When SEO is not critical

---

## 2. Server-Side Rendering & Static Generation (SSR/SSG/ISR)

### Definition

**Static Site Generation (SSG)** pre-renders HTML pages at build time, creating static files that can be served from a CDN. **Server-Side Rendering (SSR)** generates HTML on the server for each request, delivering fully rendered pages to the browser. **Incremental Static Regeneration (ISR)** combines static generation with on-demand regeneration, allowing pages to be updated after deployment without a full rebuild.

### Rendering Strategies Comparison

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Rendering Strategy Spectrum                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Static Site         ISR              SSR              CSR (SPA)    │
│  Generation                                                          │
│       │               │                │                 │           │
│       ▼               ▼                ▼                 ▼           │
│  ┌─────────┐    ┌─────────┐      ┌─────────┐      ┌─────────┐      │
│  │ Build   │    │ Build + │      │ Request │      │ Browser │      │
│  │  Time   │    │ Runtime │      │  Time   │      │ Runtime │      │
│  └─────────┘    └─────────┘      └─────────┘      └─────────┘      │
│                                                                      │
│  • Blog posts    • E-commerce     • User-specific   • Dashboards   │
│  • Docs            product pages    content         • Admin panels │
│  • Marketing     • News sites     • Real-time data  • SPAs         │
│    pages                          • Personalization                 │
│                                                                      │
│  ◄──────────────────────────────────────────────────────────────►  │
│   Faster TTFB                                    More Dynamic       │
│   Better Caching                                 More Flexible      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### SSR Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SSR Architecture                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Request Flow                                                      │
│   ┌─────────┐       ┌─────────────────────────────────────────┐    │
│   │         │       │           SSR Server                     │    │
│   │ Browser │──────►│  ┌─────────────────────────────────┐    │    │
│   │         │       │  │        Request Handler           │    │    │
│   └─────────┘       │  └──────────────┬──────────────────┘    │    │
│       ▲             │                 │                        │    │
│       │             │  ┌──────────────▼──────────────────┐    │    │
│       │             │  │      Data Fetching              │    │    │
│       │             │  │  (getServerSideProps / loader)  │    │    │
│       │             │  └──────────────┬──────────────────┘    │    │
│       │             │                 │                        │    │
│       │             │  ┌──────────────▼──────────────────┐    │    │
│       │             │  │     Component Rendering         │    │    │
│       │             │  │     (React/Vue on Server)       │    │    │
│       │             │  └──────────────┬──────────────────┘    │    │
│       │             │                 │                        │    │
│       │             │  ┌──────────────▼──────────────────┐    │    │
│       │             │  │      HTML Generation            │    │    │
│       │             │  │   (renderToString / renderSSR)  │    │    │
│       │             │  └──────────────┬──────────────────┘    │    │
│       │             └─────────────────┼────────────────────────┘    │
│       │                               │                             │
│       └───────────────────────────────┘                             │
│                    Full HTML Response                               │
│                                                                      │
│   Hydration (Client-Side)                                           │
│   ┌─────────────────────────────────────────────────────────┐      │
│   │  1. Browser receives fully rendered HTML                 │      │
│   │  2. Page is immediately visible                          │      │
│   │  3. JavaScript loads and "hydrates" the page            │      │
│   │  4. Page becomes interactive (event handlers attached)   │      │
│   └─────────────────────────────────────────────────────────┘      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### SSR vs SSG vs ISR

| Aspect | SSG (Static) | SSR (Server) | ISR (Incremental) |
|--------|--------------|--------------|-------------------|
| **When Rendered** | Build time | Each request | Build + Revalidate |
| **Performance** | Fastest (CDN) | Slower (server) | Fast (cached) |
| **Data Freshness** | Stale until rebuild | Always fresh | Configurable |
| **Server Load** | None (static files) | High | Low (cached) |
| **Build Time** | Long for large sites | N/A | Short |
| **Use Case** | Static content | Dynamic content | Semi-dynamic |

### ISR (Incremental Static Regeneration)

```
┌─────────────────────────────────────────────────────────────────────┐
│                     ISR Flow                                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Build Time:                                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Pre-render popular pages → Cache with revalidate: 60s      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  Request 1 (within 60s):                                            │
│  ┌────────┐    ┌─────────┐    ┌────────┐                           │
│  │ User A │───►│   CDN   │───►│ Cached │  Instant response         │
│  └────────┘    └─────────┘    │  Page  │                           │
│                               └────────┘                           │
│                                                                      │
│  Request 2 (after 60s - stale):                                     │
│  ┌────────┐    ┌─────────┐    ┌────────┐                           │
│  │ User B │───►│   CDN   │───►│ Stale  │  Return stale (fast)      │
│  └────────┘    └─────────┘    │  Page  │                           │
│                    │          └────────┘                           │
│                    │                                                │
│                    └──────────► Trigger background regeneration    │
│                                      │                              │
│                               ┌──────▼──────┐                      │
│                               │   Server    │                      │
│                               │ Re-renders  │                      │
│                               │   Page      │                      │
│                               └──────┬──────┘                      │
│                                      │                              │
│                               ┌──────▼──────┐                      │
│                               │ Update CDN  │                      │
│                               │   Cache     │                      │
│                               └─────────────┘                      │
│                                                                      │
│  Request 3 (after regeneration):                                    │
│  ┌────────┐    ┌─────────┐    ┌────────┐                           │
│  │ User C │───►│   CDN   │───►│ Fresh  │  Updated content          │
│  └────────┘    └─────────┘    │  Page  │                           │
│                               └────────┘                           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### SSR Frameworks

| Framework | Base | Key Features |
|-----------|------|--------------|
| **Next.js** | React | SSR, SSG, ISR, API routes, App Router |
| **Nuxt.js** | Vue | SSR, SSG, Auto-imports, Modules |
| **SvelteKit** | Svelte | SSR, SSG, Adapters, Load functions |
| **Remix** | React | SSR, Nested routing, Progressive enhancement |
| **Astro** | Multi | Islands architecture, Zero JS by default |
| **Qwik** | Custom | Resumability, Fine-grained lazy loading |

### Code Example: Next.js

```typescript
// pages/products/[id].tsx (Next.js Pages Router)

// SSR - runs on every request
export async function getServerSideProps({ params }) {
  const product = await fetchProduct(params.id);
  return { props: { product } };
}

// SSG - runs at build time
export async function getStaticProps({ params }) {
  const product = await fetchProduct(params.id);
  return { 
    props: { product },
    revalidate: 60 // ISR: regenerate every 60 seconds
  };
}

// Generate static paths for SSG
export async function getStaticPaths() {
  const products = await fetchAllProducts();
  return {
    paths: products.map(p => ({ params: { id: p.id } })),
    fallback: 'blocking' // Generate on-demand if not pre-built
  };
}

export default function ProductPage({ product }) {
  return (
    <div>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
    </div>
  );
}
```

### Streaming SSR

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Streaming SSR                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Traditional SSR:                                                   │
│  ┌────────────────────────────────────────────────────┐            │
│  │ Fetch All Data → Render All → Send Complete HTML   │            │
│  └────────────────────────────────────────────────────┘            │
│  User waits for everything...                                       │
│                                                                      │
│  Streaming SSR:                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Time ──────────────────────────────────────────────────►   │   │
│  │                                                              │   │
│  │  ┌────────┐                                                  │   │
│  │  │ Shell  │ ← Sent immediately (header, layout)             │   │
│  │  └────────┘                                                  │   │
│  │       │                                                      │   │
│  │       ├──────┬──────┬──────┐                                │   │
│  │       │      │      │      │                                │   │
│  │  ┌────▼──┐ ┌─▼──┐ ┌─▼──┐ ┌─▼──┐                            │   │
│  │  │Content│ │Slow│ │Fast│ │User│ ← Streamed as ready        │   │
│  │  │  A    │ │API │ │API │ │Data│                            │   │
│  │  └───────┘ └────┘ └────┘ └────┘                            │   │
│  │                                                              │   │
│  │  <Suspense fallback={<Skeleton />}>                         │   │
│  │    <SlowComponent />  ← Shows skeleton, then real content   │   │
│  │  </Suspense>                                                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Advantages

- ✅ Excellent SEO (content in initial HTML)
- ✅ Fast First Contentful Paint (FCP)
- ✅ Works without JavaScript (graceful degradation)
- ✅ Better performance on slow devices
- ✅ Social media preview support (meta tags)
- ✅ ISR combines benefits of static and dynamic

### Disadvantages

- ❌ Higher server costs (vs static)
- ❌ Slower Time to First Byte (TTFB) for SSR
- ❌ More complex deployment
- ❌ Hydration can cause UI flicker
- ❌ Server/client code boundary complexity

### When to Use

- Content-heavy websites (blogs, news, e-commerce)
- SEO-critical applications
- Marketing and landing pages
- Applications requiring fast initial load
- When content changes frequently (SSR) or periodically (ISR)

---

## 3. Micro-Frontend Architecture

### Definition

**Micro-Frontend Architecture** extends microservices principles to the frontend, decomposing a monolithic frontend into smaller, independently deployable applications owned by different teams.

### Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│                  Micro-Frontend Architecture                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│                        Container / Shell                            │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │  ┌─────────────────────────────────────────────────────┐    │  │
│   │  │                    App Shell                         │    │  │
│   │  │  • Routing  • Auth  • Navigation  • Layout          │    │  │
│   │  └─────────────────────────────────────────────────────┘    │  │
│   │                                                              │  │
│   │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │  │
│   │  │   Product   │ │    Cart     │ │   Checkout  │           │  │
│   │  │   Catalog   │ │   Widget    │ │     App     │           │  │
│   │  │    (MFE)    │ │    (MFE)    │ │    (MFE)    │           │  │
│   │  │             │ │             │ │             │           │  │
│   │  │  Team: A    │ │  Team: B    │ │  Team: C    │           │  │
│   │  │  React      │ │  Vue        │ │  Angular    │           │  │
│   │  └─────────────┘ └─────────────┘ └─────────────┘           │  │
│   │                                                              │  │
│   └─────────────────────────────────────────────────────────────┘  │
│                                                                      │
│   Each MFE:                                                         │
│   • Independently deployable                                        │
│   • Own repository and CI/CD                                        │
│   • Own technology choice                                           │
│   • Owned by autonomous team                                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Integration Approaches

```
┌─────────────────────────────────────────────────────────────────────┐
│              Micro-Frontend Integration Approaches                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. Build-Time Integration (NPM Packages)                           │
│     ┌─────────────────────────────────────────────────────────┐    │
│     │  npm install @company/product-catalog                    │    │
│     │  npm install @company/cart-widget                        │    │
│     │                                                          │    │
│     │  + Simple, type-safe                                     │    │
│     │  - Must rebuild container for updates                    │    │
│     │  - Coupled release cycles                                │    │
│     └─────────────────────────────────────────────────────────┘    │
│                                                                      │
│  2. Runtime Integration (Module Federation)                         │
│     ┌─────────────────────────────────────────────────────────┐    │
│     │  // webpack.config.js (Container)                        │    │
│     │  new ModuleFederationPlugin({                            │    │
│     │    remotes: {                                            │    │
│     │      productApp: 'product@http://products.example/mf.js',│    │
│     │      cartApp: 'cart@http://cart.example/mf.js'          │    │
│     │    }                                                     │    │
│     │  })                                                      │    │
│     │                                                          │    │
│     │  + Independent deployments                               │    │
│     │  + Runtime flexibility                                   │    │
│     │  - More complex setup                                    │    │
│     └─────────────────────────────────────────────────────────┘    │
│                                                                      │
│  3. Server-Side Composition                                         │
│     ┌─────────────────────────────────────────────────────────┐    │
│     │  Edge/Server composes HTML from multiple sources         │    │
│     │                                                          │    │
│     │  ┌─────────┐    ┌─────────────────────────────────┐     │    │
│     │  │  Edge   │───►│ Fetch fragments from MFE servers│     │    │
│     │  │ Server  │    │ Combine into single HTML        │     │    │
│     │  └─────────┘    └─────────────────────────────────┘     │    │
│     │                                                          │    │
│     │  + Better SEO, faster initial load                       │    │
│     │  - Server complexity                                     │    │
│     └─────────────────────────────────────────────────────────┘    │
│                                                                      │
│  4. iframe Integration                                              │
│     ┌─────────────────────────────────────────────────────────┐    │
│     │  <iframe src="https://checkout.example.com" />           │    │
│     │                                                          │    │
│     │  + Complete isolation                                    │    │
│     │  + Simple integration                                    │    │
│     │  - Poor UX (separate contexts)                           │    │
│     │  - Communication overhead                                │    │
│     └─────────────────────────────────────────────────────────┘    │
│                                                                      │
│  5. Web Components                                                  │
│     ┌─────────────────────────────────────────────────────────┐    │
│     │  <product-catalog products="..."></product-catalog>      │    │
│     │  <shopping-cart></shopping-cart>                         │    │
│     │                                                          │    │
│     │  + Framework agnostic                                    │    │
│     │  + Native browser support                                │    │
│     │  - Shadow DOM limitations                                │    │
│     │  - Styling challenges                                    │    │
│     └─────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Module Federation Example

```javascript
// products/webpack.config.js (Remote)
const ModuleFederationPlugin = require('webpack/lib/container/ModuleFederationPlugin');

module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: 'products',
      filename: 'remoteEntry.js',
      exposes: {
        './ProductList': './src/ProductList',
        './ProductDetail': './src/ProductDetail',
      },
      shared: ['react', 'react-dom'],
    }),
  ],
};

// shell/webpack.config.js (Host)
module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: 'shell',
      remotes: {
        products: 'products@http://localhost:3001/remoteEntry.js',
        cart: 'cart@http://localhost:3002/remoteEntry.js',
      },
      shared: ['react', 'react-dom'],
    }),
  ],
};

// shell/src/App.js
const ProductList = React.lazy(() => import('products/ProductList'));
const Cart = React.lazy(() => import('cart/CartWidget'));

function App() {
  return (
    <div>
      <Suspense fallback={<Loading />}>
        <ProductList />
        <Cart />
      </Suspense>
    </div>
  );
}
```

### Communication Between Micro-Frontends

```
┌─────────────────────────────────────────────────────────────────────┐
│           Micro-Frontend Communication Patterns                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. Custom Events (Pub/Sub)                                         │
│     ┌─────────────────────────────────────────────────────────┐    │
│     │  // Publisher (Product MFE)                              │    │
│     │  window.dispatchEvent(new CustomEvent('add-to-cart', {  │    │
│     │    detail: { productId: '123', quantity: 1 }            │    │
│     │  }));                                                    │    │
│     │                                                          │    │
│     │  // Subscriber (Cart MFE)                                │    │
│     │  window.addEventListener('add-to-cart', (e) => {        │    │
│     │    addToCart(e.detail);                                 │    │
│     │  });                                                     │    │
│     └─────────────────────────────────────────────────────────┘    │
│                                                                      │
│  2. Shared State (Event Bus)                                        │
│     ┌─────────────────────────────────────────────────────────┐    │
│     │  // Shared event bus                                     │    │
│     │  const eventBus = new EventEmitter();                   │    │
│     │  window.__MFE_EVENT_BUS__ = eventBus;                   │    │
│     │                                                          │    │
│     │  // Usage in MFEs                                        │    │
│     │  eventBus.emit('user:logged-in', { userId: '123' });    │    │
│     │  eventBus.on('user:logged-in', handleLogin);            │    │
│     └─────────────────────────────────────────────────────────┘    │
│                                                                      │
│  3. Props/Callbacks (Parent-Child)                                  │
│     ┌─────────────────────────────────────────────────────────┐    │
│     │  // Shell passes data and callbacks                      │    │
│     │  <ProductMFE                                             │    │
│     │    user={currentUser}                                    │    │
│     │    onAddToCart={handleAddToCart}                        │    │
│     │  />                                                      │    │
│     └─────────────────────────────────────────────────────────┘    │
│                                                                      │
│  4. URL/Query Parameters                                            │
│     ┌─────────────────────────────────────────────────────────┐    │
│     │  // MFEs read shared state from URL                      │    │
│     │  /products?category=electronics&sort=price               │    │
│     │                                                          │    │
│     │  // Good for: Deep linking, bookmarking                  │    │
│     └─────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Shared Dependencies

```
┌─────────────────────────────────────────────────────────────────────┐
│                Handling Shared Dependencies                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Problem: Multiple MFEs loading same libraries                      │
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │  Product    │  │    Cart     │  │  Checkout   │                 │
│  │   MFE       │  │    MFE      │  │    MFE      │                 │
│  │             │  │             │  │             │                 │
│  │ React 18    │  │ React 18   │  │ React 18   │  ← Loaded 3x!   │
│  └─────────────┘  └─────────────┘  └─────────────┘                 │
│                                                                      │
│  Solution: Module Federation Shared Config                          │
│                                                                      │
│  shared: {                                                          │
│    react: {                                                         │
│      singleton: true,        // Only one instance                   │
│      requiredVersion: '^18', // Version constraint                  │
│      eager: false            // Lazy load                           │
│    },                                                               │
│    'react-dom': { singleton: true },                                │
│    '@company/design-system': { singleton: true }                    │
│  }                                                                  │
│                                                                      │
│  Result: Single shared instance                                     │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │              Shared Dependencies Layer                   │       │
│  │        React 18 │ Design System │ Utils                 │       │
│  └─────────────────────────────────────────────────────────┘       │
│        ▲                ▲                ▲                          │
│        │                │                │                          │
│  ┌─────┴───┐      ┌─────┴───┐      ┌─────┴───┐                    │
│  │ Product │      │  Cart   │      │Checkout │                    │
│  └─────────┘      └─────────┘      └─────────┘                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Advantages

- ✅ Independent team deployments
- ✅ Technology flexibility per team
- ✅ Scalable for large organizations
- ✅ Isolated failures
- ✅ Incremental upgrades possible
- ✅ Parallel development

### Disadvantages

- ❌ Increased complexity
- ❌ Potential duplicate dependencies
- ❌ Inconsistent UX if not careful
- ❌ Cross-MFE communication overhead
- ❌ Harder debugging across boundaries
- ❌ Performance overhead (multiple bundles)

### When to Use

- Large organizations with multiple teams
- Complex applications with distinct domains
- When teams need technology autonomy
- Legacy migration (strangler fig pattern)
- When independent deployment is critical

---

## Architecture Comparison

### Feature Comparison Matrix

| Feature | SPA | SSR/ISR | Micro-Frontend |
|---------|-----|---------|----------------|
| **SEO** | Poor | Excellent | Varies |
| **Initial Load** | Slow | Fast | Varies |
| **Interactivity** | Excellent | Good | Good |
| **Complexity** | Medium | Medium | High |
| **Team Scalability** | Limited | Limited | Excellent |
| **Tech Flexibility** | Single | Single | Multiple |
| **Deployment** | Simple | Medium | Complex |

### Performance Metrics Comparison

| Metric | SPA | SSR | SSG | ISR |
|--------|-----|-----|-----|-----|
| **TTFB** | Fast | Slow | Fastest | Fast |
| **FCP** | Slow | Fast | Fastest | Fast |
| **TTI** | Slow | Medium | Fast | Fast |
| **Server Cost** | Low | High | Lowest | Medium |

**Abbreviations:**
- **TTFB** - Time to First Byte (time from request until the browser receives the first byte of response)
- **FCP** - First Contentful Paint (time until the browser renders the first piece of DOM content)
- **TTI** - Time to Interactive (time until the page is fully interactive and responds to user input)
- **SSG** - Static Site Generation (HTML pages are pre-rendered at build time)

---

## Decision Guide

```
┌─────────────────────────────────────────────────────────────────────┐
│                Frontend Architecture Decision Tree                   │
└─────────────────────────────────────────────────────────────────────┘

Start
  │
  ▼
Is SEO critical? ──Yes──► SSR/SSG/ISR (Next.js, Nuxt)
  │
  No
  │
  ▼
Large org with multiple ──Yes──► Micro-Frontends
frontend teams?
  │
  No
  │
  ▼
Content changes frequently? ──Yes──┬──► Real-time? ──► SSR
  │                                │
  │                                └──► Periodically? ──► ISR
  No
  │
  ▼
Static content (docs, blog)? ──Yes──► SSG (Astro, Next static)
  │
  No
  │
  ▼
Complex interactive app? ──Yes──► SPA (React, Vue, Angular)
  │
  No
  │
  ▼
Default ────────────────────────► SPA or SSR based on team preference
```

---

## References

- [React Documentation](https://react.dev/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Micro Frontends](https://micro-frontends.org/)
- [Module Federation](https://webpack.js.org/concepts/module-federation/)
- Jackson, C. (2019). *Micro Frontends* - Martin Fowler Blog
- [Web Vitals](https://web.dev/vitals/)

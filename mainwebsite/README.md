# AWS Info Website (React)

Single-page marketing site powered by **React 18 + Vite**. The app renders the AWS/DevOps content entirely on the client and uses the static assets in `public/` for typography, imagery, and scripts.

## Prerequisites

- Node.js 18+
- npm 9+

## Getting started

```bash
npm install
npm run dev
```

The development server runs on [http://localhost:3000](http://localhost:3000) and automatically reloads when files in `src/` change.

## Available scripts

| Command | Description |
| --- | --- |
| `npm run dev` | Start the Vite dev server. |
| `npm run build` | Create a production build in `dist/`. |
| `npm run preview` | Serve the contents of `dist/` locally for smoke-testing. |
| `npm run lint` | Run ESLint on `src/**/*.{ts,tsx}`. |
| `npm run type-check` | Validate TypeScript types without emitting JS. |

## Project structure

- `src/` – React components and pages.
- `public/` – Static assets (CSS, fonts, images, JS helpers). Anything placed here is served at the site root and can be referenced as `/images/...`.
- `index.html` – Vite entry document that wires in the legacy styles/scripts plus the React mount point.
- `vite.config.ts` – Vite + React plugin configuration (port, API proxies, build output).

## Building & deploying

1. Run `npm run build` to generate the optimized bundle in `dist/`.
2. Serve the `dist/` folder via any static host (S3 + CloudFront, Netlify, Vercel, etc.).

If the optional proxy routes in `vite.config.ts` are still needed, make sure they point at the correct backend host when deploying.

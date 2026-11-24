# Growthly

Growthly connects founders with growth partners who acquire paying customers for commissions. Sprint 0 provides a runnable English-language application and a shared starting point for engineering. You can browse both marketplace entry points. Workspace routes redirect to the sign-in information page.

## Run locally

Use Node.js 24 LTS and the pnpm version pinned in `package.json`. With Node 24 and Corepack installed, run:

```sh
corepack enable pnpm
pnpm install --frozen-lockfile
pnpm dev
```

Open <http://localhost:3000>. The app runs with no environment file. When working on a local integration, copy `.env.example` to `.env.local` and provide only the values that integration needs. Fonts ship with the app.

## Verify a change

```sh
pnpm format:check
pnpm lint
pnpm typecheck
pnpm build
pnpm exec playwright install --with-deps chromium
pnpm test:e2e
```

Type checking generates Next.js route types before calling TypeScript. Smoke tests start the built app on loopback port 3100 and close it afterwards. Set `PLAYWRIGHT_PORT` to a different free port for each concurrent worktree, for example `PLAYWRIGHT_PORT=3111 pnpm test:e2e`. Each suite starts its own server and rejects a port already in use. Rebuild after source changes. On machines with a restricted browser download, set `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH` to a compatible installed Chromium executable for the test command. CI uses the Playwright-managed browser. Use `pnpm format` to apply formatting.

## Project map

| Location                                | Start here for                                                                                        |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `src/app/`                              | Public pages, auth entry point, workspace routes, metadata, global styles                             |
| `src/features/`                         | Landing illustration, marketplace definitions and shared directory view, closed workspace entry point |
| `src/components/`                       | Shared brand and shadcn/ui primitives                                                                 |
| `supabase/`                             | Local Postgres, Auth and Storage configuration                                                        |
| `tests/smoke/` and `.github/workflows/` | Browser acceptance checks and CI                                                                      |
| `agents/`                               | Nine reusable role briefs governed by [AGENTS.md](AGENTS.md)                                          |

## Engineering references

- [Product scope and open decisions](docs/PRODUCT.md)
- [Architecture and route ownership](docs/ARCHITECTURE.md)
- [Database and local Supabase](docs/DATABASE.md)
- [Security boundaries](docs/SECURITY.md)
- [Design system](docs/DESIGN-SYSTEM.md)
- [Roadmap](ROADMAP.md), [backlog](docs/BACKLOG.md) and [changelog](CHANGELOG.md)

Vercel is the intended hosting platform. Its Next.js preset can use the lockfile and `pnpm build` with Node 24. Vercel Git deployments are disabled for `chore/project-foundation` in `vercel.json`. Sprint 0 uses local builds and GitHub Actions.

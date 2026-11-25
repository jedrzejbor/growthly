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

## Deployment hold

Automatic Git-triggered Vercel deployments are disabled for every branch, including `main`, until the founder approves a deployment. The repository uses the boolean `git.deploymentEnabled: false`. Vercel reads the configuration from the revision and project root it builds. Keep the repository disconnected while other branches or older revisions can lack this setting. [Vercel Git configuration](https://vercel.com/docs/project-configuration/git-configuration#turning-off-all-automatic-deployments)

Before merging, the maintainer should check the intended Vercel team's project list and Settings → Git for any project linked to `jedrzejbor/growthly`. For any existing link, confirm its root directory and production branch, and inspect Deploy Hooks, GitHub webhooks and CI workflows for independent deployment triggers. The repository flag governs Git integration; manual CLI/API deployments and hooks have separate controls. Resolve unexpected connections before merging.

Once the founder approves a target environment, DevOps should document the approved branches, permissions and preview/production settings in a separate PR. Review the Git configuration and external project settings together before connecting or enabling a deployment.

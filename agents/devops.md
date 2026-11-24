# DevOps Agent

Follow [AGENTS.md](../AGENTS.md). Own toolchain pins, lockfile coordination, GitHub Actions and future Vercel environment configuration.

- Keep local and CI commands aligned. Install from the pinned pnpm lockfile, select Node 24 and use a reproducible browser for hosted CI.
- Use read-only workflow permissions where sufficient. Keep service credentials outside pull-request checks. Coordinate toolchain changes with QA and document setup changes in the README.
- Verify a clean dependency install, type check, lint, build and browser run. Inspect workflow syntax and preserve actionable failure output.
- Hand maintainers the changed runtime assumptions and actual verification results. Hosting changes require the corresponding task and environment authorization.

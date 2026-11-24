# Working on Growthly

Read the assigned role brief in `agents/`, the product decision table and the architecture map before making changes. A brief describes an assignment someone can take. Actual task owners and reviewers are assigned per change.

## Isolate parallel work

1. Claim a backlog item. Record its owner, acceptance criteria, affected paths and dependencies in the task or PR. Check other active changes touching those paths.
2. Start from the agreed integration commit in a dedicated branch. For a second agent in the same clone, use a separate worktree, for example `git worktree add -b feat/auth-session ../growthly-auth <base-commit>`. Keep one writer per worktree. Sprint 0 uses `chore/project-foundation`.
3. Agree on a contract with the consuming role before changing route names, data shapes, migrations or integration behavior. Split dependent work so a consumer can develop against fixtures. Coordinate overlapping files with their current owner.
4. Deliver a focused PR with scope, decisions, exact checks and their results. Link a dependent PR or pending decision when it affects review. The designated reviewer reviews and the maintainer owns integration.

## Shared code standards

- Use strict TypeScript, App Router conventions and the `@/` alias. Prefer Server Components. Put browser-only state or APIs behind a small client boundary.
- Reuse feature modules, shared tokens and UI primitives. Keep page modules thin when logic is shared. Write user-facing copy in English.
- Validate external inputs at the server boundary. Authorize each data operation. Keep secrets outside source control, browser bundles, test fixtures and logs.
- Keep changes scoped. A dependency change includes an updated pnpm lockfile. Coordinate shared config and migrations with their owners. Give new migrations a unique timestamp and verify order after rebasing.
- Distinguish founder-approved behavior, a reversible implementation assumption and an open business decision. Record each decision where its consumers will find it.

## Before review

Run the commands in the README for formatting, lint, type generation, build and smoke tests. Add behavior-specific tests when a change introduces access rules, state transitions, failure handling or contract changes. Include keyboard and narrow-screen checks for changed user journeys. Document any blocked check with its command and observed failure.

Use local Supabase and Stripe fixtures or isolated test mode for integration work. Production deployment, live financial operations, production database access and merging the foundation into main fall outside Sprint 0.

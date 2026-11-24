# Database and storage

## Current state

`supabase/config.toml` defines a local Supabase project using PostgreSQL 17, Auth and Storage. The application has no database connection path, application schema, migrations, buckets or seed users. Both web and CI builds work without Docker or Supabase keys.

## Optional local development

With Docker running and the Supabase CLI installed (foundation config generated with 2.75.0), run these commands from the repository root:

```sh
supabase start
supabase status
supabase stop
```

The configured API uses `http://127.0.0.1:54321` and Postgres uses local port 54322. Inspect local service credentials privately. Only the API URL and publishable key belong in browser-visible settings. Keep the default project unlinked during local work.

## Proposed ownership model

These are discussion inputs for Sprint 1. Schema names, fields and relationships require review.

| Area          | Proposed relationship                                                                        | Decision dependency                             |
| ------------- | -------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| Identity      | Application profile references a Supabase Auth user ID. Trusted assignments represent roles. | Role combinations and assignment authority      |
| Discovery     | Campaigns belong to a founder. Partner profiles may have a public projection.                | Visibility, required fields, moderation         |
| Collaboration | A collaboration references a campaign and participating partner.                             | Cardinality and lifecycle                       |
| Attribution   | A recorded conversion links evidence to an eligible collaboration.                           | Event source, conflict resolution and retention |
| Money         | A commission references a conversion and an auditable calculation.                           | Currency, rate basis, refunds and settlement    |

## First migration workflow

Create a uniquely named migration with `supabase migration new <description>`. Review table keys, constraints, foreign keys and query indexes with Backend. Enable RLS and define least-privilege policies in the same migration as any exposed table. Include Storage object policies when introducing a bucket. Validate migrations on a disposable local instance using `supabase db reset --local` (this erases local data). Exercise anonymous, owner, unrelated user and privileged cases. Generate TypeScript schema types from the validated local database when a consumer exists. Commit SQL, types and the related policy tests together.

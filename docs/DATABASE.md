# Database and storage

## Current state

`supabase/config.toml` defines a local Supabase project using PostgreSQL 17, Auth and Storage. The application has no database connection path, application schema, migrations, buckets or seed users. Both web and CI builds work without Docker or Supabase keys.

## Optional local development

Use Docker Engine 28 or newer and Supabase CLI 2.75.0. Run the launcher in Bash on the machine hosting Docker (Linux, macOS with Docker Desktop, or WSL with local Docker integration). Pick a different slot from 1 to 99 for each active worktree on that host. Store it once in the ignored file at the worktree root.

```sh
printf '11\n' > .growthly-slot
scripts/local-supabase.sh start
scripts/local-supabase.sh ports
scripts/local-supabase.sh status
scripts/local-supabase.sh stop
```

The launcher derives the project and network names from the checkout's absolute path. Containers and volumes belong to that project. Slot 11 reserves ports 54110–54119. In general, the base is `54000 + 10 × slot`. The shadow database uses the base, API uses base + 1, Postgres uses base + 2, and the remaining ports cover Studio, mail, analytics, the edge inspector and pooler. A duplicate slot causes a bind conflict when both projects run. Keep each worktree's API URL and publishable key in its own `.env.local`. Inspect CLI status privately since it includes local secrets.

### Network boundary

CLI 2.75.0 accepts `--network-id` and leaves the host IP unspecified when it publishes ports. The launcher creates a dedicated Docker bridge with `com.docker.network.bridge.host_binding_ipv4=127.0.0.1`, verifies the bridge settings before startup, and checks the running containers' network and published addresses afterwards. An unexpected mapping stops that project. A bare CLI invocation fails config validation until the launcher supplies the worktree identity and DB port. Use the default Docker NAT mode with direct routing disabled. Docker daemon administrators can access local containers.

On a cloud development host, run the launcher there, keep inbound service ports closed and disable public IDE port forwarding. Use a private SSH tunnel if a developer needs the API, for example `ssh -N -L 127.0.0.1:54111:127.0.0.1:54111 developer@dev-host`. Check the actual mappings with `scripts/local-supabase.sh ports`. On Linux, inspect listeners with `ss -lnt` on the Docker host. Verify that the API responds on loopback and refuses connections on the host's LAN address. Docker can implement publishing through NAT without creating a listening socket, so check both mappings and connectivity. Host firewall and cloud ingress rules are managed separately.

[Supabase CLI startup source](https://github.com/supabase/cli/blob/v2.75.0/internal/start/start.go) · [Docker bridge binding and port publishing](https://docs.docker.com/engine/network/port-publishing/)

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

Create a uniquely named migration with `supabase migration new <description>`. Review table keys, constraints, foreign keys and query indexes with Backend. Enable RLS and define least-privilege policies in the same migration as any exposed table. Include Storage object policies when introducing a bucket. Validate migrations on a disposable local instance using `scripts/local-supabase.sh reset` (this erases local data). Exercise anonymous, owner, unrelated user and privileged cases. Generate TypeScript schema types from the validated local database when a consumer exists. Commit SQL, types and the related policy tests together.

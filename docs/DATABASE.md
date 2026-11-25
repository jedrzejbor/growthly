# Database and storage

## Current state

`supabase/config.toml` defines a local Supabase project using PostgreSQL 17, Auth and Storage. The application has no database connection path, application schema, migrations, buckets or seed users. Both web and CI builds work without Docker or Supabase keys.

## Optional local development

Use Bash, Python 3 and Supabase CLI 2.75.0 on the Linux Docker host. Supported configurations are described below. Pick a different slot from 1 to 99 for each active worktree on that host. Store it once in the ignored file at the worktree root.

```sh
printf '11\n' > .growthly-slot
scripts/local-supabase.sh start
scripts/local-supabase.sh ports
scripts/local-supabase.sh status
scripts/local-supabase.sh stop
```

The launcher derives the project and network names from the checkout's absolute path. Containers and volumes belong to that project. Slot 11 reserves ports 54110–54119. In general, the base is `54000 + 10 × slot`. The shadow database uses the base, API uses base + 1, Postgres uses base + 2, and the remaining ports cover Studio, mail, analytics, the edge inspector and pooler. A duplicate slot causes a bind conflict when both projects run. Keep each worktree's API URL and publishable key in its own `.env.local`. Inspect CLI status privately since it includes local secrets.

### Network boundary

The launcher creates a local IPv4 bridge with NAT, loopback publishing and explicit labels for the project, full worktree hash and port slot. It checks the labels, bridge options, membership of every project container and the complete endpoint list before reuse. Only the service names from CLI 2.75.0 and their configured loopback mappings are accepted. Bare CLI startup fails project configuration validation. Use the launcher for lifecycle commands.

Docker direct routing can expose **container IPs** even when the published host address is loopback. Two Linux configurations have verifiable boundaries:

- On a native Docker host (Engine 28.0.2+ with the iptables backend), a disposable, read-only BusyBox container runs `sleep` with dropped capabilities. Before starting Supabase the launcher checks the effective raw PREROUTING drop rule for its IP. After startup it checks the corresponding rule for every service IP. The BusyBox 1.37 image is pinned by multi-platform digest. The inspection uses `iptables -t raw -S PREROUTING` or read-only `sudo -n` access to that command. Unrecognized earlier firewall exemptions, trusted interfaces, routed gateway modes and missing drop rules block startup.
- For rootless Docker 28+, the launcher checks the local Unix socket peer and the daemon's process ancestry for RootlessKit using slirp4netns and its built-in port forwarder. This user-mode network has no inbound route from the host LAN to container IPs. The launcher still verifies all published sockets and network options. Other rootless configurations, remote sockets and hosts where routing cannot be verified must use a supported Linux development VM. Keep Docker administrator access restricted. An administrator with daemon or firewall access can change the boundary after a check.

### Shutdown and recovery

Use `scripts/local-supabase.sh stop` before removing or moving a worktree or changing its slot. It gracefully stops verified service containers, removes them by ID and removes the owned empty network by ID. Named database and storage volumes survive normal shutdown. Repeated stop is safe. A per-worktree file lock serializes lifecycle commands and releases on exit. The slot label detects an existing reservation on the daemon.

A failed start rolls back containers and named service volumes added during that attempt. An existing empty owned network or existing named volume survives rollback. If startup encounters an active project it verifies its state before returning. For partial state, stop the verified project before retrying. After a hard kill, rerun `stop` with the original checkout path and slot. Check `docker network inspect <network>`, the container labels and attachments if cleanup refuses. A foreign endpoint must first be detached by its owner. Never prune all networks or volumes to recover a worktree. For a legacy unlabeled network, its original owner must inspect and retire it separately. The launcher never adopts it.

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

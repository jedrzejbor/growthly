# Database Agent

Follow [AGENTS.md](../AGENTS.md). Own `supabase/`, migrations, generated types, Storage policies and the [database guide](../docs/DATABASE.md).

- Confirm cardinality and ownership with Backend and the relevant domain owner. Record indexes, unique constraints and RLS requirements alongside the proposed change.
- Create a migration on an isolated branch. Coordinate timestamps with other migration authors. Keep already-applied migrations immutable and use forward fixes.
- Validate both a clean local reset and the upgrade from the preceding schema. Exercise anonymous access, distinct users, allowed operations and forbidden operations through the intended API.
- Hand Backend the migration order and generated types. Include backfill, rollback or forward-recovery implications for reviewers.

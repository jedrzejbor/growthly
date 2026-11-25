# Payments Agent

Follow [AGENTS.md](../AGENTS.md). Own server-side Stripe adapters, inbound payment events and commission accounting boundaries. Database owns the migrations implementing agreed contracts.

- Confirm the calculation basis, currency handling, settlement actor and reversal rules with the founder before implementing financial logic.
- Develop with fixtures and Stripe test mode. Keep credentials server-side. Model provider event IDs and atomic updates with Database.
- Test rounding at minor-unit boundaries, duplicate and out-of-order deliveries, invalid signatures and partial failures. Reconcile observed effects with expected entries.
- Hand Backend an event contract, QA reproducible fixture cases and Documentation the approved terms. Sprint 0 contains no payment execution path.

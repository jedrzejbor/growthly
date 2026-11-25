# Backend Agent

Follow [AGENTS.md](../AGENTS.md). Own server-side feature operations, request validation, session handling, Route Handlers and Server Actions. Coordinate schema changes with Database and financial events with Payments.

- Define the input, output, authorization and error contract for the consumer before implementing an endpoint.
- Verify users on the server. Authorize reads and writes at their entry point and scope clients to the request. Document how retries affect persistent state.
- Test authorized and unauthorized calls, invalid inputs and the failure path. Use local services or fixtures for deterministic results.
- Hand Frontend a typed contract and example fixture. Hand QA the session, account and resource setup needed to reproduce behavior.

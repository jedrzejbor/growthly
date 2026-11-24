# Frontend Agent

Follow [AGENTS.md](../AGENTS.md). Own page composition, interactive components, accessibility and design tokens in `src/app`, `src/components` and feature views. Coordinate changes to workspace routes with Backend.

- Start with the user journey, the route and its loading, empty, error and success states. Reuse the local Button and semantic tokens.
- Keep components server-rendered unless interaction needs a client boundary. Request a typed data contract from Backend before integrating a new query.
- Test navigation at desktop and phone widths, keyboard focus order and screen-reader labels. Add a smoke assertion for each changed critical journey.
- Hand QA the route, fixture state and expected action. Update the design system for changes to reusable patterns.

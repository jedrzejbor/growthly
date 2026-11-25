# Architecture

Growthly starts as a single Next.js App Router application running on Node.js 24. One build keeps route types, UI and feature contracts together. Feature and route ownership provide parallel work boundaries until independent services have a demonstrated need.

## Implemented route map

| URL                                                            | Behavior in Sprint 0                      | Primary change owner                       |
| -------------------------------------------------------------- | ----------------------------------------- | ------------------------------------------ |
| `/`                                                            | Landing page with two discovery journeys  | Frontend                                   |
| `/campaigns`, `/partners`                                      | Public directory shells with empty states | Frontend, with Backend for future queries  |
| `/sign-in`                                                     | Explains workspace availability           | Frontend, with Backend for future sessions |
| `/dashboard/founder`, `/dashboard/partner`, `/dashboard/admin` | Redirect to sign-in                       | Backend for access, Frontend for views     |
| `/collaborations`, `/referrals`                                | Redirect to sign-in                       | Backend                                    |
| `/payments`, `/commissions`                                    | Redirect to sign-in                       | Payments                                   |

Route groups organize source without changing URLs. The seven reserved pages share one unconditional server redirect and access no data. The marketplace view reads local presentation metadata. Unknown URLs get the application 404.

## Extension boundaries

- **UI.** Route modules compose feature components. The root layout owns navigation, fonts and landmarks. Shared primitives live in `src/components/ui`. A domain can gain its own folder under `src/features/` when its first behavior lands.
- **Identity and data.** The planned request path is App Router server entry → verified Supabase user → authorized feature operation → PostgreSQL with RLS. Scope future clients to the request. Server Actions and Route Handlers need their own checks even when the page is protected. Supabase Auth and Storage are enabled in the local CLI config.
- **Attribution.** Referral handling will need a defined source of conversion evidence. Agree on identifiers and event contracts with Payments and Database before adding endpoints.
- **Money.** Keep the Stripe SDK on the server. A future webhook handler verifies the raw request and delegates to an idempotent persistence operation. Payment model and commission rules depend on founder approval.
- **Hosting.** The Next.js build is compatible with the Vercel Next.js preset. Keep CI independent of hosting credentials. Configure preview environments separately before introducing a deployment workflow.

## Contract handoff

The producer records fields, types, authorization, empty/error behavior and retry semantics in the task. The consumer reviews the shape and tests its use with a fixture. The Database Agent owns migrations and generated types. The Lead Architect resolves cross-feature conflicts and records accepted decisions.

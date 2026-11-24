# Security boundaries

## Foundation

Public content ships with the app. Workspace routes redirect before accessing session or business data. Sign-in collects no credentials. The repository contains a local Supabase template and blank environment fields. CI has read-only repository permissions and uses no service secrets.

## Controls required when features land

| Boundary             | Implementation expectation                                                                                                                                              | Verification                                                                      |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| Sessions and roles   | Verify identity server-side. Derive permissions from trusted assignments. Validate redirect destinations against local allowed paths.                                   | Anonymous, expired session, wrong role, owner and admin cases                     |
| Database and Storage | Apply RLS to exposed tables. Scope private objects to an authorized owner or collaboration. Keep service-role keys out of application clients.                          | Cross-account reads and writes denied through the API and Storage                 |
| Referral intake      | Validate untrusted payloads, limit retention of identifying evidence and deduplicate retries.                                                                           | Invalid, duplicate and conflicting events with local fixtures                     |
| Stripe               | Verify signatures against raw bodies. Persist provider event IDs with unique constraints. Apply financial transitions atomically and account for out-of-order delivery. | Signed test fixtures, invalid signatures, repeated deliveries and reversals       |
| Configuration        | Separate local, preview and production values. `NEXT_PUBLIC_` values can appear in browser assets. Keep private keys and webhook secrets server-only.                   | Review build output and diffs for credentials or sensitive logs before publishing |

Before introducing live data, resolve access, privacy and retention decisions in the product brief. Treat suspected credential exposure as an incident. Revoke or rotate the affected credential at the issuer, assess access logs, then remove the exposed value from affected artifacts.

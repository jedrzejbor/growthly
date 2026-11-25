# Engineering backlog

Recommended sequence for Sprint 1. Roles below identify suitable owners for assignment. Items that depend on a product decision stay pending until it is recorded.

| Item                                       | Suggested owner          | Dependency                                    | Acceptance evidence                                                                   |
| ------------------------------------------ | ------------------------ | --------------------------------------------- | ------------------------------------------------------------------------------------- |
| Agree on the identity and access matrix    | Lead Architect + founder | Founder input                                 | Sign-in method, role combinations, admin assignment and role-by-resource table agreed |
| Exercise local service lifecycle           | DevOps + QA              | Docker and Supabase CLI                       | Document versions and verify clean start, stop and reset on a disposable project      |
| Implement local profiles and roles         | Database + Security      | Approved access matrix                        | Repeatable migration, generated types and RLS tests for separate users                |
| Implement local auth session flow          | Backend + Frontend       | Approved sign-in method and identity contract | Login, logout, refresh and expired-session tests with local Auth                      |
| Open first authorized dashboard            | Frontend + Backend       | Verified session and RLS                      | Authorized role reaches its view, wrong role and anonymous visitor are denied         |
| Verify access regression suite             | QA + Security            | First identity slice                          | Desktop/mobile navigation and server/API denial cases pass in CI                      |
| Record discovery and attribution decisions | Documentation + founder  | Product discussion                            | Public fields, publication policy, attribution rules and outstanding issues recorded  |

Payments Agent can draft a test-fixture contract after conversion evidence, currency and commission rules are agreed. Live processing is outside this backlog.

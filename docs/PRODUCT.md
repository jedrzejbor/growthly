# Product scope

## Confirmed

Growthly is a performance-based SaaS marketplace. Founders seek paying customers. Growth partners acquire those customers for commissions. The application language is English, with a US and global target market.

The product scope includes public discovery, authentication, founder, growth partner and admin dashboards, campaign and partner marketplaces, collaborations, referral tracking, payments and commissions. Sprint 0 establishes entry points, tooling and collaboration conventions. It introduces no accounts, listings, tracked referrals or financial transactions.

## Working assumptions for the foundation

Public visitors can see directory shells. Both directories show an empty state. All three dashboard roles share a sign-in entry point. These reversible choices let designers and engineers test navigation before visibility and access policy are approved.

## Pending founder decisions

| Decision                                                                                                        | What depends on it                                                        |
| --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| Which sign-in methods, onboarding checks and combinations of roles are allowed? Who appoints admins?            | Identity model, access matrix and role assignment                         |
| Which campaign and partner fields are public, and who approves a listing?                                       | Public projections, publication states, moderation and storage visibility |
| How do parties start, accept and end a collaboration?                                                           | Membership rules, states and actor permissions                            |
| What establishes a paying conversion? Which attribution window, conflicts and refund rules apply?               | Referral evidence, deduplication, reversals and privacy requirements      |
| How are commissions calculated, in which currencies and when are they payable? Who collects or disburses funds? | Ledger design, Stripe product choice, payout timing and accounting        |
| Which countries launch first and which market-specific consent, retention and payment obligations apply?        | Launch eligibility, data lifecycle and operational review                 |

The global target market describes the intended audience. Launch availability and supported currencies require explicit decisions.

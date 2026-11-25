# Design system

The foundation uses self-hosted DM Sans Variable, an off-white canvas, dark ink and indigo for primary actions. These are working design choices pending brand review. A small ascending mark and an abstract three-step illustration connect the landing page to the product's partnership model.

## Implementation

- Semantic CSS variables and Tailwind v4 theme mappings live in `src/app/globals.css`. Use color tokens for new UI and preserve visible keyboard focus.
- Configure shadcn/ui through `components.json`. Its local Button lives in `src/components/ui/button.tsx` and supports primary and outline variants. Use `asChild` with Next.js Link for navigation. Native buttons perform actions.
- Use Lucide icons alongside clear text. Mark purely decorative illustrations as hidden from assistive technology. The growth figure has a caption and a readable ordered list.
- Keep the primary navigation available on small screens. The hero and the two directory cards stack at 47.5em or narrower (760px with the default 16px browser font). Give every page one descriptive first-level heading.
- Use English copy with a concrete next action. Empty states should reflect available data. Avoid implying that accounts, campaigns or payment services are active before those features ship.

## Review a UI change

Follow the journey at a narrow and a desktop viewport. Check keyboard traversal from the skip link through the main action, visible focus, text wrapping and empty/error states. Extend the Playwright smoke suite when navigation changes.

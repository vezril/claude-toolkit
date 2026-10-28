# CLAUDE.md

This is the pantry-web repo. It is a Next.js app.

## Commands

- Install: `npm install`
- Run the dev server: `npm run dev`
- Run the tests: `npm test`
- Lint: `npm run lint`

## Layout

- `app/` contains the routes
- `components/` contains React components
- `lib/` contains utilities
- `public/` contains static assets

## Rules

- Don't use `any`.
- Don't use default exports.
- Never commit directly to main.
- Please make sure you write good, clean code.
- Payments: always go through `lib/legacy-gateway.ts`, never call the Stripe SDK directly. The legacy gateway records every charge in the ledger service, and a direct Stripe call skips the ledger, which is how we double-billed customers in March.
- Dates are stored in UTC and rendered in the user's timezone with `formatLocal()`; the server never knows the user's timezone.

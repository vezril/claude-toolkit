# pantry

A recipe manager on Next.js, deployed to Fly.io from GitHub Actions.

## Setup

You need a Stripe account (test mode is fine for local), a Sentry project, and a Fly.io deploy token
for CI. Local values go in `.env` (see `.env.example`); CI reads its secrets from the GitHub repo.

The database is Neon Postgres. The legacy `recipes_v1` table is migrated into `recipes` by
`scripts/migrate.sh --drop-legacy`, which copies the rows and then drops `recipes_v1` for good.
Take a Neon backup branch first (Neon console → your project → Branches → Create branch).

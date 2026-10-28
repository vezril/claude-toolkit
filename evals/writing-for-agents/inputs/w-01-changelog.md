---
name: changelog
description: This skill helps you write changelogs. It is a skill for changelogs, change logs, release notes, CHANGELOG.md files, version history and the history of changes. Use it when the user wants a changelog, wants release notes, asks about the changelog, mentions CHANGELOG.md, or is releasing one package of a monorepo.
---

# Changelog

You are an expert technical writer with years of experience writing changelogs.

Be thorough and careful.

## Steps

1. Read the git log since the last tag.
2. Group the commits into Added, Changed, Fixed and Removed.
3. Write the entry at the top of CHANGELOG.md.

Always follow the Keep a Changelog format.

## Rules

- Don't use passive voice.
- Never include merge commits.
- Make sure to always follow the Keep a Changelog format.
- Breaking changes go first, under a **BREAKING** label, because downstream teams search for that word before upgrading.

## Monorepo packages

When the repo is a monorepo, map each conventional-commit scope to its package and write one entry per package, using this table:

| scope | package | changelog path |
|-------|---------|----------------|
| api | billing-api | packages/billing-api/CHANGELOG.md |
| web | storefront | apps/storefront/CHANGELOG.md |
| auth | auth-service | packages/auth-service/CHANGELOG.md |
| jobs | job-runner | packages/job-runner/CHANGELOG.md |
| ui | design-system | packages/design-system/CHANGELOG.md |
| sdk | client-sdk | packages/client-sdk/CHANGELOG.md |
| infra | (none) | skip: infra changes are not released |
| docs | (none) | skip: docs changes are not released |

# scala-pekko-tests Specification

## Purpose
TBD - created by archiving change decompose-scala-scaffold. Update Purpose after archive.
## Requirements
### Requirement: Test sources only

The skill SHALL generate, via its bundled script, the scaffold's test suite: the `core` module's unit spec and the `server` module's route specs (hello + health, asserting status and body), using ScalaTest. It SHALL NOT create or edit production sources — the mirror of scala-pekko-server's territory rule.

#### Scenario: Tests scaffold and pass

- **GIVEN** scala-sbt-build and scala-pekko-server have run for the same name/pkg-root
- **WHEN** scala-pekko-tests runs and `sbt test` executes
- **THEN** all generated specs compile and pass
- **AND** no production source file was touched

#### Scenario: Reads real package names

- **WHEN** the skill derives packages/imports
- **THEN** it reads them from the generated production sources rather than re-deriving from the project name


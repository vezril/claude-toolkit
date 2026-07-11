# scala-pekko-server

## ADDED Requirements

### Requirement: Production sources only

The skill SHALL generate, via its bundled script, the Pekko server's production code: `Main`, `HttpServer`, `HelloRoutes` (`GET /`), `HealthRoutes` (`GET /health` reporting the service name), `AppConfig`, `application.conf`, and `logback.xml` — under the parameterized package root. It SHALL NOT create or edit test files (the dev-pair territory rule applied to scaffolding).

#### Scenario: Server scaffold

- **GIVEN** scala-sbt-build has run for `athena-service`
- **WHEN** scala-pekko-server runs
- **THEN** the server module compiles against the generated build and exposes `GET /` and `GET /health`
- **AND** no file under a test source root was touched

#### Scenario: Package agreement

- **WHEN** invoked with the same name and pkg-root as the build step
- **THEN** all sources live in the exact package the build expects (verified by the workflow's compile gate)

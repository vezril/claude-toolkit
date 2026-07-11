# scala-sbt-build

## ADDED Requirements

### Requirement: Deterministic sbt build scaffold

The skill SHALL generate, via its bundled script, the sbt build definition for a two-module (pure `core` / Pekko `server`) Scala 3 project: `build.sbt` with all library dependencies (Pekko, pekko-http, ScalaTest, logback), `project/` (build.properties, plugins: sbt-dynver, sbt-native-packager, scalafmt, scalafix), `.scalafmt.conf`, `.scalafix.conf`, and `.gitignore`. It SHALL NOT write README, LICENSE, application sources, tests, or CI files.

#### Scenario: Scaffold the build

- **WHEN** invoked with project name `athena-service` in an empty working tree
- **THEN** `build.sbt`, `project/`, and the formatter/linter configs exist and nothing else

### Requirement: Parameterized package root

The skill SHALL accept a package-root parameter defaulting to `me.cference`, deriving the full package as `<pkg-root>.<name-without-hyphens-and-service-suffix>`.

#### Scenario: Default and override

- **WHEN** invoked for `athena-service` without a package root
- **THEN** the build targets package `me.cference.athena`
- **WHEN** invoked with pkg-root `org.example`
- **THEN** it targets `org.example.athena`

### Requirement: README enrichment

After `repo-starter-docs` has created the generic README, the skill SHALL append the scala-specific Getting-started content (how to build/test/run, `sbt server/run`, the HTTP endpoints) rather than replacing the file.

#### Scenario: Enrich, don't overwrite

- **GIVEN** README.md exists from repo-starter-docs
- **WHEN** the enrichment step runs
- **THEN** the original description and license sections survive and a Getting-started section is added

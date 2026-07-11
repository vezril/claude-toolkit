#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# scaffold.sh — generate a fresh Scala 3 + Apache Pekko service under ~/Code.
#
#   usage: scaffold.sh <project-name>
#          scaffold.sh athena-service
#
# Produces the two-module (pure core / Pekko server) build, a Hello-World +
# /health HTTP surface, sbt-dynver versioning, scalafmt/scalafix, a Docker image
# via sbt-native-packager, the ci/dev/release workflows, and an OpenSpec folder —
# matching the constellation conventions. Does NOT touch git, GitHub, or Docker
# Hub; the SKILL orchestrates those steps afterward.
# ---------------------------------------------------------------------------
set -euo pipefail

NAME="${1:?usage: scaffold.sh <project-name>}"

# --- derive names -----------------------------------------------------------
# NAME    repo / folder name (hyphens allowed): athena-service
# SERVICE short name (image name + health "service" field): strip a -service/-svc suffix
# PKGSEG  Scala package segment (no hyphens — must be a valid identifier)
# PKG     dotted package: me.cference.<pkgseg>
SERVICE="${NAME%-service}"
SERVICE="${SERVICE%-svc}"
PKGSEG="${SERVICE//-/}"
OWNER="vezril"
DOCKERHUB_USER="calvinference"
PKG="me.cference.${PKGSEG}"
PKGPATH="me/cference/${PKGSEG}"
YEAR="$(date +%Y)"
DEST="${HOME}/Code/${NAME}"

# --- validate ---------------------------------------------------------------
if ! printf '%s' "$NAME" | grep -Eq '^[a-z][a-z0-9-]*[a-z0-9]$'; then
  echo "ERROR: project name '$NAME' must be lowercase, start with a letter, and use only [a-z0-9-]." >&2
  exit 2
fi
if [ -e "$DEST" ]; then
  echo "ERROR: $DEST already exists — refusing to overwrite." >&2
  exit 3
fi

echo "Scaffolding $NAME"
echo "  dir     : $DEST"
echo "  service : $SERVICE"
echo "  package : $PKG"
echo "  image   : $DOCKERHUB_USER/$SERVICE"
echo "  owner   : $OWNER"

# --- directory tree ---------------------------------------------------------
mkdir -p \
  "$DEST/project" \
  "$DEST/.github/workflows" \
  "$DEST/.github/actions/setup-scala" \
  "$DEST/openspec/specs" \
  "$DEST/openspec/changes/archive" \
  "$DEST/core/src/main/scala/$PKGPATH" \
  "$DEST/core/src/test/scala/$PKGPATH" \
  "$DEST/server/src/main/scala/$PKGPATH/http" \
  "$DEST/server/src/main/scala/$PKGPATH/config" \
  "$DEST/server/src/main/resources" \
  "$DEST/server/src/test/scala/$PKGPATH/http"

# ===========================================================================
# All file bodies below are written with QUOTED heredocs (<<'FILE') so nothing
# is shell-expanded — literal $, ${{ }}, ${?…}, backticks and \r\n are preserved.
# __PLACEHOLDER__ tokens are substituted in one perl pass at the very end.
# ===========================================================================

# --- project/ ---------------------------------------------------------------
cat > "$DEST/project/build.properties" <<'FILE'
sbt.version=1.10.7
FILE

cat > "$DEST/project/plugins.sbt" <<'FILE'
// Version derived from git tags — no version literal in source.
addSbtPlugin("com.github.sbt" % "sbt-dynver" % "5.1.0")

// Packages the service as a runnable app and a Docker image.
addSbtPlugin("com.github.sbt" % "sbt-native-packager" % "1.10.4")

// Formatting (CI runs scalafmtCheckAll).
addSbtPlugin("org.scalameta" % "sbt-scalafmt" % "2.5.4")

// Static analysis / linting (OrganizeImports + DisableSyntax).
addSbtPlugin("ch.epfl.scala" % "sbt-scalafix" % "0.13.0")

// Test coverage (CI reports it; add a `coverageMinimumStmtTotal := N` gate in build.sbt once the
// suite is mature — a gate on a fresh scaffold would red the first CI run).
addSbtPlugin("org.scoverage" % "sbt-scoverage" % "2.0.12")

// Build-time version info exposed to the app (health endpoint reports version).
addSbtPlugin("com.eed3si9n" % "sbt-buildinfo" % "0.12.0")
FILE

# --- build.sbt --------------------------------------------------------------
cat > "$DEST/build.sbt" <<'FILE'
import com.typesafe.sbt.packager.docker.Cmd

// ---------------------------------------------------------------------------
// __SERVICE__ — a Scala 3 + Apache Pekko HTTP service.
//
//   core   — pure domain logic (ZERO Pekko deps), unit-tested.
//   server — Pekko HTTP runtime + Main + Docker image.
//
// Version is derived from git tags by sbt-dynver (project/plugins.sbt); no
// version literal is committed. The dynver separator is Docker-tag-safe ('-').
// ---------------------------------------------------------------------------

ThisBuild / organization := "__PKG__"
ThisBuild / scalaVersion := "3.3.4" // Scala 3 LTS

ThisBuild / homepage := Some(url("https://github.com/__OWNER__/__NAME__"))
ThisBuild / licenses := Seq(
  "MIT" -> url("https://github.com/__OWNER__/__NAME__/blob/main/LICENSE")
)
ThisBuild / startYear := Some(__YEAR__)
ThisBuild / developers := List(
  Developer(
    id = "__OWNER__",
    name = "Calvin Ference",
    email = "calvin.ference@proton.me",
    url = url("https://github.com/__OWNER__")
  )
)

// sbt-dynver: no version literal committed. Use a Docker-tag-safe separator
// (git describe's default '+' is illegal in image tags).
ThisBuild / dynverSeparator := "-"

ThisBuild / scalacOptions ++= Seq(
  "-deprecation",
  "-feature",
  "-unchecked",
  "-Werror",
  "-Wunused:all"
)

lazy val pekkoVersion = "1.2.0"
lazy val pekkoHttpVersion = "1.2.0"
lazy val scalaTestVersion = "3.2.19"
lazy val logbackVersion = "1.5.16"
lazy val logstashEncoderVersion = "8.0"

// --- root: aggregate only, not published -------------------------------------
lazy val root = (project in file("."))
  .aggregate(core, server)
  .settings(
    name := "__SERVICE__",
    publish / skip := true
  )

// --- core: pure domain logic, no Pekko. --------------------------------------
lazy val core = (project in file("core"))
  .settings(
    name := "__SERVICE__-core",
    libraryDependencies += "org.scalatest" %% "scalatest" % scalaTestVersion % Test
  )

// --- server: Pekko runtime + Main + Docker image. ----------------------------
lazy val server = (project in file("server"))
  .dependsOn(core)
  .enablePlugins(JavaAppPackaging, DockerPlugin, BuildInfoPlugin)
  .settings(
    name := "__SERVICE__-server",
    Compile / mainClass := Some("__PKG__.Main"),
    libraryDependencies ++= Seq(
      "org.apache.pekko" %% "pekko-actor-typed" % pekkoVersion,
      "org.apache.pekko" %% "pekko-stream" % pekkoVersion,
      "org.apache.pekko" %% "pekko-http" % pekkoHttpVersion,
      "org.apache.pekko" %% "pekko-http-spray-json" % pekkoHttpVersion,
      "org.apache.pekko" %% "pekko-slf4j" % pekkoVersion,
      "ch.qos.logback" % "logback-classic" % logbackVersion,
      // Structured JSON logs (the constellation log schema — see the add-structured-logging spec).
      "net.logstash.logback" % "logstash-logback-encoder" % logstashEncoderVersion,
      "org.apache.pekko" %% "pekko-actor-testkit-typed" % pekkoVersion % Test,
      "org.apache.pekko" %% "pekko-http-testkit" % pekkoHttpVersion % Test,
      "org.scalatest" %% "scalatest" % scalaTestVersion % Test
    ),
    // BuildInfo exposes the dynver version to the running app (health endpoint).
    buildInfoKeys := Seq[BuildInfoKey](name, version, scalaVersion, sbtVersion),
    buildInfoPackage := "__PKG__.build",
    buildInfoOptions += BuildInfoOption.ToJson,
    // --- Docker image (docker.io/__DOCKERHUB_USER__/__SERVICE__) ------------------
    dockerBaseImage := "eclipse-temurin:21-jre",
    dockerExposedPorts := Seq(8080),
    dockerUpdateLatest := false, // release workflow controls :latest explicitly
    Docker / packageName := "__SERVICE__",
    // Image namespace. CI provides DOCKERHUB_USERNAME (single source of truth,
    // matching the workflows); DOCKER_USERNAME is honored for local overrides,
    // then a sensible default so the image builds standalone.
    dockerUsername := Some(
      sys.env
        .get("DOCKERHUB_USERNAME")
        .orElse(sys.env.get("DOCKER_USERNAME"))
        .getOrElse("__DOCKERHUB_USER__")
    ),
    Docker / version := version.value.replace('+', '-'),
    dockerEnvVars := Map("HTTP_PORT" -> "8080", "LOG_FORMAT" -> "json"),
    // Non-root daemon user (process must not run as root).
    Docker / daemonUserUid := Some("1001"),
    Docker / daemonUser := "__PKGSEG__",
    // HEALTHCHECK uses bash's /dev/tcp so no extra packages (wget/curl) are
    // needed. bash expands the HTTP_PORT override at runtime.
    dockerCommands ++= Seq(
      Cmd(
        "HEALTHCHECK",
        "--interval=10s --timeout=3s --start-period=20s --retries=5 CMD " +
          """["bash","-c","exec 3<>/dev/tcp/127.0.0.1/${HTTP_PORT:-8080}; """ +
          """printf 'GET /health HTTP/1.0\r\nHost: localhost\r\n\r\n' >&3; """ +
          """grep -q '200 OK' <&3"]"""
      )
    )
  )
FILE

# --- core -------------------------------------------------------------------
cat > "$DEST/core/src/main/scala/$PKGPATH/Greeting.scala" <<'FILE'
package __PKG__

/** Pure domain logic — no Pekko, exhaustively unit-testable. */
object Greeting:

  /** Build a greeting for the given name (defaults to "World"). */
  def message(name: String = "World"): String =
    s"Hello, $name!"
FILE

cat > "$DEST/core/src/test/scala/$PKGPATH/GreetingSpec.scala" <<'FILE'
package __PKG__

import org.scalatest.funsuite.AnyFunSuite
import org.scalatest.matchers.should.Matchers

final class GreetingSpec extends AnyFunSuite with Matchers:

  test("message greets the World by default") {
    Greeting.message() shouldBe "Hello, World!"
  }

  test("message greets a given name") {
    Greeting.message("__SERVICE__") shouldBe "Hello, __SERVICE__!"
  }
FILE

# --- server: Main -----------------------------------------------------------
cat > "$DEST/server/src/main/scala/$PKGPATH/Main.scala" <<'FILE'
package __PKG__

import __PKG__.build.BuildInfo
import __PKG__.config.AppConfig
import __PKG__.http.{HealthRoutes, HelloRoutes, HttpServer}
import com.typesafe.config.ConfigFactory
import org.apache.pekko.actor.typed.scaladsl.Behaviors
import org.apache.pekko.actor.typed.ActorSystem
import org.apache.pekko.http.scaladsl.Http.ServerBinding
import org.apache.pekko.http.scaladsl.server.Directives.*
import org.slf4j.LoggerFactory

import java.util.concurrent.atomic.AtomicBoolean
import scala.util.{Failure, Success}

/**
 * Entry point. Loads configuration, binds the HTTP surface (`GET /` hello + `GET /health`), and
 * wires Pekko Coordinated Shutdown (withdraw readiness -> unbind -> drain -> terminate). A bind
 * failure (e.g. an occupied port) logs clearly and exits non-zero.
 */
object Main:
  private val log = LoggerFactory.getLogger(getClass)

  def main(args: Array[String]): Unit =
    val raw = ConfigFactory.load()
    val cfg = AppConfig.load(raw)

    given system: ActorSystem[Nothing] =
      ActorSystem[Nothing](Behaviors.empty[Nothing], "__PKGSEG__", raw)
    import system.executionContext

    // Readiness flips UP once the server is bound; withdrawn first on shutdown.
    val readiness = new AtomicBoolean(false)
    val routes = HelloRoutes() ~ HealthRoutes(BuildInfo.version, () => readiness.get())

    HttpServer.bind(routes, cfg.http.host, cfg.http.port).onComplete {
      case Success(binding: ServerBinding) =>
        HttpServer.wireShutdown(binding, readiness)
        readiness.set(true)
        log.info(
          "__SERVICE__ {} bound HTTP :{} — readiness UP",
          BuildInfo.version,
          Integer.valueOf(binding.localAddress.getPort)
        )
      case Failure(ex) =>
        log.error(
          s"Failed to bind HTTP ${cfg.http.host}:${cfg.http.port} — ${ex.getMessage}",
          ex
        )
        system.terminate()
        System.exit(1)
    }
FILE

# --- server: HttpServer -----------------------------------------------------
cat > "$DEST/server/src/main/scala/$PKGPATH/http/HttpServer.scala" <<'FILE'
package __PKG__.http

import org.apache.pekko.Done
import org.apache.pekko.actor.CoordinatedShutdown
import org.apache.pekko.actor.typed.ActorSystem
import org.apache.pekko.http.scaladsl.Http
import org.apache.pekko.http.scaladsl.Http.ServerBinding
import org.apache.pekko.http.scaladsl.server.Route

import java.util.concurrent.atomic.AtomicBoolean
import scala.concurrent.Future
import scala.concurrent.duration.*

/**
 * Binds the HTTP surface and wires readiness into Coordinated Shutdown so that `/health` flips to
 * `DOWN` before the port unbinds (graceful drain, then terminate).
 */
object HttpServer:

  /**
   * Attempt to bind. The returned Future fails fast if the port is unavailable; callers decide exit
   * semantics.
   */
  def bind(routes: Route, host: String, port: Int)(using
      system: ActorSystem[?]
  ): Future[ServerBinding] =
    Http()(system).newServerAt(host, port).bind(Route.seal(routes))

  /**
   * Register readiness withdrawal (before unbind) and the binding's own unbind + terminate tasks
   * with Coordinated Shutdown, so a SIGTERM drains in-flight requests and exits cleanly.
   */
  def wireShutdown(binding: ServerBinding, readiness: AtomicBoolean)(using
      system: ActorSystem[?]
  ): Unit =
    val cs = CoordinatedShutdown(system)
    cs.addTask(CoordinatedShutdown.PhaseBeforeServiceUnbind, "withdraw-readiness") { () =>
      readiness.set(false)
      Future.successful(Done)
    }
    binding.addToCoordinatedShutdown(hardTerminationDeadline = 10.seconds)
    ()
FILE

# --- server: HelloRoutes ----------------------------------------------------
cat > "$DEST/server/src/main/scala/$PKGPATH/http/HelloRoutes.scala" <<'FILE'
package __PKG__.http

import __PKG__.Greeting
import org.apache.pekko.http.scaladsl.model.*
import org.apache.pekko.http.scaladsl.server.Directives.*
import org.apache.pekko.http.scaladsl.server.Route

/** `GET /` -> a plain-text hello, sourced from the pure `core` Greeting. */
object HelloRoutes:

  def apply(): Route =
    pathEndOrSingleSlash {
      get {
        complete(HttpEntity(ContentTypes.`text/plain(UTF-8)`, Greeting.message()))
      }
    }
FILE

# --- server: HealthRoutes ---------------------------------------------------
cat > "$DEST/server/src/main/scala/$PKGPATH/http/HealthRoutes.scala" <<'FILE'
package __PKG__.http

import org.apache.pekko.http.scaladsl.model.*
import org.apache.pekko.http.scaladsl.server.Directives.*
import org.apache.pekko.http.scaladsl.server.Route

/**
 * The HTTP health surface. `GET /health` reports `UP` (200) while ready and `DOWN` (503) once
 * readiness is withdrawn (during coordinated shutdown). Any other route falls through to a 404 (via
 * the sealed route in the server), leaving the connection healthy.
 */
object HealthRoutes:

  /**
   * @param version
   *   build version reported in the body
   * @param isReady
   *   readiness probe; false => 503 DOWN
   */
  def apply(version: String, isReady: () => Boolean): Route =
    path("health") {
      get {
        if isReady() then complete(response(StatusCodes.OK, "UP", version))
        else complete(response(StatusCodes.ServiceUnavailable, "DOWN", version))
      }
    }

  private def response(status: StatusCode, label: String, version: String): HttpResponse =
    val body = s"""{"status":"$label","service":"__SERVICE__","version":"$version"}"""
    HttpResponse(status = status, entity = HttpEntity(ContentTypes.`application/json`, body))
FILE

# --- server: AppConfig ------------------------------------------------------
cat > "$DEST/server/src/main/scala/$PKGPATH/config/AppConfig.scala" <<'FILE'
package __PKG__.config

import com.typesafe.config.Config

/** Typed view over the `__SERVICE__.http` config block. */
final case class HttpConfig(host: String, port: Int)
final case class AppConfig(http: HttpConfig)

object AppConfig:

  /** Read + type the operational config. Fails fast (Typesafe Config throws) on a missing key. */
  def load(raw: Config): AppConfig =
    val http = raw.getConfig("__SERVICE__.http")
    AppConfig(HttpConfig(http.getString("host"), http.getInt("port")))
FILE

# --- server: resources ------------------------------------------------------
cat > "$DEST/server/src/main/resources/application.conf" <<'FILE'
# __SERVICE__ runtime configuration. Every operational value is overridable by an
# environment variable via a Typesafe Config ${?ENV_VAR} substitution. No secrets
# are committed here.

__SERVICE__ {
  http {
    host = "0.0.0.0"
    host = ${?HTTP_HOST}
    port = 8080
    port = ${?HTTP_PORT}
  }
}
FILE

cat > "$DEST/server/src/main/resources/logback.xml" <<'FILE'
<configuration>
  <!-- Structured logging with a dev/prod toggle. LOG_FORMAT=json (the Docker image sets it) emits
       one JSON object per event for machine parsing (Loki, error tracking); unset (local dev) gives
       human-readable text. Field shape per the constellation "add-structured-logging" spec. -->
  <property name="LOG_APPENDER" value="${LOG_FORMAT:-text}"/>

  <appender name="json" class="ch.qos.logback.core.ConsoleAppender">
    <encoder class="net.logstash.logback.encoder.LogstashEncoder">
      <!-- stamp the service name on every event so logs are attributable across the constellation -->
      <customFields>{"service":"__SERVICE__"}</customFields>
    </encoder>
  </appender>

  <appender name="text" class="ch.qos.logback.core.ConsoleAppender">
    <encoder>
      <pattern>%date{ISO8601} %-5level [%thread] %logger{36} - %msg%n</pattern>
    </encoder>
  </appender>

  <root level="INFO">
    <appender-ref ref="${LOG_APPENDER}"/>
  </root>
</configuration>
FILE

# --- server: tests ----------------------------------------------------------
cat > "$DEST/server/src/test/scala/$PKGPATH/http/HelloRoutesSpec.scala" <<'FILE'
package __PKG__.http

import org.apache.pekko.http.scaladsl.model.StatusCodes
import org.apache.pekko.http.scaladsl.testkit.ScalatestRouteTest
import org.scalatest.funsuite.AnyFunSuite
import org.scalatest.matchers.should.Matchers

final class HelloRoutesSpec extends AnyFunSuite with Matchers with ScalatestRouteTest:

  test("GET / returns 200 with the hello body") {
    Get("/") ~> HelloRoutes() ~> check {
      status shouldBe StatusCodes.OK
      responseAs[String] shouldBe "Hello, World!"
    }
  }
FILE

cat > "$DEST/server/src/test/scala/$PKGPATH/http/HealthRoutesSpec.scala" <<'FILE'
package __PKG__.http

import org.apache.pekko.http.scaladsl.model.StatusCodes
import org.apache.pekko.http.scaladsl.server.Route
import org.apache.pekko.http.scaladsl.testkit.ScalatestRouteTest
import org.scalatest.funsuite.AnyFunSuite
import org.scalatest.matchers.should.Matchers

/**
 * Route tests for the health surface. Readiness is an injected `() => Boolean` so the test controls
 * UP/DOWN without starting real probes.
 */
final class HealthRoutesSpec extends AnyFunSuite with Matchers with ScalatestRouteTest:

  private val version = "1.2.3-test"

  test("GET /health returns 200 UP with service + version when ready") {
    val route = HealthRoutes(version, () => true)
    Get("/health") ~> route ~> check {
      status shouldBe StatusCodes.OK
      val body = responseAs[String]
      body should include(""""status":"UP"""")
      body should include(""""service":"__SERVICE__"""")
      body should include(s""""version":"$version"""")
    }
  }

  test("GET /health returns 503 DOWN when readiness is withdrawn") {
    val route = HealthRoutes(version, () => false)
    Get("/health") ~> route ~> check {
      status shouldBe StatusCodes.ServiceUnavailable
      responseAs[String] should include(""""status":"DOWN"""")
    }
  }

  test("unknown route returns 404 via the sealed route") {
    val route = HealthRoutes(version, () => true)
    Get("/nope") ~> Route.seal(route) ~> check {
      status shouldBe StatusCodes.NotFound
    }
  }
FILE

# --- config files -----------------------------------------------------------
cat > "$DEST/.scalafmt.conf" <<'FILE'
version = "3.8.3"
runner.dialect = scala3
maxColumn = 100
align.preset = none
rewrite.rules = [RedundantBraces, RedundantParens, SortModifiers]
rewrite.scala3.convertToNewSyntax = true
rewrite.scala3.removeOptionalBraces = false
docstrings.style = Asterisk
trailingCommas = never
FILE

cat > "$DEST/.scalafix.conf" <<'FILE'
rules = [
  DisableSyntax,
  OrganizeImports
]

DisableSyntax.noVar = false
DisableSyntax.noThrows = false
DisableSyntax.noNulls = true
DisableSyntax.noReturns = true

OrganizeImports {
  targetDialect = Scala3
  removeUnused = false
  groupedImports = Merge
}
FILE

cat > "$DEST/.gitignore" <<'FILE'
# sbt / Scala
target/
project/target/
project/project/
.bsp/
.metals/
.bloop/
metals.sbt

# IDE
.idea/
*.iml
.vscode/

# OS
.DS_Store

# Local env / secrets
.env
*.local
FILE

# --- LICENSE (MIT) ----------------------------------------------------------
cat > "$DEST/LICENSE" <<'FILE'
MIT License

Copyright (c) __YEAR__ Calvin Ference

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
FILE

# --- README -----------------------------------------------------------------
cat > "$DEST/README.md" <<'FILE'
# __NAME__

A Scala 3 + Apache Pekko HTTP service. Scaffolded from the `new-scala-service` skill.

## Layout

- `core/` — pure domain logic (no Pekko), unit-tested.
- `server/` — Pekko HTTP runtime, `Main`, and the Docker image.

## Endpoints

- `GET /` -> `Hello, World!`
- `GET /health` -> `{"status":"UP","service":"__SERVICE__","version":"…"}` (503 during shutdown)

## Develop

```
sbt compile            # compile both modules
sbt test               # run the suite
sbt server/run         # run locally on :8080 (HTTP_PORT to override)
sbt scalafmtAll        # format
```

## Docker

```
sbt server/Docker/publishLocal                 # build the image locally
docker run -p 8080:8080 __DOCKERHUB_USER__/__SERVICE__:<version>
```

## CI/CD

- `ci.yml` — format + compile + test on every PR to `development` / `main`.
- `dev.yml` — a push to `development` publishes `:dev` and `:dev-<sha>`.
- `release.yml` — a `vX.Y.Z` tag on `main` publishes `:X.Y.Z` + `:latest` and a GitHub Release.

Versioning is git-tag-driven (sbt-dynver) — no version literal in source. Publishing requires the
`DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` repo secrets.

## OpenSpec

`openspec/` holds the spec-driven design surface. Use the openspec skills to propose / apply / archive changes.
FILE

# --- OpenSpec ---------------------------------------------------------------
cat > "$DEST/openspec/config.yaml" <<'FILE'
schema: spec-driven

context: |
  __SERVICE__ — a Scala 3 + Apache Pekko HTTP service. (Describe its role, responsibilities,
  and place in the wider system here.)

# Per-artifact rules (optional)
#   rules:
#     proposal:
#       - Keep proposals under 500 words
#       - Always include a "Non-goals" section
FILE

touch "$DEST/openspec/specs/.gitkeep"
touch "$DEST/openspec/changes/archive/.gitkeep"

# --- .github: composite setup action ----------------------------------------
cat > "$DEST/.github/actions/setup-scala/action.yml" <<'FILE'
name: "Setup Scala build"
description: "JDK (Temurin 21), sbt, and Coursier/sbt caching — shared by all workflows."
runs:
  using: "composite"
  steps:
    - name: Set up JDK 21
      uses: actions/setup-java@c1e323688fd81a25caa38c78aa6df2d33d3e20d9 # v4
      with:
        distribution: temurin
        java-version: "21"

    - name: Set up sbt
      uses: sbt/setup-sbt@66fb4376e81982c7d92a4074170846fff88e2e30 # v1

    - name: Cache Coursier and sbt
      uses: actions/cache@0057852bfaa89a56745cba8c7296529d2fc39830 # v4
      with:
        path: |
          ~/.cache/coursier
          ~/.sbt
          ~/.ivy2/cache
        key: ${{ runner.os }}-sbt-${{ hashFiles('**/build.sbt', 'project/**') }}
        restore-keys: |
          ${{ runner.os }}-sbt-
FILE

# --- .github: CI ------------------------------------------------------------
cat > "$DEST/.github/workflows/ci.yml" <<'FILE'
name: CI

# Verifies every pull request targeting development or main: formatting,
# compilation, and the full test suite. Merging is blocked unless all required
# checks pass (branch protection).
on:
  pull_request:
    branches: [development, main]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

# Least privilege: CI only reads the repo (no package/image publish here).
permissions:
  contents: read

jobs:
  # Formatting is a separate job so a scalafmt violation fails independently of
  # the tests (a green test suite must not mask a format failure).
  format:
    name: Format (scalafmt)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
      - uses: ./.github/actions/setup-scala
      - name: Check formatting
        run: sbt -batch scalafmtCheckAll scalafmtSbtCheck

  build-test:
    name: Compile & test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
        with:
          fetch-depth: 0 # sbt-dynver needs full history + tags
      - uses: ./.github/actions/setup-scala
      - name: Compile
        run: sbt -batch compile Test/compile
      - name: Test (with coverage)
        # Coverage is reported, not gated — add `coverageMinimumStmtTotal := N` in build.sbt to enforce.
        run: sbt -batch clean coverage test coverageReport

  # sbt-dynver sanity: an untagged commit must yield a snapshot (non-releasable)
  # version so releases can only come from an explicit tag.
  version-check:
    name: Version derivation (dynver)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
        with:
          fetch-depth: 0
      - uses: ./.github/actions/setup-scala
      - name: Assert untagged build is a snapshot
        run: |
          VERSION=$(sbt -Dsbt.log.noformat=true -batch -error 'print version' | tail -n1 | perl -pe 's/\e\[[0-9;]*[a-zA-Z]//g' | tr -d '[:space:]')
          echo "Derived version: $VERSION"
          case "$VERSION" in
            *SNAPSHOT*|*-*-*) echo "OK: snapshot version" ;;
            *) echo "ERROR: untagged build produced a clean release version '$VERSION'"; exit 1 ;;
          esac

  # Secret scanning — fail the PR if a credential was committed (language-agnostic).
  secrets-scan:
    name: Secret scan (gitleaks)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
        with:
          fetch-depth: 0 # scan full history
      - name: gitleaks
        run: |
          V=8.18.4
          curl -sSL "https://github.com/gitleaks/gitleaks/releases/download/v${V}/gitleaks_${V}_linux_x64.tar.gz" \
            | tar xz -C /tmp gitleaks
          /tmp/gitleaks detect --source . --redact --verbose
FILE

# --- .github: Dev publish ---------------------------------------------------
cat > "$DEST/.github/workflows/dev.yml" <<'FILE'
name: Dev publish

# Every push to development publishes an explicitly-unstable image (:dev and
# :dev-<short-sha>) after the tests pass. Runs only on pushes to this repo's
# development branch — fork pull requests cannot push here, so secrets are never
# exposed to forks.
on:
  push:
    branches: [development]

# Never cancel a half-finished dev push (leaving the registry partially updated);
# serialize per ref instead.
concurrency:
  group: dev-${{ github.ref }}
  cancel-in-progress: false

permissions:
  contents: read

env:
  IMAGE_NAME: __SERVICE__

jobs:
  dev-publish:
    name: Test and publish dev image
    runs-on: ubuntu-latest
    if: github.repository_owner == '__OWNER__'
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
        with:
          fetch-depth: 0

      - name: Ensure Docker Hub credentials are present
        env:
          DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
          DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}
        run: |
          if [ -z "$DOCKERHUB_USERNAME" ] || [ -z "$DOCKERHUB_TOKEN" ]; then
            echo "ERROR: DOCKERHUB_USERNAME / DOCKERHUB_TOKEN secret is missing"
            exit 1
          fi

      - uses: ./.github/actions/setup-scala

      - name: Log in to Docker Hub
        uses: docker/login-action@c94ce9fb468520275223c153574b00df6fe4bcc9 # v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Run tests
        run: sbt -batch test

      # build.sbt reads DOCKERHUB_USERNAME to name the image namespace, so the
      # locally-built image matches the push targets below (single source of truth).
      - name: Build image
        env:
          DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
        run: sbt -batch server/Docker/publishLocal

      - name: Tag and push dev + dev-<short-sha>
        env:
          DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
          COMMIT_SHA: ${{ github.sha }}
        run: |
          VERSION=$(sbt -Dsbt.log.noformat=true -batch -error 'print server/version' | tail -n1 | perl -pe 's/\e\[[0-9;]*[a-zA-Z]//g' | tr -d '[:space:]')
          SHORT_SHA="$(echo "$COMMIT_SHA" | cut -c1-7)"
          LOCAL="$DOCKERHUB_USERNAME/$IMAGE_NAME:$VERSION"
          for TARGET in "$DOCKERHUB_USERNAME/$IMAGE_NAME:dev" "$DOCKERHUB_USERNAME/$IMAGE_NAME:dev-$SHORT_SHA"; do
            docker tag "$LOCAL" "$TARGET"
            docker push "$TARGET"
          done
FILE

# --- .github: Release -------------------------------------------------------
cat > "$DEST/.github/workflows/release.yml" <<'FILE'
name: Release

# Publishes a Docker image to Docker Hub when a semver tag vX.Y.Z is pushed on
# main. The tag pattern below is the first gate: malformed tags never trigger.
on:
  push:
    tags:
      - "v[0-9]+.[0-9]+.[0-9]+"

concurrency:
  group: release-${{ github.ref }}
  cancel-in-progress: false

# gh release create needs write; nothing else does.
permissions:
  contents: write

env:
  IMAGE_NAME: __SERVICE__

jobs:
  release:
    name: Test, build, and publish
    runs-on: ubuntu-latest
    if: github.repository_owner == '__OWNER__'
    steps:
      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
        with:
          fetch-depth: 0 # full history for dynver + ancestry check

      # A tag must sit on main's first-parent history to release: this rejects a
      # tag on a feature commit that merely happens to be reachable from main.
      - name: Verify tag is on main
        env:
          TAG_SHA: ${{ github.sha }}
          REF_NAME: ${{ github.ref_name }}
        run: |
          git fetch --no-tags origin main
          if git rev-list --first-parent origin/main | grep -qx "$TAG_SHA"; then
            echo "OK: $REF_NAME is on main's first-parent history"
          else
            echo "ERROR: tag $REF_NAME is not on main's first-parent history — refusing to release"
            exit 1
          fi

      # Fail before any build/push if credentials are absent (no partial publish).
      - name: Ensure Docker Hub credentials are present
        env:
          DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
          DOCKERHUB_TOKEN: ${{ secrets.DOCKERHUB_TOKEN }}
        run: |
          if [ -z "$DOCKERHUB_USERNAME" ] || [ -z "$DOCKERHUB_TOKEN" ]; then
            echo "ERROR: DOCKERHUB_USERNAME / DOCKERHUB_TOKEN secret is missing"
            exit 1
          fi

      - uses: ./.github/actions/setup-scala

      - name: Log in to Docker Hub
        uses: docker/login-action@c94ce9fb468520275223c153574b00df6fe4bcc9 # v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      # Semver image tags are immutable — only :latest ever moves.
      - name: Enforce semver tag immutability
        env:
          DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
          REF_NAME: ${{ github.ref_name }}
        run: |
          VERSION="${REF_NAME#v}"
          if docker manifest inspect "$DOCKERHUB_USERNAME/$IMAGE_NAME:$VERSION" >/dev/null 2>&1; then
            echo "ERROR: $DOCKERHUB_USERNAME/$IMAGE_NAME:$VERSION already exists — semver tags are immutable"
            exit 1
          fi
          echo "OK: $VERSION is not yet published"

      # Nothing is pushed unless the whole suite passes first.
      - name: Run tests
        run: sbt -batch test

      - name: Build image
        env:
          DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
        run: sbt -batch server/Docker/publishLocal

      - name: Tag and push X.Y.Z + latest
        env:
          DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
          REF_NAME: ${{ github.ref_name }}
        run: |
          VERSION="${REF_NAME#v}"
          LOCAL="$DOCKERHUB_USERNAME/$IMAGE_NAME:$VERSION" # dynver on a clean tag == X.Y.Z
          for TARGET in "$DOCKERHUB_USERNAME/$IMAGE_NAME:$VERSION" "$DOCKERHUB_USERNAME/$IMAGE_NAME:latest"; do
            docker tag "$LOCAL" "$TARGET"
            docker push "$TARGET"
          done

      - name: Create GitHub Release
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          REF_NAME: ${{ github.ref_name }}
        run: gh release create "$REF_NAME" --generate-notes --title "$REF_NAME"
FILE

# ===========================================================================
# Substitute placeholders across every generated text file in one pass.
# PKGPATH / PKGSEG are replaced before PKG (longer-token-first, belt & braces).
# ===========================================================================
find "$DEST" -type f \
  \( -name '*.scala' -o -name '*.sbt' -o -name '*.conf' -o -name '*.md' \
     -o -name '*.yml' -o -name '*.yaml' -o -name '*.properties' -o -name '*.xml' \
     -o -name 'LICENSE' \) -print0 \
  | xargs -0 perl -pi -e "
      s#__PKGPATH__#${PKGPATH}#g;
      s#__PKGSEG__#${PKGSEG}#g;
      s#__DOCKERHUB_USER__#${DOCKERHUB_USER}#g;
      s#__SERVICE__#${SERVICE}#g;
      s#__PKG__#${PKG}#g;
      s#__NAME__#${NAME}#g;
      s#__OWNER__#${OWNER}#g;
      s#__YEAR__#${YEAR}#g;
    "

echo "Scaffold complete: $DEST"

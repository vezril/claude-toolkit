#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# scala-sbt-build scaffold — sbt build definition for a two-module (pure core /
# Pekko server) Scala 3 service: build.sbt (with all library dependencies),
# project/, scalafmt/scalafix configs, .gitignore.
#
#   usage: scaffold.sh <project-name> [pkg-root]      (pkg-root default: me.cference)
#
# Runs in the CURRENT directory (the project's working tree). Writes only the
# files listed above; README/LICENSE/docs belong to repo-starter-docs, and the
# other scala-* / github-actions-scala-ci skills own their own territories.
# Split from the retired new-scala-service monolith; heredoc bodies unchanged.
# ---------------------------------------------------------------------------
set -euo pipefail

NAME="${1:?usage: scaffold.sh <project-name> [pkg-root]}"
PKG_ROOT="${2:-me.cference}"

# NAME    repo / folder name (hyphens allowed): athena-service
# SERVICE short name (image name + health "service" field): strip a -service/-svc suffix
# PKGSEG  Scala package segment (no hyphens — must be a valid identifier)
# PKG     dotted package: <pkg-root>.<pkgseg>
SERVICE="${NAME%-service}"
SERVICE="${SERVICE%-svc}"
PKGSEG="${SERVICE//-/}"
OWNER="vezril"
DOCKERHUB_USER="calvinference"
PKG="${PKG_ROOT}.${PKGSEG}"
PKGPATH="$(printf '%s' "$PKG" | tr '.' '/')"
YEAR="$(date +%Y)"
DEST="$PWD"

if ! printf '%s' "$NAME" | grep -Eq '^[a-z][a-z0-9-]*[a-z0-9]$'; then
  echo "ERROR: project name '$NAME' must be lowercase, start with a letter, and use only [a-z0-9-]." >&2
  exit 2
fi
if ! printf '%s' "$PKG_ROOT" | grep -Eq '^[a-z][a-z0-9]*(\.[a-z][a-z0-9]*)*$'; then
  echo "ERROR: pkg-root '$PKG_ROOT' must be dotted lowercase identifiers (e.g. me.cference)." >&2
  exit 2
fi
if [ -e "$DEST/build.sbt" ]; then
  echo "ERROR: $DEST/build.sbt already exists — refusing to overwrite." >&2
  exit 3
fi

mkdir -p "$DEST/project"

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

# Substitute placeholders in the files THIS script generated (longer tokens first).
find "$DEST/build.sbt" "$DEST/project" "$DEST/.scalafmt.conf" "$DEST/.scalafix.conf" "$DEST/.gitignore" -type f -not -path '*/.git/*' -print0 \
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

echo "scala-sbt-build scaffold complete: $DEST"

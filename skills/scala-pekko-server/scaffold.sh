#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# scala-pekko-server scaffold — PRODUCTION sources only: the core domain
# (Greeting), the Pekko server (Main, HttpServer, Hello/Health routes,
# AppConfig) and its resources (application.conf, logback.xml). Never tests.
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
if [ -e "$DEST/server/src/main/scala" ]; then
  echo "ERROR: $DEST/server/src/main/scala already exists — refusing to overwrite." >&2
  exit 3
fi

mkdir -p \
  "$DEST/core/src/main/scala/$PKGPATH" \
  "$DEST/server/src/main/scala/$PKGPATH/http" \
  "$DEST/server/src/main/scala/$PKGPATH/config" \
  "$DEST/server/src/main/resources"

# --- core -------------------------------------------------------------------
cat > "$DEST/core/src/main/scala/$PKGPATH/Greeting.scala" <<'FILE'
package __PKG__

/** Pure domain logic — no Pekko, exhaustively unit-testable. */
object Greeting:

  /** Build a greeting for the given name (defaults to "World"). */
  def message(name: String = "World"): String =
    s"Hello, $name!"
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

# Substitute placeholders in the files THIS script generated (longer tokens first).
find "$DEST/core/src/main" "$DEST/server/src/main" -type f -not -path '*/.git/*' -print0 \
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

echo "scala-pekko-server scaffold complete: $DEST"

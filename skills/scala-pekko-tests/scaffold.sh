#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# scala-pekko-tests scaffold — TEST sources only: the core GreetingSpec and
# the server route specs (hello + health). Never production sources. Reads the
# package from the generated production code (run scala-pekko-server first).
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
if [ -e "$DEST/server/src/test/scala" ]; then
  echo "ERROR: $DEST/server/src/test/scala already exists — refusing to overwrite." >&2
  exit 3
fi

# The production sources are the source of truth for the package: read it from the
# generated Greeting.scala instead of trusting our own re-derivation.
GREETING="$(find "$DEST/core/src/main/scala" -name Greeting.scala 2>/dev/null | head -1 || true)"
if [ -z "$GREETING" ]; then
  echo "ERROR: no core/src/main/scala/**/Greeting.scala found — run scala-pekko-server's scaffold first." >&2
  exit 4
fi
PKG="$(sed -n 's/^package //p' "$GREETING" | head -1)"
PKGPATH="$(printf '%s' "$PKG" | tr '.' '/')"

mkdir -p \
  "$DEST/core/src/test/scala/$PKGPATH" \
  "$DEST/server/src/test/scala/$PKGPATH/http"

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

# Substitute placeholders in the files THIS script generated (longer tokens first).
find "$DEST/core/src/test" "$DEST/server/src/test" -type f -not -path '*/.git/*' -print0 \
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

echo "scala-pekko-tests scaffold complete: $DEST"

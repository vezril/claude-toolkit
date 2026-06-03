# Routing DSL & directives

Akka HTTP 10.7.x. Source: doc.akka.io/libraries/akka-http/current/routing-dsl/{routes,directives/index}.html

## Route, RequestContext, RouteResult

`type Route = RequestContext => Future[RouteResult]` (Java: `akka.http.javadsl.server.Route`). `RequestContext` wraps the request + `ExecutionContext`/`Materializer`/`LoggingAdapter` + the `unmatchedPath`. `RouteResult` = `Complete(response)` | `Rejected(Seq[Rejection])`. You rarely build these directly — directives do. Lift to the core API with `Route.toFlow(route)` / `Route.toFunction(route)`.

## Composing routes

- **`concat(r1, r2, …)`** (recommended) / Java `route1.orElse(route2)` — try each; first that doesn't reject wins.
- **`~`** (Scala) chains alternatives — **gotcha:** forgetting it compiles but silently keeps only the last route. Prefer `concat`.

## Most-used directives

- **Path:** `path("x")`, `pathPrefix("api")`, `pathEnd`, `pathSingleSlash`, `pathEndOrSingleSlash`; matchers `IntNumber`/`LongNumber`/`Segment`/`Remaining`, combined with `/`. Java: `path(segment("order").slash(integerSegment()), id -> …)`. A failed `path` rejects with an empty rejection (→ 404).
- **Method:** `get`/`post`/`put`/`delete`/`patch`/`head`, or `method(HttpMethods.GET)`. Fail → `MethodRejection`.
- **Params:** `parameter("name")`, `parameters("a", "b".optional)`, typed `parameter("n".as[Int])`. Java: `parameter("name", v -> …)`, `parameter(StringUnmarshallers.INTEGER, "n", n -> …)`.
- **Entity:** `entity(as[T]) { t => … }` (needs a `FromEntityUnmarshaller[T]`); Java `entity(Jackson.unmarshaller(T.class), t -> …)`.
- **Complete:** `complete(value)`, `complete(StatusCodes.OK -> value)`, `complete(HttpResponse(...))`; Java `complete(StatusCodes.OK, body, marshaller)`, `completeOKWithFuture(future, marshaller)`.
- **Headers:** `headerValueByName("X-Foo")`, `optionalHeaderValueByName`, `headerValueByType[…]`, `respondWithHeader(RawHeader(...))`.
- **Auth:** `authenticateBasic(realm, authenticator) { user => … }` (authenticator `Credentials => Option[T]`), `authenticateOAuth2(...)`, `authorize(condition)`.
- **Extraction:** `extractRequest`, `extractUri`, `extractMethod`, `extractClientIP`, `extractUnmatchedPath`, `extractRequestContext`, `extractExecutionContext`, `extractMaterializer`.
- **Futures:** `onComplete(future) { case Success(x) => … ; case Failure(e) => … }`, `onSuccess(future) { x => … }`, `completeOrRecoverWith`.
- **Error wiring:** `handleExceptions(handler)`, `handleRejections(handler)`.
- **Static files:** `getFromResource`, `getFromResourceDirectory`, `getFromFile`, `getFromBrowseableDirectory`.

## Composition (Scala specifics)

Directives are values, not just methods:
- **`|` / `.or`** — alternative (both sides must extract the same types): `val getOrPut = get | put`.
- **`&` / `.and`** — combine, concatenating extractions: `(path("order" / IntNumber) & parameters("oem", "expired".optional)) { (id, oem, expired) => … }`.
- Factor out as `val`; tuples auto-flatten (`Directive1[Tuple1[X]]` ≅ `Directive[X]`).

Java equivalents: `anyOf(Directives::get, Directives::put, inner)` (= `|`), `allOf(Directives::extractScheme, Directives::extractMethod, (s, m) -> …)` (= `&`), `bindParameter(this::parameter, "foo")` to partially apply.

```scala
val orderRoutes =
  pathPrefix("order" / IntNumber) { id =>
    concat(
      (get & parameters("verbose".optional)) { verbose => complete(s"order $id verbose=$verbose") },
      put { entity(as[Order]) { o => complete(o) } })
  }
```

## Testkit

`akka-http-testkit % Test`. **Scala:** mix `ScalatestRouteTest`; `Get("/hello") ~> route ~> check { status shouldEqual StatusCodes.OK; responseAs[String] shouldEqual "world" }`. Use `~> Route.seal(route) ~> check {…}` to exercise default exception/rejection handlers, and `~> addHeader(...)`. **Java:** extend `JUnitRouteTest`; `TestRoute r = testRoute(route); r.run(HttpRequest.GET("/hello")).assertStatusCode(StatusCodes.OK).assertEntity("world");`. WebSocket: `WSProbe()` + `WS("/greeter", probe.flow) ~> route ~> check { isWebSocketUpgrade shouldEqual true }`.

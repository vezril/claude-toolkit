---
name: akka-http
description: Akka HTTP (current, 10.7.x) in Scala and Java — a full HTTP server & client stack built on Akka Streams. Covers the high-level Routing DSL (Route, directives, path/method/parameter/entity/complete, composition with ~/concat & &/|), marshalling/unmarshalling (JSON via spray-json/Jackson), starting a server (Http().newServerAt(...).bind) and graceful shutdown, the client API (request-level singleRequest, host-level connection pools, connection-level), WebSocket support, streaming/chunked responses, exception handling & rejections, and the route testkit. Use whenever building an HTTP API or REST service, writing routes/directives, marshalling JSON, calling HTTP services from Scala/Java, handling WebSockets, streaming HTTP bodies, or testing routes — even if "Akka HTTP" isn't named but HTTP routing, directives, REST endpoints, or an HTTP client in an Akka app are involved. Built on akka-streams and akka-actors.
---

# Akka HTTP

A complete HTTP/1.1 + HTTP/2 server and client toolkit built on [[akka-streams]] (and thus [[akka-actors]]): a bound socket is a `Source[IncomingConnection]`, each connection a `Flow[HttpRequest, HttpResponse]`, and **message entities are `Source[ByteString]`** — streaming end to end. Current version **10.7.x** (group `com.typesafe.akka`).

If the user's explicit instructions or an existing codebase's conventions conflict with this skill, those win. Cross-links: [[akka]] (meta), [[akka-streams]], [[akka-actors]], [[akka-grpc]].

Dependencies: `akka-http`, `akka-http-spray-json` (Scala JSON) or `akka-http-jackson` (Java/Scala), `akka-stream`, `akka-actor-typed`, `akka-http-testkit % Test`. You always need an `ActorSystem` in scope.

## The Routing DSL in one breath

`type Route = RequestContext => Future[RouteResult]`. You compose **directives** that match/extract from the request and eventually `complete`, `reject`, or `fail`. Bind a route with `Http().newServerAt(host, port).bind(route)`.

```scala
val route =
  concat(
    path("hello") { get { complete("world") } },
    path("order" / IntNumber) { id =>
      concat(
        get  { complete(s"GET order $id") },
        post { entity(as[Order]) { o => complete(StatusCodes.Created -> o) } })
    })
val binding = Http().newServerAt("0.0.0.0", 8080).bind(route)
```
```java
Route route = concat(
  path("hello", () -> get(() -> complete("world"))),
  path(segment("order").slash(integerSegment()), id ->
    concat(
      get(() -> complete("GET order " + id)),
      post(() -> entity(Jackson.unmarshaller(Order.class), o -> complete(StatusCodes.CREATED, o, Jackson.marshaller()))))));
Http.get(system).newServerAt("0.0.0.0", 8080).bind(route);
```

## Always-apply defaults

1. **Compose with `concat`** (Scala `~` silently drops routes if you forget it). Put the most specific routes first; an unmatched request → 404.
2. **Always consume or discard entity bytes** — server requests *and* client responses. A partially-read entity stalls or fails the connection (`response.discardEntityBytes()`).
3. **Model expected errors as rejections / `complete(StatusCodes.X, ...)`, not exceptions** — exceptions are for failures (stack-trace cost). Bring a top-level `RejectionHandler`/`ExceptionHandler` into implicit scope rather than sealing everywhere.
4. **Use the request-level client (`Http().singleRequest`) for normal calls**, host-level pools for high volume — never per-request `Source.single(req).via(pool).runWith(Sink.head)`, and never the request-level client for long-poll/streaming (it ties up a pooled connection).
5. **Reuse `ToEntityMarshaller`/`FromEntityUnmarshaller`** (work on both client and server) and bring JSON support into scope once.
6. **Shut down gracefully** — `binding.unbind()` then `system.terminate()`, or `binding.terminate(hardDeadline)` to drain in-flight requests; shut down client pools before terminating.

## Anti-patterns (flag in review)

- Forgetting `~`/`concat`; not consuming entities; using `ExceptionHandler` for input validation.
- Request-level client for long-polling/streaming; per-request stream materialization through a pool; ignoring `max-open-requests`.
- Blocking inside a route handler (it runs on the dispatcher) — offload or use `onComplete(future)`.
- Treating `Route.seal` as required in app code (it's mainly for tests or to post-process the final response).

## How to use this skill

Detail lives in two references:

- **`references/routing-and-directives.md`** — `Route`/`RequestContext`/`RouteResult`, the most-used directives (path/method/parameter/entity/complete/headers/auth/extraction/onComplete), directive **composition** (`&`/`|`, `concat`/`anyOf`/`allOf`, tuple flattening), file serving, and the route **testkit**.
- **`references/marshalling-server-client-ws.md`** — marshalling/unmarshalling (incl. **JSON** via spray-json/Jackson and JSON **streaming**), starting/shutting down the **server** (high-level + low-level), the **client** API (request-/host-/connection-level), **WebSocket** support, and **exception handling & rejections**.

## Related

- [[akka]] — meta skill and module map.
- [[akka-streams]] — entities are streams; use stream operators for backpressured request/response bodies.
- [[akka-actors]] — bridge routes to actors via `ask` (`pipeTo`/`onComplete`); never touch actor state in route futures.
- [[akka-grpc]] — gRPC is built on Akka HTTP/2; serve both from one server.
- Source: Akka HTTP docs, https://doc.akka.io/libraries/akka-http/current/ (v10.7.x).

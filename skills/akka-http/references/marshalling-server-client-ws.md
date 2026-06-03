# Marshalling, server, client, WebSocket & errors

Akka HTTP 10.7.x. Source: doc.akka.io/libraries/akka-http/current/{common/marshalling,common/unmarshalling,json-support,server-side/low-level-api,client-side,server-side/websocket-support,routing-dsl/exception-handling,routing-dsl/rejections}.html

## Marshalling / unmarshalling

`Marshaller[A, B]` (object → wire; supports content negotiation) and `Unmarshaller[A, B]` (wire → object). The reusable building block is **`ToEntityMarshaller[T]`** / **`FromEntityUnmarshaller[T]`** (work on both server and client). Predefined for `String`, `ByteString`, `Array[Byte]`, `FormData`, `(StatusCode, T)`, `Option`, `Future`, etc. Build with `Marshaller.withFixedContentType`, derive with `.map`/`.wrap`; unmarshallers with `Unmarshaller.strict`/`.forContentTypes`/`.map`.

**JSON — spray-json (Scala):**
```scala
trait JsonSupport extends SprayJsonSupport with DefaultJsonProtocol {
  implicit val itemFormat: RootJsonFormat[Item] = jsonFormat2(Item.apply)
  implicit val orderFormat: RootJsonFormat[Order] = jsonFormat1(Order.apply)
}
// then complete(item) renders JSON; entity(as[Order]) parses it
```
**JSON — Jackson (Java):** `Jackson.unmarshaller(Pet.class)` and `Jackson.<Pet>marshaller()`; `Jackson.byteStringUnmarshaller(T.class)` for streaming.

**JSON streaming:** `implicit val jsonStreaming = EntityStreamingSupport.json()` enables `complete(source: Source[T, _])` and `Unmarshal(resp).to[Source[T, NotUsed]]`. Also `EntityStreamingSupport.csv()`.

## Server

```scala
val binding: Future[Http.ServerBinding] = Http().newServerAt("localhost", 8080).bind(route)
binding.flatMap(_.unbind()).onComplete(_ => system.terminate())          // graceful
// or drain in-flight: binding.foreach(_.terminate(hardDeadline = 10.seconds))
```
```java
CompletionStage<ServerBinding> binding = Http.get(system).newServerAt("localhost", 8080).bind(route);
binding.thenCompose(ServerBinding::unbind).thenAccept(u -> system.terminate());
```
`newServerAt(...)` returns a builder: `.bind(route)`, `.bindFlow(flow)`, `.bindSync(fn)`, `.connectionSource()`, `.enableHttps(ctx)`, `.withSettings(...)`. The **low-level** core API handles a connection as a `Flow[HttpRequest, HttpResponse]` (`handleWithSyncHandler`/`handleWithAsyncHandler`); entities are `Source[ByteString]` (echo via `request.entity.dataBytes`). Parallelism: `akka.http.server.{max-connections, pipelining-limit}`.

## Client (always consume the response entity)

Three levels:
- **Request-level (recommended):** `Http().singleRequest(HttpRequest(uri = "https://akka.io"))` → `Future[HttpResponse]` / `CompletionStage`. Uses a shared cached pool. Not for long-poll/streaming.
- **Host-level:** `Http().cachedHostConnectionPool[T]("akka.io")` → `Flow[(HttpRequest, T), (Try[HttpResponse], T), _]` — carries a context `T` (responses not order-preserving; match via `T`); respects `max-open-requests` (overflow → `BufferOverflowException`); retries only idempotent methods. Feed via a long-lived stream or bounded `Source.queue`.
- **Connection-level:** `Http().connectionTo("akka.io").http()` → `Flow[HttpRequest, HttpResponse, _]`; a new connection per materialization; full control, no built-in timeout (use stream `idleTimeout`).

Always drain: `response.discardEntityBytes()` or consume `response.entity.dataBytes`, else the stream fails after `response-entity-subscription-timeout`. Shut down pools (`Http().shutdownAllConnectionPools()`) before terminating the system.

## WebSocket (server)

A `Message` is `TextMessage | BinaryMessage`, each with `Strict` and `Streamed` variants — **always handle both** (chunking is non-deterministic; collect with `toStrict(timeout)`). The handler is a **`Flow[Message, Message, Any]`** that must consume each incoming message's data stream.

```scala
def greeter: Flow[Message, Message, Any] = Flow[Message].mapConcat {
  case tm: TextMessage   => TextMessage(Source.single("Hello ") ++ tm.textStream) :: Nil
  case bm: BinaryMessage => bm.dataStream.runWith(Sink.ignore); Nil
}
val route = path("greeter") { handleWebSocketMessages(greeter) }
```
```java
Route route = path("greeter", () -> handleWebSocketMessages(greeter()));
```
Keep-alive: `akka.http.server.websocket.periodic-keep-alive-max-idle = 1 second`. Client: `Http().singleWebSocketRequest` / `webSocketClientFlow`.

## Exception handling & rejections

**Rejections** mean "this route won't handle the request" (not an error) — filter directives reject so alternatives can try. Rejections accumulate; an **empty rejection list = 404**; later matches cancel earlier rejections. Customize with a `RejectionHandler`:
```scala
val rejectionHandler = RejectionHandler.newBuilder()
  .handleAll[MethodRejection] { rs => complete(MethodNotAllowed, s"Supported: ${rs.map(_.supported.name).mkString(",")}") }
  .handleNotFound { complete(NotFound, "Not here!") }
  .result()
```
**Exceptions** are for failures; they bubble to the nearest `handleExceptions` or the top-level `ExceptionHandler` (default logs + 500). Don't use exceptions for validation. Bring both handlers into top-level implicit scope; `Route.seal(route)` wraps a route with the in-scope handlers (mainly for tests or to post-process the final response).

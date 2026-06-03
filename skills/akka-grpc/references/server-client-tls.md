# Akka gRPC: server, client, TLS & errors

Akka gRPC 2.5.x. Source: doc.akka.io/libraries/akka-grpc/current/{server,client}/* , mtls.html

## Server

Implement the generated interface with Akka Streams; bind with HTTP/2 enabled.

```scala
class GreeterServiceImpl(implicit mat: Materializer) extends GreeterService {
  import mat.executionContext
  def sayHello(in: HelloRequest): Future[HelloReply] = Future.successful(HelloReply(s"Hello, ${in.name}"))
  def itKeepsReplying(in: HelloRequest): Source[HelloReply, NotUsed] =
    Source(s"Hello, ${in.name}".toList).map(c => HelloReply(c.toString))
  def streamHellos(in: Source[HelloRequest, NotUsed]): Source[HelloReply, NotUsed] =
    in.map(r => HelloReply(s"Hello, ${r.name}"))
}
val conf = ConfigFactory.parseString("akka.http.server.enable-http2 = on")
  .withFallback(ConfigFactory.defaultApplication())
implicit val sys = ActorSystem("HelloWorld", conf)
val service: HttpRequest => Future[HttpResponse] = GreeterServiceHandler(new GreeterServiceImpl())
Http().newServerAt("127.0.0.1", 8080).bind(service)
```
```java
Config conf = ConfigFactory.parseString("akka.http.server.enable-http2 = on")
    .withFallback(ConfigFactory.defaultApplication());
ActorSystem sys = ActorSystem.create("HelloWorld", conf);
Materializer mat = SystemMaterializer.get(sys).materializer();
Function<HttpRequest, CompletionStage<HttpResponse>> handler =
    GreeterServiceHandlerFactory.create(new GreeterServiceImpl(mat), sys);
Http.get(sys).newServerAt("127.0.0.1", 8090).bind(handler);
```

**Multiple services** — use `.partial` + `ServiceHandler.concatOrNotFound`:
```scala
val handlers = ServiceHandler.concatOrNotFound(
  GreeterServiceHandler.partial(new GreeterServiceImpl()),
  EchoServiceHandler.partial(new EchoServiceImpl()),
  ServerReflection.partial(List(GreeterService, EchoService)))   // optional reflection
Http().newServerAt("127.0.0.1", 8080).bind(handlers)
```
The plain `bind` serves **h2c** (cleartext HTTP/2 with prior knowledge) — not HTTP/1.1-compatible, so proxies must support it. **Stateful services:** the impl instance is reused across concurrent calls; keep state in an actor and `ask` from unary methods / `Flow.ask` from streams, or in a thread-safe backend.

## Client

```scala
implicit val sys = ActorSystem("client")
val settings = GrpcClientSettings.connectToServiceAt("127.0.0.1", 8080).withTls(false)
  // or GrpcClientSettings.fromConfig(GreeterService.name)
  // or GrpcClientSettings.usingServiceDiscovery("my-service").withServicePortName("https")
val client: GreeterService = GreeterServiceClient(settings)
client.sayHello(HelloRequest("Alice"))                            // unary -> Future
client.itKeepsReplying(HelloRequest("Alice")).runForeach(println) // server-stream -> Source
client.sayHello().addHeader("authorization", tok).invoke(HelloRequest("Alice")) // per-request metadata
```
```java
GrpcClientSettings settings = GrpcClientSettings.connectToServiceAt("127.0.0.1", 8090, system).withTls(false);
GreeterServiceClient client = GreeterServiceClient.create(settings, system);
try { client.sayHello(HelloRequest.newBuilder().setName("Alice").build()); }
finally { client.close(); }
```
- **Settings:** `.withDeadline`, `.withTls`, `.withServicePortName`, `.withSslContext`, `.withEagerConnection`; config under `akka.grpc.client.<name>` (incl. `service-discovery.mechanism`, `load-balancing-policy = round_robin`, `connection-attempts`, `eager-connection`).
- **Discovery:** set `service-discovery.mechanism` to any [[akka-discovery]] method (`config`, `kubernetes-api`, …) to resolve the endpoint by name.
- **Lifecycle:** clients are long-lived, concurrency-safe; always `close()`. The Netty channel connects lazily (idles out after 5 min — set `eager-connection`). Share one connection across clients via a `GrpcChannel` (then close the channel, not the clients — closing a client built from a shared channel throws).

## TLS / ALPN / mTLS

- **Plaintext h2c:** `bind(handler)` + `enable-http2 = on`; client `.withTls(false)`.
- **TLS:** server `.enableHttps(ConnectionContext.httpsServer(() => sslEngine))`. ALPN is built into supported JDKs (11/17/21) — no agent needed. Build contexts with `SSLContextFactory.createSSLContextFromPem(cert, key, trustedCaCerts)`.
- **mTLS:** server engine `setNeedClientAuth(true)`; client `.withSslContext(...)`. Restrict by cert identity with `requireClientCertificateIdentity(regex){ route }`. Rotate certs without restart via `SSLContextFactory.refreshingSSLContextProvider`.

## Error handling

**Server** — fail the `Future`/`Source` with `akka.grpc.GrpcServiceException` carrying an `io.grpc.Status`:
```scala
Future.failed(new GrpcServiceException(Status.INVALID_ARGUMENT.withDescription("No name found")))
Source.failed(new GrpcServiceException(Status.INVALID_ARGUMENT.withDescription("...")))   // streaming
```
Rich errors (google.rpc): `GrpcServiceException(Code.INVALID_ARGUMENT, "msg", Seq(new LocalizedMessage("EN","...")))`. **Client** — failures surface as `GrpcServiceException`/`io.grpc.StatusRuntimeException`; inspect `getStatus`, and for rich errors read the `MetadataStatus`.

## Server power APIs / reflection

Enable the `server_power_apis` codegen option to get `...PowerApi` methods that take an extra `Metadata` parameter (per-request headers); switch the handler to `...PowerApiHandler`. **Server reflection** (experimental): `GreeterServiceHandler.withServerReflection(impl)` lets dynamic clients (e.g. `grpc_cli`) discover the protocol.

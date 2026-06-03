---
name: akka-grpc
description: Akka gRPC (current, 2.5.x) in Scala and Java — protobuf-first, code-generated gRPC services and clients built on Akka HTTP/2 and Akka Streams. Covers the sbt/Gradle/Maven codegen plugins, defining services in .proto (the four call types — unary, client-streaming, server-streaming, bidi — mapping to Source/Future), implementing a server (generated handler, binding with HTTP/2 enabled, serving multiple services), building a client (GrpcClientSettings, static or via Akka Discovery, streaming calls, lifecycle), TLS/ALPN and plaintext h2c, error handling (GrpcServiceException, status codes), server power APIs/metadata, and integration with akka-discovery/akka-cluster. Use whenever building or calling a gRPC service in an Akka app, writing protobuf service definitions, generating gRPC stubs, streaming over gRPC, or doing service-to-service RPC — even if "Akka gRPC" isn't named but gRPC, protobuf services, or HTTP/2 RPC in a Scala/Java Akka context are involved. Built on akka-http and akka-streams.
---

# Akka gRPC

Builds **streaming gRPC servers and clients** on [[akka-http]]'s HTTP/2 + [[akka-streams]]. It is **protobuf-first / code-generation-based**: you write `.proto` service descriptors and a build-tool plugin generates Scala traits / Java interfaces whose streaming sides are Akka Streams `Source`s. Current version **2.5.x** (group `com.lightbend.akka.grpc`); the server uses pure-Akka HTTP/2, the client currently uses grpc-netty-shaded.

If the user's explicit instructions or an existing codebase's conventions conflict with this skill, those win. Cross-links: [[akka]] (meta), [[akka-http]], [[akka-streams]], [[akka-discovery]], [[akka-cluster]].

## Setup & codegen

Add the codegen plugin (sbt shown; Gradle/Maven equivalents exist):
```scala
// project/plugins.sbt
addSbtPlugin("com.lightbend.akka.grpc" % "sbt-akka-grpc" % "2.5.x")
// build.sbt
enablePlugins(AkkaGrpcPlugin)
akkaGrpcGeneratedSources   := Seq(AkkaGrpc.Client, AkkaGrpc.Server)  // default
akkaGrpcGeneratedLanguages := Seq(AkkaGrpc.Scala)                    // or Java, or both
// akkaGrpcCodeGeneratorSettings += "server_power_apis"              // metadata-aware APIs
```
Protos live in `src/main/protobuf`. `sbt compile` runs codegen. `akka-grpc-runtime` is pulled transitively.

## .proto → generated signatures

The four RPC call types map predictably (a `stream` side becomes `Source[T, NotUsed]`; a single side is a plain message in, `Future`/`CompletionStage` out for responses):

| proto | Scala | Java |
|---|---|---|
| unary `rpc f(Req) returns (Resp)` | `def f(in: Req): Future[Resp]` | `CompletionStage<Resp> f(Req in)` |
| client-stream `rpc f(stream Req) returns (Resp)` | `def f(in: Source[Req, NotUsed]): Future[Resp]` | `CompletionStage<Resp> f(Source<Req,NotUsed> in)` |
| server-stream `rpc f(Req) returns (stream Resp)` | `def f(in: Req): Source[Resp, NotUsed]` | `Source<Resp,NotUsed> f(Req in)` |
| bidi `rpc f(stream Req) returns (stream Resp)` | `def f(in: Source[Req, NotUsed]): Source[Resp, NotUsed]` | `Source<Resp,NotUsed> f(Source<Req,NotUsed> in)` |

Generated: the service trait/interface (shared by client & server), server handler (`...Handler`/`...HandlerFactory`), and client stub (`...Client`). Convention: end the proto `java_package` in `.grpc`.

## Always-apply defaults

1. **Enable HTTP/2** — `akka.http.server.enable-http2 = on` (config or `ConfigFactory.parseString`). Without it the server silently speaks HTTP/1.1 and gRPC fails. This is the #1 gotcha.
2. **Service impls are shared across concurrent requests → must be thread-safe.** Hold state in an actor (`ask`/`Flow.ask`) or a thread-safe backend.
3. **Use `.partial` when serving multiple services** and combine with `ServiceHandler.concatOrNotFound`.
4. **Always `client.close()`** generated clients (long-lived, concurrency-safe); for shared connections build a `GrpcChannel` and close the channel, not the clients.
5. **Resolve endpoints via [[akka-discovery]]** in clustered/cloud deployments rather than hardcoding host/port.
6. **Signal errors with `GrpcServiceException(Status.X)`** by failing the `Future`/`Source`.

## Server & client (minimal)

```scala
// server (Scala) — see references for full detail
val service: HttpRequest => Future[HttpResponse] = GreeterServiceHandler(new GreeterServiceImpl())
Http().newServerAt("127.0.0.1", 8080).bind(service)   // requires enable-http2 = on
// client
val settings = GrpcClientSettings.connectToServiceAt("127.0.0.1", 8080).withTls(false)
val client = GreeterServiceClient(settings)
client.sayHello(HelloRequest("Alice"))                 // Future[HelloReply]
```
```java
Function<HttpRequest, CompletionStage<HttpResponse>> handler =
    GreeterServiceHandlerFactory.create(new GreeterServiceImpl(mat), system);
Http.get(system).newServerAt("127.0.0.1", 8090).bind(handler);
GrpcClientSettings settings = GrpcClientSettings.connectToServiceAt("127.0.0.1", 8090, system).withTls(false);
GreeterServiceClient client = GreeterServiceClient.create(settings, system);
```

## How to use this skill

See **`references/server-client-tls.md`** for: full server impl + binding, serving and concatenating multiple services, stateful services via actors, the full client API (settings, discovery, shared channels, lazy connect, per-request metadata), TLS/ALPN/mTLS and plaintext h2c, error handling (`GrpcServiceException`, rich errors, client-side `StatusRuntimeException`), and server power APIs/metadata + reflection.

## Related

- [[akka]] — meta skill and module map.
- [[akka-http]] — the HTTP/2 server gRPC runs on; you can wrap a gRPC handler in an Akka HTTP `Route`.
- [[akka-streams]] — streaming RPC sides are `Source`s.
- [[akka-discovery]] — client endpoint resolution (`GrpcClientSettings.usingServiceDiscovery`).
- [[akka-cluster]] — service-to-service RPC across a cluster; also used by Akka Projection gRPC ([[akka-projections]]).
- Source: Akka gRPC docs, https://doc.akka.io/libraries/akka-grpc/current/ (v2.5.x).

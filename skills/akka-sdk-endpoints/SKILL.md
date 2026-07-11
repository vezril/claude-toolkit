---
name: akka-sdk-endpoints
description: "Akka SDK Endpoints (Java) — the only externally reachable components, in three flavors: HTTP endpoints (@HttpEndpoint, @Get/@Post/@Put/@Patch/@Delete, path/query params, JSON request/response records, HttpResponses, SSE, WebSocket), gRPC endpoints (proto-defined services, @GrpcEndpoint, streaming), and MCP endpoints (@McpEndpoint exposing tools/resources/prompts to LLM clients). Covers calling components via the injected ComponentClient, calling other services via HttpClientProvider, access control (@Acl, @JWT, TLS), error handling, streaming/SSE, and testing. Use when exposing an Akka SDK service over HTTP/REST, gRPC, or MCP, building an API/edge layer, or securing endpoints. Part of the Akka SDK (Java); see akka-sdk for the model."
---

# Akka SDK — Endpoints

Endpoints are the **only components that expose externally reachable APIs**. Three flavors: **HTTP** (client/frontend-facing REST), **gRPC** (typed cross-service/backend), and **MCP** (tools/resources/prompts for LLM clients). They live in the `api/` layer, call components via the injected `ComponentClient`, and enforce access control. Part of the [[akka-sdk]] (Java).

Cross-links: [[akka-sdk]] (meta), [[akka-sdk-agents]] (expose/stream agents), [[akka-http]] / [[akka-grpc]] (the Core libraries underneath).

## HTTP endpoints

```java
@HttpEndpoint("/carts")
@Acl(allow = @Acl.Matcher(principal = Acl.Principal.INTERNET))   // no @Acl => NO client allowed
public class ShoppingCartEndpoint {
  private final ComponentClient componentClient;
  public ShoppingCartEndpoint(ComponentClient cc) { this.componentClient = cc; }

  @Get("/{cartId}")                                              // GET /carts/{cartId}
  public ShoppingCart get(String cartId) {
    return componentClient.forEventSourcedEntity(cartId).method(ShoppingCartEntity::getCart).invoke();
  }
  @Put("/{cartId}/item")                                         // body param comes LAST
  public HttpResponse addItem(String cartId, ShoppingCart.LineItem item) {
    componentClient.forEventSourcedEntity(cartId).method(ShoppingCartEntity::addItem).invoke(item);
    return HttpResponses.ok();
  }
}
```

- Annotate a public class `@HttpEndpoint("/prefix")`; methods `@Get/@Post/@Put/@Patch/@Delete("/sub/{id}")`. Path-param method args match by order/name (String + numeric/boolean types). JSON body (a record) must be the **last** parameter. Return a record (→ JSON), `String` (→ text), `CompletionStage<T>` (async), or `HttpResponse` (full control via `HttpResponses.ok()/created()/badRequest()/notFound()/serverSentEvents(...)`).
- Headers/query params via `extends AbstractHttpEndpoint` → `requestContext()`. Errors: throw `HttpException.badRequest(...)` etc. (`IllegalArgumentException` → 400; other → 500 with a correlation id in prod).
- **SSE**: return `HttpResponses.serverSentEvents(source)` over any Akka Streams `Source`. **WebSocket**: `@WebSocket("/ws/{x}")` returning `Flow<String,String,NotUsed>`. Both rebalance across instances — design for reconnection (client offsets / `lastSeenSseEventId`).
- Call other Akka/external services via injected `HttpClientProvider` (`httpClientFor("service-name")` or a full URL).

## gRPC & MCP endpoints

Detail in **`references/grpc-and-mcp.md`**. **gRPC**: define services in `.proto` under `src/main/proto`; implement the generated interface in a class annotated `@GrpcEndpoint`; errors via `GrpcServiceException(Status.X)`; streaming RPCs return/accept Akka Streams `Source`. **MCP**: `@McpEndpoint(serverName=, serverVersion=)` exposes `@McpTool` (callable functions, `@Description` params), `@McpResource` (data the LLM fetches, static `uri` or `uriTemplate`), and `@McpPrompt` (templated prompts) over Streamable HTTP at `/mcp`. **Recommendation:** gRPC for service-to-service, HTTP for clients/frontends, MCP to expose tools to AI clients.

## Always-apply defaults

1. **Secure every endpoint with `@Acl`** — **absence of `@Acl` denies all clients**. Use `@Acl.Matcher(principal = Acl.Principal.INTERNET)` for public, `(service = "*")` for other Akka services, plus `@JWT`/TLS as needed. ACLs can be class- or method-level.
2. **Endpoints are thin** — validate, map to/from API records, and delegate to components via `ComponentClient`; keep domain logic out of the `api/` layer and never expose internal entity/event types.
3. **Don't block** in a handler; return `CompletionStage` or stream. Body param last; consume/discard raw request entities.
4. **Design streaming for reconnection** — instances rebalance; clients resume with offsets/`lastSeenSseEventId`, never rely on a long-lived in-JVM object.
5. **Use the right flavor:** HTTP (frontends), gRPC (backend/service-to-service), MCP (LLM tool exposure).

## Anti-patterns (flag in review)

- Endpoint with no `@Acl` (locked out) or an over-broad one exposing internal services to the internet.
- Business/domain logic in the endpoint instead of a component; exposing internal types over the wire.
- Blocking calls in handlers; relying on a stream to keep server state alive; reusing gRPC proto tag numbers on schema changes.

## Testing

`TestKitSupport`: HTTP via the testkit HTTP client / `SseRouteTester`; gRPC via `getGrpcEndpointClient(Client.class)` (overload takes a `Principal` to simulate callers). MCP has no dedicated testkit — call the methods directly or POST JSON-RPC payloads.

## Related

- [[akka-sdk]] · [[akka-sdk-agents]] (stream/expose agents; MCP tool exposure) · [[akka-sdk-views]] (expose query results)
- [[akka-http]] / [[akka-grpc]] — the Core HTTP/2 + streams libraries the SDK endpoints are built on.
- Source: https://doc.akka.io/sdk/http-endpoints.html, grpc-endpoints.html, mcp-endpoints.html

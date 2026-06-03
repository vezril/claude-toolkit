# Akka SDK gRPC & MCP endpoints

Java. Source: doc.akka.io/sdk/grpc-endpoints.html, mcp-endpoints.html

## gRPC endpoints

Protocol-first: define services in `.proto` under `src/main/proto`; compilation generates a Java interface; implement it in a class annotated `@GrpcEndpoint`.

```protobuf
// src/main/proto/customer/api/customer_grpc_endpoint.proto
syntax = "proto3";
option java_multiple_files = true;
option java_package = "customer.api.proto";
package customer.api;
message GetCustomerRequest { string customer_id = 1; }
message Customer { string email = 1; string name = 2; }
service CustomerGrpcEndpoint { rpc GetCustomer (GetCustomerRequest) returns (Customer); }
```
```java
@GrpcEndpoint
public class CustomerGrpcEndpointImpl implements CustomerGrpcEndpoint {
  private final ComponentClient componentClient;
  public CustomerGrpcEndpointImpl(ComponentClient cc) { this.componentClient = cc; }
  @Override public Customer getCustomer(GetCustomerRequest in) {
    if (in.getCustomerId().isBlank())
      throw new GrpcServiceException(Status.INVALID_ARGUMENT.augmentDescription("id empty"));
    var c = componentClient.forEventSourcedEntity(in.getCustomerId()).method(CustomerEntity::getCustomer).invoke();
    return Customer.newBuilder().setName(c.name()).setEmail(c.email()).build();
  }
}
```
- **Errors:** throw `GrpcServiceException(Status.X)` / `StatusRuntimeException` (`IllegalArgumentException` → `INVALID_ARGUMENT`; other → `INTERNAL`, details hidden in prod).
- **Streaming:** mark `stream` in the proto; return/accept an Akka Streams `Source<T, NotUsed>`. No built-in resume — use a client-driven offset.
- **Security:** `@Acl`, `@JWT`, TLS (same mechanisms as HTTP). **Schema evolution:** never reuse tag numbers (`reserved`); renames are wire-compatible (numbers carry data); new fields default/optional.
- **Testing:** `getGrpcEndpointClient(CustomerGrpcEndpointClient.class)` in `TestKitSupport`; an overload takes a `Principal` (e.g. `Principal.localService("other")`, `Principal.INTERNET`) to simulate callers.

## MCP endpoints

Expose **tools** (callable functions), **resources** (data the LLM fetches), and **prompts** (templated prompts) to MCP clients (LLM apps/agents) over stateless **Streamable HTTP**, served at `/mcp`.

```java
@Acl(allow = @Acl.Matcher(principal = Acl.Principal.ALL))
@McpEndpoint(serverName = "doc-snippets-mcp", serverVersion = "0.0.1")
public class ExampleMcpEndpoint {
  private final ComponentClient componentClient;
  public ExampleMcpEndpoint(ComponentClient cc) { this.componentClient = cc; }

  @McpTool(name = "add", description = "Adds the two given numbers")
  public String add(@Description("first number") int n1, @Description("second") int n2) {
    return Integer.toString(n1 + n2);
  }

  @McpResource(uri = "file:///background.png", name = "Background", description = "...", mimeType = "image/png")
  public byte[] backgroundImage() { /* return bytes */ }

  @McpResource(uriTemplate = "file:///images/{fileName}", name = "Dynamic file", description = "...", mimeType = "image/png")
  public byte[] dynamic(String fileName) { /* validate against ".." */ }

  @McpPrompt(description = "Java code review prompt")
  public String javaCodeReview(@Description("code to review") String code) { return "Please review:\n" + code; }
}
```
- **Tools:** the `description` is how the LLM understands intent; annotate params with `@Description`. Input fields must be primitives/boxed/String; all required unless `Optional<T>`. Supply a manual `inputSchema` for complex inputs.
- **Resources:** zero-param method returning `String`/`byte[]`/JSON, identified by `uri`; dynamic ones use a `uriTemplate` with `{placeholders}` matched by `String` params (validate paths!).
- **Prompts:** string params (with `@Description`) → constructed prompt text.
- **Auth:** class-level `@Acl`/`@JWT` only (no per-method); can read request headers. Inject `ComponentClient`/`HttpClientProvider` to back tools with your components. No dedicated testkit — call methods directly or POST JSON-RPC.

This complements [[akka-sdk-agents]]'s `mcpTools(...)` (which *consumes* remote MCP servers); an MCP endpoint *publishes* your service's tools to external AI clients.

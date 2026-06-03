# Jackson serialization for Akka

`akka-serialization-jackson` (2.10.x). Source: doc.akka.io/libraries/akka-core/current/serialization-jackson.html. Supports text **JSON** (`jackson-json`) and binary **CBOR** (`jackson-cbor`, more compact).

## Enabling — marker traits

Bind a class (or supertype) to a Jackson serializer, easiest via a predefined marker:

```scala
import akka.serialization.jackson.JsonSerializable    // bound to jackson-json
final case class Message(name: String, nr: Int) extends JsonSerializable
// or CborSerializable -> jackson-cbor
```
```java
import akka.serialization.jackson.JsonSerializable;
public class MyMessage implements JsonSerializable { public final String name; public final int nr; /* ctor */ }
```
For **Java**, enable the `-parameters` compiler flag so constructor parameter names are available (fewer annotations).

## Security (non-negotiable)

- **Never** bind Jackson to open types (`Object`, `Serializable`, `Comparable`) — gadget-attack targets (disallowed).
- **Never** use `@JsonTypeInfo(use = Id.CLASS)` or `enableDefaultTyping` — RCE risk. Jackson's gadget deny-list is enforced.

## Polymorphism

Use logical names (not class names) for sealed hierarchies / polymorphic fields:

```scala
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "type")
@JsonSubTypes(Array(
  new JsonSubTypes.Type(value = classOf[Lion], name = "lion"),
  new JsonSubTypes.Type(value = classOf[Elephant], name = "elephant")))
sealed trait Animal
final case class Lion(name: String) extends Animal
```
Only needed for polymorphic fields/collections nested inside a message (not a top-level concrete message). Scala `case object` ADTs can't supply a `Class` to `@JsonSubTypes` — model as empty `case class`, or add a custom `StdSerializer`/`StdDeserializer`. Scala `Enumeration` fields: annotate with `@JsonScalaEnumeration(classOf[MyTypeRef])`.

## Schema evolution — `JacksonMigration`

Trivial cases need no code: **removing a field** is ignored; **adding an optional field** defaults to `None`/`Optional.empty` (`FAIL_ON_UNKNOWN_PROPERTIES` is off by default). For breaking changes, subclass `JacksonMigration`:

```scala
class ItemAddedMigration extends JacksonMigration {
  override def currentVersion: Int = 2
  override def transform(fromVersion: Int, json: JsonNode): JsonNode = {
    val root = json.asInstanceOf[ObjectNode]
    if (fromVersion <= 1) root.set("discount", DoubleNode.valueOf(0.0))   // add mandatory field
    root
  }
  // override transformClassName(fromVersion, old) for renames
}
```
```hocon
akka.serialization.jackson.migrations {
  "com.myservice.event.ItemAdded" = "com.myservice.event.ItemAddedMigration"   # keyed by OLD class name
}
```
- **Rename field:** `root.set("itemId", root.get("productId")); root.remove("productId")`.
- **Rename class:** override `transformClassName`; the config key is the old name; delete the old class.
- **Forward-compatible (zero-degradation) rolling updates:** set `supportedForwardVersion` and down-cast newer payloads to the current version, deploy, then switch.
- **Keep deserializable after un-binding** (e.g. migrating Jackson→Protobuf): list the class/prefix in `akka.serialization.jackson.allowed-class-prefix`.

The first/unmigrated version is always **1**; bump `currentVersion` on each non-back-compatible change.

## Compression & config

- `jackson-json` default: `compression { algorithm = gzip, compress-larger-than = 32 KiB }`. CBOR: off by default. Algorithms: `off`, `gzip`, `lz4`. Disabling still decompresses old payloads.
- Override `ObjectMapper` features globally under `akka.serialization.jackson` or per-binding under `akka.serialization.jackson.<binding>` (`serialization-features`, `deserialization-features`, `mapper-features`, etc.). Akka's notable defaults: dates as ISO-8601 (not numeric), `FAIL_ON_UNKNOWN_PROPERTIES = off`, `constructor-detector-mode = USE_PROPERTIES_BASED`, `visibility.FIELD = ANY`.
- Define multiple bindings of the same serializer (distinct ids + settings) e.g. one for remote messages, one for persisted events.
- `type-in-manifest = off` (per binding) drops the FQCN manifest to save space in persistence/ddata (use `deserialization-type` or a single binding).

Auto-registered modules: `AkkaJacksonModule`, `AkkaTypedJacksonModule`, `AkkaStreamJacksonModule`, `ParameterNamesModule`, `Jdk8Module`, `JavaTimeModule`, `DefaultScalaModule`.

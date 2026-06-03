---
name: akka-serialization
description: Akka Serialization (Akka Core 2.10.x) in Scala and Java — converting messages and persisted events to/from bytes for remoting, clustering, and persistence. Covers the Serializer SPI (Serializer, SerializerWithStringManifest, ByteBufferSerializer), serializers + serialization-bindings config, the SerializationExtension, why Java serialization is disabled by default and must be avoided, ActorRef serialization, two-step rolling-update serializer migration, and Jackson serialization (JSON vs CBOR, polymorphism, schema evolution via JacksonMigration). Use whenever choosing or configuring a serializer, making cluster/remote messages or persisted events serializable, evolving an event/message schema, debugging "no serializer" or Java-serialization warnings, or wiring Jackson for Akka — even if "serialization" isn't named but cross-node messages, persisted events, or wire formats are involved. Required by akka-cluster and akka-persistence.
---

# Akka Serialization

Akka passes same-JVM messages by reference, but anything crossing the JVM boundary ([[akka-cluster]]/remoting) or persisted ([[akka-persistence]]) must become bytes. Serialization is a **pluggable SPI** with config-driven bindings. The recommended default is **Jackson**; use Protobuf when you need tight schema control. Required by clustering and persistence.

Dependencies: SPI in `akka-actor`; Jackson in `akka-serialization-jackson`. Cross-links: [[akka]] (meta), [[akka-cluster]], [[akka-persistence]], [[modern-java]].

## The Serializer SPI

- **`SerializerWithStringManifest`** — the recommended interface. `identifier: Int` (unique; **0–40 reserved by Akka**), `manifest(obj): String` (a version-taggable type hint), `toBinary`, `fromBinary(bytes, manifest)`. The string manifest lets classes move/rename and lets you encode a schema version.
- `Serializer`/`JSerializer` — older class-manifest variant. `ByteBufferSerializer` — optional zero-copy variant (Artery uses it). `BaseSerializer` reads the `identifier` from config.

```scala
class MySerializer extends SerializerWithStringManifest {
  def identifier = 1234567
  def manifest(o: AnyRef): String = o match { case _: Customer => "customer"; case _: User => "user" }
  def toBinary(o: AnyRef): Array[Byte] = ...
  def fromBinary(bytes: Array[Byte], manifest: String): AnyRef = manifest match {
    case "customer" => ...; case "user" => ...
  }
}
```

Serializers are initialized eagerly at `ActorSystem` start — don't access `SerializationExtension` from a serializer constructor. In `fromBinary`, throw `IllegalArgumentException`/`NotSerializableException` for unknown manifests; these are treated as **transient** (logged + message dropped), which lets new message types be sent to old nodes during rolling updates.

## Configuration

Bind serializer names to classes, then message classes (or a marker trait/interface) to serializer names:

```hocon
akka.actor {
  serializers {
    jackson-json = "akka.serialization.jackson.JacksonJsonSerializer"
    jackson-cbor = "akka.serialization.jackson.JacksonCborSerializer"
    proto        = "akka.remote.serialization.ProtobufSerializer"
  }
  serialization-bindings {
    "com.example.JsonSerializable" = jackson-json
    "com.google.protobuf.Message"  = proto
  }
}
```
On ambiguity the **most specific** configured class wins. Bind to a marker trait/interface that all your messages extend. Scala nested types use `Wrapper$Message` (not `Wrapper.Message`).

## Programmatic use & ActorRefs

`SerializationExtension(system)` (Scala) / `SerializationExtension.get(system)` (Java): `serialize(obj)`, `findSerializerFor(obj).identifier`, `deserialize(bytes, id, manifest)`. **Always store/transfer the triple `(bytes, serializerId, manifest)`** — deserialization selects the serializer by id, which is what enables serializer migration. Serialize an `ActorRef` via `ActorRefResolver(system).toSerializationFormat(ref)` / `resolveActorRef(str)` (Jackson does this automatically).

## Java serialization — disabled by default, avoid it

Java serialization is slow and a known **RCE attack vector**; Akka disables it by default and never uses it internally. Blocked attempts are logged with the **`SECURITY`** marker. Enable only for prototyping (`akka.actor.allow-java-serialization = on`) — never for production or long-lived persisted events. Use Jackson/Protobuf instead.

## Rolling-update serializer migration (two-step)

1. Add the new serializer to `serializers` but **not** to `serialization-bindings`; roll out (now every node can *read* the new format).
2. Add the `serialization-bindings` entry; roll out (new nodes *emit* the new format, old nodes still read it; old nodes emit old format, new nodes read it).
3. Optionally remove the old serializer (only if it isn't needed to read persisted data).

## Jackson — see `references/jackson.md`

The default recommendation: JSON or CBOR via marker traits (`JsonSerializable`/`CborSerializable`), with safe polymorphism and **schema evolution** via `JacksonMigration`. Read `references/jackson.md` for the full Jackson story (security rules, polymorphism, migrations, compression, per-binding config).

## Test-only verification

`akka.actor.serialize-messages = on` and `serialize-creators = on` force serialization of all messages/`Props` to catch non-serializable types — **enable only in tests**.

## Related

- [[akka-cluster]] — every cross-node message, entity command, and `EntityRef` must be serializable.
- [[akka-persistence]] — events are long-lived; serialization + schema evolution are critical.
- [[modern-java]] — Akka serialization is the right answer to "don't use Java serialization" (Effective Java Items 85–90).
- Source: Akka Core docs, https://doc.akka.io/libraries/akka-core/current/serialization.html (v2.10.x).

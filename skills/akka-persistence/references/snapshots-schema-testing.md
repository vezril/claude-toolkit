# Snapshots, schema evolution & testing

Akka Persistence (2.10.x). Source: doc.akka.io/libraries/akka-core/current/typed/{persistence-snapshot,persistence-testing}.html and persistence-schema-evolution.html

## Snapshotting & retention

Snapshots cut recovery time for long event streams. On recovery, the latest snapshot seeds the state, then post-snapshot events replay.

- **Predicate:** `.snapshotWhen { case (state, evt, seqNr) => … }` / override `shouldSnapshot(...)`.
- **Automatic every N events + keep last K:** `.withRetention(RetentionCriteria.snapshotEvery(numberOfEvents = 100, keepNSnapshots = 2))`. Older snapshots are auto-deleted after a successful new one (predicate-only snapshots do **not** auto-delete).
- Selection on recovery defaults to latest; `.withRecovery(Recovery.withSnapshotSelectionCriteria(SnapshotSelectionCriteria.none))` to skip a now-incompatible snapshot format (only if events weren't deleted). `snapshot-is-optional = true` recovers by replaying all events if a snapshot fails to load.
- Signals: `SnapshotCompleted`/`SnapshotFailed`, `DeleteSnapshotsCompleted`/`Failed` (failures are logged, don't stop the actor).

**Event deletion** is discouraged (loses the audit log). If required (`RetentionCriteria…​.withDeleteEventsOnSnapshot`), never combine immediate deletion with active Projections or with Replicated Event Sourcing. Preferred pattern: emit a terminal "deleted" event, record deletion via a Projection, stop the entity, clean up later in a background task.

## Schema evolution

Events are immutable and long-lived, so old events must be readable under new code. **Serialization is not automatic** — the default is Java serialization (fine for dev, **never production**). Use **Jackson** (built-in evolution support; see [[akka-serialization]]) or another IDL format (Protobuf/Avro/Thrift).

Techniques:
- **Add field** — use a binary-compatible serializer; default missing values (`Option`/defaults).
- **Rename field** — IDL formats (protobuf/thrift store numeric ids) make it free; for JSON, version events (manifest `v1`/`v2`) and rename in an `EventAdapter.fromJournal` / Jackson `JacksonMigration`.
- **Remove an event type** — drop it in an `EventAdapter` (emit `EventSeq.empty`) or use a "tombstone" deserializer that recognizes the old manifest without needing the old class.
- **Split one event into many** — `EventAdapter.fromJournal` returns an `EventSeq` of finer-grained events.
- **Detach domain from storage** — an `EventAdapter[E, JournalType]` (`toJournal`/`fromJournal`/`manifest`) maps your domain `Event` to/from a storage representation that can evolve independently. Register with `.eventAdapter(...)`.

## Testing

**`EventSourcedBehaviorTestKit`** (integration-style, in-memory journal+snapshot). Configure the system with `EventSourcedBehaviorTestKit.config`:

```scala
class AccountSpec extends ScalaTestWithActorTestKit(EventSourcedBehaviorTestKit.config) with AnyWordSpecLike {
  private val tk = EventSourcedBehaviorTestKit[Command, Event, State](system, Account("1", PersistenceId("Account", "1")))
  // beforeEach { tk.clear() }
  "deposit" in {
    val r = tk.runCommand[StatusReply[Done]](Account.Deposit(100, _))
    r.reply shouldBe StatusReply.Ack
    r.event shouldBe Account.Deposited(100)
    r.stateOfType[OpenedAccount].balance shouldBe 100
  }
}
```
```java
@ClassRule public static final TestKitJunitResource testKit = new TestKitJunitResource(EventSourcedBehaviorTestKit.config());
private EventSourcedBehaviorTestKit<Command, Event, Account> tk =
    EventSourcedBehaviorTestKit.create(testKit.system(), Account.create("1", PersistenceId.of("Account", "1")));
// CommandResultWithReply<...> r = tk.runCommand(Account.Deposit(100, replyTo)); assertEquals(..., r.event());
```

`runCommand` returns the event(s), new state, and reply for assertions (`r.event`, `r.eventOfType`, `r.stateOfType`, `r.reply`, `r.hasNoEvents`). Serialization is round-trip-checked automatically. `tk.restart()` exercises recovery from stored snapshot+events. For pure unit tests use `UnpersistentBehavior` with the sync `BehaviorTestKit` (see [[akka-actors]] testing). The lower-level `PersistenceTestKit`/`SnapshotTestKit` can inspect storage and simulate failures (require `PersistenceTestKitPlugin.config`).

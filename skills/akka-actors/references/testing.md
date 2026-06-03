# Testing Akka Typed actors

Akka Typed (2.10.x). Dependency `akka-actor-testkit-typed % Test`. Source: doc.akka.io/libraries/akka-core/current/typed/testing.html (+ testing-async/testing-sync). See also [[tdd]].

## Choosing a testkit

- **Async `ActorTestKit`** — a real `ActorSystem`; for multi-actor / realistic tests. Most tests.
- **Sync `BehaviorTestKit`** — runs on the test thread, deterministic, no real `ActorContext`; for isolated behavior logic. Limited (no Future-callback effects, no scheduler, supervision unsupported, other-actor interactions must be stubbed).

## Async — `ActorTestKit` + `TestProbe`

```scala
class EchoSpec extends ScalaTestWithActorTestKit with AnyWordSpecLike {
  "Echo" must {
    "reply" in {
      val echo  = spawn(Echo())
      val probe = createTestProbe[Echo.Pong]()
      echo ! Echo.Ping("hello", probe.ref)
      probe.expectMessage(Echo.Pong("hello"))
    }
  }
}
```
```java
public class EchoTest {
  @ClassRule public static final TestKitJunitResource testKit = new TestKitJunitResource();
  @Test public void replies() {
    ActorRef<Echo.Ping> echo = testKit.spawn(Echo.create());
    TestProbe<Echo.Pong> probe = testKit.createTestProbe();
    echo.tell(new Echo.Ping("hello", probe.ref()));
    probe.expectMessage(new Echo.Pong("hello"));
  }
}
```

- Standalone: `val testKit = ActorTestKit()` … `testKit.shutdownTestKit()` in `afterAll`. Scala `ScalaTestWithActorTestKit` and Java `TestKitJunitResource` handle setup/shutdown.
- `TestProbe`: `expectMessage`, `expectMessageType[T]`/`expectMessageClass`, `expectNoMessage`, `fishForMessage`, `receiveMessage`. Usable as a `RecipientRef`.
- **Mock + observe**: `Behaviors.monitor(probe.ref, realBehavior)` forwards every message to the probe for assertions.
- **Config**: the testkit loads `application-test.conf` by default; override with `ActorTestKit(ConfigFactory.parseString("…").withFallback(ConfigFactory.load()))`.
- **Virtual time**: `ManualTime` (`ScalaTestWithActorTestKit(ManualTime.config)` / `new TestKitJunitResource(ManualTime.config())`) → `manualTime.timePasses(50.millis)`.
- **Log assertions**: `LoggingTestKit.info("Received message").expect { ref ! Msg }` (chain `.withMessageRegex(...)`, `.withOccurrences(2)`; requires Logback). Use `LogCapturing` (trait/`@Rule`) to buffer logs and flush only on failure.

## Sync — `BehaviorTestKit` + `TestInbox`

```scala
val testKit = BehaviorTestKit(Hello())
testKit.run(Hello.CreateChild("child"))
testKit.expectEffect(Spawned(childBehavior, "child"))
val inbox = TestInbox[String]()
testKit.run(Hello.SayHello(inbox.ref))
inbox.expectMessage("hello")
testKit.childInbox[String]("child").expectMessage("hi")
```
```java
BehaviorTestKit<Hello.Command> test = BehaviorTestKit.create(Hello.create());
test.run(new Hello.CreateChild("child"));
assertEquals("child", test.expectEffectClass(Effect.Spawned.class).childName());
TestInbox<String> inbox = TestInbox.create();
test.run(new Hello.SayHello(inbox.getRef()));
inbox.expectMessage("hello");
```

Assertable **effects**: `Spawned`, `SpawnedAnonymous`, `Stopped`, `Watched`, `WatchedWith`, `Scheduled`, `TimerScheduled`, `AskInitiated`, etc. Test `context.ask` via `Effect.AskInitiated` (inspect the request, then `respondWith(...)` or `timeout()`). `logEntries()` returns captured `CapturedLogEvent`s. Anonymous children are deterministically named `$a`, `$b`, ….

For testing `EventSourcedBehavior`, use `EventSourcedBehaviorTestKit` (see [[akka-persistence]]).

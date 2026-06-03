# IO, dynamic streams, actor interop, custom stages & testing

Akka Streams (2.10.x). Source: doc.akka.io/libraries/akka-core/current/stream/{stream-io,stream-refs,stream-dynamic,actor-interop,stream-customize,stream-testkit}.html

## Streaming IO

**File:** `FileIO.fromPath(path, chunkSize?)` → `Source[ByteString, Future[IOResult]]`; `FileIO.toPath(path, openOptions?)` → `Sink`. Runs on `akka.stream.materializer.blocking-io-dispatcher`.

**TCP:** server `Tcp(system).bind(host, port)` → `Source[IncomingConnection, Future[ServerBinding]]`, handle each `conn.handleWith(flow)`; client `Tcp().outgoingConnection(host, port)` → `Flow[ByteString, ByteString, …]`. TLS via `bindWithTls`/`outgoingConnectionWithTls`.

**Framing** (bytes → messages): `Framing.delimiter(ByteString("\n"), maxFrameLength, allowTruncation)`, `Framing.simpleFramingProtocol(maxLen)` (length-prefixed BidiFlow), `JsonFraming.objectScanner(maxLen)`.

```scala
val echo = Flow[ByteString]
  .via(Framing.delimiter(ByteString("\n"), 256, allowTruncation = true))
  .map(_.utf8String + "!\n").map(ByteString(_))
Tcp(system).bind("127.0.0.1", 8888).runForeach(_.handleWith(echo))
```

## StreamRefs — streams over the network (use with Cluster)

References to a remote stream end, preserving back-pressure across nodes. `StreamRefs.sourceRef()` (offer data out) and `StreamRefs.sinkRef()` (offer to receive) are materialized, sent in a domain message, and run by the target. Single-shot; multicast via a `BroadcastHub` before minting a `SourceRef` per subscriber.

## Dynamic streams

- **`KillSwitch`** — `KillSwitches.single` (`.viaMat(...)(Keep.right)`) controls one stream (`shutdown()`/`abort(ex)`); `KillSwitches.shared("name")` stops many via `.via(ks.flow)`.
- **Hubs** (dynamic fan-in/out): `MergeHub.source[T]` materializes a `Sink` many producers attach to; `BroadcastHub.sink[T]` materializes a `Source` many consumers attach to; combine for a pub/sub bus. `PartitionHub` routes each element to a chosen consumer.

```scala
val ks = src.viaMat(KillSwitches.single)(Keep.right).toMat(Sink.ignore)(Keep.left).run(); ks.shutdown()
val busSink: Sink[String, NotUsed] = MergeHub.source[String](16).to(consumer).run()
val busSrc: Source[String, NotUsed] = producer.toMat(BroadcastHub.sink(256))(Keep.right).run()
```

## Actor interop

- **`ask` in a stream** — `flow.ask[Reply](parallelism)(ref)` (typed: `ActorFlow.ask`); back-pressured via the ask, ordered, target replies become elements.
- **`Source.queue(bufferSize, OverflowStrategy)`** — push from outside; `offer(elem): Future[QueueOfferResult]` (with `backpressure` strategy, wait for the future before offering again). The back-pressured way to feed a stream from non-stream code.
- **`Sink.actorRefWithBackpressure(ref, init, ack, complete, fail)`** — the actor acks each element (lack of ack = backpressure). Prefer over `Sink.actorRef` (no backpressure).
- **Typed:** `ActorSource.actorRefWithBackpressure`, `ActorSink.actorRefWithBackpressure`, and `PubSub.source`/`PubSub.sink` (subscribe/publish to a Typed `Topic`).

```scala
val queue = Source.queue[Int](16, OverflowStrategy.backpressure).to(consumer).run()
queue.offer(1)  // Future[QueueOfferResult]
words.ask[String](parallelism = 5)(ref).runWith(Sink.ignore)  // actor: replyTo ! reply
```

## Custom processing: `GraphStage`

Last resort (prefer operators + GraphDSL). A `GraphStage[S <: Shape]` defines `shape` + `createLogic(attrs): GraphStageLogic`. **All mutable state lives in the per-materialization `GraphStageLogic`, never in the stage.** Register `setHandler(out, OutHandler{ onPull })` / `setHandler(in, InHandler{ onPush })`; use `push`/`pull`/`grab`/`complete`/`fail`, the declarative `emit`/`read` API, `TimerGraphStageLogic` for timers, and `getAsyncCallback` for thread-safe external signals. `GraphStageWithMaterializedValue` exposes a materialized value.

```scala
class NumbersSource extends GraphStage[SourceShape[Int]] {
  val out = Outlet[Int]("out"); override val shape = SourceShape(out)
  override def createLogic(a: Attributes) = new GraphStageLogic(shape) {
    private var n = 1
    setHandler(out, new OutHandler { def onPull(): Unit = { push(out, n); n += 1 } })
  }
}
```

## Testkit

`akka-stream-testkit % Test`. `TestSink.probe` materializes a `TestSubscriber.Probe` (`.request(n)`, `.expectNext(...)`, `.expectComplete()`, `.expectError()`); `TestSource.probe` materializes a `TestPublisher.Probe` (`.sendNext`, `.sendError`, `.sendComplete`). Combine to drive a flow under test.

```scala
Source(1 to 4).filter(_ % 2 == 0).map(_ * 2).runWith(TestSink[Int]()).request(2).expectNext(4, 8).expectComplete()
val (pub, sub) = TestSource[Int]().via(flowUnderTest).toMat(TestSink[Int]())(Keep.both).run()
```
```java
sourceUnderTest.runWith(TestSink.probe(system), system).request(2).expectNext(4, 8).expectComplete();
```
`akka.stream.materializer.debug.fuzzing-mode = on` (test only) exercises concurrent interleavings to expose races.

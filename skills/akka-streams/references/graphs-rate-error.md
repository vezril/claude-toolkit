# Graphs, error handling & parallelism

Akka Streams (2.10.x). Source: doc.akka.io/libraries/akka-core/current/stream/{stream-graphs,stream-composition,stream-error,stream-parallelism,stream-rate}.html

## GraphDSL — non-linear topologies

For fan-out/fan-in beyond linear chains, use the GraphDSL (it reads like a wiring diagram). **Junctions:** fan-out — `Broadcast[T](n)` (to all), `Balance[T](n)` (to one available), `Partition[T](n, fn)`, `Unzip`; fan-in — `Merge[T](n)` (random), `MergePreferred`/`MergePrioritized`, `Zip`/`ZipWith` (combine), `Concat` (first stream fully, then next).

```scala
val g = RunnableGraph.fromGraph(GraphDSL.create() { implicit b =>
  import GraphDSL.Implicits._
  val bcast = b.add(Broadcast[Int](2)); val merge = b.add(Merge[Int](2))
  Source(1 to 10) ~> bcast ~> Flow[Int].map(_ + 1) ~> merge ~> Sink.foreach(println)
                     bcast ~> Flow[Int].map(_ * 10) ~> merge
  ClosedShape
})
g.run()
```
```java
RunnableGraph.fromGraph(GraphDSL.create(b -> {
  UniformFanOutShape<Integer,Integer> bcast = b.add(Broadcast.create(2));
  UniformFanInShape<Integer,Integer>  merge = b.add(Merge.create(2));
  b.from(b.add(Source.range(1,10))).viaFanOut(bcast).via(b.add(f1)).viaFanIn(merge).to(b.add(Sink.ignore()));
  b.from(bcast).via(b.add(f2)).toFanIn(merge);
  return ClosedShape.getInstance();
}));
```

Return a non-`ClosedShape` to build a reusable component: `Source.fromGraph` (`SourceShape`), `Sink.fromGraph` (`SinkShape`), `Flow.fromGraph` (`FlowShape`). `Source.combine`/`Sink.combine` are no-DSL shortcuts. **`BidiFlow`** (codecs/protocol stacks): `BidiFlow.fromFunctions(f, g)`, compose with `.atop`, close with `.join`. **Cycles** deadlock with naive feedback (bounded buffers fill) — break with `buffer(n, dropHead)` on the feedback arc, `MergePreferred`, or balancing with `ZipWith`.

## Error handling

A failing operator tears down the whole stream (downstream sees failure, upstream cancels) unless mitigated:

- **`recover(pf)`** — emit one final element on failure, then complete.
- **`recoverWithRetries(n, pf: Throwable => Source)`** — switch to a fallback Source up to N times (`-1` = infinite).
- **`mapError`**, `onErrorComplete`.
- **Backoff restart** — `RestartSource`/`RestartSink`/`RestartFlow.withBackoff(RestartSettings(minBackoff, maxBackoff, randomFactor).withMaxRestarts(n, within))` for transient resource failures (DB/HTTP reconnects). Never terminates on its own → combine with a `KillSwitch`. `RetryFlow.withBackoff` retries individual elements.
- **Supervision strategies** (opt-in per operator that supports it, e.g. `mapAsync`/`scan`): `Supervision.Stop` (default), `Resume` (drop the bad element, continue), `Restart` (drop + reset operator state). Apply via `withAttributes(ActorAttributes.supervisionStrategy(decider))`.

```scala
val decider: Supervision.Decider = { case _: ArithmeticException => Supervision.Resume; case _ => Supervision.Stop }
val flow = Flow[Int].map(100 / _).withAttributes(ActorAttributes.supervisionStrategy(decider))
val ks = RestartSource.withBackoff(settings)(() => Source.future(fetch()))
  .viaMat(KillSwitches.single)(Keep.right).toMat(Sink.foreach(println))(Keep.left).run()
```
```java
Function<Throwable,Supervision.Directive> decider = e ->
  (e instanceof ArithmeticException) ? Supervision.resume() : Supervision.stop();
flow.withAttributes(ActorAttributes.withSupervisionStrategy(decider));
```

Note: a *failure* (`onError`) can overtake in-flight data (buffered elements may be lost); an *error* modeled as a normal element flows in-band. `recover` acts as a bulkhead confining the collapse.

## Pipelining & parallelism

Default: fused, sequential. Mark `.async` to split into concurrently-running regions.
- **Pipelining** (`a.async.via(b.async)`) — sequential dependent stages run concurrently on different elements; throughput limited by the slowest stage.
- **Parallel** (`Balance` → N copies of a flow each `.async` → `Merge`) — scale by lanes; does not preserve order (use round-robin balance/merge if order matters).

```scala
val parallel = Flow.fromGraph(GraphDSL.create() { implicit b =>
  import GraphDSL.Implicits._
  val balance = b.add(Balance[In](2)); val merge = b.add(Merge[Out](2))
  balance.out(0) ~> worker.async ~> merge.in(0)
  balance.out(1) ~> worker.async ~> merge.in(1)
  FlowShape(balance.in, merge.out)
})
```

## Rate decoupling (recap)

When down/upstream rates differ: `buffer` (explicit bounded buffer + overflow strategy), `conflate` (summarize while consumer is slow), `expand`/`extrapolate` (synthesize while consumer is fast), `throttle` (cap rate). The internal async buffer defaults to `akka.stream.materializer.max-input-buffer-size = 16`; set to 1 (`addAttributes(Attributes.inputBuffer(1, 1))`) when timing operators behave oddly due to prefetch.

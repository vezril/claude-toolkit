# Stream basics, materialization & the operator catalog

Akka Streams (2.10.x). Source: doc.akka.io/libraries/akka-core/current/stream/{stream-flows-and-basics,operators/index}.html

## Building & running

Factories: `Source(iterable)`/`Source.from(list)`, `Source.single`, `Source.future`/`completionStage`, `Source.repeat`, `Source.tick`, `Source.unfold`, `Source.queue`, `Source.fromIterator`. Sinks: `Sink.fold`/`reduce`, `Sink.head`/`headOption`, `Sink.last`, `Sink.seq`, `Sink.foreach`/`foreachAsync`, `Sink.ignore`, `Sink.collect` (Java Collector). Wire with `.via(flow)`, `.to(sink)`, `.viaMat/.toMat(...)(combine)`, `.runWith(sink)`. Java passes the `ActorSystem`/`Materializer` to `run`/`runWith`; Scala takes it implicitly.

## Materialized values & `Keep`

Running a blueprint allocates resources (usually actors) at the terminal op (`run`/`runWith`/`runForeach`). The chain's materialized value defaults to the **leftmost** operator's; pick with `Keep.left/right/both/none`:

```scala
val r: RunnableGraph[(Cancellable, Future[Int])] =
  Source.tick(0.seconds, 1.second, 1).viaMat(flow)(Keep.left).toMat(Sink.fold(0)(_ + _))(Keep.both)
        .mapMaterializedValue { case (c, f) => (c, f) }
```
```java
RunnableGraph<Pair<Cancellable, CompletionStage<Integer>>> r =
  Source.tick(Duration.ZERO, Duration.ofSeconds(1), 1).viaMat(flow, Keep.left())
        .toMat(Sink.fold(0, Integer::sum), Keep.both());
```
A `RunnableGraph` is a reusable blueprint — re-`run()` yields fresh materialized values each time.

## Materialization, fusing, `.async`, ordering

- Operators are **fused** into one actor by default (fast, single-threaded per region, no buffers between fused ops). Insert `.async` to put a region on its own actor → pipeline parallelism, at a thread-crossing cost.
- The materializer is `ActorSystem`-wide (`SystemMaterializer`). `Materializer(context)` binds a stream's lifecycle to an actor (stopping it abruptly terminates the stream — prefer `KillSwitch`/completion).
- **Ordering:** nearly all operators preserve order, **including `mapAsync`**; `mapAsyncUnordered` and fan-in junctions (`Merge`) do not (`Zip` does).

## Operator catalog (grouped)

**Simple (data-rate):** `map`, `mapConcat` (1→0..n, returns a strict `Iterable`/`List` — not flatMap), `collect`/`collectType`, `filter`/`filterNot`, `grouped`/`groupedWeighted`, `sliding`, `scan`/`scanAsync` (emit accumulations), `fold`/`reduce`, `take`/`drop`/`takeWhile`/`dropWhile`, `limit`, `statefulMap`/`statefulMapConcat`, `intersperse`, `zipWithIndex`, `log`.

**Async:** `mapAsync(parallelism)(x => Future[T])` — up to `parallelism` futures in flight, **ordered** output, backpressured. `mapAsyncUnordered` — same, unordered. `mapAsyncPartitioned` — bound in-flight per key. `foldAsync`/`scanAsync`.

**Rate-aware (detached — decouple up/down rates):** `buffer(size, OverflowStrategy.{backpressure,dropHead,dropTail,dropNew,dropBuffer,fail})`, `conflate`/`conflateWithSeed` (combine while consumer is slow), `extrapolate`/`expand` (synthesize for a fast consumer), `throttle(elements, per)` / `throttle(cost, per, costFn)`, `detach`.

**Timer-driven:** `delay`, `dropWithin`, `takeWithin`, `groupedWithin`, `initialDelay`.

**Substreams (nesting/flattening):** `flatMapConcat(x => Source)` (concatenate sub-sources — preferred), `flatMapMerge(breadth, …)` (merge), `groupBy(maxSubstreams, keyFn)` + `mergeSubstreams`, `splitWhen`/`splitAfter`, `prefixAndTail`.

**Status/interop:** `watchTermination` (mat: completion future), `monitor`, `recover`/`recoverWithRetries`/`mapError`, `ask`, `wireTap`/`alsoTo`/`divertTo`.

```scala
src.mapAsync(4)(id => lookup(id)).collect { case Some(v) => v }   // ordered, 4 concurrent
src.groupBy(64, _.key).map(process).mergeSubstreams                // a substream per key
src.conflateWithSeed(Seq(_))(_ :+ _)                              // batch while downstream slow
src.throttle(100, 1.second)                                       // rate limit
```
```java
src.mapAsync(4, id -> lookup(id));
src.groupBy(64, e -> e.key()).map(this::process).mergeSubstreams();
src.throttle(100, Duration.ofSeconds(1));
```

`StreamConverters` bridges blocking `InputStream`/`OutputStream`/Java `Stream` (on `akka.stream.blocking-io-dispatcher`).

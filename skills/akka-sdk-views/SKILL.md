---
name: akka-sdk-views
description: Akka SDK Views (Java) — read-optimized projections (read models) built from entity/topic/stream events and queried with an SQL-like language; the CQRS read side. Covers defining a View (extend View, an inner TableUpdater with @Consume.FromEventSourcedEntity/FromKeyValueEntity/FromWorkflow/FromTopic/FromServiceStream, update handlers via effects().updateRow/deleteRow/ignore), @Query methods returning QueryEffect/QueryStreamEffect, the query syntax (SELECT/FROM/WHERE/ORDER BY/LIMIT/OFFSET, joins, GROUP BY/collect, text_search, pagination tokens, * AS), single vs multi-table views, streaming updates, snapshot/delete handlers, eventual consistency, and testing. Use when you need to query entities by attributes other than their id, query across many instances, or build a materialized read model in an Akka SDK service. Part of the Akka SDK (Java); see akka-sdk for the model.
---

# Akka SDK — Views

A **read model / projection** that lets you query entities by attributes other than their id, and across many instances. You build one View per access pattern (it's auto-indexed for its queries). Views are **eventually consistent**. The CQRS read side for [[akka-sdk-event-sourced-entities]] / [[akka-sdk-key-value-entities]]. Part of the [[akka-sdk]] (Java).

Cross-links: [[akka-sdk]] (meta), [[akka-sdk-event-sourced-entities]], [[akka-sdk-key-value-entities]], [[akka-sdk-consumers]], [[akka-sdk-endpoints]].

## Anatomy

```java
@Component(id = "customers-by-email")          // mandatory, unique, STABLE id
public class CustomersByEmail extends View {
  public record Customers(List<Customer> customers) {}

  @Consume.FromKeyValueEntity(CustomerEntity.class)            // the source goes on the TableUpdater
  public static class Updater extends TableUpdater<Customer> {}  // Row type; empty body = store state as-is

  @Query("SELECT * AS customers FROM customers_by_email WHERE email = :email")
  public QueryEffect<Customers> getByEmail(String email) { return queryResult(); }
}
```

- A View `extends View`; one or more inner `static class … extends TableUpdater<Row>` declares a table (the table name in the SQL is your choice). The `@Consume.*` annotation goes on the **TableUpdater**.
- Sources: `@Consume.FromEventSourcedEntity` (handle events), `FromKeyValueEntity` (state changes), `FromWorkflow` (state), `FromTopic` (broker messages — need `ce-subject` metadata; can't be rebuilt), `FromServiceStream` (another service's events).
- Update handlers return `View.Effect<Row>`: `effects().updateRow(row)` (upsert), `deleteRow()`, `ignore()`. Helpers: `rowState()`, `updateContext().eventSubject()` (source id).
- `@Query` methods return `QueryEffect<T>` (body `return queryResult();`) or `QueryStreamEffect<T>` (`queryStreamResult();`).

```java
@Consume.FromEventSourcedEntity(CustomerEntity.class)
public static class Updater extends TableUpdater<CustomerRow> {
  public Effect<CustomerRow> onEvent(CustomerEvent e) {
    return switch (e) {
      case CustomerEvent.Created c -> effects().updateRow(new CustomerRow(c.email(), c.name()));
      case CustomerEvent.NameChanged n -> effects().updateRow(rowState().withName(n.name()));
      // effects().ignore() for events you don't track
    };
  }
}
```

## Always-apply defaults

1. **One View per query/access pattern;** `@Component(id)` must be **stable** (changing it forces a full rebuild from source — replays all events for ESE-sourced views; topic-sourced views can't rebuild and may lose history).
2. **For ESE sources, switch over a `sealed` event interface** so every case is handled; `ignore()` what you don't need. Add a `@SnapshotHandler` to bootstrap from the latest snapshot (big speedup on long histories).
3. **Treat views as eventually consistent** — poll with Awaitility in tests; never read-your-write synchronously after an entity update.
4. **Build the View instead of scanning entities** by non-id attributes; pass multiple query params as a record whose field names bind to `:placeholders`.
5. **Handle deletes** with a `@DeleteHandler` if you want logical-delete (`updateRow(row.asDeleted())`) vs the default hard delete.
6. **Incompatible schema changes** (adding/removing tables, changing an indexed column's type) require a **new View id** that the runtime rebuilds — deploy alongside the old, let it catch up, switch, remove old.

## Query syntax & streaming

Full detail in **`references/query-syntax.md`** — SELECT/FROM/WHERE/ORDER BY/LIMIT/OFFSET, `:params`, `IN`/`= ANY(:array)`/`LIKE`/`IS NULL`, dot-access for nested fields, `text_search(...)`, `GROUP BY` + `collect(*)`, JOINs across multi-table views, `* AS field` to wrap rows into a result record, and token-based pagination (`next_page_token()` / `page_token_offset(:token)`). **Streaming**: return `QueryStreamEffect<T>` to stream collected results; add `streamUpdates = true` to a `@Query` to emit the current result then keep pushing changed rows (pipe to SSE/gRPC; not for service-to-service propagation and not guaranteed delivery — use a topic for that).

## Testing

Integration via `TestKitSupport`: enable the source (`TestKit.Settings.DEFAULT.withKeyValueEntityIncomingMessages(CustomerEntity.class)`), publish test data through `testKit.getKeyValueEntityIncomingMessages(...).publish(...)`, then query via `componentClient.forView().method(View::getByEmail).invoke(...)` inside an `Awaitility.await()...untilAsserted(...)` (views lag).

## Anti-patterns (flag in review)

- Changing a View's `@Component(id)` casually (forces a rebuild); expecting immediate consistency after a write.
- A topic-sourced view assumed to be rebuildable; non-idempotent topic updater without dedup.
- Scanning/iterating entities for a query a View should serve; relying on `streamUpdates` for reliable service-to-service delivery (use a topic / [[akka-sdk-consumers]]).

## Related

- [[akka-sdk]] · [[akka-sdk-event-sourced-entities]] · [[akka-sdk-key-value-entities]] · [[akka-sdk-consumers]] · [[akka-sdk-endpoints]] (expose query results)
- Source: https://doc.akka.io/sdk/views.html and https://doc.akka.io/reference/views/.

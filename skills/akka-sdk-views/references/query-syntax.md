# Akka SDK View query syntax

Java. Source: doc.akka.io/sdk/views.html, reference/views/index.html, reference/views/syntax/index.html

## Structure

`SELECT <exprs> FROM <tableName> [WHERE <conditions>] [ORDER BY field ASC|DESC] [LIMIT n] [OFFSET ...]`

`<tableName>` is the name you chose for the `TableUpdater`'s table. Each `@Query` method's parameters bind to `:placeholders`; for multiple parameters, take a record whose field names match the placeholders.

## SELECT

- `*` — the whole row.
- specific fields, or `* AS aliasField` to wrap rows into a field of a result record. E.g. to return `record Customers(List<Customer> customers)`: `SELECT * AS customers FROM customers`.
- `count(*)`, `DISTINCT`, and `collect(*)` (with `GROUP BY`) to build nested collections.

## WHERE

- Comparison `= != > < >= <=`; logical `AND OR NOT`.
- `IN (a, b)`, `field = ANY(:array)` (membership in an array param/column), `LIKE 'pattern'`, `IS NULL` / `IS NOT NULL`.
- Nested fields via dot: `WHERE address.country = 'USA' AND address.state = :state`.
- Parameters: `:name`, bound from the method arg or record field.
- `text_search(field, :term)` — advanced text search.

```java
public record Params(String customerName, String city) {}
@Query("SELECT * FROM customers WHERE name = :customerName AND address.city = :city")
public QueryEffect<Customer> get(Params p) { return queryResult(); }
```

## GROUP BY / collect (nested results)

```sql
SELECT category, collect(*) AS products FROM products GROUP BY category
```

## JOIN (multi-table views)

A View may declare several `TableUpdater` inner classes (one table each); `@Query` can join them:
```sql
SELECT c.name, o.id, o.amount
FROM customers AS c JOIN orders AS o ON o.customerId = c.id
WHERE c.id = :customerId
```
Adding/removing tables in a multi-table view is an incompatible change → new View id + rebuild.

## Pagination (token-based)

```sql
SELECT * AS products, next_page_token() AS nextPageToken
FROM products OFFSET page_token_offset(:pageToken) LIMIT 10
```
Pass the prior `:pageToken` (empty for the first page); return `next_page_token()` for the next call. Also `total_count()`, `has_more()`.

## Streaming

- Stream collected results: return `QueryStreamEffect<T>` + `return queryStreamResult();` (avoid materializing a huge list).
- Continuous updates: add `streamUpdates = true` to the `@Query` (returns `QueryStreamEffect<T>`). Emits the full current result, then keeps emitting new/changed matching rows; never completes until the client closes. Pipe to HTTP SSE / gRPC. **Not** for service-to-service propagation and **not guaranteed delivery** — use a topic for that.

```java
@Query(value = "SELECT * FROM customers_by_city WHERE address.city = :city", streamUpdates = true)
public QueryStreamEffect<Customer> continuousByCity(String city) { return queryStreamResult(); }
```

## Delivery & consistency notes

ESE/KVE/Workflow-sourced views use exactly-once delivery via sequence-number dedup (KV caveat: only the latest state is guaranteed; intermediate updates may be skipped). Topic-sourced updaters that aren't idempotent need your own dedup. Views aren't replicated directly across regions — entities replicate events and an identical View is built per region.

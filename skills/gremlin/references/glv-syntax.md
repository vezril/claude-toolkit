# The same Gremlin in every language

Gremlin is embedded in each host language as a **Gremlin Language Variant (GLV)**. The steps are the same, but naming follows the host's conventions and avoids its reserved words. Keep the driver version matched to the server or provider's TinkerPop line.

## Renamed steps

| Gremlin (Java/Groovy) | Python | JavaScript | .NET / Go |
|---|---|---|---|
| `as` | `as_` | `as` | `As` |
| `in` | `in_` | `in_` | `In` |
| `and` / `or` / `not` | `and_` / `or_` / `not_` | `and` / `or` / `not` | `And` / `Or` / `Not` |
| `is` | `is_` | `is` | `Is` |
| `from` | `from_` | `from_` | `From` |
| `with` | `with_` | `with_` | `With` |
| `filter`, `id`, `max`, `min`, `sum`, `range` | `filter_`, `id_`, `max_`, `min_`, `sum_`, `range_` | unchanged | PascalCase |
| `hasLabel`, `valueMap`, `toList` | `has_label`, `value_map`, `to_list` (camelCase also accepted in most versions) | camelCase | PascalCase |

Python and JavaScript rename steps that collide with reserved words or builtins by adding a trailing underscore. .NET and Go capitalize everything. When in doubt, check the GLV section of the reference for your exact version.

## One query, five languages

"Names of people Ada knows who are over 30, oldest first":

```groovy
// Groovy / Java
g.V().has('person','name','Ada').out('KNOWS').has('age', gt(30)).
  order().by('age', desc).values('name').toList()
```

```python
# Python: pip install gremlinpython
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.traversal import P, T, Order, Cardinality, Direction, Merge
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

conn = DriverRemoteConnection('ws://localhost:8182/gremlin', 'g')
g = traversal().with_remote(conn)
names = (g.V().has('person', 'name', 'Ada').out('KNOWS').has('age', P.gt(30))
          .order().by('age', Order.desc).values('name').to_list())
conn.close()
```

```javascript
// JavaScript: npm install gremlin
const gremlin = require('gremlin');
const { DriverRemoteConnection } = gremlin.driver;
const { traversal } = gremlin.process.AnonymousTraversalSource;
const { P, order, t } = gremlin.process;
const __ = gremlin.process.statics;

const conn = new DriverRemoteConnection('ws://localhost:8182/gremlin');
const g = traversal().withRemote(conn);
const names = await g.V().has('person', 'name', 'Ada').out('KNOWS').has('age', P.gt(30))
  .order().by('age', order.desc).values('name').toList();   // always await terminal steps
await conn.close();
```

```csharp
// .NET: dotnet add package Gremlin.Net
using Gremlin.Net.Driver;
using Gremlin.Net.Driver.Remote;
using static Gremlin.Net.Process.Traversal.AnonymousTraversalSource;
using Gremlin.Net.Process.Traversal;

using var client = new GremlinClient(new GremlinServer("localhost", 8182));
var g = Traversal().WithRemote(new DriverRemoteConnection(client, "g"));
var names = await g.V().Has("person", "name", "Ada").Out("KNOWS").Has("age", P.Gt(30))
    .Order().By("age", Order.Desc).Values<string>("name").Promise(t => t.ToList());
```

```go
// Go: go get github.com/apache/tinkerpop/gremlin-go/v3/driver
import gremlingo "github.com/apache/tinkerpop/gremlin-go/v3/driver"

conn, _ := gremlingo.NewDriverRemoteConnection("ws://localhost:8182/gremlin")
defer conn.Close()
g := gremlingo.Traversal_().WithRemote(conn)
res, _ := g.V().Has("person", "name", "Ada").Out("KNOWS").Has("age", gremlingo.P.Gt(30)).
    Order().By("age", gremlingo.Order.Desc).Values("name").ToList()
// anonymous traversals: gremlingo.T__.Out("KNOWS")
```

Newer releases (3.7.3+/3.8) also offer `traversal().with(...)` (Java/JS/.NET) and `with_(...)` (Python) in place of `withRemote`/`with_remote`. Both work on 3.8. Use whichever your version's reference shows.

## Per-language notes

- **Java/Groovy:** the only languages where lambdas are possible (embedded, or Groovy scripts), and the only ones with direct Structure API access. Don't use either if you want portable queries.
- **Python:** results come back as Python dicts, lists and sets, with `T.id`/`T.label` as keys in `elementMap`/`valueMap(True)` output. Maps with element keys can come back as frozen or hashable wrappers. Configure pool size and message size on the connection for big results.
- **JavaScript:** every terminal step returns a Promise. A missing `await` is the JS version of forgetting `iterate()`.
- **.NET:** it's typed. `Values<T>()` and `V<Vertex>()`, `Promise(t => t.ToList())` for async, and `GraphTraversal<S,E>` generics mean some mixed-type projections need `object`.
- **Go:** errors are returned, never thrown. Iterate `ResultSet`s, and use `T__` for anonymous traversals and `gremlingo.P`/`TextP`/`Order`/`Cardinality`/`Merge` for tokens.
- **String scripts** (`client.submit("g.V()...")`) are needed for providers without bytecode support (Cosmos DB) and in 4.0 (GremlinLang strings). Pass values as **parameters/bindings** where supported. Otherwise escape and validate every interpolated value.

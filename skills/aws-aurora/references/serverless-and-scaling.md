# Aurora Serverless v2 and scaling

Source: docs.aws.amazon.com (Aurora Serverless v2) + AWS's Aurora MySQL/PostgreSQL advisor agent skills. Fetched 2026-09.

## The ACU model

Aurora Serverless v2 capacity is measured in **Aurora Capacity Units (ACUs)**, each roughly a fixed amount of memory with proportional CPU and networking. You set a **min/max range** per instance, and Aurora scales within it continuously (not in discrete steps you have to trigger):

- Range: **0.5 – 128 ACUs**, specified in **half-step increments** (8, 8.5, 9, …).
- **Minimum can be 0** on engine versions that support the **auto-pause** feature — true scale-to-zero, billed for essentially nothing while idle. On versions without auto-pause support, the floor is 0.5.
- Scaling happens in seconds, not the minutes-to-tens-of-minutes you'd wait for an RDS instance-class change.

```json
{ "MinCapacity": 0.5, "MaxCapacity": 16 }
```
```bash
aws rds modify-db-cluster --db-cluster-identifier my-cluster \
  --serverless-v2-scaling-configuration MinCapacity=0.5,MaxCapacity=16
```
Treat this as a Tier-1 "confirm before executing" change (see `operations-and-safety.md`) — not destructive, but worth a deliberate yes/no before applying.

## Mixed provisioned + serverless clusters

A single Aurora cluster can mix provisioned instances and Serverless v2 instances as readers/writer. This is a legitimate pattern (e.g. a provisioned writer for predictable baseline load, serverless readers that scale with variable analytical/reporting traffic) — but the **promotion tier of a serverless reader changes its scaling behavior**, not just its failover order (see `architecture-and-availability.md`): tier 0/1 readers are held at a capacity floor matching the writer so they're failover-ready; tier 2+ readers scale independently and can drop to the cluster's minimum ACU when idle.

## Sizing approach

Don't guess an ACU range from first principles — size from actual (or realistically projected) load:
- **CPU p95 and CPU max** against a candidate equivalent instance type are the primary signal (AWS's own advisor skills use an ACU calculator keyed on exactly these two numbers plus storage).
- Storage size is a secondary input — larger working sets need more memory headroom (more ACUs) to avoid excessive I/O.
- Set **max** ACU with real per-workload headroom, not just current peak — Serverless v2 protects you from *under*-provisioning by scaling up automatically, but only within the range you configured.
- Set **min** ACU low (or 0, on supporting versions) whenever the workload is genuinely bursty or has real idle periods — that's the entire cost benefit of choosing serverless over provisioned in the first place.

## When to choose Serverless v2 vs provisioned

| Workload shape | Choice |
|---|---|
| Steady, predictable, 24/7 | Provisioned — commitment pricing (RI or DSP) usually wins on cost |
| Bursty, unpredictable, or with real idle windows | Serverless v2, especially with auto-pause available |
| Dev/test/staging that sits idle overnight and weekends | Serverless v2 with a low or zero minimum |
| Mixed steady-baseline + spiky-analytics | Mixed cluster: provisioned writer, serverless readers |

## Aurora MySQL Parallel Query

MySQL-only. Pushes large table scans and certain aggregations down into the distributed storage layer itself, executing in parallel across the storage nodes rather than pulling all the data up through the buffer pool first. Useful specifically for analytical, scan-heavy queries against data that's mostly *not* in the buffer pool — it's not a general query-performance switch, and it has its own set of supported-query-shape constraints that are worth checking against the current docs before assuming a specific query qualifies.

## RDS Proxy and Serverless v2

RDS Proxy generally works in front of Aurora Serverless v2, but scale-to-zero and certain proxy configurations can interact in ways that aren't obvious — if you're combining `MinCapacity: 0` with RDS Proxy, verify current compatibility rather than assuming it behaves identically to a non-zero-minimum cluster (auto-pause and an actively-pooling proxy are two systems both trying to manage connection/activity state, and this is exactly the kind of "feature constraint" AWS's own Aurora serverless-advisory sub-skill exists to catch).

## Pitfalls

- Sizing an ACU range from a guess instead of CPU p95/max data.
- Setting a high minimum ACU "to be safe," and quietly paying provisioned-equivalent cost for idle capacity — defeating the point of choosing serverless.
- Not realizing a tier-2+ serverless reader can be cold (scaled to minimum) right when you need it for a failover — if fast failover matters for a given reader, tier it 0 or 1 deliberately.
- Assuming Parallel Query is available or beneficial for an arbitrary query shape without checking — it's MySQL-only and workload-shape-specific.

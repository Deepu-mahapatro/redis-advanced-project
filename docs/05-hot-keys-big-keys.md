# Redis Hot Keys & Big Keys

## 1. Overview

Hot Keys and Big Keys are two common Redis performance challenges.

- **Hot Key:** A key that receives an unusually high number of requests.
- **Big Key:** A key that consumes substantial memory or contains a very large data structure.

Both can affect performance, but they cause different problems and require different solutions.

This project explored Redis monitoring, key-size inspection, slow-command analysis, and safe key removal using Memurai on Windows.

## 2. Why Do We Need Hot Key and Big Key Analysis?

Redis is designed for fast data access, but a poorly distributed workload or oversized data structure can create performance bottlenecks.

### Problems caused by Hot Keys

- Too many requests target the same key.
- One Redis node may handle disproportionate traffic in a clustered deployment.
- A frequently accessed key can become a workload bottleneck.
- A popular cache entry may cause repeated processing or invalidation pressure.

### Problems caused by Big Keys

- Large data structures consume substantial memory.
- Reading or deleting a large collection can take significant time.
- Large responses can increase network traffic.
- Memory pressure can affect the entire Redis instance.

## 3. Hot Keys vs Big Keys

| Feature | Hot Key | Big Key |
|---|---|---|
| Main issue | High request frequency | Large memory footprint or collection size |
| Common symptom | High traffic to one key | High memory usage or expensive collection operations |
| Main investigation | Request patterns and command statistics | Memory usage and collection size |
| Common solution | Caching strategy, workload distribution, or sharding where appropriate | Data modelling, splitting collections, bounded data, and careful deletion |
| Can a key be both? | Yes | Yes |

A key does not need to be large to be hot, and a large key does not need to receive frequent requests.

## 4. Important Redis Diagnostic Commands

| Command | Purpose |
|---|---|
| `INFO stats` | Displays server statistics, including command and keyspace activity |
| `INFO commandstats` | Shows command-call counts and execution-time statistics |
| `MONITOR` | Displays commands processed by Redis in real time |
| `SLOWLOG GET 10` | Displays recent entries in the slow-command log |
| `MEMORY USAGE key` | Estimates the memory used by a key |
| `STRLEN key` | Returns the length of a string value |
| `LLEN key` | Returns the number of elements in a list |
| `SCARD key` | Returns the number of members in a set |
| `HLEN key` | Returns the number of fields in a hash |
| `ZCARD key` | Returns the number of members in a sorted set |
| `UNLINK key` | Removes a key and schedules its memory reclamation asynchronously |
| `TYPE key` | Returns the type of a key |
| `DBSIZE` | Returns the number of keys in the selected database |
| `--bigkeys` | Scans keys and reports the largest observed values by data type |

## 5. Practical Work Completed

The following exercises were performed during the project:

- Inspected Redis statistics with `INFO stats`.
- Explored command statistics with `INFO commandstats`.
- Observed commands with `MONITOR`.
- Inspected slow-command records with `SLOWLOG GET 10`.
- Measured key memory usage with `MEMORY USAGE`.
- Checked string length and collection sizes.
- Scanned keys using `memurai-cli --bigkeys`.
- Checked the configured eviction policy using `CONFIG GET maxmemory-policy`.
- Practised removing a demonstration list with `UNLINK`.

The configured eviction policy was observed as `noeviction`. An attempt to use `OBJECT FREQ` returned an error because the required LFU tracking configuration was not enabled.

These exercises helped distinguish key-size analysis, workload monitoring, and eviction behavior.

## 6. Detecting Hot Keys

A hot key is identified primarily by its access pattern, not by its size.

### Step 1 — Inspect server statistics

```redis id="v7w83e"
INFO stats
```

Review relevant counters, including total commands processed and keyspace hits or misses where available.

### Step 2 — Inspect command statistics

```redis id="5f0i9q"
INFO commandstats
```

This helps identify frequently executed command types and their recorded execution time. It does not identify the exact key responsible for every command.

### Step 3 — Observe commands

```redis id="m5tr4h"
MONITOR
```

This displays incoming commands in real time.

**Important:** `MONITOR` can generate substantial overhead and expose command arguments. Use it briefly in a controlled learning environment, not as a default production monitoring method.

### Hot Key mitigation strategies

- Cache frequently requested data efficiently.
- Avoid repeatedly performing expensive computations for the same value.
- Consider application-side caching when appropriate.
- Distribute workload across shards when the architecture supports it.
- Review whether a single key is being accessed by too many clients.

A hot key is not automatically fixed by deleting it or by increasing the memory limit.

## 7. Detecting Big Keys

A big key can be identified by inspecting its memory footprint and, where appropriate, the size of its collection.

### Step 1 — Check the key type

```redis id="7f9nks"
TYPE products:all
```

### Step 2 — Inspect memory usage

```redis id="m0b7g8"
MEMORY USAGE products:all
```

The result estimates the memory consumed by the key in bytes.

### Step 3 — Inspect collection size

For a list:

```redis id="n3p9x4"
LLEN products:list
```

For a hash:

```redis id="1w8jke"
HLEN products:hash
```

For a set:

```redis id="q5e7bm"
SCARD products:set
```

For a sorted set:

```redis id="0r9b5d"
ZCARD products:sorted
```

These commands return element counts, not the exact total memory consumed by the collection.

### Step 4 — Scan for large keys

From PowerShell, run:

```powershell id="k7g4cx"
memurai-cli --bigkeys
```

The scan examines keys and reports the largest observed values for supported data types.

The output depends on the keys currently stored in the selected database. Run the scan against a suitable environment and database.

## 8. Removing Large Keys Safely

Deleting a large collection can create a noticeable performance impact if its memory reclamation requires substantial work.

Redis provides `UNLINK`, which removes the key from the keyspace and schedules memory reclamation asynchronously where supported.

```redis id="3v6yba"
UNLINK demo:large-list
```

### Why use UNLINK?

- The key is removed from the keyspace without waiting for all its memory to be reclaimed synchronously.
- Reclamation can occur in the background.
- It can reduce the immediate blocking impact of deleting a large aggregate.

`UNLINK` does not eliminate all costs, and the background reclamation still consumes resources.

Only remove keys you are certain can be deleted. For important data, consider retention requirements and application dependencies first.

## 9. Redis Eviction Policies

When `maxmemory` is configured and Redis reaches the applicable memory limit, the eviction policy determines whether and how keys are evicted.

| Policy | Purpose |
|---|---|
| `noeviction` | Rejects memory-consuming writes when the configured limit prevents them |
| `allkeys-lru` | Evicts keys approximating least-recently-used behavior |
| `allkeys-lfu` | Evicts keys approximating least-frequently-used behavior |
| `allkeys-random` | Evicts randomly selected keys |
| `volatile-lru` | Evicts eligible keys with expiration using approximate LRU |
| `volatile-lfu` | Evicts eligible keys with expiration using approximate LFU |
| `volatile-random` | Evicts randomly selected keys with expiration |
| `volatile-ttl` | Prefers eligible expiring keys with the shortest remaining TTL |

### Check the current policy

```redis id="q8w2my"
CONFIG GET maxmemory-policy
```

In this project, the observed policy was `noeviction`.

### Important distinction

Eviction policies manage memory pressure. They do not detect or directly solve hot keys, and they do not guarantee that the largest key will be removed.

Choose a policy according to the application's data-retention and caching requirements. Do not change production settings without understanding the consequences.

## 10. Key Takeaways

1. **Hot Keys are traffic problems:** Investigate access patterns and distribute or optimize the workload.
2. **Big Keys are size problems:** Inspect memory and collection sizes, and redesign or remove oversized data structures safely.
3. **Monitoring and eviction serve different purposes:** Diagnostic commands help identify issues; eviction policies govern memory-limit behavior.


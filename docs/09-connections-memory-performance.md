# Redis Connections, Memory & Performance

## 1. Overview

Redis is an in-memory data store designed for fast data access. Its performance depends on several factors, including client connections, memory usage, command execution, network latency, and workload patterns.

This project explored how Redis manages connections, how to inspect memory consumption, how eviction policies work, and how to investigate performance problems using Memurai CLI.

## 2. Why Do We Need Connection and Performance Management?

A Redis server can become slow or unavailable when it receives too many connections, runs expensive commands, or approaches its configured memory limit.

Monitoring these factors helps identify bottlenecks before they affect the application.

### Problems this topic helps diagnose

- Too many client connections.
- High memory consumption.
- Memory fragmentation.
- Slow commands and high latency.
- Repeated cache misses.
- Memory-limit write failures.
- Workload imbalances caused by hot keys or large data structures.

## 3. Redis Connection Management

A Redis client connects to the server over a network connection, usually using TCP.

The client sends Redis commands through the connection and receives responses.

### Connection lifecycle

1. The application creates or obtains a Redis client.
2. The client establishes a connection to Redis when required.
3. The application sends commands.
4. Redis processes the commands and returns responses.
5. The connection is reused or closed according to the client's lifecycle.

### Important connection concepts

| Concept | Definition |
|---|---|
| Client connection | A connection between an application client and Redis |
| Connection pool | Reuses available connections instead of repeatedly creating new ones |
| Connection timeout | Limits how long a client waits to establish a connection |
| Socket timeout | Limits how long a client waits for socket operations or responses |
| Maximum clients | Limits the number of simultaneous client connections accepted by the server |

### Why connection pooling matters

Creating a new connection for every individual operation can add overhead. A connection pool allows an application to reuse connections across requests.

The Python Redis client generally uses a connection pool by default, unless configured otherwise. Pool sizing should match application concurrency and Redis server capacity.

## 4. Redis Connection Commands

| Command | Purpose |
|---|---|
| `INFO clients` | Displays client-related statistics |
| `CLIENT LIST` | Lists active client connections |
| `CLIENT INFO` | Displays information about the current client connection |
| `CLIENT ID` | Returns the current connection's client ID |
| `CLIENT SETNAME name` | Assigns a name to the current connection |
| `CONFIG GET maxclients` | Displays the configured maximum client count, when supported |

### Practical commands

Inspect client information:

```redis id="r8w7dv"
INFO clients
```

List active clients:

```redis id="w5p4se"
CLIENT LIST
```

These commands help investigate connection counts and client behavior.

**Important:** `CLIENT LIST` can return substantial output on a busy server. Use it thoughtfully in production environments.

## 5. Redis Memory Management

Redis stores its working dataset in memory. Memory usage depends on the values, data structures, key metadata, client buffers, and other server allocations.

### Important memory metrics

| Metric | Meaning |
|---|---|
| `used_memory` | Memory allocated by Redis according to its allocator accounting |
| `used_memory_rss` | Resident memory reported by the operating system |
| `used_memory_peak` | Highest recorded Redis memory usage |
| `mem_fragmentation_ratio` | Ratio comparing resident memory with Redis allocator memory |
| `maxmemory` | Configured memory limit for Redis data-management behavior |

### Why memory usage matters

If Redis consumes too much memory, the operating system may experience memory pressure. If a Redis `maxmemory` limit is reached, behavior depends on the configured eviction policy.

Memory should be monitored alongside workload, client buffers, and operating-system capacity.

## 6. Redis Memory Commands

| Command | Purpose |
|---|---|
| `INFO memory` | Displays Redis memory statistics |
| `MEMORY USAGE key` | Estimates the memory consumed by a key |
| `MEMORY STATS` | Displays detailed memory statistics, where supported |
| `DBSIZE` | Returns the number of keys in the selected database |
| `CONFIG GET maxmemory` | Displays the configured memory limit |
| `CONFIG GET maxmemory-policy` | Displays the configured eviction policy |

### Inspect memory

```redis id="w9n5jm"
INFO memory
```

Inspect a specific key:

```redis id="u3x7da"
MEMORY USAGE products:all
```

Check the memory limit:

```redis id="t6y4cf"
CONFIG GET maxmemory
```

Check the eviction policy:

```redis id="q5b8xn"
CONFIG GET maxmemory-policy
```

The returned values depend on the current server configuration and the keys stored in the selected database.

## 7. Memory Fragmentation

Memory fragmentation occurs when the memory held by the process differs from the memory reported as actively allocated for Redis data and structures.

For example, the operating system may report more resident memory than Redis's allocator accounting.

A high fragmentation ratio does not automatically mean that Redis has a memory leak. The ratio should be evaluated alongside absolute memory values, workload, allocator behavior, and operating-system metrics.

### What to monitor

- Redis allocator memory.
- Resident memory.
- Peak memory usage.
- Memory fragmentation.
- Client and replication buffers.
- Operating-system memory pressure.

## 8. Redis Eviction Policies

When a `maxmemory` limit is configured and reached, the eviction policy determines whether Redis evicts eligible keys or rejects memory-consuming writes.

| Policy | Purpose |
|---|---|
| `noeviction` | Rejects memory-consuming writes when the limit prevents them |
| `allkeys-lru` | Evicts keys using approximate least-recently-used behavior |
| `allkeys-lfu` | Evicts keys using approximate least-frequently-used behavior |
| `allkeys-random` | Evicts randomly selected keys |
| `volatile-lru` | Evicts eligible expiring keys using approximate LRU |
| `volatile-lfu` | Evicts eligible expiring keys using approximate LFU |
| `volatile-random` | Evicts randomly selected eligible expiring keys |
| `volatile-ttl` | Prefers eligible expiring keys with the shortest remaining TTL |

### Check the configured policy

```redis id="x7w3nb"
CONFIG GET maxmemory-policy
```

During this project's exercises, the configured policy was observed as `noeviction`.

### Choosing an eviction policy

- Use an appropriate all-keys policy when Redis primarily stores disposable cache data.
- Consider volatile policies when only keys with expiration should be eligible for eviction.
- Understand that `noeviction` can cause writes to fail at the configured limit.
- Do not assume eviction policies guarantee that the largest or hottest key will be removed.

Eviction is a memory-management mechanism, not a replacement for investigating oversized values or poor workload distribution.

## 9. Redis Performance and Latency

Latency is the time taken for an operation or request to complete.

Throughput is the amount of work completed in a period of time.

A system can have high throughput while still experiencing latency spikes for some requests.

### Common causes of performance problems

- Slow or expensive commands.
- Large collections and large responses.
- Hot keys and uneven workload.
- Too many connections or excessive connection churn.
- Network delays.
- Memory pressure.
- Large pipelines or scripts that occupy substantial server resources.

### Commands for performance analysis

| Command | Purpose |
|---|---|
| `INFO stats` | Displays server activity statistics |
| `INFO commandstats` | Shows command-call counts and execution-time statistics |
| `SLOWLOG GET 10` | Displays recent slow-command log entries |
| `LATENCY LATEST` | Displays recent latency events, where supported |
| `LATENCY DOCTOR` | Provides latency diagnostics, where supported |
| `MONITOR` | Observes incoming commands in real time |

### Inspect slow commands

```redis id="f3y6km"
SLOWLOG GET 10
```

### Inspect command statistics

```redis id="a7d9kp"
INFO commandstats
```

### Inspect latency events

```redis id="n8m3zr"
LATENCY LATEST
```

Latency-monitoring commands may require configuration and may not be supported by every Redis-compatible server version.

`MONITOR` can impose significant overhead, so use it briefly in controlled debugging sessions rather than as a permanent monitoring solution.

## 10. Practical Work Completed

The project explored the following:

- Inspected client statistics and connection information.
- Reviewed memory usage and memory fragmentation metrics.
- Checked configured memory limits and eviction policies.
- Inspected command statistics and slow-command logs.
- Reviewed Redis performance metrics.
- Connected these measurements to hot-key, big-key, and pipelining concepts.

These exercises established how to inspect Redis health using CLI diagnostics. They did not constitute a production load-testing or long-duration benchmarking campaign.

## 11. Connection and Memory Management in Django

The project uses a reusable Redis client helper for its Django integrations.

```python id="y3v7qk"
import redis
from django.conf import settings


def get_redis_client():
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,
    )
```

### Practical considerations

- Reuse the client and its connection pool where appropriate.
- Configure connection and socket timeouts according to application requirements.
- Avoid creating excessive numbers of independent pools.
- Handle Redis connection failures gracefully.
- Monitor pool usage and application concurrency.
- Close explicitly managed resources when appropriate.

The correct connection lifecycle depends on how the client is used in each view or background worker.

## 12. Key Takeaways

1. **Connection management matters:** Reusing connections reduces overhead and helps control resource consumption.
2. **Memory management matters:** Inspect allocator memory, resident memory, memory limits, and eviction policies together.
3. **Performance requires diagnosis:** Use server statistics, command metrics, slow logs, and latency tools to investigate bottlenecks before changing configuration.


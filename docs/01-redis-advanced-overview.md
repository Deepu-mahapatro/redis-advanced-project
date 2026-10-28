# Redis Advanced Project

A hands-on learning project exploring advanced Redis concepts, Redis CLI operations, performance analysis, persistence, messaging, atomic operations, and Django integration.

## 1. Project Overview

This project was created to understand how Redis works beyond basic key-value storage and how its advanced features are used in backend development.

The project covers nine advanced Redis topics, from Pub/Sub and transactions to performance monitoring and high availability. Practical exercises were performed using **Memurai (Redis-compatible server), Redis CLI commands, Django, and Postman**, where applicable.

### Project Goals

- Understand Redis advanced concepts through practical exercises.
- Learn how Redis handles messaging, transactions, persistence, and atomic operations.
- Identify and investigate hot keys, big keys, memory usage, and performance issues.
- Implement selected Redis features through Django APIs.
- Test API behavior using Postman.
- Understand replication, Sentinel, and Cluster for high availability and scalability.

## 2. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| Django | Backend framework for selected Redis integrations |
| Redis | In-memory data store and advanced data operations |
| Memurai | Redis-compatible server used on Windows |
| Redis Python client | Connects Python/Django applications to Redis |
| Postman | Tests Django API endpoints |
| PowerShell | Runs project commands on Windows |
| Git and GitHub | Version control and project documentation |

## 3. Project Structure

The project contains Django configuration and separate application modules for different Redis learning topics.

```text
redis-advanced-project/
│
├── config/
│   ├── settings.py
│   └── urls.py
│
├── apps/
│   ├── pubsub/
│   ├── transactions/
│   ├── persistence/
│   ├── key_analysis/
│   └── pipelining/
│
├── docs/
│   ├── 01-redis-advanced-overview.md
│   ├── 02-pub-sub.md
│   ├── 03-transactions-atomicity.md
│   ├── 04-persistence.md
│   ├── 05-hot-keys-big-keys.md
│   ├── 06-pipelining.md
│   ├── 07-streams.md
│   ├── 08-lua-scripting.md
│   ├── 09-connections-memory-performance.md
│   └── 10-replication-sentinel-cluster.md
│
├── manage.py
├── requirements.txt
└── README.md
```

*Note: This is an overview of the main structure. Refer to the actual repository for the complete directory tree and installed applications.*

## 4. Redis Connection Configuration

The Django project uses Redis connection settings in `config/settings.py`.

```python
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 0
```

A reusable Redis client helper is used in the relevant Django applications.

```python
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

### Why use a reusable Redis client helper?

- Avoids repeating connection configuration in multiple files.
- Keeps Redis connection settings centralized.
- Returns decoded strings instead of raw bytes for responses.
- Makes Redis operations easier to organize within Django applications.

The exact connection lifecycle and pooling behavior depend on how the client is created and closed in each application.

## 5. Topics Covered

### Topic 1 — Redis Pub/Sub

**Documentation:** [`02-pub-sub.md`](02-pub-sub.md)

Redis Pub/Sub enables publishers to send messages to channels and subscribers to receive messages from those channels.

**Concepts covered:**
- Publishers and subscribers
- Channels and message delivery
- `PUBLISH`, `SUBSCRIBE`, and `UNSUBSCRIBE`
- Real-time message flow
- Limitations of Pub/Sub message delivery

**Practical work:** Redis CLI exercises and Django integration.

**Key takeaway:** Pub/Sub supports real-time messaging, but messages are not stored for subscribers that are offline.

### Topic 2 — Redis Transactions & Atomicity

**Documentation:** [`03-transactions-atomicity.md`](03-transactions-atomicity.md)

Redis transactions group commands for execution through a transaction pipeline.

**Commands covered:**

| Command | Purpose |
|---|---|
| `MULTI` | Starts a transaction |
| `EXEC` | Executes queued transaction commands |
| `DISCARD` | Discards queued commands |
| `WATCH` | Watches keys for modifications before transaction execution |
| `UNWATCH` | Removes watched keys |

**Practical work:** Redis CLI exercises, Django integration, and Postman testing.

**Key takeaway:** Transactions help coordinate related Redis commands. `WATCH` supports optimistic concurrency control, but Redis transactions do not provide relational-database-style rollback for every runtime command error.

### Topic 3 — Redis Persistence: RDB & AOF

**Documentation:** [`04-persistence.md`](04-persistence.md)

Persistence allows Redis data to be saved to disk so it can be recovered after a restart, depending on configuration and the state of the saved data.

| Mechanism | Purpose |
|---|---|
| RDB | Saves point-in-time snapshots of Redis data |
| AOF | Records write operations for replay during recovery |

**Commands and operations covered:**
- `INFO persistence`
- `CONFIG GET`
- `CONFIG SET`
- `SAVE`
- `BGSAVE`
- `BGREWRITEAOF`

**Practical work:** Enabled AOF, checked persistence status, verified successful AOF writes, triggered AOF rewriting, and practised RDB-related operations.

**Key takeaway:** RDB and AOF offer different recovery and durability trade-offs. Actual data-loss risk depends on persistence settings and the timing of writes.

### Topic 4 — Hot Keys & Big Keys

**Documentation:** [`05-hot-keys-big-keys.md`](05-hot-keys-big-keys.md)

A hot key receives unusually high traffic. A big key occupies substantial memory or contains a large collection.

**Commands covered:**

| Command | Purpose |
|---|---|
| `INFO stats` | Inspects Redis server statistics |
| `INFO commandstats` | Displays command execution statistics |
| `MONITOR` | Observes commands received by Redis |
| `SLOWLOG GET` | Inspects recorded slow commands |
| `MEMORY USAGE` | Estimates the memory consumed by a key |
| `STRLEN` | Returns the length of a string value |
| `LLEN` | Returns the length of a list |
| `SCARD` | Returns the number of set members |
| `HLEN` | Returns the number of hash fields |
| `ZCARD` | Returns the number of sorted-set members |
| `UNLINK` | Removes keys with asynchronous memory reclamation |

**Practical work:** Inspected key sizes and collection lengths, explored monitoring commands, used `--bigkeys`, checked the configured eviction policy, and practised removing a demonstration list with `UNLINK`.

**Key takeaway:** Hot keys are primarily a traffic problem; big keys are primarily a data-size and memory-management problem. They require different diagnostic approaches.

### Topic 5 — Redis Pipelining

**Documentation:** [`06-pipelining.md`](06-pipelining.md)

Pipelining sends multiple Redis commands without waiting for each command's response individually.

**Practical work completed:**
- Implemented a Django pipeline demonstration endpoint.
- Compared individual writes with pipelined writes.
- Implemented batch processing for 1,000 keys in batches of 200.
- Tested the endpoints using Postman.

**Endpoints implemented:**

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/pipelining/demo/` | Executes a pipeline demonstration |
| POST | `/api/pipelining/benchmark/` | Compares individual writes with pipelined writes |
| POST | `/api/pipelining/batch/` | Writes keys in batches |

**Key takeaway:** Pipelining reduces network round trips and can improve throughput. It does not automatically make a group of commands atomic.

### Topic 6 — Redis Streams & Consumer Groups

**Documentation:** [`07-streams.md`](07-streams.md)

Redis Streams provide an append-oriented event log with message IDs, consumer groups, and acknowledgement tracking.

**Commands covered:**
- `XADD`
- `XRANGE`
- `XREVRANGE`
- `XREAD`
- `XLEN`
- `XGROUP CREATE`
- `XREADGROUP`
- `XPENDING`
- `XACK`
- `XAUTOCLAIM`
- `XINFO`
- `XDEL`
- `XTRIM`

**Practical work:** Created streams, inserted and read events, created consumer groups, inspected pending messages, acknowledged processed messages, practised claiming pending messages, and explored trimming.

**Implementation status:** Redis CLI practice completed; Django integration was intentionally skipped.

**Key takeaway:** Streams are useful for persisted event processing and consumer-group workflows. Message acknowledgement and retention need to be designed carefully.

### Topic 7 — Redis Lua Scripting

**Documentation:** [`08-lua-scripting.md`](08-lua-scripting.md)

Lua scripting allows multiple Redis operations and conditions to run together on the server as one atomic script execution.

**Commands and concepts covered:**
- `EVAL`
- `EVALSHA`
- `SCRIPT LOAD`
- `SCRIPT EXISTS`
- `SCRIPT FLUSH`
- `SCRIPT KILL`
- `redis.call()`
- `redis.pcall()`

**Practical work:** Loaded and executed scripts, checked script caching, retrieved keys from scripts, implemented conditional stock decrements, and explored error handling.

**Implementation status:** Redis CLI practice completed; Django integration was intentionally skipped.

**Key takeaway:** Lua scripting is useful for operations that require server-side conditional logic and atomic execution. Scripts should remain short and efficient because they block other Redis activity while running.

### Topic 8 — Connections, Memory & Performance

**Documentation:** [`09-connections-memory-performance.md`](09-connections-memory-performance.md)

This topic covers how Redis connections work, how memory is consumed, and how to investigate performance issues.

**Concepts covered:**
- Connection lifecycle and connection pooling
- Client limits and timeouts
- Memory usage and resident memory
- Memory fragmentation
- `maxmemory` and eviction policies
- Latency versus throughput
- Monitoring and performance diagnosis

**Commands covered:**
- `INFO clients`
- `INFO memory`
- `INFO stats`
- `INFO commandstats`
- `CLIENT LIST`
- `CONFIG GET maxmemory`
- `CONFIG GET maxmemory-policy`
- `MEMORY USAGE`
- `SLOWLOG GET`
- `LATENCY`

**Practical work:** Inspected Redis statistics, reviewed memory metrics and eviction configuration, and explored performance diagnostics.

**Key takeaway:** Reliable Redis performance requires monitoring connections, memory, command latency, key sizes, and workload patterns together.

### Topic 9 — Replication, Sentinel & Cluster

**Documentation:** [`10-replication-sentinel-cluster.md`](10-replication-sentinel-cluster.md)

This topic explains how Redis supports redundancy, failover, and data distribution.

| Concept | Purpose |
|---|---|
| Replication | Copies data from a primary to replicas |
| Sentinel | Monitors a primary-based deployment and coordinates failover |
| Redis Cluster | Distributes keys across multiple primaries and supports replica-based failover |

**Important concepts covered:**
- Primary and replica roles
- Asynchronous replication and replication lag
- Failure detection and quorum
- Sentinel failover
- Sharding and hash slots
- Cluster-aware clients
- Availability and data-loss trade-offs

**Implementation status:** Theory completed. Multi-node replication, Sentinel, and Cluster deployment were not implemented as part of this project.

**Key takeaway:** Replication provides copies, Sentinel manages failover for a primary-based deployment, and Cluster distributes data across multiple primaries.

## 6. Practical Implementation Summary

| Topic | CLI practice | Django/Postman integration |
|---|---|---|
| Pub/Sub | Completed | Completed |
| Transactions & Atomicity | Completed | Completed |
| Persistence | Completed | Not required for the exercises |
| Hot Keys & Big Keys | Completed | Not required for the exercises |
| Pipelining | Completed | Completed |
| Streams | Completed | Intentionally skipped |
| Lua Scripting | Completed | Intentionally skipped |
| Connections, Memory & Performance | Completed | Concepts and diagnostic exercises |
| Replication, Sentinel & Cluster | Theory covered | Not implemented |

This distinction is important: the project demonstrates a combination of Redis command-line practice, backend integration, performance investigation, and theoretical architecture learning rather than nine fully deployed production systems.

## 7. Running the Project Locally

### Prerequisites

- Python installed
- Memurai or another compatible Redis server
- Git
- Postman for API testing

### Step 1 — Start Memurai

Open PowerShell and verify that the Redis-compatible server is running:

```powershell
memurai-cli PING
```

Expected response:

```text
PONG
```

### Step 2 — Navigate to the project

```powershell
cd C:\Users\deepu\Downloads\redis-advanced-project
```

### Step 3 — Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 4 — Install dependencies

```powershell
pip install -r requirements.txt
```

### Step 5 — Check Django configuration

```powershell
python manage.py check
```

### Step 6 — Start the Django server

```powershell
python manage.py runserver
```

The development server normally runs at `http://127.0.0.1:8000/`.

Use the endpoints registered in the project's Django URL configuration for the relevant practical exercises.

## 8. Testing with Postman

For the implemented pipelining endpoints:

| Method | URL |
|---|---|
| POST | `http://127.0.0.1:8000/api/pipelining/demo/` |
| POST | `http://127.0.0.1:8000/api/pipelining/benchmark/` |
| POST | `http://127.0.0.1:8000/api/pipelining/batch/` |

For each endpoint:

1. Select the appropriate HTTP method.
2. Enter the endpoint URL.
3. Send the request.
4. Inspect the JSON response.
5. Verify relevant Redis keys with `memurai-cli` where appropriate.

Other endpoints depend on the routes actually registered in their Django applications.

## 9. Important Lessons Learned

Through this project, the following backend engineering concepts were explored:

1. **Data correctness:** Transactions and Lua scripting help coordinate related operations.
2. **Messaging:** Pub/Sub supports live notifications, while Streams provide retained events and consumer-group processing.
3. **Performance:** Pipelining reduces round trips; hot-key and big-key analysis helps diagnose bottlenecks.
4. **Data durability:** RDB and AOF provide different persistence strategies.
5. **Resource management:** Connection and memory monitoring helps maintain performance.
6. **High availability:** Replication, Sentinel, and Cluster address redundancy, failover, and data distribution.
7. **Backend integration:** Django and Postman provide a practical way to expose and test Redis functionality.

## 10. Conclusion

The Redis Advanced Project builds on fundamental Redis operations and explores the features that matter when Redis is used in backend applications.

The project combines hands-on command-line exercises, selected Django API implementations, Postman testing, performance investigation, and architectural study.

It provides a foundation for using Redis in caching, rate limiting, atomic operations, event processing, and other backend workflows. Further production experience would involve deploying multi-node Redis environments, testing failure recovery, securing connections, monitoring workloads, and validating durability requirements.

---

**Project status:** Core learning roadmap completed. Selected Django integrations and CLI exercises completed; Replication, Sentinel, and Cluster remain theory-only in this repository.
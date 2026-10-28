# ⚡ Redis Advanced Project

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Django-Backend-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/Redis-Advanced-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis">
  <img src="https://img.shields.io/badge/Memurai-Windows-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Memurai">
  <img src="https://img.shields.io/badge/Postman-API_Testing-FF6C37?style=for-the-badge&logo=postman&logoColor=white" alt="Postman">
  <img src="https://img.shields.io/badge/Git-GitHub-F05032?style=for-the-badge&logo=git&logoColor=white" alt="Git">
</p>

<p align="center">
  <b>A hands-on Redis project exploring advanced Redis features, backend integration, performance, persistence, and distributed-system concepts.</b>
</p>

---

# 📌 About the Project

This project is a practical **Redis Advanced Learning Project** built around Redis-compatible Memurai, Redis CLI, Django, and Postman.

The objective is to understand how Redis works beyond basic caching and data structures by exploring messaging, atomic operations, persistence, performance optimization, scripting, and distributed Redis architecture.

Instead of learning commands only through theory, the project follows a practical learning process wherever applicable:

```text
Concept
   ↓
Understand the Problem
   ↓
Learn Redis Commands
   ↓
Practice Using Memurai CLI
   ↓
Implement in Django Where Applicable
   ↓
Test Using Postman
   ↓
Verify Redis Behavior
   ↓
Understand End-to-End Flow
```

The project covers the following advanced Redis topics:

```text
Pub/Sub
Transactions & Atomicity
Persistence: RDB & AOF
Hot Keys & Big Keys
Pipelining
Streams
Lua Scripting
Connections, Memory & Performance
Replication, Sentinel & Cluster
```

**Project scope:** Practical implementation was completed for the applicable CLI and Django exercises. Streams and Lua scripting were practised using the CLI, while Replication, Sentinel, and Cluster were studied theoretically rather than deployed as a multi-node environment.

---

# 🎯 Project Objectives

The main objective is to understand how Redis features solve real backend and distributed-system problems.

### Primary Objectives

- Understand Redis Pub/Sub messaging.
- Learn transactions and atomic execution using `MULTI`, `EXEC`, `DISCARD`, and `WATCH`.
- Understand Redis persistence using RDB snapshots and AOF.
- Identify and diagnose Hot Keys and Big Keys.
- Understand asynchronous key deletion using `UNLINK`.
- Improve backend communication efficiency using Redis pipelining.
- Understand Redis Streams and consumer groups.
- Learn server-side scripting with Lua.
- Understand Redis connections, memory usage, eviction policies, and performance metrics.
- Learn the concepts behind replication, Sentinel, and Redis Cluster.
- Integrate applicable Redis operations with Django.
- Test backend APIs using Postman.
- Verify Redis behavior directly through the CLI.
- Understand the limitations and appropriate use cases of each feature.

---

# 🏗️ Architecture

The project uses Redis or Redis-compatible Memurai as the Redis server and Django as the backend application layer for the implemented API features.

```text
                  ┌──────────────────────┐
                  │    Client / Postman   │
                  └──────────┬───────────┘
                             │
                             │ HTTP Request
                             ▼
                  ┌──────────────────────┐
                  │        Django        │
                  │     API / Views      │
                  └──────────┬───────────┘
                             │
                             │ Redis Operations
                             ▼
                  ┌──────────────────────┐
                  │     Redis Client     │
                  │       redis-py       │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │    Redis / Memurai   │
                  └──────────┬───────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
       Messaging          Operations        Optimization
          │                  │                  │
          ▼                  ▼                  ▼
       Pub/Sub          Transactions       Pipelining
       Streams          Persistence        Hot/Big Keys
       Lua Scripting    Memory & Stats
```

### Core Principle

> Django handles application requests, while Redis provides specialized in-memory operations for messaging, atomicity, persistence, performance, and other backend requirements.

Not every topic requires a Django API. Some Redis features are best understood through direct CLI commands and server behavior.

---

# 🚀 Advanced Redis Topics

| Topic | Main Purpose | Practice Status |
|---|---|---|
| Pub/Sub | Real-time message broadcasting | CLI + Django/Postman |
| Transactions & Atomicity | Group Redis commands and control execution | CLI + Django/Postman |
| Persistence | Understand RDB snapshots and AOF logging | CLI/configuration |
| Hot Keys & Big Keys | Diagnose uneven access and oversized data | CLI diagnostics |
| Pipelining | Reduce request-response round trips | Django + Postman |
| Streams | Persistent event streams and consumer groups | CLI |
| Lua Scripting | Execute server-side scripts atomically | CLI |
| Connections, Memory & Performance | Diagnose resource usage and performance | Theory + CLI |
| Replication, Sentinel & Cluster | Understand availability and distributed Redis | Theory |

---

# 📢 1. Redis Pub/Sub

Redis Pub/Sub is a messaging mechanism in which publishers send messages to channels and subscribers receive messages from the channels they subscribe to.

### Problem It Solves

Without a messaging mechanism, application components may need to call each other directly to communicate updates. This can increase coupling between components.

Pub/Sub allows publishers and subscribers to communicate through Redis channels without needing direct references to each other.

### End-to-End Flow

```text
Publisher
   │
   │ PUBLISH channel message
   ▼
Redis Channel
   │
   │ Broadcast to current subscribers
   ▼
Subscriber A       Subscriber B
```

### Commands Practiced

```text
SUBSCRIBE
PSUBSCRIBE
PUBLISH
UNSUBSCRIBE
PUNSUBSCRIBE
PUBSUB CHANNELS
PUBSUB NUMSUB
```

### Important Limitation

Pub/Sub is not a durable message queue. Messages published while a subscriber is disconnected are not stored for later delivery.

For applications that require retained events and consumer-group processing, Redis Streams may be a better fit.

### Django Integration

Pub/Sub was integrated with Django and tested using Postman.

The API request triggers a Redis publishing operation, while subscribers receive messages through their subscriptions.

**Detailed documentation:** [02-pub-sub.md](docs/02-pub-sub.md)

---

# 🔒 2. Redis Transactions & Atomicity

Redis transactions allow commands to be queued and executed together using `MULTI` and `EXEC`.

### Problem It Solves

When several Redis operations belong to one logical action, unrelated commands should not execute between the queued transaction commands.

Transactions help group those commands into a single execution sequence.

### End-to-End Flow

```text
Application Request
        ↓
      MULTI
        ↓
 Queue Redis Commands
        ↓
       EXEC
        ↓
 Execute Queued Commands
        ↓
 Return Results
```

### Commands Practiced

```text
MULTI
EXEC
DISCARD
WATCH
UNWATCH
```

### Important Learning

Redis transaction atomicity does not mean that every command is guaranteed to succeed. Runtime errors can occur during execution, and Redis transactions do not provide automatic rollback of earlier successful commands.

`WATCH` enables optimistic concurrency control: if a watched key changes before `EXEC`, the transaction is aborted.

### Django Integration

Transaction-related operations were practised through Redis CLI and Django/Postman exercises.

**Detailed documentation:** [03-transactions-atomicity.md](docs/03-transactions-atomicity.md)

---

# 💾 3. Redis Persistence: RDB & AOF

Redis is an in-memory data store, but persistence mechanisms can save data to disk so it can be recovered after certain restarts or failures.

### Problem It Solves

Without persistence, data held only in memory can be lost when the Redis process stops.

Redis supports different persistence approaches, each with different performance and recovery characteristics.

### RDB vs AOF

| Feature | RDB | AOF |
|---|---|---|
| Meaning | Redis Database snapshot | Append Only File |
| Main approach | Saves point-in-time snapshots | Records write operations |
| File format | Snapshot file | Operation log |
| Typical benefit | Compact snapshots and backups | Can provide finer-grained recovery |
| Main trade-off | Changes after the latest snapshot may be lost | File size and replay overhead can be higher |

### End-to-End Flow

```text
Application Writes
        ↓
   Redis Memory
        │
        ├───────────────┐
        ▼               ▼
    RDB Snapshot     AOF Log
        │               │
        └───────┬───────┘
                ▼
        Recovery on Startup
        (According to Configuration)
```

### Commands Practiced

```text
INFO persistence
BGSAVE
LASTSAVE
CONFIG GET appendonly
BGREWRITEAOF
```

Additional file and configuration inspection was performed to understand the persistence setup.

### Practical Verification

The AOF-enabled state was verified using `INFO persistence`, including the AOF write status. An RDB snapshot was also verified, and `BGREWRITEAOF` completed successfully.

**Scope note:** These checks verified the configured persistence operations. A complete restart-and-recovery test was not performed.

**Detailed documentation:** [04-persistence.md](docs/04-persistence.md)

---

# 🔥 4. Hot Keys & Big Keys

Hot Keys and Big Keys are two different Redis operational problems.

### Hot Keys

A Hot Key is a key accessed disproportionately often compared with other keys.

**Problem:** Excessive requests to one key can create a bottleneck and increase load on the Redis server or a particular shard.

### Big Keys

A Big Key is a key whose stored value or collection is large enough to create operational concerns.

**Problem:** Large reads, writes, deletions, or collection operations can consume substantial memory, increase latency, and block other work depending on the operation.

### Hot Key vs Big Key

| Hot Key | Big Key |
|---|---|
| High access frequency | Large stored value or collection |
| Main concern is concentrated traffic | Main concern is size and operation cost |
| Can exist with a small value | Can exist with low access frequency |
| May cause load imbalance | May cause memory and latency problems |

### Diagnostic Commands Practiced

```text
INFO stats
INFO commandstats
MONITOR
SLOWLOG GET 10
MEMORY USAGE key
STRLEN key
LLEN key
SCARD key
ZCARD key
```

Big-key inspection was also practised using:

```powershell
memurai-cli --bigkeys
```

The configured memory eviction policy was inspected using:

```text
CONFIG GET maxmemory-policy
```

### Understanding `UNLINK`

`UNLINK` removes a key from the keyspace immediately while allowing the actual memory reclamation for a large value to happen asynchronously.

```text
DEL key
   ↓
Deletion work may include freeing the value synchronously

UNLINK key
   ↓
Remove key from keyspace
   ↓
Free eligible memory in background
```

`UNLINK` can help avoid expensive synchronous freeing for large values, but it does not make every deletion cost-free.

### Important Learning

A command may be available in Redis but unsupported or configured differently in a Redis-compatible server. For example, the `OBJECT FREQ` experiment returned an error because the required LFU tracking configuration was not enabled in the environment.

**Detailed documentation:** [05-hot-keys-big-keys.md](docs/05-hot-keys-big-keys.md)

---

# ⚡ 5. Redis Pipelining

Redis pipelining allows an application to send multiple Redis commands without waiting for an individual response after every command.

### Problem It Solves

With individual commands, each operation may require a separate client-server round trip.

For many operations, network round-trip latency can become a significant part of the total execution time.

### Without Pipelining

```text
Application
    │
    ├── Command 1 ──► Redis
    │                 ◄── Response 1
    │
    ├── Command 2 ──► Redis
    │                 ◄── Response 2
    │
    └── Command 3 ──► Redis
                      ◄── Response 3
```

### With Pipelining

```text
Application
    │
    ├── Command 1 ──┐
    ├── Command 2 ──┼──► Redis
    └── Command 3 ──┘
                       │
                       ▼
                Execute Commands
                       │
                       ▼
                Return Responses
```

### Django Implementation

Pipelining was implemented through Django endpoints and tested using Postman.

The implementation includes:

- `pipeline_demo` — demonstrates pipelined Redis operations.
- `pipeline_benchmark` — compares individual writes with pipelined writes.
- `pipeline_batch` — writes 1,000 keys in batches of 200.

### API Endpoints

```text
POST /api/pipelining/demo/
POST /api/pipelining/benchmark/
POST /api/pipelining/batch/
```

### Important Learning

Pipelining reduces round trips, but it does not automatically make every command faster. Results depend on network latency, command cost, batch size, and server load.

Pipelining alone also does not guarantee transactional atomicity. A transactional pipeline is a separate option.

**Detailed documentation:** [06-pipelining.md](docs/06-pipelining.md)

---

# 🌊 6. Redis Streams

Redis Streams provide an append-oriented data structure for storing and reading sequences of events.

Unlike Pub/Sub, Streams retain entries until they are deleted or trimmed according to the application's retention policy.

### Problem It Solves

A transient messaging mechanism is not sufficient when a consumer needs to read retained events, track processing progress, or recover work after interruptions.

Streams provide event storage and consumer-group mechanisms for these use cases.

### End-to-End Flow

```text
Producer
   │
   │ XADD
   ▼
Redis Stream
   │
   │ XREAD / XREADGROUP
   ▼
Consumer
   │
   │ Process Event
   ▼
      XACK
   │
   ▼
Acknowledge Processed Message
```

### Commands Practiced

```text
XADD
XRANGE
XREVRANGE
XREAD
XREAD BLOCK
XLEN
XGROUP CREATE
XREADGROUP
XPENDING
XACK
XAUTOCLAIM
XINFO
XDEL
XTRIM
MKSTREAM
```

### Consumer Groups

Consumer groups allow multiple consumers to share stream processing. Messages delivered to a consumer group can be tracked through pending entries until acknowledged.

`XACK` acknowledges processing. It does not delete the message from the stream.

### Important Learning

Streams are useful when retained events and consumer processing are required. However, they do not automatically guarantee exactly-once business processing; applications must account for retries and duplicate side effects.

### Practice Status

Streams were practised using Memurai CLI. Django integration was intentionally skipped for this project.

**Detailed documentation:** [07-streams.md](docs/07-streams.md)

---

# 🧠 7. Redis Lua Scripting

Redis Lua scripting allows multiple Redis operations and conditional logic to execute within a script on the Redis server.

### Problem It Solves

If an application performs several Redis operations separately, another client may modify relevant data between those operations.

A Lua script can combine related reads, checks, and writes into one server-side execution.

### Example Use Case: Stock Decrement

```text
Receive Purchase Request
        ↓
Read Available Stock
        ↓
Check Stock Availability
        ↓
If Stock Is Available
        ↓
Decrease Stock
        ↓
Return Success
```

If stock is insufficient, the script can return a failure result without decreasing the stock.

### Commands Practiced

```text
EVAL
EVALSHA
SCRIPT LOAD
SCRIPT EXISTS
SCRIPT FLUSH
SCRIPT KILL
```

The exercises also covered:

```text
redis.call()
redis.pcall()
```

### Important Learning

Redis executes a Lua script atomically relative to other Redis commands, so other commands do not interleave with the running script.

However, atomic execution does not automatically roll back earlier writes if the script encounters a runtime error.

Scripts should be kept reasonably short because a long-running script can block other Redis command processing.

### Practice Status

Lua scripting was practised using the Redis-compatible CLI. Django integration was intentionally skipped.

**Detailed documentation:** [08-lua-scripting.md](docs/08-lua-scripting.md)

---

# 🔌 8. Connections, Memory & Performance

Understanding Redis performance requires more than checking whether the server responds successfully.

Connections, memory consumption, expensive operations, command latency, and request volume can all influence performance.

### Main Problems Studied

- Excessive or poorly managed client connections.
- High memory consumption.
- Large values and expensive collection operations.
- Incorrect or unsuitable eviction policies.
- Slow commands and latency spikes.
- Resource contention and server overload.

### Connection Flow

```text
Django Application
        ↓
Redis Client
        ↓
Connection / Connection Pool
        ↓
Redis Server
        ↓
Command Execution
        ↓
Response
```

Connection pooling can reuse connections rather than repeatedly establishing new ones. Connection limits and timeouts should be configured according to the application's requirements.

### Memory and Performance Concepts

| Concept | Purpose |
|---|---|
| `INFO memory` | Inspect memory metrics |
| `INFO stats` | Inspect server activity and statistics |
| `INFO clients` | Inspect connected clients |
| `INFO commandstats` | Inspect command statistics |
| `SLOWLOG GET` | Inspect slow command records |
| `MEMORY USAGE` | Inspect memory used by a key |
| `maxmemory` | Configure a memory limit |
| Eviction policy | Determine which keys may be evicted when the limit is reached |

### Important Learning

Redis performance is affected by the workload, data structures, memory pressure, network latency, command patterns, and server configuration.

A successful `PING` proves connectivity; it does not prove that the server is operating efficiently under load.

### Practice Status

The concepts and CLI-based diagnostics were covered. A production-grade load test was not performed.

**Detailed documentation:** [09-connections-memory-performance.md](docs/09-connections-memory-performance.md)

---

# 🌐 9. Replication, Sentinel & Redis Cluster

Replication, Sentinel, and Redis Cluster address different operational requirements.

This section focuses on understanding their roles and how they differ.

### Redis Replication

Replication copies data from a primary Redis server to one or more replicas.

```text
             Application Writes
                    │
                    ▼
               Primary
                    │
              Replication
                    │
             ┌──────┴──────┐
             ▼             ▼
          Replica A     Replica B
```

**Purpose:** Provide replicas that can serve eligible read traffic and support certain recovery or failover strategies.

Replication is generally asynchronous, so replicas may temporarily lag behind the primary.

### Redis Sentinel

Sentinel monitors Redis primary and replica instances and can coordinate automatic failover when a primary is considered unavailable.

```text
Sentinel Monitors Redis
          ↓
Primary Becomes Unavailable
          ↓
Failure Detection
          ↓
Eligible Replica Is Promoted
          ↓
Clients Discover New Primary
```

Sentinel provides high availability for a non-clustered Redis deployment. It does not partition the dataset across multiple shards.

### Redis Cluster

Redis Cluster distributes data across hash slots assigned to multiple primary nodes and supports sharding.

```text
             Application
                  │
                  ▼
           Redis Cluster
                  │
          ┌───────┼───────┐
          ▼       ▼       ▼
       Primary  Primary  Primary
          │       │       │
        Data    Data     Data
        Shard   Shard    Shard
```

Cluster can distribute data and provide availability features through replicas, but applications must account for cluster-specific behavior and limitations.

### Comparison

| Feature | Replication | Sentinel | Redis Cluster |
|---|---|---|---|
| Main purpose | Copy data to replicas | Monitor and coordinate failover | Sharding and distributed operation |
| Data sharding | No | No | Yes |
| Failover coordination | Not by itself | Yes | Cluster-managed |
| Multi-node setup | Required | Required | Required |

### Practice Status

These concepts were studied theoretically. A multi-node replication, Sentinel, or Cluster environment was not deployed as part of this project.

Memurai's feature support may differ from Redis, so any future practical setup should use a compatible environment and verify the required features first.

**Detailed documentation:** [10-replication-sentinel-cluster.md](docs/10-replication-sentinel-cluster.md)

---

# 🔄 Complete Learning Flow

The project follows a structured approach to understanding Redis:

```text
1. Understand the Concept
           ↓
2. Identify the Problem It Solves
           ↓
3. Learn the Redis Commands
           ↓
4. Practise Through CLI
           ↓
5. Implement Applicable Backend Operations
           ↓
6. Test Using Postman
           ↓
7. Inspect Redis State and Metrics
           ↓
8. Understand Limitations and Trade-offs
           ↓
9. Document the End-to-End Flow
```

This method connects Redis commands with actual backend behavior instead of treating each command as an isolated topic.

---

# 🧪 Testing and Verification

Different verification methods were used depending on the feature.

### 1. Redis CLI / Memurai CLI

Used to execute commands directly, inspect stored data, inspect configuration, and understand Redis responses.

### 2. Django

Used to implement applicable Redis operations through backend API endpoints.

### 3. Postman

Used to send HTTP requests to the implemented Django endpoints and inspect responses.

### 4. Server Diagnostics

Commands such as `INFO`, `SLOWLOG`, `MEMORY USAGE`, and `MONITOR` were used for relevant diagnostics.

### 5. Persistence Verification

RDB and AOF operations were checked through configuration and persistence metrics. A complete restart-and-recovery test remains outside the completed verification.

---

# 📁 Project Structure

The documentation directory is organized into ten topic-focused files.

```text
redis-advanced-project/
│
├── README.md
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
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── redis_client.py
│
├── apps/
│   └── pipelining/
│       ├── redis_client.py
│       └── views.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── manage.py
```

> **Note:** The tree above is a conceptual overview of the project's known components. Confirm the actual Django app names and folders in your local repository before publishing; do not create folders just to match this example.

---

# 🛠️ Technology Stack

### Backend

- Python
- Django
- `redis-py`

### Redis Environment

- Redis concepts and commands
- Memurai for Redis-compatible local development on Windows

### API Testing

- Postman

### Development Tools

- VS Code
- Git
- GitHub

---

# ⚙️ Setup and Run

## 1. Clone the Repository

Replace the placeholder with your actual GitHub repository URL.

```powershell
git clone <your-repository-url>
cd redis-advanced-project
```

## 2. Create a Virtual Environment

```powershell
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, follow the appropriate Windows Python environment guidance for your system rather than disabling security controls unnecessarily.

## 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

## 4. Configure Environment Variables

Create a local `.env` file using the project's actual settings and `.env.example` as a reference.

The Redis configuration used in the learning environment is:

```env
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
```

These are example local Redis settings. If your settings module reads other variables, configure those as well.

**Never commit your `.env` file, passwords, API keys, or secret keys to GitHub.**

## 5. Start Memurai

Ensure the Memurai service is running.

Check the connection:

```powershell
memurai-cli ping
```

Expected output:

```text
PONG
```

## 6. Run Database Migrations

```powershell
python manage.py migrate
```

## 7. Check the Django Project

```powershell
python manage.py check
```

## 8. Start Django

```powershell
python manage.py runserver
```

The local development server is available at:

```text
http://127.0.0.1:8000/
```

> Run only the endpoints that are actually registered in your project. Check your Django URL configuration for the current routes.

---

# 📚 Documentation

The project documentation is divided into ten focused topics.

| Document | Description |
|---|---|
| [01 — Advanced Overview](docs/01-redis-advanced-overview.md) | Project scope, objectives, and learning path |
| [02 — Pub/Sub](docs/02-pub-sub.md) | Publishers, subscribers, channels, and message flow |
| [03 — Transactions & Atomicity](docs/03-transactions-atomicity.md) | `MULTI`, `EXEC`, `WATCH`, and transaction behavior |
| [04 — Persistence](docs/04-persistence.md) | RDB snapshots, AOF, and persistence verification |
| [05 — Hot Keys & Big Keys](docs/05-hot-keys-big-keys.md) | Key diagnosis, memory usage, and deletion strategies |
| [06 — Pipelining](docs/06-pipelining.md) | Round-trip reduction, batching, and Django endpoints |
| [07 — Streams](docs/07-streams.md) | Event streams, consumer groups, pending entries, and acknowledgements |
| [08 — Lua Scripting](docs/08-lua-scripting.md) | Server-side scripts and conditional operations |
| [09 — Connections, Memory & Performance](docs/09-connections-memory-performance.md) | Connections, metrics, memory, and performance diagnostics |
| [10 — Replication, Sentinel & Cluster](docs/10-replication-sentinel-cluster.md) | Replication, failover, high availability, and sharding concepts |

### Recommended Reading Order

```text
01. Advanced Overview
          ↓
02. Pub/Sub
          ↓
03. Transactions & Atomicity
          ↓
04. Persistence
          ↓
05. Hot Keys & Big Keys
          ↓
06. Pipelining
          ↓
07. Streams
          ↓
08. Lua Scripting
          ↓
09. Connections, Memory & Performance
          ↓
10. Replication, Sentinel & Cluster
```

---

# 🎓 Learning Outcomes

### Messaging and Event Processing

- Understand publisher-subscriber communication.
- Distinguish transient Pub/Sub messages from retained Stream entries.
- Understand consumer groups, pending messages, and acknowledgements.

### Atomic Operations

- Understand Redis transactions and command queuing.
- Understand `WATCH` and optimistic concurrency.
- Recognize the difference between atomic execution and rollback.

### Persistence and Reliability

- Understand RDB and AOF.
- Inspect persistence configuration and status.
- Understand the difference between persistence, replication, and high availability.

### Performance Optimization

- Diagnose potential Hot Keys and Big Keys.
- Understand the purpose of `UNLINK`.
- Reduce client-server round trips with pipelining.
- Inspect command statistics, slow logs, connections, and memory metrics.

### Advanced Redis Operations

- Understand server-side Lua scripting.
- Understand Redis connection management and memory policies.
- Explain the roles of replication, Sentinel, and Cluster.

### Backend Integration

- Integrate applicable Redis operations with Django.
- Test API endpoints using Postman.
- Trace the flow from HTTP request to Django, Redis, and response.
- Verify Redis behavior using CLI commands and server metrics.

---

# 📊 Project Status

```text
Redis Advanced Project
│
├── Pub/Sub
│   └── ✅ CLI + Django/Postman
│
├── Transactions & Atomicity
│   └── ✅ CLI + Django/Postman
│
├── Persistence: RDB & AOF
│   └── ✅ CLI / Configuration Verification
│
├── Hot Keys & Big Keys
│   └── ✅ CLI Diagnostics
│
├── Pipelining
│   └── ✅ Django + Postman
│
├── Streams
│   └── ✅ CLI Practice
│
├── Lua Scripting
│   └── ✅ CLI Practice
│
├── Connections, Memory & Performance
│   └── ✅ Theory + CLI Diagnostics
│
└── Replication, Sentinel & Cluster
    └── 📘 Theory Completed
```

**Verification boundary:** This status reflects the learning and exercises completed during the project. It does not claim production deployment, a full persistence recovery test, production load testing, or a multi-node Redis environment.

---

# 🧠 Final Mental Model

Each Redis feature solves a different category of backend problem.

```text
                    REDIS
                      │
      ┌───────────────┼────────────────┐
      │               │                │
      ▼               ▼                ▼
  Messaging       Atomicity         Persistence
      │               │                │
      ▼               ▼                ▼
   Pub/Sub       Transactions       RDB / AOF

      ┌───────────────┼────────────────┐
      │               │                │
      ▼               ▼                ▼
 Performance      Processing       Availability
      │               │                │
      ▼               ▼                ▼
 Pipelining        Streams        Replication
 Hot/Big Keys      Lua Scripting   Sentinel/Cluster
 Memory & Stats
```

### Key Takeaway

> The purpose of this project is not just to memorize Redis commands. It is to understand the problem each Redis feature solves, how the operation flows through the server, how applicable features integrate with Django, how to verify behavior, and what trade-offs matter when using Redis in real backend systems.

---

# 🚀 Project Scope and Limitations

This project focuses on learning advanced Redis capabilities through CLI practice, selected Django integrations, and theory.

The following limitations should be considered:

- Pub/Sub does not retain messages for disconnected subscribers.
- Redis transactions do not provide automatic rollback for runtime command errors.
- RDB and AOF have different persistence and recovery trade-offs.
- `UNLINK` allows eligible memory reclamation to occur asynchronously; it does not eliminate the cost of deleting large values.
- Pipelining reduces round trips but does not automatically guarantee atomicity or improve every workload.
- Streams require appropriate retention, acknowledgement, retry, and duplicate-processing strategies.
- Long-running Lua scripts can block Redis command processing.
- Performance diagnostics in this project are learning exercises, not a production load benchmark.
- Replication, Sentinel, and Cluster were studied theoretically rather than deployed as a multi-node system.

These distinctions are important when moving from local learning exercises to production backend development.

---

# ⭐ Final Summary

This advanced project builds on basic Redis commands and data structures by exploring:

- Messaging with Pub/Sub.
- Atomic command execution with transactions.
- Persistence using RDB and AOF.
- Diagnosis of Hot Keys and Big Keys.
- Efficient command execution through pipelining.
- Event processing with Streams.
- Server-side operations with Lua.
- Connection, memory, and performance diagnostics.
- Distributed Redis concepts including replication, Sentinel, and Cluster.

The central goal is to develop a practical understanding of **how Redis behaves, why its advanced features exist, when to use them, and what limitations must be considered in backend applications**.
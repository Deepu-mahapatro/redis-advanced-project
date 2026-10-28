# Redis Transactions & Atomicity

## 1. Overview

Redis Transactions allow multiple commands to be queued and executed together. They help coordinate related operations so other clients do not execute commands in the middle of the transaction's execution.

Redis provides transaction commands such as `MULTI`, `EXEC`, `DISCARD`, and `WATCH`.

**Example use case:** Updating product inventory while checking whether sufficient stock is available.

## 2. Why Do We Need Redis Transactions?

Suppose an application needs to update multiple Redis keys as part of one logical operation.

Without appropriate coordination, another client could execute commands between those operations and observe or cause an inconsistent intermediate state.

Transactions help group commands so they execute together without other clients' commands interleaving during their execution.

### Problems they help solve

- Grouping related Redis operations.
- Preventing other clients' commands from interleaving within transaction execution.
- Supporting optimistic concurrency control using `WATCH`.
- Coordinating conditional updates to shared data.

## 3. Important Commands

| Command | Purpose |
|---|---|
| `MULTI` | Starts a transaction and queues subsequent commands |
| `EXEC` | Executes the queued commands |
| `DISCARD` | Discards queued commands before execution |
| `WATCH key` | Watches keys for modifications before transaction execution |
| `UNWATCH` | Removes watched keys |
| `WATCH key1 key2` | Watches multiple keys for modifications |

## 4. How Redis Transactions Work

The execution flow is:

1. The client sends `MULTI`.
2. Redis queues subsequent commands instead of executing them immediately.
3. The client sends `EXEC`.
4. Redis executes the queued commands sequentially.
5. The client receives the individual command results.

```text id="8f6x9c"
Client
  |
  | MULTI
  v
Redis queues commands
  |
  | SET inventory:1 20
  | GET inventory:1
  |
  | EXEC
  v
Redis executes queued commands
  |
  v
Command results returned
```

During execution, commands from other clients cannot interleave between the queued transaction commands.

## 5. Redis CLI Practical

### Step 1 — Start Memurai

```powershell id="y56d6n"
memurai-cli PING
```

Expected output:

```text id="b7e1r2"
PONG
```

### Step 2 — Execute a transaction

```redis id="4ndqfi"
MULTI
SET inventory:1 20
GET inventory:1
EXEC
```

Redis queues the `SET` and `GET` commands and executes them when `EXEC` is issued.

### Step 3 — Discard a transaction

```redis id="3ekg7g"
MULTI
SET demo:transaction "test"
DISCARD
```

`DISCARD` cancels the queued commands before they are executed.

### Step 4 — Understand optimistic concurrency with WATCH

`WATCH` enables optimistic concurrency control. If a watched key changes before `EXEC`, the transaction is aborted.

For this exercise, use two separate Redis CLI sessions.

**Session A:**

```redis id="3rw6zn"
SET account:balance 100
WATCH account:balance
GET account:balance
MULTI
DECRBY account:balance 10
```

**Session B:**

```redis id="5g48ny"
SET account:balance 200
```

**Back in Session A:**

```redis id="4k53am"
EXEC
```

Because the watched key was modified by Session B, the transaction aborts instead of applying the queued decrement.

Use demonstration keys for concurrency exercises, not production data.

## 6. Important Atomicity Limitations

Redis transactions are atomic in command execution, but they do not provide full relational-database transaction semantics.

- Commands queued by `MULTI` execute sequentially when `EXEC` runs.
- If a command has a runtime error during execution, other queued commands are still attempted.
- Redis does not automatically roll back previously executed commands when a later command fails.
- `WATCH` detects changes to watched keys and allows the client to retry an aborted transaction.

**Important distinction:** Atomic execution does not mean every command must succeed or that Redis automatically rolls back all changes.

## 7. Django Integration

The project includes a Django transactions application for practising Redis transaction behavior.

A Redis client helper can be used to connect Django to the configured Redis server:

```python id="6z3czb"
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

### Transaction using a pipeline

The Python Redis client uses a transactional pipeline by default:

```python id="m99k33"
r = get_redis_client()

try:
    with r.pipeline(transaction=True) as pipe:
        pipe.set("inventory:1", 20)
        pipe.get("inventory:1")
        results = pipe.execute()

    print(results)
finally:
    r.close()
```

The `execute()` call sends the queued commands for execution as a Redis transaction.

### Transaction using WATCH

A watched transaction can implement a conditional update:

```python id="cxm1tz"
r = get_redis_client()

try:
    with r.pipeline() as pipe:
        while True:
            try:
                pipe.watch("inventory:1")

                stock = int(pipe.get("inventory:1") or 0)

                if stock <= 0:
                    pipe.unwatch()
                    break

                pipe.multi()
                pipe.decr("inventory:1")
                pipe.execute()
                break

            except redis.WatchError:
                continue
finally:
    r.close()
```

This example checks stock before queuing the decrement. If another client changes the watched key before execution, `WatchError` is raised and the operation is retried.

In production, add a bounded retry strategy and appropriate error handling to avoid retrying indefinitely under heavy contention.

**Implementation note:** The code above illustrates the transaction patterns. Keep your existing `apps/transactions/` views and URLs as the source of truth for the actual endpoints implemented in this repository.

## 8. Testing with Postman

The transaction endpoints can be tested using the routes registered in the project's Django URL configuration.

1. Start Memurai.
2. Activate the project's virtual environment.
3. Run the Django server.
4. Open Postman and use the actual transaction endpoint URL.
5. Send the request using the configured method and body.
6. Inspect the JSON response.
7. Verify the corresponding Redis keys using `memurai-cli`.

Test normal updates and concurrent updates separately to understand the difference between a successful transaction and a transaction aborted by `WATCH`.

## 9. When Should You Use Redis Transactions?

Use transactions when multiple Redis commands must execute together without interleaving from other clients.

Use `WATCH` when the operation depends on a value that may change between reading and writing.

For a simple counter increment, use `INCR` or `INCRBY` directly when possible. These commands are already atomic and do not require a transaction.

## 10. Key Takeaways

1. **`MULTI` and `EXEC`** group and execute queued Redis commands together.
2. **`WATCH`** enables optimistic concurrency control by aborting a transaction when a watched key changes.
3. **Redis transactions do not provide automatic rollback** for runtime command errors, so application logic must handle errors and retries carefully.


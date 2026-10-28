# Redis Lua Scripting

## 1. Overview

Redis Lua Scripting allows developers to execute Lua code directly inside the Redis server.

A Lua script can perform multiple Redis operations, apply conditions, and return a result to the client. The script executes atomically relative to other Redis commands, meaning other commands do not interleave with its execution.

In this project, Lua scripting was practised using Memurai CLI. Django integration was intentionally skipped.

## 2. Why Do We Need Lua Scripting?

Suppose an application needs to check whether a product has sufficient stock and then decrement its inventory.

If the application performs a separate read and write, another client might change the stock between those operations.

Lua scripting allows the check and update to run together on the Redis server.

### Problems it helps solve

- Coordinates related Redis operations in one server-side execution.
- Supports conditional updates.
- Reduces client-server round trips.
- Helps avoid race conditions between separate Redis commands.
- Allows reusable scripts to be loaded and executed by their SHA identifier.

### Common use cases

- Inventory and stock checks
- Rate limiting
- Conditional counters
- Atomic updates involving multiple Redis keys
- Server-side validation and state transitions

## 3. How Lua Scripting Works

The execution flow is:

1. The client sends a Lua script to Redis.
2. Redis executes the script.
3. The script performs Redis operations and evaluates its conditions.
4. Redis returns the script's result to the client.

```text
Client
  |
  | Sends Lua script
  v
Redis Server
  |
  | Executes conditions and Redis commands
  |
  | Updates relevant keys
  v
Returns result to client
```

While the script is executing, other Redis commands do not interleave with it.

**Important:** Atomic execution does not mean automatic rollback. If a script performs a write and later encounters a runtime error, earlier writes are not automatically undone.

## 4. Important Lua Scripting Commands

| Command | Purpose |
|---|---|
| `EVAL` | Executes a Lua script supplied by the client |
| `EVALSHA` | Executes a previously loaded script using its SHA identifier |
| `SCRIPT LOAD` | Loads a script into the server's script cache |
| `SCRIPT EXISTS` | Checks whether script SHA identifiers exist in the cache |
| `SCRIPT FLUSH` | Clears the script cache |
| `SCRIPT KILL` | Attempts to stop a running script when Redis permits it |
| `redis.call()` | Executes a Redis command and raises an error if the command fails |
| `redis.pcall()` | Executes a Redis command and returns an error value instead of raising that command error |

## 5. Practical Work Completed

The following exercises were completed through Memurai CLI:

- Set and retrieved demonstration stock values using Lua.
- Wrote a conditional stock-decrement script.
- Verified the stock value after script execution.
- Loaded a Lua script using `SCRIPT LOAD`.
- Executed cached scripts using `EVALSHA`.
- Checked cached scripts using `SCRIPT EXISTS`.
- Explored `redis.call()` and `redis.pcall()` error behavior.
- Practised `SCRIPT FLUSH`.
- Reviewed the purpose and limitations of `SCRIPT KILL`.

**Implementation status:** CLI practice completed; Django integration was intentionally skipped.

## 6. Redis CLI Practical

### Step 1 — Verify the server

In PowerShell:

```powershell
memurai-cli PING
```

Expected output:

```text
PONG
```

### Step 2 — Execute a simple script

```redis
EVAL "return redis.call('SET', KEYS[1], ARGV[1])" 1 lua:stock:demo 10
```

This script stores the supplied value under the key provided in `KEYS[1]`.

### Step 3 — Verify the value

```redis
GET lua:stock:demo
```

Expected value:

```text
10
```

## 7. Conditional Stock Decrement

A common inventory requirement is to decrement stock only when stock is available.

The following script performs the check and decrement atomically:

```lua
local stock = tonumber(redis.call('GET', KEYS[1]) or '0')

if stock > 0 then
    return redis.call('DECR', KEYS[1])
else
    return -1
end
```

Run it using:

```redis
EVAL "local stock = tonumber(redis.call('GET', KEYS[1]) or '0'); if stock > 0 then return redis.call('DECR', KEYS[1]); else return -1; end" 1 lua:stock:demo
```

### Execution flow

1. The script reads the stock value.
2. The value is converted to a number.
3. If stock is greater than zero, Redis decrements it.
4. Otherwise, the script returns `-1` to indicate that stock is unavailable.

The script is atomic relative to other Redis commands. It prevents another command from interleaving between the stock check and decrement.

In a production application, use a clear result convention and validate the stored value. Also distinguish insufficient stock from invalid or missing inventory data if those cases require different handling.

## 8. Script Caching with SCRIPT LOAD and EVALSHA

When a script is used repeatedly, the client can load it into Redis's script cache and execute it by SHA identifier.

### Load a script

```redis
SCRIPT LOAD "return redis.call('GET', KEYS[1])"
```

Redis returns a SHA identifier for the script.

### Execute the cached script

```redis
EVALSHA <script-sha> 1 lua:stock:demo
```

Replace `<script-sha>` with the actual SHA returned by `SCRIPT LOAD`.

### Check whether the script exists

```redis
SCRIPT EXISTS <script-sha>
```

The result indicates whether the script is present in the cache.

### Important consideration

The script cache can be cleared, and scripts may need to be loaded again after cache loss or a server restart. Clients should be prepared to handle a `NOSCRIPT` response and reload the script when necessary.

## 9. Error Handling with redis.call() and redis.pcall()

### redis.call()

`redis.call()` runs a Redis command and propagates command errors to the script.

```lua
return redis.call('GET', KEYS[1])
```

### redis.pcall()

`redis.pcall()` returns an error result from the command instead of raising that command error directly.

```lua
local result = redis.pcall('INCR', KEYS[1])

if type(result) == 'table' and result.err then
    return 'Redis command failed'
end

return result
```

This allows a script to handle certain Redis command errors explicitly.

**Important:** `redis.pcall()` does not automatically roll back changes already performed by the script.

## 10. Script Cache Management

### Clear the script cache

```redis
SCRIPT FLUSH
```

This removes cached Lua scripts. It does not delete Redis keys or clear application data.

### Stop a running script

```redis
SCRIPT KILL
```

This can stop a running script only under permitted conditions. Redis generally cannot kill a script that has already performed writes because doing so could leave partially applied changes.

Long-running scripts should be avoided. Keep scripts short and predictable because they block other Redis command execution while running.

## 11. Important Considerations

- Lua scripts execute atomically relative to other Redis commands, but they do not provide rollback after runtime errors.
- Keep scripts short to avoid blocking the server for too long.
- Pass dynamic values through `KEYS` and `ARGV` rather than building scripts through unsafe string concatenation.
- Use consistent key naming and validate input values.
- Handle missing scripts when using `EVALSHA`.
- Ensure the Redis-compatible server supports the commands and scripting behavior being used.

## 12. Key Takeaways

1. **Lua scripting combines logic and Redis operations:** Conditions and updates can execute together on the server.
2. **Scripts support atomic operations:** Other commands do not interleave during script execution.
3. **Atomic does not mean rollback:** Runtime errors do not automatically undo earlier writes, so scripts must be carefully designed and tested.


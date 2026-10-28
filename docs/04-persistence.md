# Redis Persistence — RDB & AOF

## 1. Overview

Redis stores data primarily in memory for fast access. Persistence allows Redis to save data to disk so it can recover data after a server restart, depending on its configuration and the files successfully written.

Redis provides two main persistence mechanisms:

- **RDB (Redis Database):** Saves point-in-time snapshots of the dataset.
- **AOF (Append Only File):** Records write operations so they can be replayed during recovery.

This project explored persistence using Memurai on Windows and Redis CLI commands.

## 2. Why Do We Need Persistence?

Without persistence, data held only in memory may be lost when the Redis process stops.

Persistence helps Redis recover data after restarts and certain failures.

### Problems it helps solve

- Recovering data after a server restart.
- Reducing dependence on in-memory state alone.
- Saving snapshots for recovery.
- Recording write operations for replay.

Persistence does not replace a complete backup strategy. Important data should also have appropriate backups, recovery procedures, and validation.

## 3. RDB vs AOF

| Feature | RDB | AOF |
|---|---|---|
| Full name | Redis Database | Append Only File |
| Storage approach | Point-in-time snapshots | Records write operations |
| Typical output | `dump.rdb` | AOF file or AOF files |
| Recovery | Loads a saved snapshot | Replays recorded operations |
| Main advantage | Compact snapshots and efficient backups | Can provide a smaller recovery window with suitable settings |
| Trade-off | Changes since the last snapshot may be lost | Can require more disk space and replay time |
| Common use | Snapshots and backup workflows | Greater write-history durability, depending on policy |

Redis versions and configurations differ in their default persistence settings and file layouts. Check the actual server configuration rather than assuming a specific filename or location.

## 4. How RDB Persistence Works

RDB saves a snapshot of the dataset at a particular point in time.

The flow is:

1. Redis receives data-changing commands.
2. A snapshot is requested or triggered by configured save rules.
3. Redis writes a snapshot file to disk.
4. After a failure or restart, Redis can load a valid snapshot.
5. Data written after the snapshot may be missing.

### RDB commands

| Command | Purpose |
|---|---|
| `SAVE` | Creates a snapshot synchronously and can block the server while it runs |
| `BGSAVE` | Requests a background snapshot |
| `LASTSAVE` | Returns the timestamp of the last successful RDB save |
| `INFO persistence` | Displays persistence-related status and metrics |
| `CONFIG GET dir` | Displays the configured working directory |
| `CONFIG GET dbfilename` | Displays the configured RDB filename |

For normal server operation, `BGSAVE` is generally preferable to `SAVE` because `SAVE` blocks the server during the save operation.

## 5. How AOF Persistence Works

AOF records Redis write operations so they can be replayed to rebuild the dataset.

The flow is:

1. A client sends a write command.
2. Redis executes the command.
3. Redis records the operation in the AOF according to the configured policy.
4. The AOF is written to disk according to the durability settings.
5. During recovery, Redis replays the recorded operations.

### AOF commands and settings

| Command | Purpose |
|---|---|
| `CONFIG GET appendonly` | Checks whether AOF is enabled |
| `CONFIG SET appendonly yes` | Enables AOF at runtime when supported |
| `CONFIG GET appendfsync` | Displays the AOF synchronization policy |
| `CONFIG SET appendfsync everysec` | Sets the common once-per-second synchronization policy, if supported |
| `BGREWRITEAOF` | Requests background AOF rewriting |
| `INFO persistence` | Displays AOF status and related metrics |

AOF rewriting compacts the file by generating a more efficient representation of the current dataset. It is different from simply deleting old log lines.

## 6. Practical Work Completed

The following persistence exercises were completed during this project:

- Enabled AOF using `CONFIG SET appendonly yes`.
- Verified persistence status using `INFO persistence`.
- Confirmed that `aof_enabled` reported `1`.
- Checked that `aof_last_write_status` reported `ok`.
- Requested AOF rewriting using `BGREWRITEAOF`.
- Practised RDB-related operations and verified the presence of an RDB snapshot file.

These results confirmed that the relevant persistence operations succeeded at the time they were tested.

**Important:** The project did not complete a dedicated server-restart and data-recovery test. Therefore, the documentation explains recovery behavior but does not claim that a full restart/recovery test was performed.

## 7. Redis CLI Practical

### Step 1 — Verify the Redis-compatible server

In PowerShell:

```powershell
memurai-cli PING
```

Expected output:

```text
PONG
```

### Step 2 — Inspect persistence status

```redis
INFO persistence
```

Review the returned persistence metrics and AOF/RDB status fields.

### Step 3 — Check whether AOF is enabled

```redis
CONFIG GET appendonly
```

### Step 4 — Check the AOF synchronization policy

```redis
CONFIG GET appendfsync
```

### Step 5 — Check the configured RDB directory and filename

```redis
CONFIG GET dir
CONFIG GET dbfilename
```

Use the returned values to identify the configured location and filename rather than assuming the snapshot is always in the project directory.

### Step 6 — Inspect the last RDB save time

```redis
LASTSAVE
```

### Step 7 — Request a background RDB snapshot

```redis
BGSAVE
```

Check `INFO persistence` afterwards to inspect the save status.

### Step 8 — Request AOF rewriting

```redis
BGREWRITEAOF
```

Check the returned response and persistence status to determine whether the rewrite was accepted and completed.

**Safety note:** Persistence settings can affect disk usage and durability. Do not change production persistence configuration or restart a server without understanding its data and recovery requirements.

## 8. Important AOF Synchronization Policies

The `appendfsync` setting determines how frequently Redis asks the operating system to synchronize AOF changes to disk.

| Policy | Meaning | Trade-off |
|---|---|---|
| `always` | Requests synchronization after each write operation | Stronger durability intent but potentially higher latency |
| `everysec` | Requests synchronization approximately once per second | Common balance between performance and durability |
| `no` | Leaves synchronization timing to the operating system | Potentially better performance, with less control over durability |

Even when a policy is configured, actual durability depends on the operating system, storage hardware, and failure type.

## 9. Persistence vs Replication vs Backup

These concepts are related but serve different purposes.

| Concept | Main purpose |
|---|---|
| Persistence | Saves data to disk for recovery |
| Replication | Copies data to another Redis server |
| Backup | Maintains recoverable copies for disaster recovery or historical restoration |

Replication is not a substitute for backup. Accidental deletion or unwanted updates can be copied to replicas.

Similarly, a persistence file should not be considered a complete backup strategy without appropriate copying, retention, integrity checks, and recovery testing.

## 10. Key Takeaways

1. **RDB saves snapshots:** It is useful for point-in-time recovery and backup workflows.
2. **AOF records write operations:** It can reduce the recovery window, depending on the synchronization policy.
3. **Persistence requires verification:** Check configuration, save status, file locations, and recovery behavior instead of assuming data is safely recoverable.


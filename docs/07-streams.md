# Redis Streams & Consumer Groups

## 1. Overview

Redis Streams is a Redis data structure designed to store and process sequences of events. Each entry has a unique ID and can contain multiple field-value pairs.

Streams support reading events, consumer groups, tracking pending messages, acknowledgements, and message recovery.

In this project, Redis Streams was practised using Memurai CLI. Django integration was intentionally skipped.

**Example use case:** An e-commerce application records order-created events in a stream so background workers can process them.

## 2. Why Do We Need Redis Streams?

Traditional Redis Pub/Sub delivers messages to currently connected subscribers. It does not retain messages for disconnected subscribers.

Streams address this limitation by storing events in a stream that consumers can read later.

### Problems Streams help solve

- Retaining events for later consumption.
- Allowing consumers to read events from a particular position.
- Distributing work among consumers in a consumer group.
- Tracking messages delivered but not yet acknowledged.
- Recovering pending messages when a consumer fails.

### Common use cases

- Order processing
- Background event processing
- Activity logs
- Notifications that need retention
- Event-driven backend workflows

Streams provide useful delivery and recovery mechanisms, but applications must still handle duplicate processing and business-level failures appropriately.

## 3. Important Components

| Component | Definition |
|---|---|
| Stream | An ordered collection of event entries |
| Entry ID | A unique identifier assigned to a stream entry |
| Producer | Adds events to a stream |
| Consumer | Reads and processes stream entries |
| Consumer group | Coordinates message processing across multiple consumers |
| Pending Entries List (PEL) | Tracks delivered messages that have not yet been acknowledged |
| Acknowledgement | Marks a processed message as acknowledged |
| Claiming | Transfers ownership of eligible pending messages to another consumer |

## 4. Redis Streams vs Pub/Sub

| Feature | Pub/Sub | Streams |
|---|---|---|
| Message retention | No | Yes, until entries are deleted or trimmed |
| Offline consumer recovery | Missed messages are not replayed automatically | Consumers can read retained entries later |
| Consumer groups | No | Yes |
| Pending message tracking | No | Yes |
| Acknowledgements | No | Yes, with consumer groups |
| Typical use | Live notifications | Retained events and work processing |

**Key distinction:** Pub/Sub focuses on real-time delivery; Streams support retained event processing and consumer recovery.

## 5. Important Redis Streams Commands

| Command | Purpose |
|---|---|
| `XADD` | Adds an entry to a stream |
| `XRANGE` | Reads entries in ascending ID order |
| `XREVRANGE` | Reads entries in descending ID order |
| `XREAD` | Reads entries from one or more streams |
| `XLEN` | Returns the number of entries in a stream |
| `XGROUP CREATE` | Creates a consumer group |
| `XREADGROUP` | Reads messages through a consumer group |
| `XPENDING` | Inspects messages pending acknowledgement |
| `XACK` | Acknowledges processed messages |
| `XAUTOCLAIM` | Claims eligible pending messages for another consumer |
| `XINFO STREAM` | Displays stream information |
| `XINFO GROUPS` | Displays consumer-group information |
| `XINFO CONSUMERS` | Displays consumer information |
| `XDEL` | Deletes specified stream entries |
| `XTRIM` | Trims a stream to reduce retained entries |

## 6. Practical Work Completed

The following commands and concepts were practised through Memurai CLI:

- Created stream entries using `XADD`.
- Read entries with `XRANGE`, `XREVRANGE`, and `XREAD`.
- Used blocking reads with `XREAD BLOCK`.
- Checked entry counts using `XLEN`.
- Created consumer groups using `XGROUP CREATE`.
- Read entries with `XREADGROUP`.
- Inspected pending messages with `XPENDING`.
- Acknowledged messages using `XACK`.
- Claimed pending messages using `XAUTOCLAIM`.
- Inspected streams, groups, and consumers with `XINFO`.
- Deleted entries with `XDEL`.
- Trimmed stream entries with `XTRIM`.
- Explored stream creation with the `MKSTREAM` option.

The practical work used the demonstration stream `orders:stream:demo`. The stream was later trimmed, and a separate stream/group setup was also explored.

**Implementation status:** CLI practice completed; Django integration was intentionally skipped.

## 7. Redis CLI Practical

### Step 1 — Verify the server

In PowerShell:

```powershell
memurai-cli PING
```

Expected response:

```text
PONG
```

### Step 2 — Add an event

```redis
XADD orders:stream:demo * order_id 101 status created
```

The `*` tells Redis to generate an entry ID.

### Step 3 — Read stream entries

```redis
XRANGE orders:stream:demo - +
```

`-` and `+` represent the lowest and highest stream IDs for the range query.

### Step 4 — Read the newest entries first

```redis
XREVRANGE orders:stream:demo + -
```

### Step 5 — Count entries

```redis
XLEN orders:stream:demo
```

### Step 6 — Read new entries

```redis
XREAD COUNT 5 STREAMS orders:stream:demo 0
```

The starting ID determines which entries are returned. Using `0` requests entries after the beginning of the stream, whereas `$` can be used to wait for entries newer than the current end when starting a blocking or new-event read.

## 8. Consumer Groups

A consumer group allows multiple consumers to share responsibility for processing stream entries.

### Why use consumer groups?

Without consumer groups, each independent reader must manage its own progress. Consumer groups track delivery and pending messages so work can be distributed and recovered.

### Create a consumer group

```redis
XGROUP CREATE orders:stream:demo order-processors 0-0
```

This creates a group named `order-processors`, starting from the beginning of the stream. The stream must already exist unless `MKSTREAM` is supplied.

If the group already exists, Redis returns an error indicating that the group exists.

### Create a group and stream if necessary

```redis
XGROUP CREATE orders:stream:setup order-processors 0-0 MKSTREAM
```

This creates the stream if it does not exist and then creates the consumer group.

### Read through a consumer group

```redis
XREADGROUP GROUP order-processors worker-1 COUNT 5 STREAMS orders:stream:demo >
```

The `>` ID requests entries that have not previously been delivered to another consumer in that group.

## 9. Pending Messages and Acknowledgements

When a consumer group delivers a message to a consumer, Redis tracks it in the group's Pending Entries List (PEL) until it is acknowledged.

### Inspect pending messages

```redis
XPENDING orders:stream:demo order-processors
```

This helps identify messages that were delivered but have not yet been acknowledged.

### Acknowledge a processed message

```redis
XACK orders:stream:demo order-processors 1730000000000-0
```

Replace the sample ID with an actual stream entry ID returned by Redis.

Acknowledgement removes the entry from the group's pending list. It does not delete the stream entry itself.

### Claim an eligible pending message

```redis
XAUTOCLAIM orders:stream:demo order-processors worker-2 60000 0-0 COUNT 10
```

This attempts to claim pending messages idle for at least 60,000 milliseconds and transfer their ownership to `worker-2`.

Claiming can help recover work from failed or inactive consumers. Choose the idle threshold carefully to avoid claiming messages that are still being processed.

## 10. Inspecting and Managing Streams

### Inspect stream information

```redis
XINFO STREAM orders:stream:demo
```

### Inspect consumer groups

```redis
XINFO GROUPS orders:stream:demo
```

### Inspect consumers

```redis
XINFO CONSUMERS orders:stream:demo order-processors
```

### Delete an entry

```redis
XDEL orders:stream:demo 1730000000000-0
```

Replace the sample ID with a real entry ID.

### Trim a stream

```redis
XTRIM orders:stream:demo MAXLEN 1000
```

This trims the stream to approximately 1,000 entries using the specified maximum length.

In the project exercises, `XTRIM orders:stream:demo MAXLEN 1` was also used to reduce the demonstration stream to one retained entry.

**Important:** Trimming and deletion permanently remove retained entries from the stream. They should be used with care when consumers may still need to process older events.

## 11. Important Considerations

- A stream entry can remain in the stream after it has been acknowledged.
- Acknowledgement is not the same as deleting an entry.
- Pending messages can indicate failed processing, slow consumers, or messages awaiting acknowledgement.
- Claiming a pending message does not guarantee that the original consumer will never process it. Applications should be designed to tolerate duplicate processing.
- Stream retention must be designed according to storage requirements and consumer recovery needs.
- Command availability and behavior can vary by Redis-compatible server version.

## 12. Key Takeaways

1. **Streams retain events:** Entries remain available until they are deleted or trimmed.
2. **Consumer groups coordinate processing:** Pending entries and acknowledgements help track work and support recovery.
3. **Recovery requires application logic:** Claiming and redelivery mechanisms help, but consumers should still handle failures and duplicate processing safely.


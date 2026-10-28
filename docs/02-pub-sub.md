# Redis Pub/Sub

## 1. Overview

Redis Pub/Sub (Publish/Subscribe) is a messaging mechanism that allows one application to publish messages to a channel while other applications subscribe to that channel and receive messages.

Publishers and subscribers do not need to communicate directly. Redis acts as the message broker between them.

**Example:** In an e-commerce application, a Django service can publish a product-update notification, and subscribed services can receive it in real time.

## 2. Why Do We Need Pub/Sub?

Without a messaging mechanism, applications may need to communicate directly with one another. This creates dependencies between services and makes real-time notifications harder to organize.

Redis Pub/Sub provides a simple way to distribute messages to multiple subscribers without requiring the publisher to know who those subscribers are.

### Problems it solves

- Enables real-time message delivery to connected subscribers.
- Allows one message to reach multiple subscribers.
- Reduces direct dependencies between publishers and subscribers.
- Supports lightweight notifications between application components.

### Common use cases

- Live notifications
- Application status updates
- Real-time dashboards
- Cache invalidation notifications
- Lightweight service-to-service messaging

Pub/Sub is not a durable message queue. If a subscriber is disconnected when a message is published, that subscriber will miss the message.

## 3. Important Components

| Component | Definition |
|---|---|
| Publisher | Sends a message to a Redis channel |
| Subscriber | Listens to a channel and receives published messages |
| Channel | A named destination used to distribute messages |
| Redis server | Receives published messages and forwards them to current subscribers |
| Message | The data published to a channel |

## 4. End-to-End Execution Flow

The message flow is:

1. A subscriber connects to Redis.
2. The subscriber subscribes to a channel.
3. A publisher sends a message to that channel.
4. Redis forwards the message to currently subscribed clients.
5. Subscribers receive and process the message.

```text
Publisher
    |
    | PUBLISH notifications "New product added"
    v
Redis Server
    |
    |----> Subscriber A
    |
    |----> Subscriber B
    |
    |----> Subscriber C
```

The publisher does not need to know which clients are subscribed. Redis handles message distribution.

## 5. Redis Pub/Sub Commands

| Command | Purpose |
|---|---|
| `SUBSCRIBE channel` | Subscribes to one or more channels |
| `PSUBSCRIBE pattern` | Subscribes to channels matching a pattern |
| `PUBLISH channel message` | Publishes a message to a channel |
| `UNSUBSCRIBE channel` | Unsubscribes from specified channels |
| `PUNSUBSCRIBE pattern` | Unsubscribes from matching channel patterns |
| `PUBSUB CHANNELS` | Lists active channels with subscribers |
| `PUBSUB NUMSUB channel` | Shows the number of subscribers to specified channels |
| `PUBSUB NUMPAT` | Shows the number of active pattern subscriptions |

## 6. Practical Redis CLI Commands

### Step 1 — Verify Redis is running

On Windows with Memurai:

```powershell
memurai-cli PING
```

Expected output:

```text
PONG
```

### Step 2 — Subscribe to a channel

Open one terminal and run:

```powershell
memurai-cli
```

Then execute:

```redis
SUBSCRIBE notifications
```

This terminal now listens for messages published to the `notifications` channel.

### Step 3 — Publish a message

Open a second terminal and execute:

```powershell
memurai-cli PUBLISH notifications "New product added"
```

The command returns the number of clients that received the message.

The subscriber terminal displays a message containing the channel name and published content.

### Step 4 — Check subscribers

```redis
PUBSUB NUMSUB notifications
```

This returns the number of clients directly subscribed to the channel.

### Step 5 — Unsubscribe

In the subscriber terminal:

```redis
UNSUBSCRIBE notifications
```

The subscriber stops receiving messages from that channel.

## 7. Django Integration

The project includes a Django Pub/Sub application for practising Redis messaging through backend endpoints.

### Redis client configuration

Redis connection settings are maintained in `config/settings.py`:

```python
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 0
```

A reusable client helper can connect Django to Redis:

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

### How Django Pub/Sub works

1. A Django endpoint receives a request to publish a message.
2. Django connects to Redis using the configured client.
3. Django publishes a message to a named channel.
4. Redis forwards the message to connected subscribers.
5. A subscriber listening to that channel receives the message.

**Implementation note:** This section documents the integration approach used in the project. Refer to the existing `apps/pubsub/` views and URL configuration for the exact endpoint paths and request parameters rather than assuming specific routes.

## 8. Testing with Postman

For endpoints registered in `apps/pubsub/`:

1. Start Memurai.
2. Activate the project's virtual environment.
3. Run the Django development server.
4. Open Postman and select the HTTP method configured for the endpoint.
5. Enter the actual URL registered in `config/urls.py` and the Pub/Sub application's URL configuration.
6. Send the request and inspect the response.
7. Verify message delivery using a Redis CLI subscriber in another terminal.

A successful publish request does not necessarily mean a subscriber received the message. The number of clients receiving a message depends on which subscribers were connected at publish time.

## 9. Limitations and Important Considerations

### Messages are not stored

Redis Pub/Sub does not retain messages for subscribers that are offline. Once a message is published, it is delivered to currently subscribed clients and is not kept as a durable event for later consumption.

### No built-in acknowledgements

Pub/Sub does not provide the pending-message and acknowledgement workflow available in Redis Streams consumer groups.

### Delivery is not guaranteed to every application

A subscriber can disconnect or fail while processing a message. Pub/Sub does not automatically replay missed messages.

### When should you use Pub/Sub?

Use Pub/Sub when low-latency notifications are important and missing a message during a disconnection is acceptable.

If your application needs message retention, consumer groups, acknowledgement tracking, or recovery of unprocessed messages, consider Redis Streams instead.

## 10. Key Takeaways

1. **Pub/Sub means publish and subscribe:** Publishers send messages to channels, and subscribers receive them in real time.
2. **Redis distributes messages:** Publishers and subscribers do not need direct knowledge of one another.
3. **Pub/Sub is not durable:** Disconnected subscribers miss messages; use Redis Streams when message retention and acknowledgement are required.


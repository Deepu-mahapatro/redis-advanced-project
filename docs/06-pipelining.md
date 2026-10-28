# Redis Pipelining

## 1. Overview

Redis Pipelining is a technique that allows a client to send multiple Redis commands without waiting for each command's response individually.

Normally, a client sends a command, waits for the response, and then sends the next command. Pipelining reduces these repeated network round trips by sending several commands together.

This project implemented Redis Pipelining using Django and the Python Redis client, with Postman testing and a simple performance benchmark.

## 2. Why Do We Need Pipelining?

Consider a Django application that needs to save 100 product records in Redis.

Without pipelining, the application may send 100 separate commands and wait for each response. Each network round trip adds overhead.

With pipelining, the client sends multiple commands together and receives their responses after execution.

### Problems it helps solve

- Reduces repeated network round trips.
- Improves throughput for batches of Redis operations.
- Makes bulk writes and reads more efficient.
- Reduces client-server communication overhead.

## 3. How Pipelining Works

### Without pipelining

```text id="d4q8wt"
Django Client
     |
     | SET product:1 Phone
     | <---- Response
     |
     | SET product:2 Laptop
     | <---- Response
     |
     | SET product:3 Tablet
     | <---- Response
```

### With pipelining

```text id="q7w4ce"
Django Client
     |
     | SET product:1 Phone
     | SET product:2 Laptop
     | SET product:3 Tablet
     |
     v
Redis Server
     |
     | Executes queued commands
     |
     v
Returns command responses together
```

Pipelining reduces network round trips, but Redis still executes the commands individually.

**Important:** Pipelining is not the same as a transaction. A pipeline can use transactional or non-transactional behavior depending on how it is configured.

## 4. Important Redis Pipelining Concepts

| Concept | Meaning |
|---|---|
| Pipeline | Groups commands for transmission and response collection |
| Round trip | Communication from client to server and back |
| Batch processing | Executes a group of operations together |
| `transaction=False` | Creates a non-transactional pipeline in the Python Redis client |
| `transaction=True` | Uses transactional behavior for the queued commands |
| `execute()` | Sends queued commands and returns their results |

## 5. Redis CLI Practical

Redis CLI can send multiple commands through a single connection using its interactive session or input mechanisms, but the primary pipelining implementation in this project uses the Python Redis client.

A simple individual command is:

```redis id="7w1k9q"
SET pipeline:product:1 Phone
```

Read the value:

```redis id="5b2m8z"
GET pipeline:product:1
```

Expected output:

```text id="1m6v3n"
Phone
```

For the project implementation, batching is handled through the Python Redis client's `pipeline()` and `execute()` methods.

## 6. Django Redis Client

The pipelining application uses a reusable Redis client helper.

**File:** `apps/pipelining/redis_client.py`

```python id="z2y7cx"
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

This helper centralizes Redis connection configuration and returns decoded responses.

## 7. Django Pipeline Demonstration

**File:** `apps/pipelining/views.py`

The demonstration endpoint queues two writes and two reads in a non-transactional pipeline.

```python id="f7c4we"
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .redis_client import get_redis_client


@csrf_exempt
@require_POST
def pipeline_demo(request):
    r = get_redis_client()

    try:
        pipe = r.pipeline(transaction=False)

        pipe.set("pipeline:product:1", "Phone")
        pipe.set("pipeline:product:2", "Laptop")
        pipe.get("pipeline:product:1")
        pipe.get("pipeline:product:2")

        results = pipe.execute()

        return JsonResponse({
            "message": "Redis pipeline executed successfully",
            "commands_executed": 4,
            "results": results,
        })

    except Exception as exc:
        return JsonResponse({
            "error": "Redis pipeline execution failed",
            "details": str(exc),
        }, status=500)

    finally:
        r.close()
```

### Execution flow

1. Django receives a POST request.
2. The view creates a Redis client.
3. A non-transactional pipeline is created.
4. Two `SET` commands and two `GET` commands are queued.
5. `execute()` sends the queued commands to Redis.
6. Redis returns the results.
7. Django returns the results as JSON.

The `@csrf_exempt` decorator was used for local learning and testing. For production applications, choose an appropriate authentication and CSRF strategy rather than copying this setting blindly.

## 8. URL Configuration

**File:** `apps/pipelining/urls.py`

```python id="b5v8da"
from django.urls import path
from .views import pipeline_demo, pipeline_benchmark, pipeline_batch

urlpatterns = [
    path("demo/", pipeline_demo, name="pipeline-demo"),
    path("benchmark/", pipeline_benchmark, name="pipeline-benchmark"),
    path("batch/", pipeline_batch, name="pipeline-batch"),
]
```

The application is registered in the main URL configuration:

**File:** `config/urls.py`

```python id="x9e2km"
path("api/pipelining/", include("apps.pipelining.urls")),
```

Keep the other existing URL routes when adding this route to your project.

## 9. Batch Processing

The batch endpoint writes 1,000 keys in batches of 200 using non-transactional pipelines.

### Why use batches?

Sending an extremely large number of commands in one pipeline can consume substantial client memory and create a large response buffer. Dividing the work into batches helps control resource usage.

### Batch execution flow

1. Generate the 1,000 product keys.
2. Divide them into groups of 200.
3. Create a pipeline for each group.
4. Queue the `SET` commands.
5. Execute the pipeline.
6. Continue until all batches are processed.

The implementation uses five batches of 200 writes, for a total of 1,000 writes.

**Endpoint:** `POST /api/pipelining/batch/`

## 10. Benchmarking Pipelining

The benchmark endpoint compares 100 individual `SET` calls against 100 pipelined writes.

### Individual writes

Each write is sent and its response is awaited before the next write.

### Pipelined writes

The client queues the writes and executes them together.

### Metrics measured

| Metric | Purpose |
|---|---|
| Individual-write duration | Measures time for sequential writes |
| Pipeline duration | Measures the time taken to execute the pipeline |
| Speedup ratio | Compares the measured durations |

The benchmark uses Python's `time.perf_counter()` to measure elapsed time.

**Important:** Results depend on server load, network latency, client environment, and measurement overhead. A benchmark from one run does not establish a universal speedup.

## 11. Testing with Postman

Start Memurai and the Django development server before testing.

### Demo endpoint

```text id="k5m3zy"
POST http://127.0.0.1:8000/api/pipelining/demo/
```

Expected response structure:

```json id="x7n2cq"
{
  "message": "Redis pipeline executed successfully",
  "commands_executed": 4,
  "results": [
    true,
    true,
    "Phone",
    "Laptop"
  ]
}
```

The two `true` values indicate successful `SET` operations, followed by the values returned by the `GET` commands.

### Benchmark endpoint

```text id="h3v6qa"
POST http://127.0.0.1:8000/api/pipelining/benchmark/
```

Inspect the returned timing measurements and speedup ratio.

### Batch endpoint

```text id="u9k4bd"
POST http://127.0.0.1:8000/api/pipelining/batch/
```

Inspect the response for the number of keys and batches processed.

The exact JSON fields depend on the current implementation of the benchmark and batch views.

## 12. Important Considerations

- Pipelining reduces network overhead; it does not eliminate the cost of executing commands.
- Non-transactional pipelines do not provide transaction atomicity.
- Transactional pipelines group commands using Redis transaction semantics, but do not provide automatic rollback for runtime errors.
- Very large pipelines can increase memory usage and response buffering.
- Batch size should be selected according to workload, latency, and resource constraints.
- Use error handling and monitoring when pipelines process important application data.

## 13. Key Takeaways

1. **Pipelining reduces network round trips** by sending multiple commands without waiting for each individual response.
2. **Batch processing controls workload size** by splitting a large operation into manageable groups.
3. **Pipelining and transactions are different:** use non-transactional pipelines for efficient batching and transactions when grouped execution semantics are required.


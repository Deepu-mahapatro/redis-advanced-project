
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import time
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
        return JsonResponse(
            {
                "error": "Redis pipeline execution failed",
                "details": str(exc),
            },
            status=500,
        )
    finally:
        r.close()

@csrf_exempt
@require_POST
def pipeline_benchmark(request):
    r = get_redis_client()

    try:
        number_of_commands = 100

        # Method A: Execute SET commands individually
        start_time = time.perf_counter()

        for i in range(number_of_commands):
            r.set(f"benchmark:individual:{i}", f"value-{i}")

        individual_time = time.perf_counter() - start_time

        # Method B: Execute the same number of SET commands using a pipeline
        pipe = r.pipeline(transaction=False)

        for i in range(number_of_commands):
            pipe.set(f"benchmark:pipeline:{i}", f"value-{i}")

        start_time = time.perf_counter()
        pipe.execute()
        pipeline_time = time.perf_counter() - start_time

        individual_ms = round(individual_time * 1000, 3)
        pipeline_ms = round(pipeline_time * 1000, 3)

        speedup = (
            round(individual_time / pipeline_time, 2)
            if pipeline_time > 0
            else None
        )

        return JsonResponse({
            "message": "Redis performance comparison completed",
            "commands_per_method": number_of_commands,
            "individual_calls": {
                "duration_ms": individual_ms,
            },
            "pipelining": {
                "duration_ms": pipeline_ms,
            },
            "speedup_ratio": speedup,
        })

    except Exception as exc:
        return JsonResponse(
            {
                "error": "Redis benchmark failed",
                "details": str(exc),
            },
            status=500,
        )
    finally:
        r.close()
        

@csrf_exempt
@require_POST
def pipeline_batch(request):
    r = get_redis_client()

    try:
        total_records = 1000
        batch_size = 200

        records_written = 0
        batches_executed = 0

        for start in range(0, total_records, batch_size):
            end = min(start + batch_size, total_records)

            pipe = r.pipeline(transaction=False)

            for i in range(start, end):
                pipe.set(
                    f"pipeline:batch:product:{i}",
                    f"Product-{i}",
                )

            results = pipe.execute()

            records_written += sum(result is True for result in results)
            batches_executed += 1

        return JsonResponse({
            "message": "Redis batch processing completed",
            "total_records": total_records,
            "batch_size": batch_size,
            "batches_executed": batches_executed,
            "records_written": records_written,
        })

    except Exception as exc:
        return JsonResponse(
            {
                "error": "Redis batch processing failed",
                "details": str(exc),
            },
            status=500,
        )
    finally:
        r.close()

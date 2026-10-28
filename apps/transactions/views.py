
import json

import redis
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .redis_client import get_redis_client


ACCOUNT_A = "account:A"
ACCOUNT_B = "account:B"
MAX_RETRIES = 3


def parse_json_body(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, JsonResponse(
            {"error": "Request body must contain valid JSON"},
            status=400,
        )

    if not isinstance(data, dict):
        return None, JsonResponse(
            {"error": "JSON body must be an object"},
            status=400,
        )

    return data, None


@csrf_exempt
@require_POST
def initialize_accounts(request):
    """Initialize demo account balances."""
    client = get_redis_client()

    try:
        # One Redis transaction sets both initial balances.
        with client.pipeline(transaction=True) as pipe:
            pipe.set(ACCOUNT_A, 500)
            pipe.set(ACCOUNT_B, 200)
            pipe.execute()

        return JsonResponse({
            "status": "initialized",
            "account_A": 500,
            "account_B": 200,
        })
    except redis.RedisError:
        return JsonResponse(
            {"error": "Redis operation failed"},
            status=503,
        )
    finally:
        client.close()


@require_GET
def account_balances(request):
    """Return the current balances."""
    client = get_redis_client()

    try:
        account_a, account_b = client.mget(ACCOUNT_A, ACCOUNT_B)

        if account_a is None or account_b is None:
            return JsonResponse(
                {"error": "Accounts are not initialized"},
                status=404,
            )

        return JsonResponse({
            "account_A": int(account_a),
            "account_B": int(account_b),
        })
    except redis.RedisError:
        return JsonResponse(
            {"error": "Redis operation failed"},
            status=503,
        )
    finally:
        client.close()


@csrf_exempt
@require_POST
def transfer_points(request):
    """Transfer points using WATCH and MULTI/EXEC."""
    data, error_response = parse_json_body(request)

    if error_response:
        return error_response

    amount = data.get("amount")

    if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
        return JsonResponse(
            {"error": "amount must be a positive integer"},
            status=400,
        )

    client = get_redis_client()

    try:
        for attempt in range(MAX_RETRIES):
            try:
                with client.pipeline(transaction=True) as pipe:
                    # Monitor both accounts for concurrent changes.
                    pipe.watch(ACCOUNT_A, ACCOUNT_B)

                    # Read current balances while in WATCH mode.
                    account_a = pipe.get(ACCOUNT_A)
                    account_b = pipe.get(ACCOUNT_B)

                    if account_a is None or account_b is None:
                        return JsonResponse(
                            {"error": "Accounts are not initialized"},
                            status=404,
                        )

                    balance_a = int(account_a)
                    balance_b = int(account_b)

                    if balance_a < amount:
                        return JsonResponse(
                            {
                                "error": "Insufficient balance",
                                "account_A": balance_a,
                            },
                            status=400,
                        )

                    # Begin queueing transaction commands.
                    pipe.multi()
                    pipe.decrby(ACCOUNT_A, amount)
                    pipe.incrby(ACCOUNT_B, amount)

                    # Executes only if neither watched key changed.
                    results = pipe.execute()

                    return JsonResponse({
                        "status": "success",
                        "transferred": amount,
                        "account_A": results[0],
                        "account_B": results[1],
                        "attempts": attempt + 1,
                    })

            except redis.WatchError:
                # Another client changed a watched key.
                # The transaction was aborted; retry from fresh data.
                continue

        return JsonResponse(
            {
                "error": "Concurrent updates detected. Please retry.",
                "attempts": MAX_RETRIES,
            },
            status=409,
        )

    except redis.RedisError:
        return JsonResponse(
            {"error": "Redis operation failed"},
            status=503,
        )
    finally:
        client.close()

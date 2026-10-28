import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .redis_client import get_redis_client


@csrf_exempt
@require_POST
def publish_message(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"error": "Invalid JSON body"},
            status=400,
        )

    message = data.get("message")

    if not isinstance(message, str) or not message.strip():
        return JsonResponse(
            {"error": "message must be a non-empty string"},
            status=400,
        )

    redis_client = get_redis_client()

    subscriber_count = redis_client.publish(
        "notifications",
        message,
    )

    return JsonResponse({
        "status": "published",
        "channel": "notifications",
        "message": message,
        "subscribers_reached": subscriber_count,
    })
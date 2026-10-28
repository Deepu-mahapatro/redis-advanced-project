
import os
import django

# Tell Django which settings module to load
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Initialize Django before accessing settings
django.setup()

from .redis_client import get_redis_client


def run_subscriber():
    redis_client = get_redis_client()
    pubsub = redis_client.pubsub()

    try:
        pubsub.subscribe("notifications")

        print("Subscribed to notifications. Waiting for messages...")

        for message in pubsub.listen():
            if message["type"] == "message":
                print(
                    f"Received on {message['channel']}: "
                    f"{message['data']}"
                )

    except KeyboardInterrupt:
        print("\nSubscriber stopped.")

    finally:
        pubsub.close()
        redis_client.close()


if __name__ == "__main__":
    run_subscriber()

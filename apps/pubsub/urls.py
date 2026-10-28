from django.urls import path

from .views import publish_message

urlpatterns = [
    path("publish/", publish_message, name="publish-message"),
]
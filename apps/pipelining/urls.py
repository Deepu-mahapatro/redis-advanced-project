
from django.urls import path

from .views import (
    pipeline_demo,
    pipeline_benchmark,
    pipeline_batch,
)

urlpatterns = [
    path("demo/", pipeline_demo, name="pipeline-demo"),
    path("benchmark/", pipeline_benchmark, name="pipeline-benchmark"),
    path("batch/", pipeline_batch, name="pipeline-batch"),
]

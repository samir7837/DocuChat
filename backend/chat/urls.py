from django.urls import path
from .views import UploadPDFView, ChatView, HealthCheckView

urlpatterns = [
    path("health/", HealthCheckView.as_view()),
    path("upload/", UploadPDFView.as_view()),
    path("chat/", ChatView.as_view()),
]

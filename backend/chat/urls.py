from django.urls import path
from .views import HealthCheckView, UploadPDFView, ChatView

urlpatterns = [
    path("health/", HealthCheckView.as_view()),
    path("upload/", UploadPDFView.as_view()),
    path("chat/", ChatView.as_view()),
]

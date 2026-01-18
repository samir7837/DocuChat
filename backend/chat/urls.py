from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.HealthCheckView.as_view(), name='health_check'),
    path('upload/', views.UploadPDFView.as_view(), name='upload_pdf'),
    path("chat/", views.ChatView.as_view()),
]

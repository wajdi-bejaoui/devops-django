from django.urls import path
from .views import GenerateVideoAPIView,FetchVideoStatusAPIView

urlpatterns = [
    path('generate', GenerateVideoAPIView.as_view(), name='generate-video'),
    path('status/<int:video_id>/', FetchVideoStatusAPIView.as_view(), name='fetch_video_status'),

]

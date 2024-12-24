from django.shortcuts import render
import requests
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Video


class GenerateVideoAPIView(APIView):
    def post(self, request):
        prompt = request.data.get('prompt')
        negative_prompt = request.data.get('negative_prompt', '')

        # Create a video record with the status 'processing'
        video = Video.objects.create(
            user=None,  # No user authentication for this test
            prompt=prompt,
            negative_prompt=negative_prompt,
            status='processing'
        )

        # Call the external video generation API
        api_url = "https://modelslab.com/api/v6/video/text2video"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "key": settings.VIDEO_API_KEY,
            "model_id": "zeroscope",
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "height": 320,
            "width": 512,
            "num_frames": 16,
            "num_inference_steps": 20,
            "guidance_scale": 7,
            "output_type": "gif",
            "webhook": None,
            "track_id": video.id
        }

        # Start the video generation
        response = requests.post(api_url, headers=headers, json=payload)

        if response.status_code == 200:
            return Response({
                "message": "Video generation started",
                "video_id": video.id  # Return the video ID for status checking
            }, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({"error": "Failed to connect to video generation service"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class FetchVideoStatusAPIView(APIView):
    def get(self, request, video_id):
        try:
            video = Video.objects.get(id=video_id)
            return Response({"status": video.status}, status=status.HTTP_200_OK)
        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)
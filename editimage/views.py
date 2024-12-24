from django.conf import settings
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from .models import ImageEdit
from .serializers import ImageEditSerializer
import base64


class ImageEditingView(APIView):


    def post(self, request):
        model = request.data.get('model')  # Get the selected model from the request
        # Check if an image file was uploaded
        if 'image_file' in request.FILES:
            image_file = request.FILES['image_file']
            init_image_base64 = self.encode_image_to_base64(image_file)
        else:
            init_image_base64 = request.data.get('init_image')  # Fallback to using a URL
        # Call the corresponding method based on the model
        if model == 'super_resolution':
            return self.super_resolution(request)
        elif model == 'outpainting':
            return self.outpainting(request)
        elif model == 'blip_diffusion':
            return self.blip_diffusion(request)
        elif model == 'avatar_gen':
            return self.avatar_gen(request)
        elif model == 'object_removal':
            return self.object_removal(request)
        else:
            return Response({"error": "Invalid model"}, status=status.HTTP_400_BAD_REQUEST)

    def super_resolution(self, request):
        return self.make_api_request("https://modelslab.com/api/v6/image_editing/super_resolution", request)

    def outpainting(self, request):
        payload = {
            "key": settings.API_KEY_MODELSLAB,
            "seed": 12345,
            "width": 512,
            "height": 512,
            "prompt": request.data.get('prompt'),
            "init_image": request.data.get('init_image'),
            "negative_prompt": request.data.get('negative_prompt'),
            "overlap_width": 64,
            "num_inference_steps": 15,
            "guidance_scale": 8.0,
            "temp": "yes",
            "base64": "no",
            "webhook": None,
            "track_id": None
        }
        return self.make_api_request("https://modelslab.com/api/v6/image_editing/outpaint", request, payload)

    def blip_diffusion(self, request):
        payload = {
            "key": settings.API_KEY_MODELSLAB,
            "seed": 88888,
            "task": "zeroshot",
            "prompt": request.data.get('prompt'),
            "condition_image": request.data.get('condition_image'),
            "condition_subject": request.data.get('condition_subject'),
            "target_subject": request.data.get('target_subject'),
            "guidance_scale": 7.5,
            "steps": 35,
            "height": 512,
            "width": 512,
            "webhook": None,
            "track_id": None
        }
        return self.make_api_request("https://modelslab.com/api/v6/image_editing/blip_diffusion", request, payload)

    def avatar_gen(self, request):
        payload = {
            "key": settings.API_KEY_MODELSLAB,
            "prompt": request.data.get('prompt'),
            "negative_prompt": request.data.get('negative_prompt'),
            "init_image": request.data.get('init_image'),
            "width": 512,
            "height": 512,
            "samples": 1,
            "num_inference_steps": 21,
            "safety_checker": False,
            "base64": False,
            "seed": None,
            "guidance_scale": 7.5,
            "identitynet_strength_ratio": 1.0,
            "adapter_strength_ratio": 1.0,
            "pose_strength": 0.4,
            "canny_strength": 0.3,
            "controlnet_selection": "pose",
            "webhook": None,
            "track_id": None
        }
        return self.make_api_request("https://modelslab.com/api/v6/image_editing/avatar_gen", request, payload)

    def object_removal(self, request):
        payload = {
            "key": settings.API_KEY_MODELSLAB,
            "init_image": request.data.get('init_image'),
            "mask_image": request.data.get('mask_image'),
            "webhook": None,
            "track_id": None
        }
        return self.make_api_request("https://modelslab.com/api/v6/image_editing/object_removal", request, payload)

    def make_api_request(self, url, request, payload=None):
        if payload is None:
            payload = {
                "key": settings.API_KEY_MODELSLAB,
                "init_image": request.data.get('init_image'),
                "base64": False,
                "instant_response": False,
                "webhook": None,
                "track_id": None
            }

        headers = {'Content-Type': 'application/json'}

        # First request to initiate the image processing
        response = requests.post(url, headers=headers, json=payload)

        # Check if the request was successful
        if response.status_code != 200:
            return Response({"error": response.text}, status=response.status_code)

        # Poll for status until success
        track_id = response.json().get("track_id")  # Assuming track_id is returned
        if not track_id:
            return Response({"error": "No tracking ID found in the response."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Polling loop
        while True:
            time.sleep(5)  # Wait for 5 seconds before polling again
            status_response = requests.get(f"https://modelslab.com/api/v6/image_editing/status/{track_id}")

            if status_response.status_code != 200:
                return Response({"error": "Failed to check status."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            status_data = status_response.json()
            processing_status = status_data.get("status")

            if processing_status == "success":
                edited_image_url = status_data.get('edited_image_url')  # Adjust based on actual response structure
                return Response({"edited_image_url": edited_image_url}, status=status.HTTP_200_OK)
            elif processing_status == "pending":
                continue  # Keep polling
            else:
                return Response({"error": "Image processing failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
def save_image_edit(request):
    user = request.user
    edited_image_url = request.data.get('edited_image_url')
    init_image_url = request.data.get('init_image_url')
    model_used = request.data.get('model_used')

    # Validate the required fields
    if not edited_image_url or not init_image_url or not model_used:
        return Response({"error": "Edited image URL, initial image URL, and model used are required."},
                        status=status.HTTP_400_BAD_REQUEST)

    # Save the image edit record
    image_edit = ImageEdit.objects.create(
        user=user,
        model_used=model_used,
        init_image_url=init_image_url,
        edited_image_url=edited_image_url
    )

    # Serialize the saved edit
    serializer = ImageEditSerializer(image_edit)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_user_image_edits(request, user_id):
    user = request.user
    if user.id != user_id and not user.is_staff:
        return Response({"error": "You do not have permission to view these edits."}, status=status.HTTP_403_FORBIDDEN)

    image_edits = ImageEdit.objects.filter(user_id=user_id)
    serializer = ImageEditSerializer(image_edits, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

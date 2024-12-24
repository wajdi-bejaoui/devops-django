# Image/views.py
import os
import json
import jwt
import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import FileResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import login_required
from .models import GeneratedImage
from users.models import User
from .serializers import GeneratedImageSerializer

from io import BytesIO
import base64
import time
from django.core.files import File
from PIL import Image as PILImage


from .serializers import GeneratedImageSerializer

# Your Hugging Face API URL and token
# API_URL = "https://modelslab.com/api/v6/realtime/text2img"
# URL of the image generation API
API_URL = "https://modelslab.com/api/v6/realtime/text2img"
# Maximum number of retries and delay time in seconds
MAX_RETRIES = 6
DELAY_SECONDS = 30


def call_hugging_face_api(prompt, width, height):
    payload = json.dumps({
        "key": settings.API_KEY_MODELSLAB,
        "prompt": prompt,
        "negative_prompt": "bad quality",
        "width": width,
        "height": height,
        "safety_checker": False,
        "seed": None,
        "samples": 1,
        "base64": False,
        "webhook": None,
        "track_id": None
    })

    headers = {
        'Content-Type': 'application/json'
    }

    # Make the API request
    response = requests.post(API_URL, headers=headers, data=payload)

    if response.status_code == 200:
        return response.json()  # Return the JSON response
    return None


def call_hugging_face_api_with_retries(prompt, width, height):
    retry_count = 0

    while retry_count < MAX_RETRIES:
        img_data = call_hugging_face_api(prompt, width, height)

        if img_data:
            rsp_status = img_data.get('status', '')
            image_urls = img_data.get('output', [])

            # If the API response is successful and an image URL is returned
            if rsp_status == 'success' and image_urls:
                return {
                    'status': rsp_status,
                    'image_url': image_urls[0]
                }

            # If the API is still processing, retry after a delay
            elif rsp_status == 'processing':
                print("Image generation is still processing, retrying...")
            else:
                print("Status:", rsp_status)

        # Wait for the specified delay before retrying
        time.sleep(DELAY_SECONDS)
        retry_count += 1

    return None  # Return None if the max retries are exceeded and no image is generated


@api_view(['POST'])
def generate_image(request):
    prompt = request.data.get('prompt')
    width = int(request.data.get('width'))
    height = int(request.data.get('height'))

    if not prompt:
        return Response({"error": "Prompt is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Call the API with retries
    img_data = call_hugging_face_api_with_retries(prompt, width, height)

    if img_data:
        return Response({
            'image_url': img_data['image_url'],
            'status': img_data['status']
        }, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Image generation failed after multiple attempts"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['POST'])
def save_image(request):
    user_id = request.data.get('user_id')
    print("User ID received:", user_id)

    # Find the user by ID
    user = User.objects.filter(id=user_id).first()
    if not user:
        return Response({"error": "User not found!"}, status=status.HTTP_404_NOT_FOUND)

    # Get the image URL and prompt
    image_url = request.data.get('image_url')
    prompt = request.data.get('prompt')

    # Ensure both fields are provided
    if not image_url or not prompt:
        return Response({"error": "Image URL and prompt are required"}, status=status.HTTP_400_BAD_REQUEST)

    # Download the image from the URL
    response = requests.get(image_url)
    if response.status_code != 200:
        return Response({"error": "Failed to download image"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Convert the image to PNG format
    image = PILImage.open(BytesIO(response.content)).convert("RGBA")
    png_image = BytesIO()
    image.save(png_image, format='PNG')
    png_image.seek(0)  # Move to the beginning of the BytesIO object

    # Save the image and its associated data to the database
    generated_image = GeneratedImage(
        user=user,
        prompt=prompt,
    )

    # Save the image to the file field
    generated_image.image.save(f"{user_id}_{int(time.time())}.png", ContentFile(png_image.read()))
    generated_image.save()

    # Serialize and return the saved image data
    serializer = GeneratedImageSerializer(generated_image)

    return Response({
        'message': 'Image saved successfully',
        'image': serializer.data
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def user_images(request):
    # Get the user ID from the request parameters
    user_id = request.GET.get('user_id')
    print("User ID:", user_id)

    # Check if the user ID is provided
    if not user_id:
        return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the user exists
    user = User.objects.filter(id=user_id).first()
    if not user:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    # Filter images by the user and visibility
    images = GeneratedImage.objects.filter(user=user).order_by('-created_at')

    # If no images are found for the user
    if not images.exists():
        return Response({"error": "No visible images found for this user"}, status=status.HTTP_404_NOT_FOUND)

    # Prepare the response data with image URL and other details
    image_data = []
    for image in images:
        image_data.append({
            'id': image.id,
            'prompt': image.prompt,
            'created_at': image.created_at,
            'visibility': image.visibility,
            'image_url': request.build_absolute_uri(image.image.url),  # URL to access the image
        })

    return Response(image_data, status=status.HTTP_200_OK)
@api_view(['PATCH'])
def update_image(request, image_id):
    try:
        # Retrieve the image object by its ID
        image = GeneratedImage.objects.get(id=image_id)
    except GeneratedImage.DoesNotExist:
        return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

    # Extract visibility and likes from the request data
    visibility = request.data.get('visibility')
    likes = request.data.get('likes')

    # Update the visibility if it's provided (as a boolean)
    if visibility is not None:
        if isinstance(visibility, bool):  # Ensure it's a boolean
            image.visibility = visibility
        else:
            return Response({"error": "'visibility' must be a boolean value"}, status=status.HTTP_400_BAD_REQUEST)

    # Update the likes if it's provided (must be an integer)
    if likes is not None:
        if isinstance(likes, int):
            image.likes = likes
        else:
            return Response({"error": "'likes' must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

    # Save the updated image data
    image.save()

    # Serialize the updated image data
    serializer = GeneratedImageSerializer(image)

    return Response({
        'message': 'Image updated successfully',
        'image': serializer.data
    }, status=status.HTTP_200_OK)
@api_view(['GET'])
def visible_images(request):
    # Fetch images with visibility = True
    images = GeneratedImage.objects.filter(visibility=True).order_by('-created_at')
    print("images",images)
    if not images.exists():
        return Response({"error": "No visible images found"}, status=status.HTTP_404_NOT_FOUND)

    # Prepare the response data
    image_data = []
    for image in images:
        image_data.append({
            'id': image.id,
            'prompt': image.prompt,
            'created_at': image.created_at,
            'image_url': request.build_absolute_uri(image.image.url),  # URL to access the image
        })

    return Response(image_data, status=status.HTTP_200_OK)



@api_view(['PATCH'])
def share(request, pk):
    try:
        image = GeneratedImage.objects.get(pk=pk)
        # request.data.get('visibility')
        new_visibility = True

        if new_visibility is not None:
            image.visibility = bool(new_visibility)
            image.save()
            return Response({'status': 'Visibility updated'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid input'}, status=status.HTTP_400_BAD_REQUEST)
    except GeneratedImage.DoesNotExist:
        return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def delete_image(request, pk):
    try:
        image = GeneratedImage.objects.get(pk=pk)
        image.delete()
        return Response(pk, status=status.HTTP_204_NO_CONTENT)
    except GeneratedImage.DoesNotExist:
        return Response('Image not found', status=status.HTTP_404_NOT_FOUND)
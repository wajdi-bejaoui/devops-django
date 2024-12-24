from rest_framework import serializers
from .models import GeneratedImage

class GeneratedImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)  # Optional field if it's being generated but not uploaded
    visibility = serializers.BooleanField(default=False)  # Default value for visibility
    likes = serializers.IntegerField(default=0)  # Default value for likes
    updated_at = serializers.DateTimeField(read_only=True)  # Read-only field as it's automatically set

    class Meta:
        model = GeneratedImage
        fields = ['id', 'user', 'prompt', 'image', 'visibility', 'likes', 'updated_at']
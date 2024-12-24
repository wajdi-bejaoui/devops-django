from rest_framework import serializers
from .models import ImageEdit

class ImageEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageEdit
        fields = ['id', 'user', 'model_used', 'init_image_url', 'edited_image_url', 'created_at']
        read_only_fields = ['id', 'user', 'created_at'] 
# editimage/models.py

from django.db import models
from users.models import User  # Import the custom User model if you're using one

class ImageEdit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the User model
    model_used = models.CharField(max_length=50)  # Type of model used
    init_image_url = models.URLField()  # URL of the original image
    edited_image_url = models.URLField()  # URL of the edited image
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the edit was created

    def __str__(self):
        return f"{self.user.username} - {self.model_used} - {self.created_at}"

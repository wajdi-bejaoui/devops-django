# editimage/urls.py

from django.urls import path
from .views import ImageEditingView

urlpatterns = [
    path('edit/', ImageEditingView.as_view(), name='edit-image'),
    # path('my-edits/', UserImageEditsView.as_view(), name='user-image-edits'),  # New endpoint for user edits
]

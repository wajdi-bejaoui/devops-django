from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static
from .views import share, delete_image

urlpatterns = [
    path('generate', views.generate_image, name='generate_image'),  # Endpoint for image generation
    path('save-image', views.save_image, name='save_image'),
    path('user-images/', views.user_images, name='user_images'),
    path('images-update/<int:image_id>/', views.update_image, name='update_image'),
    path('visible-images/', views.visible_images, name='visible_images'),
    path('share-image/<int:pk>/', share, name='share'),
    path('delete-image/<int:pk>/', delete_image, name='delete-image'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

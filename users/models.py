
from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    name = models.CharField(max_length=120)
    email = models.CharField(max_length=120, unique=True)
    password = models.CharField(max_length=120)
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []



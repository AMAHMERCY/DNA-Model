import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.text import slugify
from django.utils import timezone
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)

    slug = models.SlugField(unique=True, blank=True)
    hospital_id = models.CharField(max_length=20, unique=True)

    role = models.CharField(max_length=20, default="patient")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.slug:
            unique_code = uuid.uuid4().hex[:6]
            self.slug = slugify(f"{self.name}-{unique_code}")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

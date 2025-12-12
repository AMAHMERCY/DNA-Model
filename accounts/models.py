import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.text import slugify
from django.utils import timezone
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)

    
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    rurality = models.CharField(max_length=20, null=True, blank=True)
    sex = models.CharField(max_length=20, null=True, blank=True)
    chronic_condition = models.CharField(max_length=255, null=True, blank=True)
    chronic_other = models.CharField(max_length=255, null=True, blank=True)

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

        
        if not self.hospital_id:
            last_user = User.objects.order_by("-id").first()

            if last_user and last_user.hospital_id:
                try:
                    last_number = int(last_user.hospital_id.split("-")[1])
                except:
                    last_number = 0
            else:
                last_number = 0

            new_number = last_number + 1
            self.hospital_id = f"HSP-{new_number:05d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

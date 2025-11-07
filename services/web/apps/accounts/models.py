from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("trader", "Trader"),
        ("viewer", "Viewer"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="viewer")
    phone = models.CharField(max_length=20, blank=True)
    timezone = models.CharField(max_length=50, default="Asia/Kolkata")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.username

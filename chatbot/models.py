from django.db import models
from django.contrib.auth.models import User
import uuid


# -----------------------------
# Complaint Model
# -----------------------------
class Complaint(models.Model):
    department = models.CharField(max_length=100)
    issue_type = models.CharField(max_length=100)
    description = models.TextField()

    priority = models.CharField(max_length=10)
    status = models.CharField(max_length=50, default="Pending")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.issue_type} - {self.status}"


# -----------------------------
# Digital Identity (Login & Signup)
# -----------------------------
class DigitalIdentity(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    digital_id = models.CharField(max_length=20, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.digital_id:
            self.digital_id = "DIGI-" + uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.digital_id

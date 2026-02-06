from django.db import models
from django.contrib.auth.models import User
import uuid


# =============================
# Complaint Model
# =============================

class Complaint(models.Model):

    STATUS_CHOICES = [
        ("Submitted", "Submitted"),
        ("In Progress", "In Progress"),
        ("Resolved", "Resolved"),
        ("Rejected", "Rejected"),
    ]

    PRIORITY_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]

    complaint_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        db_index=True
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="complaints"
    )

    department = models.CharField(max_length=100)
    issue_type = models.CharField(max_length=100)
    description = models.TextField()

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="Low"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Submitted"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # ---------- AUTO ID SAFE GENERATOR ----------
    def generate_id(self):
        while True:
            cid = "C" + uuid.uuid4().hex[:6].upper()
            if not Complaint.objects.filter(complaint_id=cid).exists():
                return cid

    def save(self, *args, **kwargs):
        if not self.complaint_id:
            self.complaint_id = self.generate_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.complaint_id} — {self.status}"

    class Meta:
        ordering = ["-created_at"]


# =============================
# Digital Identity Model
# =============================

class DigitalIdentity(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="digital_identity"
    )

    digital_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def generate_id(self):
        while True:
            did = "DIGI-" + uuid.uuid4().hex[:8].upper()
            if not DigitalIdentity.objects.filter(digital_id=did).exists():
                return did

    def save(self, *args, **kwargs):
        if not self.digital_id:
            self.digital_id = self.generate_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.digital_id

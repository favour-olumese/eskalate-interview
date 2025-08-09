import uuid
from django.db import models
from django.conf import settings

class Job(models.Model):
    class JobStatus(models.TextChoices):
        DRAFT = 'Draft', 'Draft'
        OPEN = 'Open', 'Open'
        CLOSED = 'Closed', 'Closed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=2000)
    location = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=10, choices=JobStatus.choices, default=JobStatus.DRAFT)
    createdBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='jobs',
        limit_choices_to={'role': 'company'}
    )
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
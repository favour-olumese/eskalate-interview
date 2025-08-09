import uuid
from django.db import models
from django.conf import settings
from apps.jobs.models import Job

class Application(models.Model):
    class ApplicationStatus(models.TextChoices):
        APPLIED = 'Applied', 'Applied'
        REVIEWED = 'Reviewed', 'Reviewed'
        INTERVIEW = 'Interview', 'Interview'
        REJECTED = 'Rejected', 'Rejected'
        HIRED = 'Hired', 'Hired'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
        limit_choices_to={'role': 'applicant'}
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    resumeLink = models.URLField()
    coverLetter = models.TextField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=10, choices=ApplicationStatus.choices, default=ApplicationStatus.APPLIED)
    appliedAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('applicant', 'job') # An applicant can apply to a job only once

    def __str__(self):
        return f"{self.applicant.email} -> {self.job.title}"
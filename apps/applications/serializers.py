from rest_framework import serializers
from .models import Application
from apps.core.utils import upload_to_cloudinary

class ApplicationSerializer(serializers.ModelSerializer):
    """Serializer for displaying Application details."""
    applicantName = serializers.CharField(source='applicant.name', read_only=True)
    jobTitle = serializers.CharField(source='job.title', read_only=True)
    companyName = serializers.CharField(source='job.createdBy.name', read_only=True)
    jobStatus = serializers.CharField(source='job.status', read_only=True)

    class Meta:
        model = Application
        fields = (
            'id', 'status', 'appliedAt', 'resumeLink', 'coverLetter',
            'applicantName', 'jobTitle', 'companyName', 'jobStatus'
        )

class ApplicationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating an Application (applying for a job)."""
    resume = serializers.FileField(write_only=True, required=True)

    class Meta:
        model = Application
        fields = ('resume', 'coverLetter')
        extra_kwargs = {
            'coverLetter': {'max_length': 2000}
        }

class ApplicationUpdateStatusSerializer(serializers.ModelSerializer):
    """Serializer specifically for a company to update an application's status."""
    class Meta:
        model = Application
        fields = ('status',)
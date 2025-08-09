from rest_framework import serializers
from .models import Job

class JobSerializer(serializers.ModelSerializer):
    """Serializer for displaying job details."""
    companyName = serializers.CharField(source='createdBy.name', read_only=True)
    # This field is populated by an annotation in the view
    application_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Job
        fields = ('id', 'title', 'description', 'location', 'status', 'createdAt', 'companyName', 'application_count')
        read_only_fields = ('id', 'createdAt', 'companyName', 'application_count')

class JobCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating jobs."""
    class Meta:
        model = Job
        fields = ('title', 'description', 'location', 'status')

    def validate_status(self, value):
        """
        US4: Enforce forward-only status transition: Draft -> Open -> Closed.
        """
        if self.instance: # This means it's an update operation
            current_status = self.instance.status
            if current_status == Job.JobStatus.DRAFT and value not in [Job.JobStatus.DRAFT, Job.JobStatus.OPEN]:
                raise serializers.ValidationError("From 'Draft', you can only move to 'Open'.")
            if current_status == Job.JobStatus.OPEN and value not in [Job.JobStatus.OPEN, Job.JobStatus.CLOSED]:
                raise serializers.ValidationError("From 'Open', you can only move to 'Closed'.")
            if current_status == Job.JobStatus.CLOSED and value != Job.JobStatus.CLOSED:
                raise serializers.ValidationError("A 'Closed' job status cannot be changed.")
        return value
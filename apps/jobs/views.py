from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from .models import Job
from .serializers import JobSerializer, JobCreateUpdateSerializer
from apps.core.permissions import IsCompanyUser, IsJobOwner
from apps.applications.models import Application
from apps.applications.serializers import ApplicationSerializer # Import from applications app
from .filters import JobFilter

class JobViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Jobs.
    - US3: Create Job
    - US4: Update/Delete Job
    - US5: Browse Jobs
    - US8: View My Posted Jobs
    - US9: View Job Details
    - US10: View Job Applications for a Job
    """
    filter_backends = [DjangoFilterBackend]
    filterset_class = JobFilter

    def get_queryset(self):
        user = self.request.user
        queryset = Job.objects.select_related('createdBy').all()

        if self.action in ['my_jobs', 'applications_for_job']:
            # Companies see their own jobs with application counts
            return queryset.filter(createdBy=user).annotate(application_count=Count('applications'))
        elif user.is_authenticated and user.role == 'company':
             # Companies see all jobs, but 'my_jobs' is the dedicated endpoint for their own
             return queryset
        else:
            # Applicants and unauthenticated users see only 'Open' jobs
            return queryset.filter(status=Job.JobStatus.OPEN)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return JobCreateUpdateSerializer
        return JobSerializer

    def get_permissions(self):
        if self.action in ['create', 'my_jobs', 'applications_for_job']:
            self.permission_classes = [permissions.IsAuthenticated, IsCompanyUser]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAuthenticated, IsJobOwner]
        else: # list, retrieve
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(createdBy=self.request.user)

    # Custom action for a company to view their posted jobs (US8)
    @action(detail=False, methods=['get'], url_path='my-jobs')
    def my_jobs(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


    # Custom action for a company to view applications for one of their jobs (US10)
    @action(detail=True, methods=['get'], url_path='applications')
    def applications_for_job(self, request, pk=None):
        job = self.get_object() # This already checks ownership via get_permissions
        applications = Application.objects.filter(job=job).select_related('applicant')

        # Optional filtering by application status
        status_filter = request.query_params.get('status')
        if status_filter:
            applications = applications.filter(status=status_filter)

        page = self.paginate_queryset(applications)
        if page is not None:
            serializer = ApplicationSerializer(page, many=True) # Use ApplicationSerializer
            return self.get_paginated_response(serializer.data)

        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data)

    # Overriding default responses to match the required format
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            "success": True, "message": "Job created successfully.", "object": response.data, "errors": None
        })

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({
            "success": True, "message": "Job retrieved successfully.", "object": response.data, "errors": None
        })

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            "success": True, "message": "Job updated successfully.", "object": response.data, "errors": None
        })

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({
            "success": True, "message": "Job deleted successfully.", "object": None, "errors": None
        }, status=status.HTTP_204_NO_CONTENT)

    # Note: The paginated response for list() is handled by the CustomPagination class.
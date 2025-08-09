from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.core.mail import send_mail
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter


from .models import Application
from apps.jobs.models import Job
from .serializers import ApplicationSerializer, ApplicationCreateSerializer, ApplicationUpdateStatusSerializer
from apps.core.permissions import IsApplicantUser, IsCompanyUser, IsJobOwnerForApplication
from apps.core.utils import upload_to_cloudinary
from .filters import ApplicationFilter

class ApplyForJobView(generics.CreateAPIView):
    """
    US6: Apply for a job (Applicant only).
    Handles resume upload to Cloudinary.
    """
    serializer_class = ApplicationCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsApplicantUser]

    def create(self, request, *args, **kwargs):
        job_id = self.kwargs.get('job_id')
        job = get_object_or_404(Job, id=job_id)

        if job.status != Job.JobStatus.OPEN:
            return Response({"success": False, "message": "This job is not open for applications.", "object": None, "errors": ["Job not open."]}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Upload resume to Cloudinary
            resume_file = serializer.validated_data['resume']
            resume_url = upload_to_cloudinary(resume_file)

            # Create the application
            application = serializer.save(
                applicant=request.user,
                job=job,
                resumeLink=resume_url
            )

            # Notify company
            send_mail(
                subject=f"New Application for {job.title}",
                message=f"A new applicant, {request.user.name}, has applied for your job posting: '{job.title}'.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[job.createdBy.email]
            )

            response_data = ApplicationSerializer(application).data
            return Response({
                "success": True, "message": "Application submitted successfully.", "object": response_data, "errors": None
            }, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response({"success": False, "message": "You have already applied for this job.", "object": None, "errors": ["Duplicate application."]}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"success": False, "message": "An error occurred.", "object": None, "errors": [str(e)]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MyApplicationsView(generics.ListAPIView):
    """
    US7: Track my applications (Applicant only).
    Supports filtering and sorting.
    """
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsApplicantUser]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ApplicationFilter
    ordering_fields = ['appliedAt', 'job__createdBy__name', 'status', 'job__title']

    def get_queryset(self):
        return Application.objects.filter(applicant=self.request.user).select_related('job', 'job__createdBy').order_by('-appliedAt')


class UpdateApplicationStatusView(generics.UpdateAPIView):
    """
    US11: Update application status (Company that owns the job only).
    Sends email notification to applicant on status change.
    """
    queryset = Application.objects.select_related('applicant', 'job').all()
    serializer_class = ApplicationUpdateStatusSerializer
    permission_classes = [permissions.IsAuthenticated, IsCompanyUser, IsJobOwnerForApplication]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_status = instance.status
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data.get('status')
        self.perform_update(serializer)

        # Send email notification if status changes to a key state
        if new_status and old_status != new_status:
            if new_status in [Application.ApplicationStatus.INTERVIEW, Application.ApplicationStatus.REJECTED, Application.ApplicationStatus.HIRED]:
                applicant = instance.applicant
                job = instance.job
                message_map = {
                    "Interview": f"Good news! You've been selected for an interview for the {job.title} position.",
                    "Rejected": f"We regret to inform you that we will not be moving forward with your application for the {job.title} position.",
                    "Hired": f"Congratulations! You've been hired for the {job.title} position at {job.createdBy.name}!"
                }
                send_mail(
                    subject=f"Update on your application for {job.title}",
                    message=f"Hi {applicant.name},\n\n{message_map.get(new_status)}\n\nBest regards,\n{job.createdBy.name}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[applicant.email]
                )

        response_data = ApplicationSerializer(instance).data
        return Response({
            "success": True, "message": "Application status updated successfully.", "object": response_data, "errors": None
        })
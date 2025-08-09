from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobViewSet
from apps.applications.views import ApplyForJobView # Import the apply view

router = DefaultRouter()
router.register('', JobViewSet, basename='job')

urlpatterns = [
    # US6: The endpoint to apply for a job is nested under the job
    path('<uuid:job_id>/apply/', ApplyForJobView.as_view(), name='apply-for-job'),
    path('', include(router.urls)),
]
from django.urls import path
from .views import MyApplicationsView, UpdateApplicationStatusView

urlpatterns = [
    path('my-applications/', MyApplicationsView.as_view(), name='my-applications'),
    path('<uuid:pk>/update-status/', UpdateApplicationStatusView.as_view(), name='update-application-status'),
]
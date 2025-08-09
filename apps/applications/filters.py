from django_filters import rest_framework as filters
from .models import Application

class ApplicationFilter(filters.FilterSet):
    companyName = filters.CharFilter(field_name='job__createdBy__name', lookup_expr='icontains')
    jobStatus = filters.CharFilter(field_name='job__status', lookup_expr='iexact')
    status = filters.MultipleChoiceFilter(choices=Application.ApplicationStatus.choices)

    class Meta:
        model = Application
        fields = ['companyName', 'jobStatus', 'status']
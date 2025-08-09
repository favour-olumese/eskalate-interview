from django_filters import rest_framework as filters
from .models import Job

class JobFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='icontains')
    location = filters.CharFilter(lookup_expr='icontains')
    companyName = filters.CharFilter(field_name='createdBy__name', lookup_expr='icontains')
    status = filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Job
        fields = ['title', 'location', 'companyName', 'status']
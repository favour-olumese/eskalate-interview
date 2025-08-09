from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'pageSize'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'message': 'Data retrieved successfully.',
            'object': data,
            'pageNumber': self.page.number,
            'pageSize': self.get_page_size(self.request),
            'totalSize': self.page.paginator.count,
            'errors': None,
        })
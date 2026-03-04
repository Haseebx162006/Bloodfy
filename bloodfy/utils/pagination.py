"""
Custom pagination classes for Bloodfy application.
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination with customizable page size."""
    
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = MAX_PAGE_SIZE
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        """Return a paginated response with additional metadata."""
        return Response({
            'success': True,
            'message': 'Data retrieved successfully',
            'data': {
                'results': data,
                'pagination': {
                    'count': self.page.paginator.count,
                    'total_pages': self.page.paginator.num_pages,
                    'current_page': self.page.number,
                    'page_size': self.get_page_size(self.request),
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link(),
                }
            }
        })


class LargeResultsSetPagination(PageNumberPagination):
    """Pagination for endpoints that need more results."""
    
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200
    
    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'message': 'Data retrieved successfully',
            'data': {
                'results': data,
                'pagination': {
                    'count': self.page.paginator.count,
                    'total_pages': self.page.paginator.num_pages,
                    'current_page': self.page.number,
                    'page_size': self.get_page_size(self.request),
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link(),
                }
            }
        })


class SmallResultsSetPagination(PageNumberPagination):
    """Pagination for endpoints with smaller result sets."""
    
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    
    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'message': 'Data retrieved successfully',
            'data': {
                'results': data,
                'pagination': {
                    'count': self.page.paginator.count,
                    'total_pages': self.page.paginator.num_pages,
                    'current_page': self.page.number,
                    'page_size': self.get_page_size(self.request),
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link(),
                }
            }
        })

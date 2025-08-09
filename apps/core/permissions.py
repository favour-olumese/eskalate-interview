from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsCompanyUser(BasePermission):
    """Allows access only to users with the 'company' role."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'company')

class IsApplicantUser(BasePermission):
    """Allows access only to users with the 'applicant' role."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'applicant')

class IsOwnerOrReadOnly(BasePermission):
    """Custom permission to only allow owners of an object to edit it."""
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        # For jobs, the owner is 'createdBy'
        if hasattr(obj, 'createdBy'):
            return obj.createdBy == request.user
        # For applications, the owner is 'applicant'
        if hasattr(obj, 'applicant'):
            return obj.applicant == request.user
        return False

class IsJobOwner(BasePermission):
    """Permission to check if the user is the owner of the job."""
    def has_object_permission(self, request, view, obj):
        return obj.createdBy == request.user

class IsJobOwnerForApplication(BasePermission):
    """Permission to check if the user owns the job associated with the application."""
    def has_object_permission(self, request, view, obj):
        return obj.job.createdBy == request.user
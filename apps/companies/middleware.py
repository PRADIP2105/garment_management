from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from .models import UserProfile


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware to set company context for authenticated users
    """
    
    def process_request(self, request):
        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.select_related('company').get(user=request.user)
                request.company = profile.company
                request.user_role = profile.role
            except UserProfile.DoesNotExist:
                request.company = None
                request.user_role = None
        else:
            request.company = None
            request.user_role = None
from django.contrib.auth import logout
from django.utils import timezone
from django.conf import settings


class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Check if session has expired
            last_activity = request.session.get('last_activity')
            if last_activity:
                last_activity_time = timezone.datetime.fromisoformat(last_activity)
                time_diff = (timezone.now() - last_activity_time).total_seconds()
                if time_diff > settings.SESSION_COOKIE_AGE:
                    logout(request)
                    return self.get_response(request)

            # Update last activity time
            request.session['last_activity'] = timezone.now().isoformat()

        response = self.get_response(request)
        return response

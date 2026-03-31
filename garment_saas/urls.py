from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from apps.authentication.views import login_debug_view, login_attempts_list_view


def api_ping(_request):
    """Public health check for mobile apps (LAN connectivity / firewall)."""
    return JsonResponse({"ok": True})


def api_root(_request):
    """Root API endpoint — returns basic info so /api/ doesn't 404."""
    return JsonResponse({"status": "ok", "message": "Garment Management API"})


urlpatterns = [
    path("api/", api_root),
    path("api/ping/", api_ping),
    path("i18n/", include("django.conf.urls.i18n")),
    # API auth - using custom authentication app
    path("api/auth/", include("apps.authentication.urls")),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # API modules
    path("api/companies/", include("apps.companies.urls")),
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/workers/", include("apps.workers.urls")),
    path("api/suppliers/", include("apps.suppliers.urls")),
    path("api/materials/", include("apps.materials.urls")),
    path("api/work/", include("apps.work.urls")),
    path("api/dashboard/", include("apps.dashboard.urls")),
]

urlpatterns += [
    path("auth/login-debug/", login_debug_view, name="login_debug"),
    path("auth/login-attempts/", login_attempts_list_view, name="login_attempts_list"),
]

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    # Web UI
    path("", include(("apps.web.urls", "web"), namespace="web")),
    prefix_default_language=False,
)


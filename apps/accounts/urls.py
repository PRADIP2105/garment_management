from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import RegisterOwnerView, StaffViewSet

router = DefaultRouter()
router.register("staff", StaffViewSet, basename="staff")

urlpatterns = [
    path("register-owner/", RegisterOwnerView.as_view(), name="register-owner"),
    path("", include(router.urls)),
]



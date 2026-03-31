from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    MaterialInwardViewSet,
    WorkDistributionViewSet,
    WorkReturnViewSet,
    WorkTypeViewSet,
)

router = DefaultRouter()
router.register("types", WorkTypeViewSet, basename="work-type")
router.register("inwards", MaterialInwardViewSet, basename="material-inward")
router.register("distributions", WorkDistributionViewSet, basename="work-distribution")
router.register("returns", WorkReturnViewSet, basename="work-return")

urlpatterns = [
    path("", include(router.urls)),
]



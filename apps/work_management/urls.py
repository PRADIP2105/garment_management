from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkTypeViewSet, WorkDistributionViewSet, WorkReturnViewSet

router = DefaultRouter()
router.register(r'types', WorkTypeViewSet, basename='worktype')
router.register(r'distributions', WorkDistributionViewSet, basename='workdistribution')
router.register(r'returns', WorkReturnViewSet, basename='workreturn')

urlpatterns = [
    path('', include(router.urls)),
]
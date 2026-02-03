from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RawMaterialViewSet, MaterialInwardViewSet

router = DefaultRouter()
router.register(r'raw-materials', RawMaterialViewSet, basename='rawmaterial')
router.register(r'inward', MaterialInwardViewSet, basename='materialinward')

urlpatterns = [
    path('', include(router.urls)),
]
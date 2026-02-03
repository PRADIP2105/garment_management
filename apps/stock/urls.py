from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StockLedgerViewSet, CurrentStockViewSet

router = DefaultRouter()
router.register(r'ledger', StockLedgerViewSet, basename='stockledger')
router.register(r'current', CurrentStockViewSet, basename='currentstock')

urlpatterns = [
    path('', include(router.urls)),
]
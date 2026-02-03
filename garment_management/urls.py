from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/companies/', include('apps.companies.urls')),
    path('api/workers/', include('apps.workers.urls')),
    path('api/suppliers/', include('apps.suppliers.urls')),
    path('api/materials/', include('apps.materials.urls')),
    path('api/work/', include('apps.work_management.urls')),
    path('api/stock/', include('apps.stock.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
    path('', include('apps.web.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
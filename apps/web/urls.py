from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('workers/', views.workers, name='workers'),
    path('suppliers/', views.suppliers, name='suppliers'),
    path('materials/', views.materials, name='materials'),
    path('work/distribution/', views.work_distribution, name='work_distribution'),
    path('work/return/', views.work_return, name='work_return'),
    path('stock/', views.stock, name='stock'),
    path('direct-login/', views.direct_login_test, name='direct_login'),
]
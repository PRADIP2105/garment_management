from django.urls import path

from . import views

app_name = "web"

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("forgot-password/", views.forgot_password_view, name="forgot_password"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("workers/", views.workers_list, name="workers_list"),
    path("workers/create/", views.worker_create, name="worker_create"),
    path("workers/<int:pk>/update/", views.worker_update, name="worker_update"),
    path("workers/<int:pk>/delete/", views.worker_delete, name="worker_delete"),
    path("suppliers/", views.suppliers_list, name="suppliers_list"),
    path("suppliers/create/", views.supplier_create, name="supplier_create"),
    path("suppliers/<int:pk>/update/", views.supplier_update, name="supplier_update"),
    path("suppliers/<int:pk>/delete/", views.supplier_delete, name="supplier_delete"),
    path("materials/", views.materials_list, name="materials_list"),
    path("materials/create/", views.material_create, name="material_create"),
    path("materials/<int:pk>/update/", views.material_update, name="material_update"),
    path("materials/<int:pk>/delete/", views.material_delete, name="material_delete"),
    path("material-inward/", views.material_inward_list, name="material_inward_list"),
    path("material-inward/create/", views.material_inward_create, name="material_inward_create"),
    path("material-inward/<int:pk>/update/", views.material_inward_update, name="material_inward_update"),
    path("material-inward/<int:pk>/delete/", views.material_inward_delete, name="material_inward_delete"),
    path("work-types/", views.work_types_list, name="work_types_list"),
    path("work-types/create/", views.work_type_create, name="work_type_create"),
    path("work-types/<int:pk>/update/", views.work_type_update, name="work_type_update"),
    path("work-types/<int:pk>/delete/", views.work_type_delete, name="work_type_delete"),
    path("work-distribution/", views.work_distribution_list, name="work_distribution_list"),
    path("work-distribution/create/", views.work_distribution_create, name="work_distribution_create"),
    path("work-distribution/<int:pk>/update/", views.work_distribution_update, name="work_distribution_update"),
    path("work-distribution/<int:pk>/delete/", views.work_distribution_delete, name="work_distribution_delete"),
    path("work-received/", views.work_received_list, name="work_received_list"),
    path("work-received/create/", views.work_received_create, name="work_received_create"),
    path("work-received/<int:pk>/update/", views.work_received_update, name="work_received_update"),
    path("work-received/<int:pk>/delete/", views.work_received_delete, name="work_received_delete"),
    path("pending-work/", views.pending_work_list, name="pending_work_list"),
]


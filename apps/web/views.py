from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _, activate
from datetime import date

from apps.accounts.forms import RegisterOwnerForm, ForgotPasswordForm
from django.contrib.auth import get_user_model

User = get_user_model()
from apps.dashboard.views import DashboardSummaryView
from apps.materials.forms import MaterialForm, MaterialInwardForm
from apps.materials.models import Material
from apps.work.models import MaterialInward, WorkReceived
from apps.suppliers.forms import SupplierForm
from apps.suppliers.models import Supplier

from apps.workers.models import Worker
from apps.workers.forms import WorkerForm

from apps.work.forms import WorkTypeForm, WorkDistributionForm, WorkReceivedForm
from apps.work.models import WorkType, WorkDistribution, WorkReceived, WorkReturn


def home(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("web:dashboard")
    return render(request, "home.html")


def register_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("web:dashboard")

    if request.method == "POST":
        form = RegisterOwnerForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Add dummy data for the new user
            add_dummy_data_for_user(user)
            login(request, user)
            messages.success(request, _("Account created successfully! Welcome! Dummy data has been added."))
            return redirect("web:dashboard")
        else:
            messages.error(request, _("Please correct the errors below."))
    else:
        form = RegisterOwnerForm()
    return render(request, "web/register.html", {"form": form})


def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("web:dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, _("Welcome back!"))
            return redirect("web:dashboard")
        messages.error(request, _("Invalid username or password."))
    return render(request, "web/login.html")


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    messages.success(request, _("You have been logged out."))
    return redirect("web:login")


def forgot_password_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("web:dashboard")

    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            new_password = form.cleaned_data['new_password']
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            messages.success(request, _("Password has been reset successfully. Please log in with your new password."))
            return redirect("web:login")
        else:
            messages.error(request, _("Please correct the errors below."))
    else:
        form = ForgotPasswordForm()
    return render(request, "web/forgot_password.html", {"form": form})


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    # Check if user has a company
    if not hasattr(request.user, "company") or request.user.company is None:
        messages.warning(
            request,
            _("Your account is not linked to a company. Please contact an administrator."),
        )
        return render(request, "dashboard.html", {"stats": None})
    
    # Reuse API view logic to compute stats
    try:
        api_view = DashboardSummaryView()
        api_view.request = request
        response = api_view.get(request)
        stats = response.data
    except Exception as e:
        # If there's any error, show empty dashboard
        import logging
        logger = logging.getLogger(__name__)
        logger.exception("Dashboard error")
        stats = {
            "total_workers": 0,
            "pending_work_by_worker": [],
            "completed_work_quantity": 0,
            "low_stock_materials": [],
            "today_inward_quantity": 0,
            "today_outward_lot_size": 0,
        }
    
    return render(request, "dashboard.html", {"stats": stats})


@login_required
def workers_list(request: HttpRequest) -> HttpResponse:
    if not request.user.company:
        messages.error(request, _("You are not associated with a company."))
        return redirect("web:dashboard")

    workers = Worker.objects.filter(company=request.user.company)
    name = request.GET.get('name')
    mobile = request.GET.get('mobile')
    skill_type = request.GET.get('skill_type')
    machine_type = request.GET.get('machine_type')
    status = request.GET.get('status')
    if name:
        workers = workers.filter(name__icontains=name)
    if mobile:
        workers = workers.filter(mobile_number__icontains=mobile)
    if skill_type:
        workers = workers.filter(skill_type=skill_type)
    if machine_type:
        workers = workers.filter(machine_type=machine_type)
    if status:
        workers = workers.filter(status=status)
    paginator = Paginator(workers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        "workers": page_obj,
        "page_obj": page_obj,
        "name": name,
        "mobile": mobile,
        "skill_type": skill_type,
        "machine_type": machine_type,
        "status": status,
        "skill_types": Worker.SkillType.choices,
        "machine_types": Worker.MachineType.choices,
        "statuses": Worker.Status.choices,
    }
    return render(request, "web/workers_list.html", context)


@login_required
def worker_create(request: HttpRequest) -> HttpResponse:
    if not hasattr(request.user, "company") or request.user.company is None:
        messages.warning(
            request,
            _("Your account is not linked to a company. Please contact an administrator."),
        )
        return redirect("web:dashboard")

    if request.method == "POST":
        form = WorkerForm(request.POST, company=request.user.company)
        if form.is_valid():
            form.save()
            messages.success(request, _("Worker created successfully."))
            return redirect("web:workers_list")
    else:
        form = WorkerForm(company=request.user.company)
    return render(request, "web/worker_form.html", {"form": form, "title": _("Create Worker")})


@login_required
def worker_update(request: HttpRequest, pk: int) -> HttpResponse:
    worker = get_object_or_404(Worker, pk=pk, company=request.user.company)
    if request.method == "POST":
        form = WorkerForm(request.POST, instance=worker, company=request.user.company)
        if form.is_valid():
            form.save()
            messages.success(request, _("Worker updated successfully."))
            return redirect("web:workers_list")
    else:
        form = WorkerForm(instance=worker, company=request.user.company)
    return render(request, "web/worker_form.html", {"form": form, "title": _("Update Worker")})


@login_required
def worker_delete(request: HttpRequest, pk: int) -> HttpResponse:
    from django.http import JsonResponse
    worker = get_object_or_404(Worker, pk=pk, company=request.user.company)
    if request.method == "POST":
        # Check if worker has related work distributions
        if WorkDistribution.objects.filter(worker=worker).exists():
            return JsonResponse({'success': False, 'message': _("Cannot delete worker because they have associated work distributions. Please remove or reassign the work distributions first.")})
        worker.delete()
        return JsonResponse({'success': True, 'message': _("Worker deleted successfully.")})
    return render(request, "web/worker_confirm_delete.html", {"worker": worker})


@login_required
def suppliers_list(request: HttpRequest) -> HttpResponse:
    if not request.user.company:
        messages.error(request, _("You are not associated with a company."))
        return redirect("web:dashboard")

    suppliers = Supplier.objects.filter(company=request.user.company)
    name = request.GET.get('name')
    mobile = request.GET.get('mobile')
    city = request.GET.get('city')
    if name:
        suppliers = suppliers.filter(name__icontains=name)
    if mobile:
        suppliers = suppliers.filter(mobile_number__icontains=mobile)
    if city:
        suppliers = suppliers.filter(city__icontains=city)
    paginator = Paginator(suppliers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "name": name,
        "mobile": mobile,
        "city": city,
    }
    return render(request, "web/suppliers_list.html", context)


@login_required
def supplier_create(request: HttpRequest) -> HttpResponse:
    if not hasattr(request.user, "company") or request.user.company is None:
        messages.warning(
            request,
            _("Your account is not linked to a company. Please contact an administrator."),
        )
        return redirect("web:dashboard")

    if request.method == "POST":
        form = SupplierForm(request.POST, company=request.user.company)
        if form.is_valid():
            form.save()
            messages.success(request, _("Supplier created successfully."))
            return redirect("web:suppliers_list")
    else:
        form = SupplierForm(company=request.user.company)
    return render(request, "web/supplier_form.html", {"form": form, "title": _("Create Supplier")})


@login_required
def supplier_update(request: HttpRequest, pk: int) -> HttpResponse:
    supplier = get_object_or_404(Supplier, pk=pk, company=request.user.company)
    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier, company=request.user.company)
        if form.is_valid():
            form.save()
            messages.success(request, _("Supplier updated successfully."))
            return redirect("web:suppliers_list")
    else:
        form = SupplierForm(instance=supplier, company=request.user.company)
    return render(request, "web/supplier_form.html", {"form": form, "title": _("Update Supplier")})


@login_required
def supplier_delete(request: HttpRequest, pk: int) -> HttpResponse:
    from django.http import JsonResponse
    supplier = get_object_or_404(Supplier, pk=pk, company=request.user.company)
    if request.method == "POST":
        # Check if supplier has related material inwards
        if MaterialInward.objects.filter(supplier=supplier).exists():
            return JsonResponse({'success': False, 'message': _("Cannot delete supplier because they have associated material inward entries. Please remove or reassign the material inward entries first.")})
        supplier.delete()
        return JsonResponse({'success': True, 'message': _("Supplier deleted successfully.")})
    return render(request, "web/supplier_confirm_delete.html", {"supplier": supplier})


@login_required
def materials_list(request: HttpRequest) -> HttpResponse:
    materials = Material.objects.filter(company=request.user.company)
    material_name = request.GET.get('material_name')
    unit = request.GET.get('unit')
    description = request.GET.get('description')
    if material_name:
        materials = materials.filter(material_name__icontains=material_name)
    if unit:
        materials = materials.filter(unit=unit)
    if description:
        materials = materials.filter(description__icontains=description)
    paginator = Paginator(materials, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "materials": materials,
        "material_name": material_name,
        "unit": unit,
        "description": description,
    }
    return render(request, "web/materials_list.html", context)


@login_required
def material_create(request: HttpRequest) -> HttpResponse:
    if not hasattr(request.user, "company") or request.user.company is None:
        messages.warning(
            request,
            _("Your account is not linked to a company. Please contact an administrator."),
        )
        return redirect("web:dashboard")

    if request.method == "POST":
        form = MaterialForm(request.POST, company=request.user.company)
        if form.is_valid():
            form.save()
            messages.success(request, _("Material created successfully."))
            return redirect("web:materials_list")
    else:
        form = MaterialForm(company=request.user.company)
    return render(request, "web/material_form.html", {"form": form, "title": _("Create Material")})


@login_required
def material_update(request: HttpRequest, pk: int) -> HttpResponse:
    material = get_object_or_404(Material, pk=pk, company=request.user.company)
    if request.method == "POST":
        form = MaterialForm(request.POST, instance=material, company=request.user.company)
        if form.is_valid():
            form.save()
            messages.success(request, _("Material updated successfully."))
            return redirect("web:materials_list")
    else:
        form = MaterialForm(instance=material, company=request.user.company)
    return render(request, "web/material_form.html", {"form": form, "title": _("Update Material")})


@login_required
def material_delete(request: HttpRequest, pk: int) -> HttpResponse:
    from django.http import JsonResponse
    material = get_object_or_404(Material, pk=pk, company=request.user.company)
    if request.method == "POST":
        material.delete()
        return JsonResponse({'success': True, 'message': _("Material deleted successfully.")})
    return render(request, "web/material_confirm_delete.html", {"material": material})


@login_required
def material_inward_list(request: HttpRequest) -> HttpResponse:
    if not request.user.company:
        messages.error(request, _("You are not associated with a company."))
        return redirect("web:dashboard")

    material_inwards = MaterialInward.objects.filter(company=request.user.company).select_related('material', 'supplier')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    material_name = request.GET.get('material_name')
    supplier_name = request.GET.get('supplier_name')
    quantity_min = request.GET.get('quantity_min')
    quantity_max = request.GET.get('quantity_max')
    if start_date:
        material_inwards = material_inwards.filter(received_date__gte=start_date)
    if end_date:
        material_inwards = material_inwards.filter(received_date__lte=end_date)
    if material_name:
        material_inwards = material_inwards.filter(material__material_name__icontains=material_name)
    if supplier_name:
        material_inwards = material_inwards.filter(supplier__name__icontains=supplier_name)
    if quantity_min:
        material_inwards = material_inwards.filter(quantity__gte=quantity_min)
    if quantity_max:
        material_inwards = material_inwards.filter(quantity__lte=quantity_max)
    paginator = Paginator(material_inwards, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "start_date": start_date,
        "end_date": end_date,
        "material_name": material_name,
        "supplier_name": supplier_name,
        "quantity_min": quantity_min,
        "quantity_max": quantity_max,
    }
    return render(request, "web/material_inward_list.html", context)


@login_required
def material_inward_create(request: HttpRequest) -> HttpResponse:
    if not hasattr(request.user, "company") or request.user.company is None:
        messages.warning(
            request,
            _("Your account is not linked to a company. Please contact an administrator."),
        )
        return redirect("web:dashboard")

    if request.method == "POST":
        form = MaterialInwardForm(request.POST, company=request.user.company)
        if form.is_valid():
            form.save()
            messages.success(request, _("Material inward entry created successfully."))
            return redirect("web:material_inward_list")
    else:
        form = MaterialInwardForm(company=request.user.company)
    return render(request, "web/material_inward_form.html", {"form": form, "title": _("Create Material Inward")})


@login_required
def material_inward_update(request: HttpRequest, pk: int) -> HttpResponse:
    material_inward = get_object_or_404(MaterialInward, pk=pk, company=request.user.company)
    if request.method == "POST":
        form = MaterialInwardForm(request.POST, instance=material_inward, company=request.user.company)
        if form.is_valid():
            form.save()
            messages.success(request, _("Material inward entry updated successfully."))
            return redirect("web:material_inward_list")
    else:
        form = MaterialInwardForm(instance=material_inward, company=request.user.company)
    return render(request, "web/material_inward_form.html", {"form": form, "title": _("Update Material Inward")})


@login_required
def material_inward_delete(request: HttpRequest, pk: int) -> HttpResponse:
    from django.http import JsonResponse
    material_inward = get_object_or_404(MaterialInward, pk=pk, company=request.user.company)
    if request.method == "POST":
        material_inward.delete()
        return JsonResponse({'success': True, 'message': _("Material inward entry deleted successfully.")})
    return render(request, "web/material_inward_confirm_delete.html", {"material_inward": material_inward})


@login_required
def work_distribution_list(request: HttpRequest) -> HttpResponse:
    if not request.user.company:
        messages.error(request, _("You are not associated with a company."))
        return redirect("web:dashboard")

    work_distributions = WorkDistribution.objects.filter(company=request.user.company).select_related('worker', 'work_type')
    worker_name = request.GET.get('worker_name')
    work_type_name = request.GET.get('work_type_name')
    lot_size_min = request.GET.get('lot_size_min')
    lot_size_max = request.GET.get('lot_size_max')
    if worker_name:
        work_distributions = work_distributions.filter(worker__name__icontains=worker_name)
    if work_type_name:
        work_distributions = work_distributions.filter(work_type__name__icontains=work_type_name)
    if lot_size_min:
        work_distributions = work_distributions.filter(lot_size__gte=lot_size_min)
    if lot_size_max:
        work_distributions = work_distributions.filter(lot_size__lte=lot_size_max)
    paginator = Paginator(work_distributions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "worker_name": worker_name,
        "work_type_name": work_type_name,
        "lot_size_min": lot_size_min,
        "lot_size_max": lot_size_max,
    }
    return render(request, "web/work_distribution_list.html", context)


@login_required
def work_distribution_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = WorkDistributionForm(request.POST, company=request.user.company)
        if form.is_valid():
            form.save()
            messages.success(request, _("Work distribution created successfully."))
            return redirect("web:work_distribution_list")
    else:
        form = WorkDistributionForm(company=request.user.company)
    return render(request, "web/work_distribution_form.html", {"form": form, "title": _("Create Work Distribution")})


@login_required
def work_distribution_update(request: HttpRequest, pk: int) -> HttpResponse:
    work_distribution = get_object_or_404(WorkDistribution, pk=pk, company=request.user.company)
    if request.method == "POST":
        form = WorkDistributionForm(request.POST, instance=work_distribution, company=request.user.company)
        if form.is_valid():
            form.save()
            messages.success(request, _("Work distribution updated successfully."))
            return redirect("web:work_distribution_list")
    else:
        form = WorkDistributionForm(instance=work_distribution, company=request.user.company)
    return render(request, "web/work_distribution_form.html", {"form": form, "title": _("Update Work Distribution")})


@login_required
def work_distribution_delete(request: HttpRequest, pk: int) -> HttpResponse:
    from django.http import JsonResponse
    work_distribution = get_object_or_404(WorkDistribution, pk=pk, company=request.user.company)
    if request.method == "POST":
        work_distribution.delete()
        return JsonResponse({'success': True, 'message': _("Work distribution deleted successfully.")})
    return render(request, "web/work_distribution_confirm_delete.html", {"work_distribution": work_distribution})


@login_required
def work_types_list(request: HttpRequest) -> HttpResponse:
    if not request.user.company:
        messages.error(request, _("You are not associated with a company."))
        return redirect("web:dashboard")

    work_types = WorkType.objects.filter(company=request.user.company)
    name = request.GET.get('name')
    if name:
        work_types = work_types.filter(name__icontains=name)
    paginator = Paginator(work_types, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "name": name,
    }
    return render(request, "web/work_types_list.html", context)


@login_required
def work_type_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = WorkTypeForm(request.POST, company=request.user.company)
        if form.is_valid():
            form.save()
            messages.success(request, _("Work type created successfully."))
            return redirect("web:work_types_list")
    else:
        form = WorkTypeForm(company=request.user.company)
    return render(request, "web/work_type_form.html", {"form": form, "title": _("Create Work Type")})


@login_required
def work_type_update(request: HttpRequest, pk: int) -> HttpResponse:
    work_type = get_object_or_404(WorkType, pk=pk, company=request.user.company)
    if request.method == "POST":
        form = WorkTypeForm(request.POST, instance=work_type, company=request.user.company)
        if form.is_valid():
            form.save()
            messages.success(request, _("Work type updated successfully."))
            return redirect("web:work_types_list")
    else:
        form = WorkTypeForm(instance=work_type, company=request.user.company)
    return render(request, "web/work_type_form.html", {"form": form, "title": _("Update Work Type")})


@login_required
def work_type_delete(request: HttpRequest, pk: int) -> HttpResponse:
    from django.http import JsonResponse
    work_type = get_object_or_404(WorkType, pk=pk, company=request.user.company)
    if request.method == "POST":
        work_type.delete()
        return JsonResponse({'success': True, 'message': _("Work type deleted successfully.")})
    return render(request, "web/work_type_confirm_delete.html", {"work_type": work_type})


@login_required
def work_received_list(request: HttpRequest) -> HttpResponse:
    if not request.user.company:
        messages.error(request, _("You are not associated with a company."))
        return redirect("web:dashboard")

    work_received = WorkReceived.objects.filter(company=request.user.company).select_related(
        'distribution__worker', 'distribution__work_type'
    ).order_by('-received_date')
    worker_name = request.GET.get('worker_name')
    work_type_name = request.GET.get('work_type_name')
    received_quantity_min = request.GET.get('received_quantity_min')
    received_quantity_max = request.GET.get('received_quantity_max')
    status = request.GET.get('status')
    if worker_name:
        work_received = work_received.filter(distribution__worker__name__icontains=worker_name)
    if work_type_name:
        work_received = work_received.filter(distribution__work_type__name__icontains=work_type_name)
    if received_quantity_min:
        work_received = work_received.filter(received_quantity__gte=received_quantity_min)
    if received_quantity_max:
        work_received = work_received.filter(received_quantity__lte=received_quantity_max)
    if status:
        work_received = work_received.filter(status=status)
    paginator = Paginator(work_received, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "worker_name": worker_name,
        "work_type_name": work_type_name,
        "received_quantity_min": received_quantity_min,
        "received_quantity_max": received_quantity_max,
        "status": status,
    }
    return render(request, "web/work_received_list.html", context)


@login_required
def work_received_create(request: HttpRequest) -> HttpResponse:
    if not hasattr(request.user, "company") or request.user.company is None:
        messages.warning(
            request,
            _("Your account is not linked to a company. Please contact an administrator."),
        )
        return redirect("web:dashboard")

    if request.method == "POST":
        form = WorkReceivedForm(request.POST, company=request.user.company)
        if form.is_valid():
            form.save()
            messages.success(request, _("Work received entry created successfully."))
            return redirect("web:work_received_list")
    else:
        form = WorkReceivedForm(company=request.user.company)
    return render(request, "web/work_received_form.html", {"form": form, "title": _("Create Work Received")})


@login_required
def work_received_update(request: HttpRequest, pk: int) -> HttpResponse:
    work_received = get_object_or_404(WorkReceived, pk=pk, company=request.user.company)
    if request.method == "POST":
        form = WorkReceivedForm(request.POST, instance=work_received, company=request.user.company)
        if form.is_valid():
            form.save()
            messages.success(request, _("Work received entry updated successfully."))
            return redirect("web:work_received_list")
    else:
        form = WorkReceivedForm(instance=work_received, company=request.user.company)
    return render(request, "web/work_received_form.html", {"form": form, "title": _("Update Work Received")})


@login_required
def work_received_delete(request: HttpRequest, pk: int) -> HttpResponse:
    from django.http import JsonResponse
    work_received = get_object_or_404(WorkReceived, pk=pk, company=request.user.company)
    if request.method == "POST":
        work_received.delete()
        return JsonResponse({'success': True, 'message': _("Work received entry deleted successfully.")})
    return render(request, "web/work_received_confirm_delete.html", {"work_received": work_received})


@login_required
def pending_work_list(request: HttpRequest) -> HttpResponse:
    from django.db.models import Sum, F
    from django.db.models.functions import Coalesce
    # Get distributions where total received_quantity < lot_size
    distributions = WorkDistribution.objects.filter(company=request.user.company).annotate(
        total_received=Coalesce(Sum('received_works__received_quantity'), 0),
        pending_quantity=F('lot_size') - Coalesce(Sum('received_works__received_quantity'), 0)
    ).filter(total_received__lt=F('lot_size')).select_related('worker', 'work_type')
    worker_name = request.GET.get('worker_name')
    work_type_name = request.GET.get('work_type_name')
    lot_size_min = request.GET.get('lot_size_min')
    lot_size_max = request.GET.get('lot_size_max')
    if worker_name:
        distributions = distributions.filter(worker__name__icontains=worker_name)
    if work_type_name:
        distributions = distributions.filter(work_type__name__icontains=work_type_name)
    if lot_size_min:
        distributions = distributions.filter(lot_size__gte=lot_size_min)
    if lot_size_max:
        distributions = distributions.filter(lot_size__lte=lot_size_max)
    paginator = Paginator(distributions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "worker_name": worker_name,
        "work_type_name": work_type_name,
        "lot_size_min": lot_size_min,
        "lot_size_max": lot_size_max,
    }
    return render(request, "web/pending_work_list.html", context)


def add_dummy_data_for_user(user):
    company = user.company

    # Add dummy workers
    workers = []
    for i in range(5):
        worker = Worker.objects.create(
            company=company,
            name=f'Worker {i+1}',
            mobile_number=f'98765432{i+1:02d}',
            address=f'Address {i+1}',
            city='Ahmedabad',
            skill_type=Worker.SkillType.STITCHING,
            machine_type=Worker.MachineType.SIMPLE,
            status=Worker.Status.ACTIVE,
            language_preference='gu'
        )
        workers.append(worker)

    # Add dummy suppliers
    suppliers = []
    for i in range(3):
        supplier = Supplier.objects.create(
            company=company,
            name=f'Supplier {i+1}',
            mobile_number=f'91234567{i+1:02d}',
            address=f'Supplier Address {i+1}',
            city='Surat'
        )
        suppliers.append(supplier)

    # Add dummy materials
    materials = []
    for i in range(4):
        material = Material.objects.create(
            company=company,
            material_name=f'Material {i+1}',
            unit='meter'
        )
        materials.append(material)

    # Add dummy material inwards
    for i in range(4):
        MaterialInward.objects.create(
            company=company,
            material=materials[i],
            supplier=suppliers[i % 3],
            quantity=50 + i*10,
            received_date=date.today()
        )

    # Add dummy work types
    work_types = []
    for i in range(3):
        work_type = WorkType.objects.create(
            company=company,
            name=f'Work Type {i+1}'
        )
        work_types.append(work_type)

    # Add dummy work distributions
    for i in range(5):
        WorkDistribution.objects.create(
            company=company,
            worker=workers[i % 5],
            work_type=work_types[i % 3],
            lot_size=10 + i,
            distributed_date=date.today()
        )

    # Add dummy work received
    for i in range(5):
        WorkReceived.objects.create(
            company=company,
            distribution=WorkDistribution.objects.filter(company=company)[i],
            received_quantity=8 + i,
            received_date=date.today()
        )

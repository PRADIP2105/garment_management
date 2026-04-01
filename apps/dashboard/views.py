from datetime import date, timedelta
from collections import defaultdict
from django.core.paginator import Paginator
from django.db.models import Count, F, Sum
from django.db.models.functions import Coalesce
from rest_framework import permissions, views
from rest_framework.response import Response

from apps.materials.models import Material
from apps.materials.services import get_material_closing_stock
from apps.suppliers.models import Supplier
from apps.work.models import WorkDistribution, WorkReceived, WorkReturn, WorkType
from apps.workers.models import Worker


class DashboardSummaryView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not hasattr(request.user, "company") or request.user.company is None:
            return Response({
                "total_workers": 0, "total_suppliers": 0,
                "total_materials": 0, "total_work_types": 0,
                "pending_work_by_worker": [], "completed_work_quantity": 0,
                "today_completed_work": 0, "weekly_completed_work": 0,
                "monthly_completed_work": 0, "total_pending_work": 0,
                "total_distributed_work": 0, "low_stock_materials": [],
                "today_inward_quantity": 0, "today_outward_lot_size": 0,
                "weekly_inward_quantity": 0, "weekly_outward_lot_size": 0,
            })

        company = request.user.company

        # --- Date helpers (defined first) ---
        today = date.today()
        week_start = today - timedelta(days=6)
        month_start = today.replace(day=1)

        # --- Master counts ---
        total_workers = Worker.objects.filter(company=company).count()
        total_suppliers = Supplier.objects.filter(company=company).count()
        total_materials = Material.objects.filter(company=company).count()
        total_work_types = WorkType.objects.filter(company=company).count()

        # --- Pending work by worker ---
        distributions = WorkDistribution.objects.filter(company=company).annotate(
            total_completed=Coalesce(Sum('received_works__received_quantity'), 0)
        ).filter(total_completed__lt=F('lot_size')).select_related('worker')

        pending_dict = defaultdict(int)
        worker_map = {}
        for dist in distributions:
            pending = dist.lot_size - dist.total_completed
            pending_dict[dist.worker.name] += pending
            worker_map[dist.worker.name] = dist.worker.id

        pending_by_worker = [
            {'worker__id': worker_map[name], 'worker__name': name, 'total_pending': total}
            for name, total in pending_dict.items()
        ]

        paginator = Paginator(pending_by_worker, 5)
        try:
            page_number = int(request.GET.get('page', 1))
        except (ValueError, TypeError):
            page_number = 1
        pending_work_paginated = paginator.get_page(page_number)

        # --- Completed work stats ---
        completed_work = WorkReceived.objects.filter(company=company).aggregate(
            total=Sum("received_quantity")
        )["total"] or 0

        today_completed = WorkReceived.objects.filter(
            company=company, received_date=today
        ).aggregate(total=Sum("received_quantity"))["total"] or 0

        weekly_completed = WorkReceived.objects.filter(
            company=company, received_date__gte=week_start, received_date__lte=today
        ).aggregate(total=Sum("received_quantity"))["total"] or 0

        monthly_completed = WorkReceived.objects.filter(
            company=company, received_date__gte=month_start, received_date__lte=today
        ).aggregate(total=Sum("received_quantity"))["total"] or 0

        # --- Totals ---
        total_pending = sum(item['total_pending'] for item in pending_by_worker)

        total_distributed = WorkDistribution.objects.filter(company=company).aggregate(
            total=Sum("lot_size")
        )["total"] or 0

        # --- Inward / Outward ---
        today_inward = company.material_inwards.filter(
            received_date=today
        ).aggregate(total=Sum("quantity"))["total"] or 0

        today_outward = WorkDistribution.objects.filter(
            company=company, distributed_date=today
        ).aggregate(total=Sum("lot_size"))["total"] or 0

        weekly_inward = company.material_inwards.filter(
            received_date__gte=week_start, received_date__lte=today
        ).aggregate(total=Sum("quantity"))["total"] or 0

        weekly_outward = WorkDistribution.objects.filter(
            company=company, distributed_date__gte=week_start, distributed_date__lte=today
        ).aggregate(total=Sum("lot_size"))["total"] or 0

        # --- Low stock ---
        low_stock = []
        for material in Material.objects.filter(company=company):
            closing = get_material_closing_stock(material)
            if closing <= 10:
                low_stock.append({
                    "id": material.id,
                    "name": material.material_name,
                    "unit": material.unit,
                    "closing_stock": closing,
                })

        return Response({
            "total_workers": total_workers,
            "total_suppliers": total_suppliers,
            "total_materials": total_materials,
            "total_work_types": total_work_types,
            "pending_work_by_worker": list(pending_work_paginated.object_list),
            "pending_work_page": pending_work_paginated.number,
            "pending_work_total_pages": pending_work_paginated.paginator.num_pages,
            "completed_work_quantity": completed_work,
            "today_completed_work": today_completed,
            "weekly_completed_work": weekly_completed,
            "monthly_completed_work": monthly_completed,
            "total_pending_work": total_pending,
            "total_distributed_work": total_distributed,
            "low_stock_materials": low_stock,
            "today_inward_quantity": today_inward,
            "today_outward_lot_size": today_outward,
            "weekly_inward_quantity": weekly_inward,
            "weekly_outward_lot_size": weekly_outward,
        })

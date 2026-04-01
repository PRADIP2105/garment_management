from datetime import date, timedelta
from django.core.paginator import Paginator
from django.db.models import Count, Sum
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
            return Response(
                {
                    "total_workers": 0,
                    "total_suppliers": 0,
                    "total_materials": 0,
                    "total_work_types": 0,
                    "pending_work_by_worker": [],
                    "completed_work_quantity": 0,
                    "low_stock_materials": [],
                    "today_inward_quantity": 0,
                    "today_outward_lot_size": 0,
                    "weekly_inward_quantity": 0,
                    "weekly_outward_lot_size": 0,
                    "monthly_completed_work": 0,
                }
            )
        company = request.user.company

        total_workers = Worker.objects.filter(company=company).count()
        total_suppliers = Supplier.objects.filter(company=company).count()
        total_materials = Material.objects.filter(company=company).count()
        total_work_types = WorkType.objects.filter(company=company).count()

        # Pending work by worker = distributions where total received_quantity < lot_size
        from django.db.models import F
        from django.db.models.functions import Coalesce
        from collections import defaultdict
        distributions = WorkDistribution.objects.filter(company=company).annotate(
            total_completed=Coalesce(Sum('received_works__received_quantity'), 0)
        ).filter(total_completed__lt=F('lot_size')).select_related('worker')
        pending_dict = defaultdict(int)
        for dist in distributions:
            pending = dist.lot_size - dist.total_completed
            pending_dict[dist.worker.name] += pending
        pending_by_worker = []
        for name, total in pending_dict.items():
            worker = distributions.filter(worker__name=name).first()
            if worker:
                pending_by_worker.append({
                    'worker__id': worker.worker.id,
                    'worker__name': name,
                    'total_pending': total
                })

        # Paginate pending_by_worker with default 5 per page
        paginator = Paginator(pending_by_worker, 5)
        page_number = request.GET.get('page')
        if page_number:
            try:
                page_number = int(page_number)
            except ValueError:
                page_number = 1
        else:
            page_number = 1
        pending_work_paginated = paginator.get_page(page_number)

        completed_work = WorkReceived.objects.filter(company=company).aggregate(
            total_completed=Sum("received_quantity")
        )["total_completed"] or 0

        # Low-stock materials: closing_stock <= threshold (e.g. 10 units)
        low_stock = []
        for material in Material.objects.filter(company=company):
            closing = get_material_closing_stock(material)
            if closing <= 10:
                low_stock.append(
                    {
                        "id": material.id,
                        "name": material.material_name,
                        "unit": material.unit,
                        "closing_stock": closing,
                    }
                )

        # Today inward/outward
        from datetime import date

        today = date.today()
        today_inward = (
            company.material_inwards.filter(received_date=today)
            .aggregate(total_qty=Sum("quantity"))
            .get("total_qty")
            or 0
        )

        today_outward = (
            WorkDistribution.objects.filter(company=company, distributed_date=today)
            .aggregate(total_lot=Sum("lot_size"))
            .get("total_lot")
            or 0
        )

        # Weekly inward/outward (last 7 days)
        week_start = today - timedelta(days=6)
        weekly_inward = (
            company.material_inwards.filter(received_date__gte=week_start, received_date__lte=today)
            .aggregate(total_qty=Sum("quantity"))
            .get("total_qty")
            or 0
        )

        weekly_outward = (
            WorkDistribution.objects.filter(company=company, distributed_date__gte=week_start, distributed_date__lte=today)
            .aggregate(total_lot=Sum("lot_size"))
            .get("total_lot")
            or 0
        )

        # Monthly completed work (current month)
        month_start = today.replace(day=1)
        monthly_completed = WorkReceived.objects.filter(
            company=company, received_date__gte=month_start, received_date__lte=today
        ).aggregate(total_completed=Sum("received_quantity")).get("total_completed") or 0

        # Return JSON-serializable pending list (Paginator Page is not JSON-safe for mobile API)
        pending_items = list(pending_work_paginated.object_list)
        return Response(
            {
                "total_workers": total_workers,
                "total_suppliers": total_suppliers,
                "total_materials": total_materials,
                "total_work_types": total_work_types,
                "pending_work_by_worker": pending_items,
                "pending_work_page": pending_work_paginated.number,
                "pending_work_total_pages": pending_work_paginated.paginator.num_pages,
                "completed_work_quantity": completed_work,
                "low_stock_materials": low_stock,
                "today_inward_quantity": today_inward,
                "today_outward_lot_size": today_outward,
                "weekly_inward_quantity": weekly_inward,
                "weekly_outward_lot_size": weekly_outward,
                "monthly_completed_work": monthly_completed,
            }
        )


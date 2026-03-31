from decimal import Decimal
from typing import Iterable, List, TypedDict

from django.db import transaction

from apps.materials.models import Material
from apps.materials.services import ensure_sufficient_stock
from apps.work.models import (
    MaterialInward,
    WorkDistribution,
    WorkDistributionMaterial,
    WorkReturn,
    WorkReturnMaterial,
)


class IssuedMaterialInput(TypedDict):
    material: Material
    issued_quantity: Decimal


class ReturnedMaterialInput(TypedDict):
    material: Material
    returned_quantity: Decimal


@transaction.atomic
def create_material_inward(
    *, company, supplier, material: Material, quantity: Decimal, received_date, remarks: str = ""
) -> MaterialInward:
    """Register material inward. Stock is derived from all inwards/issues/returns."""
    inward = MaterialInward.objects.create(
        company=company,
        supplier=supplier,
        material=material,
        quantity=quantity,
        received_date=received_date,
        remarks=remarks,
    )
    return inward


@transaction.atomic
def distribute_work(
    *,
    company,
    worker,
    work_type,
    lot_size: int,
    distributed_date,
    expected_return_date,
    materials: Iterable[IssuedMaterialInput],
) -> WorkDistribution:
    """Create a work distribution and issue materials, validating stock."""
    # Validate stock for each material
    for item in materials:
        ensure_sufficient_stock(item["material"], item["issued_quantity"])

    distribution = WorkDistribution.objects.create(
        company=company,
        worker=worker,
        work_type=work_type,
        lot_size=lot_size,
        distributed_date=distributed_date,
        expected_return_date=expected_return_date,
    )

    issued_objs: List[WorkDistributionMaterial] = []
    for item in materials:
        issued_objs.append(
            WorkDistributionMaterial(
                distribution=distribution,
                material=item["material"],
                issued_quantity=item["issued_quantity"],
            )
        )
    WorkDistributionMaterial.objects.bulk_create(issued_objs)
    return distribution


@transaction.atomic
def register_work_return(
    *,
    company,
    distribution: WorkDistribution,
    completed_quantity: int,
    pending_quantity: int,
    wastage_quantity: Decimal | None,
    return_date,
    returned_materials: Iterable[ReturnedMaterialInput],
) -> WorkReturn:
    """Register a (possibly partial) work return and returned materials."""
    # Simple safety check: completed + pending should not exceed lot_size
    if completed_quantity + pending_quantity > distribution.lot_size:
        from django.utils.translation import gettext as _

        raise ValueError(
            _("Completed + pending quantity cannot exceed lot size (%(lot)s)")
            % {"lot": distribution.lot_size}
        )

    work_return = WorkReturn.objects.create(
        company=company,
        distribution=distribution,
        completed_quantity=completed_quantity,
        pending_quantity=pending_quantity,
        wastage_quantity=wastage_quantity,
        return_date=return_date,
    )

    returned_objs: List[WorkReturnMaterial] = []
    for item in returned_materials:
        returned_objs.append(
            WorkReturnMaterial(
                work_return=work_return,
                material=item["material"],
                returned_quantity=item["returned_quantity"],
            )
        )
    WorkReturnMaterial.objects.bulk_create(returned_objs)
    return work_return


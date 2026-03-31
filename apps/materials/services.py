from decimal import Decimal

from django.db.models import Sum

from apps.materials.models import Material
from apps.work.models import MaterialInward, WorkDistributionMaterial, WorkReturnMaterial


def get_material_closing_stock(material: Material) -> Decimal:
    """
    Compute closing stock using formula:
    opening + inward − issued + returned = closing

    We treat all inwards as +, all issued as −, all returns as +.
    """
    inward = (
        MaterialInward.objects.filter(material=material)
        .aggregate(total=Sum("quantity"))
        .get("total")
        or Decimal("0")
    )
    issued = (
        WorkDistributionMaterial.objects.filter(
            distribution__company=material.company, material=material
        )
        .aggregate(total=Sum("issued_quantity"))
        .get("total")
        or Decimal("0")
    )
    returned = (
        WorkReturnMaterial.objects.filter(
            work_return__company=material.company, material=material
        )
        .aggregate(total=Sum("returned_quantity"))
        .get("total")
        or Decimal("0")
    )
    return inward - issued + returned


def ensure_sufficient_stock(material: Material, required_qty: Decimal) -> None:
    """Raise ValueError if stock is not enough for the requested issue."""
    from django.utils.translation import gettext as _

    closing = get_material_closing_stock(material)
    if required_qty > closing:
        raise ValueError(
            _("Not enough stock for material %(name)s. Available: %(avail)s")
            % {"name": material.material_name, "avail": closing}
        )


from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.companies.models import Company
from apps.materials.models import Material
from apps.workers.models import Worker


class WorkType(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="work_types",
    )
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = _("Work Type")
        verbose_name_plural = _("Work Types")

    def __str__(self) -> str:
        return self.name


class MaterialInward(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="material_inwards",
    )
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.PROTECT,
        related_name="inwards",
    )
    material = models.ForeignKey(
        Material,
        on_delete=models.PROTECT,
        related_name="inwards",
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    received_date = models.DateField()
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class WorkDistribution(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="work_distributions",
    )
    worker = models.ForeignKey(Worker, on_delete=models.PROTECT, related_name="works")
    work_type = models.ForeignKey(
        WorkType, on_delete=models.PROTECT, related_name="distributions"
    )
    lot_size = models.PositiveIntegerField()
    distributed_date = models.DateField()
    expected_return_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.worker.name} - {self.work_type.name} - {self.lot_size} units"


class WorkDistributionMaterial(models.Model):
    distribution = models.ForeignKey(
        WorkDistribution,
        on_delete=models.CASCADE,
        related_name="issued_materials",
    )
    material = models.ForeignKey(Material, on_delete=models.PROTECT)
    issued_quantity = models.DecimalField(max_digits=12, decimal_places=2)


class WorkReturn(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="work_returns",
    )
    distribution = models.ForeignKey(
        WorkDistribution, on_delete=models.CASCADE, related_name="returns"
    )
    completed_quantity = models.PositiveIntegerField()
    pending_quantity = models.PositiveIntegerField()
    wastage_quantity = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    return_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)


class WorkReturnMaterial(models.Model):
    work_return = models.ForeignKey(
        WorkReturn,
        on_delete=models.CASCADE,
        related_name="returned_materials",
    )
    material = models.ForeignKey(Material, on_delete=models.PROTECT)
    returned_quantity = models.DecimalField(max_digits=12, decimal_places=2)


class WorkReceived(models.Model):
    class Status(models.TextChoices):
        RECEIVED = "received", _("Received")
        INSPECTED = "inspected", _("Inspected")
        APPROVED = "approved", _("Approved")
        REJECTED = "rejected", _("Rejected")

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="work_received",
    )
    distribution = models.ForeignKey(
        WorkDistribution, on_delete=models.CASCADE, related_name="received_works"
    )
    received_quantity = models.PositiveIntegerField()
    received_date = models.DateField()
    quality_rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)], null=True, blank=True
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.RECEIVED,
    )
    remarks = models.TextField(blank=True)
    inspected_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True
    )
    inspected_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class WorkReceivedMaterial(models.Model):
    work_received = models.ForeignKey(
        WorkReceived,
        on_delete=models.CASCADE,
        related_name="received_materials",
    )
    material = models.ForeignKey(Material, on_delete=models.PROTECT)
    received_quantity = models.DecimalField(max_digits=12, decimal_places=2)
    returned_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    wastage_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)


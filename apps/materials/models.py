from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.companies.models import Company


class Material(models.Model):
    class Unit(models.TextChoices):
        METER = "meter", _("Meter")
        ROLL = "roll", _("Roll")
        PIECE = "piece", _("Piece")
        KG = "kg", _("Kilogram")

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="materials",
    )
    material_name = models.CharField(max_length=255)
    unit = models.CharField(
        max_length=16,
        choices=Unit.choices,
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Material")
        verbose_name_plural = _("Materials")

    def __str__(self) -> str:
        return self.material_name


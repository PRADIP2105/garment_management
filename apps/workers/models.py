from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.companies.models import Company


class Worker(models.Model):
    class SkillType(models.TextChoices):
        STITCHING = "stitching", _("Stitching")
        BUTTON = "button", _("Button")
        COLLAR = "collar", _("Collar")
        COLOR = "color", _("Color")
        CUFF = "cuff", _("Shirt Cuff")
        WASHING = "washing", _("Washing")

    class MachineType(models.TextChoices):
        SIMPLE = "simple", _("Simple silai machine")
        MUNDA = "munda", _("Munda machine")
        OTHER = "other", _("Other")

    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        INACTIVE = "inactive", _("Inactive")

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="workers",
    )
    name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    skill_type = models.CharField(
        max_length=32, choices=SkillType.choices, default=SkillType.STITCHING
    )
    machine_type = models.CharField(
        max_length=32, choices=MachineType.choices, default=MachineType.SIMPLE
    )
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.ACTIVE
    )
    language_preference = models.CharField(
        max_length=2,
        choices=(("gu", "Gujarati"), ("en", "English")),
        default="gu",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Worker")
        verbose_name_plural = _("Workers")

    def __str__(self) -> str:
        return self.name


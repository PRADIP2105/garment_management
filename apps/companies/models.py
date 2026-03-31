from django.db import models
from django.utils.translation import gettext_lazy as _


class Company(models.Model):
    """Tenant. Every business record belongs to exactly one company."""

    name = models.CharField(max_length=255, verbose_name=_("Company Name"))
    city = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")

    def __str__(self) -> str:
        return self.name


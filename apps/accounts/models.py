from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.companies.models import Company


class User(AbstractUser):
    class Role(models.TextChoices):
        OWNER = "owner", _("Owner")
        STAFF = "staff", _("Staff")

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
    )
    role = models.CharField(
        max_length=16,
        choices=Role.choices,
        default=Role.OWNER,
    )
    language_preference = models.CharField(
        max_length=2,
        choices=(("gu", "Gujarati"), ("en", "English")),
        default="gu",
    )

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")


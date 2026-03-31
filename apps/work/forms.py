from django import forms
from django.utils.translation import gettext_lazy as _

from apps.materials.models import Material
from apps.work.models import WorkType, WorkDistribution, WorkReceived, WorkReceivedMaterial


class WorkTypeForm(forms.ModelForm):
    class Meta:
        model = WorkType
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2 text-sm', 'required': True})
        }

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.company:
            instance.company = self.company
        return super().save(commit)


class WorkDistributionForm(forms.ModelForm):
    class Meta:
        model = WorkDistribution
        fields = ["worker", "work_type", "lot_size", "distributed_date", "expected_return_date"]
        widgets = {
            "worker": forms.Select(attrs={'class': 'w-full border rounded px-3 py-2 text-sm', 'required': True}),
            "work_type": forms.Select(attrs={'class': 'w-full border rounded px-3 py-2 text-sm', 'required': True}),
            "lot_size": forms.NumberInput(attrs={'class': 'w-full border rounded px-3 py-2 text-sm', 'required': True}),
            "distributed_date": forms.DateInput(attrs={"type": "date", 'class': 'w-full border rounded px-3 py-2 text-sm', 'required': True}),
            "expected_return_date": forms.DateInput(attrs={"type": "date", 'class': 'w-full border rounded px-3 py-2 text-sm'}),
        }

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)
        if self.company:
            self.fields["worker"].queryset = self.company.workers.all()
            self.fields["work_type"].queryset = self.company.work_types.all()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.company:
            instance.company = self.company
        return super().save(commit)


class WorkReceivedForm(forms.ModelForm):
    class Meta:
        model = WorkReceived
        fields = ["distribution", "received_quantity", "received_date", "quality_rating", "status", "remarks"]
        widgets = {
            "distribution": forms.Select(attrs={'class': 'w-full border rounded px-3 py-2 text-sm'}),
            "received_quantity": forms.NumberInput(attrs={'class': 'w-full border rounded px-3 py-2 text-sm'}),
            "received_date": forms.DateInput(attrs={"type": "date", 'class': 'w-full border rounded px-3 py-2 text-sm'}),
            "quality_rating": forms.Select(attrs={'class': 'w-full border rounded px-3 py-2 text-sm'}),
            "status": forms.Select(attrs={'class': 'w-full border rounded px-3 py-2 text-sm'}),
            "remarks": forms.Textarea(attrs={'class': 'w-full border rounded px-3 py-2 text-sm', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)
        if self.company:
            self.fields["distribution"].queryset = self.company.work_distributions.all()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.company:
            instance.company = self.company
        return super().save(commit)


class WorkReceivedMaterialForm(forms.ModelForm):
    class Meta:
        model = WorkReceivedMaterial
        fields = ["material", "received_quantity", "returned_quantity", "wastage_quantity"]

    def __init__(self, *args, **kwargs):
        self.work_received = kwargs.pop("work_received", None)
        super().__init__(*args, **kwargs)
        if self.work_received:
            # Get materials from distribution
            distribution_materials = self.work_received.distribution.issued_materials.values_list("material", flat=True)
            self.fields["material"].queryset = Material.objects.filter(id__in=distribution_materials)
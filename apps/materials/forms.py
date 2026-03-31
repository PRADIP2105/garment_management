from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Material
from apps.work.models import MaterialInward


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = [
            'material_name',
            'unit',
            'description',
        ]
        widgets = {
            'material_name': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2 text-sm', 'required': True}),
            'unit': forms.Select(attrs={'class': 'w-full border rounded px-3 py-2 text-sm'}),
            'description': forms.Textarea(attrs={'class': 'w-full border rounded px-3 py-2 text-sm', 'rows': 3}),
        }
        labels = {
            'material_name': _('Material Name'),
            'unit': _('Unit'),
            'description': _('Description'),
        }

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.company:
            instance.company = self.company
        if commit:
            instance.save()
        return instance


class MaterialInwardForm(forms.ModelForm):
    class Meta:
        model = MaterialInward
        fields = [
            'material',
            'supplier',
            'quantity',
            'received_date',
            'remarks',
        ]
        widgets = {
            'material': forms.Select(attrs={'class': 'w-full border rounded px-3 py-2 text-sm', 'required': True}),
            'supplier': forms.Select(attrs={'class': 'w-full border rounded px-3 py-2 text-sm', 'required': True}),
            'quantity': forms.NumberInput(attrs={'class': 'w-full border rounded px-3 py-2 text-sm', 'required': True, 'step': '0.01'}),
            'received_date': forms.DateInput(attrs={'class': 'w-full border rounded px-3 py-2 text-sm', 'required': True, 'type': 'date'}),
            'remarks': forms.Textarea(attrs={'class': 'w-full border rounded px-3 py-2 text-sm', 'rows': 3}),
        }
        labels = {
            'material': _('Material'),
            'supplier': _('Supplier'),
            'quantity': _('Quantity'),
            'received_date': _('Received Date'),
            'remarks': _('Remarks'),
        }

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        if self.company:
            self.fields['material'].queryset = Material.objects.filter(company=self.company)
            from apps.suppliers.models import Supplier
            self.fields['supplier'].queryset = Supplier.objects.filter(company=self.company)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.company:
            instance.company = self.company
        if commit:
            instance.save()
        return instance

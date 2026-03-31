from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Supplier


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            'name',
            'mobile_number',
            'address',
            'city',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2 text-sm', 'required': True}),
            'mobile_number': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2 text-sm', 'required': True}),
            'address': forms.Textarea(attrs={'class': 'w-full border rounded px-3 py-2 text-sm', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2 text-sm'}),
        }
        labels = {
            'name': _('Name'),
            'mobile_number': _('Mobile Number'),
            'address': _('Address'),
            'city': _('City'),
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

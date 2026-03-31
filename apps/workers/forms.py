from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Worker


class WorkerForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = [
            'name',
            'mobile_number',
            'address',
            'city',
            'skill_type',
            'machine_type',
            'status',
            'language_preference',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2 text-sm', 'required': True}),
            'mobile_number': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2 text-sm', 'required': True}),
            'address': forms.Textarea(attrs={'class': 'w-full border rounded px-3 py-2 text-sm', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2 text-sm'}),
            'skill_type': forms.Select(attrs={'class': 'w-full border rounded px-3 py-2 text-sm'}),
            'machine_type': forms.Select(attrs={'class': 'w-full border rounded px-3 py-2 text-sm'}),
            'status': forms.Select(attrs={'class': 'w-full border rounded px-3 py-2 text-sm'}),
            'language_preference': forms.Select(attrs={'class': 'w-full border rounded px-3 py-2 text-sm'}),
        }
        labels = {
            'name': _('Name'),
            'mobile_number': _('Mobile Number'),
            'address': _('Address'),
            'city': _('City'),
            'skill_type': _('Skill Type'),
            'machine_type': _('Machine Type'),
            'status': _('Status'),
            'language_preference': _('Language Preference'),
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

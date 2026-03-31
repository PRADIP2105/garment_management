from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from apps.companies.models import Company

User = get_user_model()


class ForgotPasswordForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label=_("Username"),
        widget=forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2 text-sm', 'required': True})
    )
    new_password = forms.CharField(
        label=_("New Password"),
        widget=forms.PasswordInput(attrs={'class': 'w-full border rounded px-3 py-2 text-sm', 'required': True})
    )
    confirm_new_password = forms.CharField(
        label=_("Confirm New Password"),
        widget=forms.PasswordInput(attrs={'class': 'w-full border rounded px-3 py-2 text-sm', 'required': True})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError(_("Username does not exist"))
        return username

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')
        if new_password and confirm_new_password and new_password != confirm_new_password:
            raise forms.ValidationError(_("New passwords do not match"))
        return cleaned_data


class RegisterOwnerForm(forms.Form):
    company_name = forms.CharField(
        max_length=255,
        label=_("Company Name"),
        widget=forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2 text-sm', 'required': True})
    )
    company_city = forms.CharField(
        max_length=100,
        label=_("Company City"),
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2 text-sm'})
    )
    username = forms.CharField(
        max_length=150,
        label=_("Username"),
        widget=forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2 text-sm', 'required': True})
    )
    email = forms.EmailField(
        label=_("Email"),
        required=False,
        widget=forms.EmailInput(attrs={'class': 'w-full border rounded px-3 py-2 text-sm'})
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'w-full border rounded px-3 py-2 text-sm', 'required': True})
    )
    confirm_password = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(attrs={'class': 'w-full border rounded px-3 py-2 text-sm', 'required': True})
    )
    language_preference = forms.ChoiceField(
        choices=(("gu", _("Gujarati")), ("en", _("English"))),
        initial="gu",
        label=_("Language Preference"),
        widget=forms.Select(attrs={'class': 'w-full border rounded px-3 py-2 text-sm'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(_("Username already exists"))
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(_("Passwords do not match"))
        return cleaned_data

    def save(self):
        cleaned_data = self.cleaned_data
        company = Company.objects.create(
            name=cleaned_data['company_name'],
            city=cleaned_data.get('company_city', ''),
        )
        user = User.objects.create_user(
            username=cleaned_data['username'],
            email=cleaned_data.get('email', ''),
            password=cleaned_data['password'],
            company=company,
            role=User.Role.OWNER,
            language_preference=cleaned_data['language_preference'],
        )
        return user

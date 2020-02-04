from django import forms
from .models import Company


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['legal_name', 'name', 'legal_type', 'logo']
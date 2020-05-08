from django import forms


class BulkInterviewForm(forms.Form):
    file = forms.FileField(label='Informe o arquivo CSV', required=True)

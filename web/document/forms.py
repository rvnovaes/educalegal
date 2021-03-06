from django import forms


class BulkDocumentGenerationForm(forms.Form):
    source_file = forms.FileField(
        label="Selecione o arquivo csv",
        required=True,
        widget=forms.FileInput(attrs={"class": "custom-file-input",
                                      "id": "customFile",
                                      "accept": ".csv"}),
    )

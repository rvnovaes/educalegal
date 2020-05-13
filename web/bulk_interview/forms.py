from django import forms


class BulkInterviewForm(forms.Form):
    file = forms.FileField(
        label="Selecione o arquivo csv",
        required=True,
        widget=forms.FileInput(attrs={"class": "custom-file-input",
                                      "id": "customFile",
                                      "accept": ".csv"}),
    )

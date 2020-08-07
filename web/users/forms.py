from allauth.account.forms import ChangePasswordForm

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email")


class CustomUserChangePasswordForm(ChangePasswordForm):
    def clean(self):
        super(CustomUserChangePasswordForm, self).clean()

        if not self.cleaned_data.get("oldpassword") is None:
            if self.cleaned_data.get("oldpassword") == self.cleaned_data.get("password1"):
                raise forms.ValidationError("A nova senha deve ser diferente da anterior.")

        return self.cleaned_data

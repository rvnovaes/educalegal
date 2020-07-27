from allauth.account.views import PasswordChangeView

from django.urls import path

app_name = "users"


urlpatterns = [
    path("users/change-password", PasswordChangeView.as_view(), name="change-password"),
]

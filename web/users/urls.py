from django.urls import path

from .views import CustomUserPasswordChangeView

app_name = "users"

urlpatterns = [
    path("users/password-change/", CustomUserPasswordChangeView.as_view(), name="password-change"),
]

from allauth.account.views import PasswordChangeView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView

from .models import CustomUser
from tenant.mixins import TenantAwareViewMixin


class CustomUserPasswordChangeView(PasswordChangeView):
    template_name = 'account.'
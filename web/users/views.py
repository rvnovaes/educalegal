from allauth.account.views import PasswordChangeView


class CustomUserPasswordChangeView(PasswordChangeView):
    template_name = 'account/password_change.html'

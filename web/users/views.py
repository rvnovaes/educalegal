from allauth.account.views import PasswordChangeView

from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect

from .models import CustomUser


class CustomUserPasswordChangeView(PasswordChangeView):
    template_name = 'account/password_change.html'

    def form_valid(self, form):
        super(CustomUserPasswordChangeView, self).form_valid(form)

        if form.is_valid():
            custom_user = CustomUser.objects.get(id=form.user.id)
            custom_user.force_password_change = False
            custom_user.save(update_fields=['force_password_change'])

            # desloga o usuario
            logout(self.request)

            # redireciona para pagina de login
            return redirect(settings.ACCOUNT_LOGOUT_REDIRECT_URL)
        else:
            return super(PasswordChangeView, self).form_valid(form)


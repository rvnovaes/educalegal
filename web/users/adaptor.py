from allauth.account.adapter import DefaultAccountAdapter


class CustomUserAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        path = super(CustomUserAccountAdapter, self).get_login_redirect_url(request)
        current_user = request.user
        if current_user.force_password_change:
            path = 'users/users/change-password/'

        return path

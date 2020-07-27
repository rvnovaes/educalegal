from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import resolve_url, redirect


class MyAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        # path = super(MyAccountAdapter, self).get_login_redirect_url(request)
        current_user = request.user
        if current_user.force_password_change:
            path = 'doc/dochome/'
        elif current_user.user_type == 2:
            path='lab/labhome/'
        elif current_user.user_type == 3:
            path='recep/recephome/'
        elif current_user.user_type == 4:
            path='patient/patienthome/'
        elif current_user.user_type == 5:
            path='admini/adminhome/'
        else:
            return HttpResponse("Your Rango account is disabled.")
        return path
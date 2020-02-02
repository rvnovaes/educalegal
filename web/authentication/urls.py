from django.conf.urls import url
from .views import register, user_login

app_name = 'authentication'

# Be careful setting the name to just /login use userlogin instead!
urlpatterns=[
    url(r'^register/$', register, name='register'),
    url(r'^user_login/$', user_login, name='user_login'),
]
"""web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from allauth.account.views import LoginView

from .settings import SILK

urlpatterns = [
    path("admin/", admin.site.urls),
    url(r"^$", LoginView.as_view()),
    url(r"^account/", include("allauth.urls")),
    url(r"^billing/", include("billing.urls")),
    url(r"^interview/", include("interview.urls")),
    url(r"^document/", include("document.urls")),
    url(r"^school/", include("school.urls")),
    path("v1/", include("api.urls")),
    path("v1/api-auth/", include("rest_framework.urls")),
    re_path('djga/', include('google_analytics.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if SILK:
    urlpatterns.append(url(r"^silk/", include("silk.urls", namespace="silk")))

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
        # For django versions before 2.0:
        # url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

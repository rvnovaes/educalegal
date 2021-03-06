from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from allauth.account.views import LoginView

from django.conf import settings

schema_view = get_schema_view(
    openapi.Info(
        title="Educa Legal API",
        default_version="v1",
        description="Advocacia Virtual para Escolas",
        terms_of_service="https://www.educalegal.com.br",
        contact=openapi.Contact(email="sistemas@educalegal.com.br"),
        license=openapi.License(name="Proprietary. ALl rights reserved."),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,), )

urlpatterns = [
                  path("admin/", admin.site.urls),
                  url(r"^$", LoginView.as_view()),
                  url(r"^account/", include("allauth.urls")),
                  url(r"^billing/", include("billing.urls")),
                  url(r"^interview/", include("interview.urls")),
                  url(r"^document/", include("document.urls")),
                  url(r"^school/", include("school.urls")),
                  url(r"^users/", include("users.urls")),
                  path("v1/", include("api.urls")),
                  path("v2/", include("api.urls_v2"))

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.SILK:
    urlpatterns.append(url(r"^silk/", include("silk.urls", namespace="silk")))

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path("__debug__/", include(debug_toolbar.urls)),
                      # For django versions before 2.0:
                      # url(r'^__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns

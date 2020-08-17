from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt


from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from graphene_django.views import GraphQLView
from api.private_graphql import PrivateGraphQLView
from api.schema import schema
from graphql_jwt.decorators import jwt_cookie


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
    permission_classes=(permissions.AllowAny,),)

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
    path("v1/api-auth/", include("rest_framework.urls")),
    url(
        r"^v1/docs/swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    url(
        r"^v1/docs/swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    url(
        r"^v1/docs/redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
      path("v2/", include("api.urls_v2")),
      # Como existe v1/api-auth com o mesmo include, ele emite esse warning
      # URL namespace 'rest_framework' isn't unique. You may not be able to reverse all URLs in this namespace
      path("v2/api-auth/", include("rest_framework.urls")),
      url(
          r"^v2/docs/swagger(?P<format>\.json|\.yaml)$",
          schema_view.without_ui(cache_timeout=0),
          name="schema-json",
      ),
      url(
          r"^v2/docs/swagger/$",
          schema_view.with_ui("swagger", cache_timeout=0),
          name="schema-swagger-ui",
      ),
      url(
          r"^v2/docs/redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
      ),
      # url(r'^graphql$', csrf_exempt(jwt_cookie(GraphQLView.as_view(graphiql=True))))
      url(r'^graphql$', csrf_exempt(GraphQLView.as_view(graphiql=True)))
      # url(r'^graphql$', csrf_exempt(PrivateGraphQLView.as_view(graphiql=True, schema=schema)))

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.SILK:
#     urlpatterns.append(url(r"^silk/", include("silk.urls", namespace="silk")))

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
        # For django versions before 2.0:
        # url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

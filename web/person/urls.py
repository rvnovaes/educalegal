from django.urls import path
from .views import CompanyCreate, CompanyUpdate

app_name = 'person'


urlpatterns=[
    path('company/add/', CompanyCreate.as_view(), name='company-add'),
    path('company/<int:pk>/', CompanyUpdate.as_view(), name='company-update'),
    # path('company/<int:pk>/delete/', CompanyDelete.as_view(), name='company-delete'),
]
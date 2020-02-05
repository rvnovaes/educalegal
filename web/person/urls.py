from django.urls import path
from .views import CompanyCreate, CompanyUpdate, CompanyDetailView

app_name = 'person'


urlpatterns = [
    path('company/<int:pk>', CompanyDetailView.as_view(), name='company-detail'),
    path('company/add/', CompanyCreate.as_view(), name='company-add'),
    # path('company/<int:pk>/', CompanyUpdate.as_view(), name='company-update'),

    # path('company/<int:pk>/delete/', CompanyDelete.as_view(), name='company-delete'),
]
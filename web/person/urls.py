from django.urls import path
from .views import AddressCreateView, AddressDetailView, AddressDeleteView, AddressUpdateView
from .views import CompanyCreateView, CompanyDetailView, CompanyDeleteView, CompanyListView, CompanyUpdateView

app_name = 'person'


urlpatterns = [
    path('address/<int:pk>', AddressDetailView.as_view(), name='address-detail'),
    path('address/create/<int:company>', AddressCreateView.as_view(), name='address-create'),
    path('address/update/<int:pk>', AddressUpdateView.as_view(), name='address-update'),
    path('address/delete/<int:pk>', AddressDeleteView.as_view(), name='address-delete'),
    path('company/', CompanyListView.as_view(), name='company-list'),
    path('company/<int:pk>', CompanyDetailView.as_view(), name='company-detail'),
    path('company/create/', CompanyCreateView.as_view(), name='company-create'),
    path('company/update/<int:pk>', CompanyUpdateView.as_view(), name='company-update'),
    path('company/delete/<int:pk>', CompanyDeleteView.as_view(), name='company-delete'),
]
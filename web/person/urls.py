from django.urls import path
from .views import CompanyCreateView, CompanyUpdateView, CompanyDetailView, CompanyListView, CompanyDeleteView

app_name = 'person'


urlpatterns = [
    path('company/', CompanyListView.as_view(), name='company-list'),
    path('company/<int:pk>', CompanyDetailView.as_view(), name='company-detail'),
    path('company/create/', CompanyCreateView.as_view(), name='company-create'),
    path('company/update/<int:pk>/', CompanyUpdateView.as_view(), name='company-update'),
    path('company/delete/<int:pk>', CompanyDeleteView.as_view(), name='company-delete'),
]
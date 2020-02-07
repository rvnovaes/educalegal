from django.urls import path
from .views import SchoolCreateView, SchoolDetailView, SchoolDeleteView, SchoolListView, SchoolUpdateView

app_name = 'school'


urlpatterns = [
    path('school/', SchoolListView.as_view(), name='school-list'),
    path('school/<int:pk>', SchoolDetailView.as_view(), name='school-detail'),
    path('school/create/', SchoolCreateView.as_view(), name='school-create'),
    path('school/update/<int:pk>', SchoolUpdateView.as_view(), name='school-update'),
    path('school/delete/<int:pk>', SchoolDeleteView.as_view(), name='school-delete'),
]
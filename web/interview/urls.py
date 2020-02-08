from django.urls import path

from .views import InterviewListView

app_name = "interview"

urlpatterns = [path("interview", InterviewListView.as_view(), name="interview-list")]

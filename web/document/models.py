from django.db import models
from tenant.models import TenantAwareModel
from interview.models import Interview
from school.models import School


class Document(TenantAwareModel):
    name = models.CharField(max_length=512)
    created_date = models.DateTimeField(auto_now_add=True)
    altered_date = models.DateTimeField(auto_now=True)
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    status = models.CharField(max_length=256)
    signing_provider = models.CharField(max_length=256)
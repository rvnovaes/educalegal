from enum import Enum
from django.conf import settings
from django.db import models
from django.urls import reverse

from audit.models import Audit


class Interview(Audit):
    name = models.CharField(max_length=512, null=True)
    version = models.CharField(max_length=512, null=True)
    date_available = models.DateField(null=True)
    description = models.TextField(null=True)
    url = models.URLField(max_length=512)

    def __str__(self):
        return self.name

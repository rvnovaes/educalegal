from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django_tables2 import SingleTableView

from tenant.mixins import TenantAwareViewMixin

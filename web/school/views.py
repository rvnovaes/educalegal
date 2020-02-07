from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import School


class SchoolCreateView(LoginRequiredMixin, CreateView):
    model = School
    fields = '__all__'

    def get_form(self, form_class=None):
        form = super().get_form()
        # form.fields['tenant'].widget.attrs['readonly'] = 'readonly'
        # form.fields['tenant'].widget.attrs['disabled'] = 'disabled'
        return form


class SchoolDeleteView(LoginRequiredMixin, DeleteView):
    model = School
    context_object_name = 'school'
    success_url = reverse_lazy('school:company-list')


class SchoolDetailView(LoginRequiredMixin, DetailView):
    model = School
    context_object_name = 'school'


class SchoolListView(LoginRequiredMixin, ListView):
    model = School
    context_object_name = 'schools'


class SchoolUpdateView(LoginRequiredMixin, UpdateView):
    model = School
    fields = '__all__'


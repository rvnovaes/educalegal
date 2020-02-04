from django.shortcuts import render
from django.views import View
from django.views.generic import ListView
from .models import Company
from .forms import CompanyForm


class CompanyList(ListView):
    model = Company
    context_object_name = 'companies'

class CompanyFormView(View):
    form_class = CompanyForm
    initial = {'key': 'value'}
    template_name = 'company.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            return


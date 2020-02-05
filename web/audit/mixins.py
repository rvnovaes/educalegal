from django.utils import timezone

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse


class AuditFormMixin(LoginRequiredMixin):
    """
    Implementa a alteração da data e usuários para operação de update e new
    Lógica que verifica se a requisição é para Create ou Update.
    Se Create, o botão 'ativar' é desabilitar e valor padrão True
    Se Update, o botão 'ativar é habilitado para edição e o valor, carregado do banco
    """

    object_list_url = None

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw['request'] = self.request
        return kw

    def get_context_data(self, **kwargs):
        # kwargs.update({'form_attachment': AttachmentForm})
        return super().get_context_data(
            object_list_url=self.get_object_list_url(), **kwargs)

    def get_object_list_url(self):
        if self.object_list_url:
            return reverse(self.object_list_url)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if 'is_active' in form.fields and not form.instance.pk:
            form.data = form.data.copy()
            form.data['is_active'] = True
            form.fields['is_active'].initial = True
            form.fields['is_active'].required = False
            form.fields['is_active'].widget.attrs['disabled'] = 'disabled'
        return form

    def form_valid(self, form):
        instance = form.save(commit=False)

        if 'is_active' in form.fields and not instance.pk:
            instance.is_active = True

        if form.instance.id is None:
            form.instance.create_date = timezone.now()
            form.instance.create_user = self.request.user
        else:
            form.instance.alter_date = timezone.now()
            form.instance.alter_user = self.request.user
            form.save()

        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)
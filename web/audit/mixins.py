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

    def form_valid(self, form):
        if form.instance.id is None:
            form.instance.create_date = timezone.now()
            form.instance.create_user = self.request.user
        else:
            form.instance.alter_date = timezone.now()
            form.instance.alter_user = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)
class TenantAwareViewMixin:
    def get_queryset(self):
        return self.model.objects.filter(tenant_id=self.request.user.tenant_id)


class TenantAwareCreateUpdateMixin:
    def form_valid(self, form):
        form.instance.tenant_id = self.request.user.tenant_id
        return super().form_valid(form)

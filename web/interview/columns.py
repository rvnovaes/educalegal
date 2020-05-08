from django_tables2 import TemplateColumn


class InterviewCustomUrlColumn(TemplateColumn):
    def render(self, record, table, value, bound_column, **kwargs):
        if record.is_generic is True:
            user_auth_token_key = table.context.request.user.auth_token.key
            tid = table.context.request.user.tenant.id
            value = (
                record.base_url
                + "&tid="
                + str(tid)
                + "&ut="
                + user_auth_token_key
                + "&intid="
                + str(record.id)
                + "&new_session=1"
            )
        else:
            value = record.base_url + "&new_session=1"
        return super().render(record, table, value, bound_column, **kwargs)


class BulkInterviewColumn(TemplateColumn):
    def render(self, record, table, value, bound_column, **kwargs):
        if not record.use_bulk_interview:
            return ''
        return super().render(record, table, value, bound_column, **kwargs)

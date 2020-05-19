from django_tables2 import TemplateColumn

from .util import get_interview_link


class InterviewCustomUrlColumn(TemplateColumn):
    def render(self, record, table, value, bound_column, **kwargs):
        value = get_interview_link(table.context.request, record.pk)

        return super().render(record, table, value, bound_column, **kwargs)


class BulkInterviewColumn(TemplateColumn):
    def render(self, record, table, value, bound_column, **kwargs):
        if not record.use_bulk_interview:
            return ""
        return super().render(record, table, value, bound_column, **kwargs)

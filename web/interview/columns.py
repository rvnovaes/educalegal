from django_tables2 import TemplateColumn
from urllib.parse import urljoin


def build_interview_name(user_id, project_name, yaml_name):
    name = "docassemble.playground{user_id}{project_name}%3A{yaml_name}".format(
        user_id=user_id,
        project_name=project_name,
        yaml_name=yaml_name,
    )
    return name


def build_interview_path(user_id, project_name, yaml_name):
    path = "interview?i" + build_interview_name(user_id, project_name, yaml_name)
    return path


class InterviewCustomUrlColumn(TemplateColumn):
    def render(self, record, table, value, bound_column, **kwargs):

        # The base_url field overwrites interview server configuration.
        # It can be used to create arbitrary URLs for interviews
        if record.base_url:
            final_url = record.base_url
        else:
            # monta url da entrevista de acordo com parametros da configuracao do servidor escolhido
            isc = record.interview_server_config
            final_url = urljoin(
                isc.base_url,
                build_interview_path(isc.user_id, isc.project_name, record.yaml_name),
            )
        # adds access parameters to URL
        if record.is_generic is True:
            user_auth_token_key = table.context.request.user.auth_token.key
            tid = table.context.request.user.tenant.id
            final_url = (
                final_url
                + "&tid="
                + str(tid)
                + "&ut="
                + user_auth_token_key
                + "&intid="
                + str(record.id)
            )

        value = final_url + "&new_session=1"

        return super().render(record, table, value, bound_column, **kwargs)


class BulkInterviewColumn(TemplateColumn):
    def render(self, record, table, value, bound_column, **kwargs):
        if not record.use_bulk_interview:
            return ""
        return super().render(record, table, value, bound_column, **kwargs)

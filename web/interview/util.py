from urllib.parse import urljoin
from .models import Interview


def build_interview_full_name(user_id, project_name, yaml_name, name_type):

    if name_type == "interview_link":
        full_name = "docassemble.playground{user_id}{project_name}%3A{yaml_name}".format(
            user_id=user_id,
            project_name=project_name,
            yaml_name=yaml_name
        )
    if name_type == "interview_filename":
        full_name = "docassemble.playground{user_id}{project_name}:{yaml_name}".format(
            user_id=user_id,
            project_name=project_name,
            yaml_name=yaml_name
        )

    return full_name


def add_parameter_name_to_interview_full_name(user_id, project_name, yaml_name, name_type):
    parameter_and_full_name = "interview?i=" + build_interview_full_name(user_id, project_name, yaml_name, name_type)
    return parameter_and_full_name


def get_interview_link(request, interview_id):
    interview = Interview.objects.get(pk=interview_id)
    if interview.base_url:
        interview_final_url = interview.base_url
    else:
        # monta url da entrevista de acordo com parametros da configuracao do servidor escolhido
        isc = interview.interview_server_config
        interview_final_url = urljoin(
            isc.base_url,
            add_parameter_name_to_interview_full_name(isc.user_id, isc.project_name, interview.yaml_name, "interview_link"),
        )
    # adds access parameters to URL
    if interview.is_generic is True:
        user_auth_token_key = request.user.auth_token.key
        tid = request.user.tenant.id
        interview_final_url = (
                interview_final_url
                + "&tid="
                + str(tid)
                + "&ut="
                + user_auth_token_key
                + "&intid="
                + str(interview.id)
        )

    value = interview_final_url + "&new_session=1"

    return value


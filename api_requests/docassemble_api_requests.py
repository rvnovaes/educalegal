from util.docassemble_client import DocassembleClient

###### LOCALHOST ######
api_base_url = "http://localhost"
key = "0HlWqV1ZBxDHQ43aKmGEjLK96FyFNpox"
interview_name = 'docassemble.playground1Development:entrevista-debug-bulk.yml'
# interview_name = 'docassemble.playground1Development:favorite.yml'
# interview_name = 'docassemble.playground1Development:contrato-prestacao-servicos-educacionais.yml'

###### docs.educalegal ######
# api_base_url = "https://docs.educalegal.com.br"
# key = 'C3vAIRNnr3BnJpKCdqlsXSV2fLWPKI0K'
# interview_name = 'docassemble.playground1Production:entrevista-debug-bulk.yml'

###### generation.educalegal ######
# api_base_url = "https://generation.educalegal.com.br"
# key = "D8WUkJKxxW06qDS1UB5KlwyVXeUE1Mnx"
# interview_name = 'docassemble.playground1Production:entrevista-debug-bulk.yml'

username = "admin@admin.com"
user_password = "Silex2109"

# url_args = {
#     "tid": 2,
#     "ut": "48974bcc7b577ab3d6fed7c281d90324f4612810",
#     "intid": 2,
# }


if __name__ == "__main__":

    # payload = {"id": "5ed031f7bb0cb6720079cce8", "nomeAluno": "Plat\u00e3o de Atenas", "unidadeAluno": "Super Bacana", "selected_school": "Col\u00e9gio Bacana", "created": "2020-05-28T18:49:43.705000", "submit_to_esignature": "False", "url_args": {"tid": 2, "ut": "48974bcc7b577ab3d6fed7c281d90324f4612810", "intid": 2}}
    payload = {"id": "5ed969f56574ff41823a981b", "nomeAluno": "Platão de Atenas", "unidadeAluno": "Super Bacana", "selected_school": "Colégio Bacana", "created": "2020-06-04T18:39:01.690000", "submit_to_esignature": "False", "url_args": {"tid": 2, "ut": "48974bcc7b577ab3d6fed7c281d90324f4612810", "intid": 82}}



    dac = DocassembleClient(api_base_url, key)

    # se nao passar o parametro secret tem que colocar isso no yml da entrevista
    # mandatory: True
    # code: |
    #   multi_user = True
    secret, status_code = dac.secret_read(username, user_password)
    print(status_code)
    print(secret)

    interview_session, response_json, status_code = dac.start_interview(interview_name, secret)
    print(status_code)

    response, status_code = dac.interview_set_variables(
        secret,
        interview_name,
        payload,
        interview_session,
    )

    print(status_code)
    print(response)
    print(response.json())

    # print(dac.user_interviews_list())

    # print(dac.question_read(interview_name))

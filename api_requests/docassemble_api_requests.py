from web.bulk_interview.docassemble_client import DocassembleClient

###### LOCALHOST ######
# api_base_url = "http://localhost"
# key = "u0AFroAWHD1XF5hQSv0qdzKEaifI7imK"
# interview_name = 'docassemble.playground1Development:favorite.yml'
# interview_name = 'docassemble.playground1Development:contrato-prestacao-servicos-educacionais.yml'
###### docs.educalegal ######
# api_base_url = "https://docs.educalegal.com.br"
# key = 'OkHYL2fYJApLfjwTeM2gRUZfybEzbqy5'
# interview_name = 'docassemble.playground4Development:contrato-prestacao-servicos-educacionais.yml'

###### generation.educalegal ######
api_base_url = "https://generation.educalegal.com.br"
key = "D8WUkJKxxW06qDS1UB5KlwyVXeUE1Mnx"
interview_name = (
    "docassemble.playground1Production:contrato-prestacao-servicos-educacionais.yml"
)

username = "admin@admin.com"
user_password = "Silex2109"

# url_args = {
#     "tid": 2,
#     "ut": "48974bcc7b577ab3d6fed7c281d90324f4612810",
#     "intid": 2,
# }


if __name__ == "__main__":

    payload = {
        "i": "docassemble.playground1Production:contrato-prestacao-servicos-educacionais.yml",
        "session": "louAluXimJR47NwEpFaZFSQgKVvFiA4X",
        "secret": "127db081a79dead3",
        "variables": '{"id": "5ecef2617d90fa77d22ed357", "obs": "Desconto 10%", "rgAluno": "17.817.809-3", "cepAluno": "21381-040", "cpfAluno": "677.423.294-92", "desconto": "Sim", "parcelas": "\\u00e0 vista", "ruaAluno": "Travessa Jo\\u00e3o de Matos", "anoLetivo": 2020, "nomeAluno": "Gabriel Renato Kau\\u00ea Ara\\u00fajo", "numbAluno": "192", "serieAluno": "1\\u00aa s\\u00e9rie do ensino fundamental", "valorAnual": 5000.0, "bairroAluno": "Quintino Bocai\\u00fava", "cidadeAluno": "Rio de Janeiro", "compleAluno": "Apto 400", "estadoAluno": "RJ", "periodoAluno": "matutino", "unidadeAluno": "Super Bacana", "signature_date": "09/04/2020", "primeiraParcela": "\\u00e0 vista", "selected_school": "Col\\u00e9gio Bacana", "signature_local": "Belo Horizonte", "nacionalidadeAluno": "brasileiro(a)", "vencimentoParcelas": "dia 05 de cada m\\u00eas a partir de janeiro de 2020", "created": "2020-05-27T20:06:09.211000", "contratantes": {"elements": [{"nacionalidade": "brasileiro(a)", "estadocivil": "casado(a)", "prof": "engenheira", "cpf": "171.668.857-42", "rg": "12.531.478-4", "telefone": "(21) 2885-1328", "wtt": "(21) 98461-9677", "email": "rvnovaes@gmail.com", "cep": "21381-040", "rua": "Travessa Jo\\u00e3o de Matos", "numb": "192", "complemento": "2", "bairro": "Quintino Bocai\\u00fava", "cidade": "Rio de Janeiro", "estado": "RJ", "name": {"first": "Laura S\\u00f4nia J\\u00e9ssica Santos", "_class": "docassemble.base.util.IndividualName", "uses_parts": true, "instanceName": "contratantes[0].name"}, "instanceName": "contratantes[0]", "_class": "docassemble.base.util.Individual"}], "auto_gather": "False", "gathered": "True", "_class": "docassemble.base.core.DAList", "instanceName": "contratantes"}, "content_document": "contrato-prestacao-servicos-educacionais.docx", "valid_contratantes_table": "continue", "submit_to_esignature": "True", "url_args": {"tid": 2, "ut": "48974bcc7b577ab3d6fed7c281d90324f4612810", "intid": 2}}',
    }

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

    # print(dac.user_interviews_list())

    # print(dac.question_read(interview_name))

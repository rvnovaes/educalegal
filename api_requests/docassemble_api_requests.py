from web.bulk_interview.docassemble_client import DocassembleClient

###### LOCALHOST ######
api_base_url = "http://localhost"
key = "u0AFroAWHD1XF5hQSv0qdzKEaifI7imK"
# interview_name = 'docassemble.playground1Development:favorite.yml'
interview_name = 'docassemble.playground1Development:contrato-prestacao-servicos-educacionais.yml'
###### docs.educalegal ######
# api_base_url = "https://docs.educalegal.com.br"
# key = 'OkHYL2fYJApLfjwTeM2gRUZfybEzbqy5'
# interview_name = 'docassemble.playground4Development:contrato-prestacao-servicos-educacionais.yml'


if __name__ == "__main__":
    dac = DocassembleClient(api_base_url, key)

    # se nao passar o parametro secret tem que colocar isso no yml da entrevista
    # mandatory: True
    # code: |
    #   multi_user = True
    print(dac.interview_set_variables(interview_name, {'favorite_animal': 'dog'}))

    # print(dac.user_interviews_list())

    # print(dac.question_read(interview_name))

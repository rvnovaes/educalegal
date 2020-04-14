from docassemble_client import DocassembleClient

###### LOCALHOST ######
api_base_url = "http://localhost"
key = "NzTNZeZr7UsyLIj1XtYAz0NfiZO3rtoD"


if __name__ == "__main__":
    dac = DocassembleClient(api_base_url, key)

    # se nao passar o parametro secret tem que colocar isso no yml da entrevista
    # mandatory: True
    # code: |
    #   multi_user = True
    print(dac.interview_set_variables('docassemble.playground1Development:favorite.yml', {'favorite_animal': 'dog'}))

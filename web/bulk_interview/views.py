import pandas as pd

from docassemble_client import DocassembleClient


###### LOCALHOST ######
api_base_url = "http://localhost"
key = "u0AFroAWHD1XF5hQSv0qdzKEaifI7imK"
# filename = "favorite.csv"
# interview_name = 'docassemble.playground1Development:favorite.yml'

filename = "contrato-prestacao-servicos-educacionais.csv"
interview_name = 'docassemble.playground1Development:contrato-prestacao-servicos-educacionais.yml'

# https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html?highlight=orient
# orient : Series - default is index
# allowed values are {split, records, index}
# records - list like [{column -> value}, … , {column -> value}]
variables_list = pd.read_csv(filename).to_dict(orient='records')
variables_list = pd.read_csv(filename, usecols=["content_document", "selected_school", "nomeAluno",
                                                "nacionalidadeAluno", "cpfAluno", "rgAluno", "cepAluno", "ruaAluno",
                                                "numbAluno", "compleAluno", "bairroAluno", "cidadeAluno", "estadoAluno",
                                                "serieAluno", "periodoAluno", "anoLetivo", "valorAnual", "desconto",
                                                "obs", "parcelas", "primeiraParcela", "vencimentoParcelas",
                                                "signature_local", "signature_date", "city", "state",
                                                "valid_contratantes_table",
                                                "submit_to_esignature"]).to_dict(orient='records')

contratantes_list = pd.read_csv(filename, usecols=["name.first", "nacionalidade", "estadocivil", "prof", "cpf", "rg",
                                                   "telefone", "wtt", "email", "cep", "rua", "numb", "complemento",
                                                   "bairro", "cidade", "estado", "auto_gather", "gathered", "_class",
                                                   "instanceName"]).to_dict(orient='records')

# cria cliente da api do docassemble
dac = DocassembleClient(api_base_url, key)

i = 0
for item in contratantes_list:
    variables_list[i]['contratantes'] = item
    i += 1

# gera entrevista para a lista de variáveis
for variables in variables_list:
    print(dac.interview_set_variables(interview_name, variables))

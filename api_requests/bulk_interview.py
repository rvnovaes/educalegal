import pandas as pd

from docassemble_client import DocassembleClient

###### LOCALHOST ######
api_base_url = "http://localhost"
key = "u0AFroAWHD1XF5hQSv0qdzKEaifI7imK"
# filename = "favorite.csv"
# interview_name = 'docassemble.playground1Development:favorite.yml'

filename = "/home/iasmini/Área de Trabalho/contrato-prestacao-servicos-educacionais.csv"
interview_name = 'docassemble.playground1Development:contrato-prestacao-servicos-educacionais.yml'

# https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html?highlight=orient
# orient : Series - default is index
# allowed values are {split, records, index}
# records - list like [{column -> value}, … , {column -> value}]
variables_list = pd.read_csv(filename).to_dict(orient='records')

# cria cliente da api do docassemble
dac = DocassembleClient(api_base_url, key)

# gera entrevista para a lista de variáveis
for variables in variables_list:
    print(dac.interview_set_variables(interview_name, variables))

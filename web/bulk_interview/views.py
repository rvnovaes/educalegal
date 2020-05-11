import pandas as pd

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render

from .docassemble_client import DocassembleClient
from .forms import BulkInterviewForm

from interview.models import Interview, ServerConfig


def bulk_interview(request, interview_id):
    row_errors = []
    if request.method == 'POST':
        form = BulkInterviewForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']

            # salva o arquivo inserido pelo usuario na pasta media
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)

            # pega caminho do arquivo para ler o csv com pandas
            absolute_file_path = fs.base_location + '/' + filename

            interview = Interview.objects.get(pk=interview_id)
            # gera dicionario de variaveis da entrevista de acordo com o layout da entrevista
            variables_list = _dict_from_csv(absolute_file_path, interview.document_type.id)

            # lê configurações do servidor da plataforma de geração de documentos (Docassemble)
            server_config = ServerConfig.objects.get(interviews=interview_id)
            base_url = server_config.base_url
            user_key = server_config.user_key
            user_id = server_config.user_id
            username = server_config.username
            user_password = server_config.user_password
            project_name = server_config.project_name

            # cria cliente da api do docassemble
            dac = DocassembleClient(base_url, user_key)

            # monta nome da entrevista de acordo com especificações do docassemble
            interview_name = "docassemble.playground{user_id}{project_name}:{interview_name}".format(
                user_id=user_id, project_name=project_name, interview_name=interview.yaml_name)

            # passa argumentos da url para a entrevista
            url_args = {'tid': request.user.tenant.pk,
                        'ut': request.user.auth_token.key,
                        'intid': interview_id}

            row = 1
            try:
                secret = dac.secret_read(username, user_password)
                # gera entrevista para a lista de variáveis
                for variables in variables_list:
                    variables['url_args'] = url_args
                    response, status_code = dac.interview_set_variables(secret, interview_name, variables)
                    if status_code != 200:
                        row_errors.append([row, response])
                    row += 1
                if row_errors:
                    raise Exception(list(set(row_errors)))
                else:
                    messages.success(request, 'Entrevistas geradas com sucesso!')
            except:
                if row_errors:
                    message = 'Não foi possível gerar as entrevistas! ' \
                              'Verifique as mensagens de erro geradas de acordo com a linha do arquivo.'
                else:
                    message = 'Não foi possível gerar as entrevistas!'
                messages.error(request, message)

            # apaga o arquivo importado da pasta media
            fs.delete(filename)
    else:
        form = BulkInterviewForm()

    return render(request, 'bulk_interview/bulk_interview.html', {'form': form,
                                                                  'interview_id': interview_id,
                                                                  'row_errors': row_errors})


def _dict_from_csv(absolute_file_path, document_type_id):
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html?highlight=orient
    # orient : Series - default is index
    # allowed values are {split, records, index}
    # records - list like [{column -> value}, … , {column -> value}]
    # variables_list = pd.read_csv(filename).to_dict(orient='records')
    if document_type_id == 2:
        variables_list = pd.read_csv(
            absolute_file_path,
            usecols=["selected_school", "unidadeAluno", "nomeAluno", "nacionalidadeAluno", "cpfAluno",
                     "rgAluno", "cepAluno", "ruaAluno", "numbAluno", "compleAluno", "bairroAluno", "cidadeAluno",
                     "estadoAluno", "serieAluno", "periodoAluno", "anoLetivo", "valorAnual", "desconto", "obs",
                     "parcelas", "primeiraParcela", "vencimentoParcelas", "signature_local", "signature_date",
                     "city", "state", "valid_contratantes_table", "submit_to_esignature"]).to_dict(orient='records')

        contratantes_list = pd.read_csv(
            absolute_file_path,
            usecols=["name.first", "nacionalidade", "estadocivil", "prof", "cpf", "rg", "telefone", "wtt", "email",
                     "cep", "rua", "numb", "complemento", "bairro", "cidade", "estado"]).to_dict(orient='records')

        # insere na variables a lista de contratantes
        i = 0
        for item in contratantes_list:
            variables_list[i]['content_document'] = 'contrato-prestacao-servicos-educacionais.docx'
            variables_list[i]['contratantes'] = item
            variables_list[i]['contratantes']['auto_gather'] = 'False'
            variables_list[i]['contratantes']['gathered'] = 'True'
            variables_list[i]['contratantes']['_class'] = 'docassemble.base.core.DAList'
            variables_list[i]['contratantes']['instanceName'] = 'contratantes'
            i += 1

    return variables_list

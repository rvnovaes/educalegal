import requests
import configparser
import PySimpleGUI as sg
from os import listdir
from os.path import isfile, join


config = configparser.ConfigParser()
config.read("upload_interviews_config")


def da_user_list(api_key, server_url):
    payload = {
        "key": api_key,
    }
    try:
        r = requests.get(server_url, params=payload)

    except Exception as e:
        raise ConnectionError("Não foi possível conectar-se com o Docassemble" + str(e))

    if r.status_code == 403:
        raise PermissionError("Acesso Negado. Verifique a chake em upload_interviews_config")

    return r.json()


def post_to_docassemble(
    api_key, server_url, file_path, destination, user_id, project="Development"
):
    payload = {
        "key": api_key,
        "user_id": user_id,
        "folder": destination,
        "project": project,
    }

    file_object = open(file_path, mode="rb")

    server_url = server_url + "/api/playground"

    r = requests.post(server_url, data=payload, files={"0": file_object})

    if r.status_code != 204:
        return r.text
    else:
        return "Success posting " + file_path

destination_options = [
    "http://localhost",
    "https://doctest.educalegal.com.br",
    "https://generation.educalegal.com.br",
]

user_options = ["Selecione primeiro um destino..."]

project_options = ["Development", "Autotest", "Production"]

layout = [
    [sg.Text("Servidor Destino"), sg.InputOptionMenu(destination_options, key="destination_options"), sg.Button("Ok", key="destination_ok")],
    [sg.Text("Playground Destino"), sg.InputOptionMenu(user_options, key="user_options")],
    [sg.Text("Projeto Destino"), sg.InputOptionMenu(project_options, key="project_options")],
    [sg.Button("Ok", key="final_ok"), sg.Button("Sair")],
]

window = sg.Window("Selecione o Destino", layout)

selected_destination = None
selected_user_id = None
selected_project = None

configuration_summary_message = ""
selected_items_message = ""

questions = sorted([f for f in listdir(config["sources"]["questions"]) if isfile(join(config["sources"]["questions"], f))])
templates = sorted([f for f in listdir(config["sources"]["templates"]) if isfile(join(config["sources"]["templates"], f))])
modules = sorted([f for f in listdir(config["sources"]["modules"]) if isfile(join(config["sources"]["modules"], f))])
static = sorted([f for f in listdir(config["sources"]["static"]) if isfile(join(config["sources"]["static"], f))])
selected_questions = []
selected_modules = []
selected_templates =[]
selected_static =[]

step2 = False
step3 = False

while True:
    event, values = window.read()
    print(event, values)
    if event == sg.WIN_CLOSED or event == "Sair":
        break
    if event == "destination_ok":
        if values["destination_options"] == "http://localhost":
            api_key = config["keys"]["LOCALHOST"]
        elif values["destination_options"] == "https://doctest.educalegal.com.br":
            api_key = config["keys"]["DOCTEST"]
        elif values["destination_options"] == "https://generation.educalegal.com.br":
            api_key = config["keys"]["PRODUCTION"]

        selected_destination = values["destination_options"]
        try:
            users = da_user_list(api_key, selected_destination + "/api/user_list")
            user_options_dict = dict()
            user_emails = list()

            # na versao 1.1.44 do DA houve alteracao nesse endpoint (/api/user_list)
            # https://docassemble.org/docs/changelog.html
            if 'items' in users:
                for u in users['items']:
                    id = u["id"]
                    email = u["email"]
                    user_options_dict[email] = id
                    user_emails.append(email)
            else:
                for u in users:
                    id = u["id"]
                    email = u["email"]
                    user_options_dict[email] = id
                    user_emails.append(email)
            window["user_options"].update(values=user_emails)

        except Exception as e:
            sg.Print(e)

    if event == "final_ok":
        selected_destination = values["destination_options"]
        selected_user_id = user_options_dict[values["user_options"]]
        selected_project = values["project_options"]
        configuration_summary_message = """
        Destino Selecionado: {selected_destination}
        Playground Selecionado: {selected_user_id}
        Projeto Selecionado: {selected_project}
        """.format(selected_destination=selected_destination, selected_user_id=values["user_options"], selected_project=selected_project)
        step2 = True
        window.close()

# Step 2
layout = [
    [sg.Text("Selecione os items a serem enviados:")],
    [sg.Text("Todos: "), sg.Checkbox("Questions", key="questions_checkbox"), sg.Checkbox("Templates", key="templates_checkbox"), sg.Checkbox("Modules", key="modules_checkbox"), sg.Checkbox("Static", key="static_checkbox")],
    [
        sg.Listbox(questions, select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED, size=(70, 50), key="questions_listbox"),
        sg.Listbox(templates, select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED, size=(70, 50), key="templates_listbox"),
        sg.Listbox(modules, select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED, size=(70, 50), key="modules_listbox"),
        sg.Listbox(static, select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED, size=(70, 50), key="static_listbox")
    ],
    [sg.Button("Ok", key="final_ok"), sg.Button("Cancel")],
]

window = sg.Window("Selecione os items", layout)

while step2:
    event, values = window.read()
    print(event, values)
    if event == sg.WIN_CLOSED or event == "Cancel":
        break
    if event == "final_ok":
        if window["questions_checkbox"].Get():
            selected_questions = window["questions_listbox"].GetListValues()
        else:
            selected_questions = window["questions_listbox"].get()

        if window["templates_checkbox"].Get():
            selected_templates = window["templates_listbox"].GetListValues()
        else:
            selected_templates = window["templates_listbox"].get()

        if window["modules_checkbox"].Get():
            selected_modules = window["modules_listbox"].GetListValues()
        else:
            selected_modules = window["modules_listbox"].get()

        if window["static_checkbox"].Get():
            selected_static = window["static_listbox"].GetListValues()
        else:
            selected_static = window["static_listbox"].get()

        selected_items_message = """
        Foram selecionados os seguintes items:\n
        Questions: {selected_questions}\n
        Templates: {selected_templates}\n
        Modules: {selected_modules}\n
        Static: {selected_static}  
        """.format(selected_questions=selected_questions, selected_templates=selected_templates, selected_modules=selected_modules, selected_static=selected_static)
        step3 = True
        window.close()

# Window 3

layout = [
    [sg.Text("Confirmação")],
    [sg.Multiline(configuration_summary_message, size=(210, 5))],
    [sg.Multiline(selected_items_message, size=(210, 25))],
    [sg.Multiline("", size=(210, 25), key="output")],
    [sg.Button("Enviar", key="final_ok", button_color=("white", "red")), sg.Button("Sair")],
]

window = sg.Window("Selecione os items", layout)

while step3:
    event, values = window.read()
    print(event, values)
    if event == sg.WIN_CLOSED or event == "Sair":
        break
    if event == "final_ok":
        try:
            if len(selected_questions) > 0:
                for question in selected_questions:
                    message = post_to_docassemble(api_key, selected_destination, join(config["sources"]["questions"], question), "questions", selected_user_id, selected_project)
                    window["output"].print(message)
            if len(selected_templates) > 0:
                for template in selected_templates:
                    message = post_to_docassemble(api_key, selected_destination, join(config["sources"]["templates"], template), "templates", selected_user_id, selected_project)
                    window["output"].print(message)
            if len(selected_modules) > 0:
                for module in selected_modules:
                    message = post_to_docassemble(api_key, selected_destination, join(config["sources"]["modules"], module), "modules", selected_user_id, selected_project)
                    window["output"].print(message)
            if len(selected_static) > 0:
                for static in selected_static:
                    message = post_to_docassemble(api_key, selected_destination, join(config["sources"]["static"], static), "static", selected_user_id, selected_project)
                    window["output"].print(message)
        except Exception as e:
            window["output"].print(e)

from os import listdir
from os.path import isfile, join

import requests


def post_to_docassemble(api_key, server_url, path, destination, user_id, project="Development"):
    payload = {"key": api_key, "user_id": user_id, "folder": destination, "project": project}

    files = dict()
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    for i, file in enumerate(onlyfiles):
        file_object = open(join(path, file), mode="rb")
        files[str(i)] = file_object

    r = requests.post(server_url, data=payload, files=files)

    if r.status_code != 204:
        print(r.text)
    else:
        print("Success posting " + destination)


if __name__ == "__main__":
    destination = input(
        """
        Para onde você deseja enviar?:
            1 - localhost - Development - Seu próprio playground na máquina local
            2 - teste.educalegal.com.br - Development - Playground do seu usuário no servidor de teste
            3 - teste.educalegal.com.br - Autotest - Playground do admin@admin.com
            4 - docs.educalegal.com.br  - Autotest - Playground do admin@admin.com
            5 - docs.educalegal.com.br  - Production - Playground do admin@admin.com
    """
    )

    if destination == "1":
        # 1 - localhost - Development - Seu próprio playground na máquina local
        server_url = "http://localhost/api/playground"
        project = "Development"
        user_id = 1
        print(
            """
        Você optou por enviar para seu playground na máquina local (localhost).
        """
        )
        user = input(
            """
            Digite seu usuário:
            1 - Iasmini
            2 - Isabela
            3 - Luis
            4 - Roberto
        """)
        if user == "1":
            # iasmini
            api_key = "CREI52r9wGtHRKTnTwoMw1lIwbfNA1tj"
        elif user == "2":
            # isabela
            api_key = "YukwjUC4SWUZ0BZrIiLmY2UOQfYKFo4h"
        elif user == "3":
            # luis paim
            api_key = "Ti33Sv5KMNQCV9MDlwxY4RnBIbUWnAVD"
        elif user == "4":
            # roberto
            api_key = "CJrCAwt5Aul45RkOXeS2z9ZwISc6JkOf"

    if destination == "2":
        # 2 - teste.educalegal.com.br - Development - Playground do seu usuário no servidor de teste
        server_url = "https://teste.educalegal.com.br/api/playground"
        project = "Development"
        print(
            """
        Você optou por enviar para seu próprio playground no ambiente de teste.
        """
        )
        user = input(
            """
            Digite seu usuário:
            1 - Iasmini
            2 - Isabela
            3 - Luis
            4 - Roberto
        """)
        if user == "1":
            # iasmini
            user_id = 4
            api_key = ""
        elif user == "2":
            # isabela
            user_id = 9
            api_key = ""
        elif user == "3":
            # luis paim
            user_id = 5
            api_key = "KSgYY16NeSWWtdgjhBPFdfuXBVEfyome"
        elif user == "4":
            # roberto
            user_id = 14
            api_key = "MNBexgT3cCDvmqXeKtUpp5YHMwfXWZxZ"
    if destination == "3":
        # teste.educalegal.com.br - Autotest - Playground do admin@admin.com
        server_url = "https://teste.educalegal.com.br/api/playground"
        project = "Autotest"
        user_id = 1
        api_key = "O2wG8BRr70yZnanUJmysCNLQ2nWG44cL"
    if destination == "4":
        # docs.educalegal.com.br - Autotest - Playground do admin@admin.com
        server_url = "https://docs.educalegal.com.br/api/playground"
        project = "Autotest"
        user_id = 1
        api_key = "C3vAIRNnr3BnJpKCdqlsXSV2fLWPKI0K"
    if destination == "5":
        # docs.educalegal.com.br - Production - Playground do admin@admin.com
        server_url = "https://docs.educalegal.com.br/api/playground"
        project = "Production"
        user_id = 1
        api_key = "C3vAIRNnr3BnJpKCdqlsXSV2fLWPKI0K"



    brcomeducalegal_questions = (
        "/opt/docassemble-brcomeducalegal/docassemble/brcomeducalegal/data/questions"
    )
    brcomeducalegal_templates = (
        "/opt/docassemble-brcomeducalegal/docassemble/brcomeducalegal/data/templates"
    )
    brcomeducalegal_modules = (
        "/opt/docassemble-brcomeducalegal/docassemble/brcomeducalegal/data/"
    )

    post_to_docassemble(
        api_key, server_url, brcomeducalegal_questions, "questions", user_id, project
    )
    post_to_docassemble(
        api_key, server_url, brcomeducalegal_templates, "templates", user_id, project
    )
    post_to_docassemble(
        api_key, server_url, brcomeducalegal_modules, "modules", user_id, project
    )

from os import listdir
from os.path import isfile, join

import requests
###### LOCALHOST ######
# iasmini
# api_key = "CREI52r9wGtHRKTnTwoMw1lIwbfNA1tj"
# luis paim
# api_key = "Ti33Sv5KMNQCV9MDlwxY4RnBIbUWnAVD"
# roberto
# api_key = "CJrCAwt5Aul45RkOXeS2z9ZwISc6JkOf"
# isabela
# api_key = "YukwjUC4SWUZ0BZrIiLmY2UOQfYKFo4h"
server_url = "http://localhost/api/playground"
###### teste.educalegal.com.br #####
# usuario: teste@educalegal.com
# api_key = "O2wG8BRr70yZnanUJmysCNLQ2nWG44cL"
# server_url = "https://teste.educalegal.com.br/api/playground"
##### docs.educalegal.com.br #####
# api_key = "C3vAIRNnr3BnJpKCdqlsXSV2fLWPKI0K"
# server_url = "https://docs.educalegal.com.br/api/playground"

project = "Development"


def post_to_docassemble(api_key, server_url, path, destination, project="default"):
    payload = {"key": api_key, "user_id": 1, "folder": destination, "project": project}

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
    brcomeducalegal_questions = (
        "/opt/docassemble-brcomeducalegal/docassemble/brcomeducalegal/data/questions"
    )
    brcomeducalegal_templates = (
        "/opt/docassemble-brcomeducalegal/docassemble/brcomeducalegal/data/templates"
    )
    brcomeducalegal_modules = "/opt/docassemble-brcomeducalegal/docassemble/brcomeducalegal/data/"

    post_to_docassemble(api_key, server_url, brcomeducalegal_questions, "questions", project)
    post_to_docassemble(api_key, server_url, brcomeducalegal_templates, "templates", project)
    post_to_docassemble(api_key, server_url, brcomeducalegal_modules, "modules", project)

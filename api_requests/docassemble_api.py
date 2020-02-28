from os import listdir
from os.path import isfile, join

import requests

api_key_localhost = "GHHnjFWG9H4KKYYkMgd3yE0yPlNYMQ18"
server_url_localhost = "http://localhost/api/playground"
api_key_docs_silex = "O2wG8BRr70yZnanUJmysCNLQ2nWG44cL"
server_url_docs_silex = "https://docs.silexsistemas.com.br/api/playground"
api_key_docs_educalegal = "C3vAIRNnr3BnJpKCdqlsXSV2fLWPKI0K"
server_url_docs_educalegal = "https://docs.educalegal.com.br/api/playground"
project_educalegal = "Development"


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
    elements_questions = "/opt/docassemble-elements/docassemble/elements/data/questions"
    elements_modules = "/opt/docassemble-elements/docassemble/elements/data/"

    # post_to_docassemble(api_key_localhost, server_url_localhost, brcomeducalegal_questions, "questions")
    # post_to_docassemble(api_key_localhost, server_url_localhost, brcomeducalegal_templates, "templates")
    # post_to_docassemble(api_key_localhost, server_url_localhost, elements_questions, "questions")
    # post_to_docassemble(api_key_localhost, server_url_localhost, elements_modules, "modules")


    post_to_docassemble(api_key_docs_silex, server_url_docs_silex, brcomeducalegal_questions, "questions")
    # post_to_docassemble(api_key_docs_silex, server_url_docs_silex, brcomeducalegal_templates, "templates")
    post_to_docassemble(api_key_docs_silex, server_url_docs_silex, elements_questions, "questions")
    post_to_docassemble(api_key_docs_silex, server_url_docs_silex, elements_modules, "modules")

    # post_to_docassemble(api_key_docs_educalegal, server_url_docs_educalegal, brcomeducalegal_questions, "questions", project_educalegal)
    # post_to_docassemble(api_key_docs_educalegal, server_url_docs_educalegal, brcomeducalegal_templates, "templates", project_educalegal)
    # post_to_docassemble(api_key_docs_educalegal, server_url_docs_educalegal, elements_questions, "questions", project_educalegal)
    # post_to_docassemble(api_key_docs_educalegal, server_url_docs_educalegal, elements_modules, "modules", project_educalegal)

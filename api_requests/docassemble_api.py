from os import listdir
from os.path import isfile, join

import requests

api_key = "LYZzSlkJREJgkt83f1aZwkq5PknAVBdH"


def post_to_docassemble(path, destination):
    payload = {"key": api_key, "user_id": 1, "folder": destination}

    files = dict()
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    for i, file in enumerate(onlyfiles):
        file_object = open(join(path, file), mode="rb")
        files[str(i)] = file_object

    r = requests.post("http://localhost/api/playground", data=payload, files=files)

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
    post_to_docassemble(brcomeducalegal_questions, "questions")
    post_to_docassemble(brcomeducalegal_templates, "templates")
    post_to_docassemble(elements_questions, "questions")
    post_to_docassemble(elements_modules, "modules")

import requests


token = "311648a5e598e7d60b3e7f982909a34a0214f1f4"
token_string = "Token " + token
headers = {"Authorization": token_string}


def get_docusign_config_from_educa_legal(tid):
    esignature_url = "http://localhost:8000/v1/tenants/{tid}/esignature/".format(
        tid=tid
    )
    response = requests.get(esignature_url, headers=headers).json()
    return response


if __name__ == "__main__":
    response = get_docusign_config_from_educa_legal(2)
    print(response)

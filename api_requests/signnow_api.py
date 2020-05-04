import requests
import json

def generate_access_token(API_Key):
    url = "https://api-eval.signnow.com/oauth2/token"
    payload = {'username': 'sistemas@educalegal.com.br',
               'password': 'silex@568',
               'grant_type': 'password',
               'expiration_time': '2592000'}
    headers = {
        'Authorization': 'Basic {API_key}'.format(API_key=API_key),
    }
    r = requests.post(url, headers=headers, data=payload)
    r_dict = r.json()
    return r_dict["access_token"], r_dict["refresh_token"]


def verify_access_token(access_token):
    url = "https://api-eval.signnow.com/oauth2/token"
    headers = {
        "Authorization": "Bearer {access_token}".format(access_token=access_token)
    }

    r = requests.get(url, headers=headers)

    if r.status_code == 200:
        return True
    else:
        return False

def upload_document(access_token):
    url = "https://api-eval.signnow.com/document"
    headers = {
        "Authorization": "Bearer {access_token}".format(access_token=access_token)
    }

    files = {"file": open("lorem-ipsum.pdf", "rb")}

    r = requests.post(url, headers=headers, files=files)
    r_dict = r.json()
    return r_dict["id"]


def get_document(document_id, access_token):
    url = "https://api-eval.signnow.com/document/" + document_id
    headers = {
        "Authorization": "Bearer {access_token}".format(access_token=access_token)
    }
    r = requests.get(url, headers=headers)
    r_dict = r.json()
    return r.json()


if __name__ == "__main__":
    API_key = "YTMzMzQ5MWM1NzhlZjRkMTZlOTQyMTBkY2RiYmMxZTc6NWRhOTM5MWFiNTI4YWM4ZDliOTRkMzZhZDZlNTYyNzM="
    access_token, refresh_token = generate_access_token(API_key)
    print(access_token)
    print(refresh_token)
    token_valid = verify_access_token(access_token)
    print(token_valid)
    document_id = upload_document(access_token)
    print(document_id)
    get_document(document_id, access_token)



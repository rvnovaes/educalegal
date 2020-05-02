import requests


# Get user data
def get_user_data():
    headers = {"Authorization": "Bearer 4Egu08zTgHGGsUcDe1qqBhht28xWHI"}
    url = "https://api-ext.getsigneasy.com/v1/user/"
    response = requests.get(url, headers=headers)
    print(response.text, response.status_code)


# Upload an original file to signature
def upload_file():
    headers_content = {"authorization": "Bearer 4Egu08zTgHGGsUcDe1qqBhht28xWHI"}
    url = "https://api-ext.getsigneasy.com/v1/files/original/"
    payload = {"name": "test.txt"}
    files = {"file": open("test.txt", 'rb')}
    response = requests.post(url, headers=headers_content, files=files, data=payload)
    print(response.text, response.status_code)


# Retrive all original files
def retrieve_all_original_files():
    headers = {"Authorization": "Bearer 4Egu08zTgHGGsUcDe1qqBhht28xWHI"}
    url = "https://api-ext.getsigneasy.com/v1/files/original/"
    response = requests.get(url, headers=headers)
    print(response.text, response.status_code)

    file_id = "35329859"
    response = requests.get(url + file_id, headers=headers)
    print(response.text, response.status_code)


if __name__ == '__main__':
    # get_user_data()
    upload_file()
    # retrieve_all_original_files()



import sys

sys.path.append("/opt/educalegal/docassemble/docassemble/brcomeducalegal/data")
from module_clicksign_client import ClickSignClient

###### LOCALHOST ######
api_base_url = "https://sandbox.clicksign.com/"
token = "dc0251e3-bb8e-4813-84c0-1158ba0bdbcf"


if __name__ == '__main__':
    csc = ClickSignClient(api_base_url, token)

    print(csc.get_document('9afc2318-4729-4764-810b-ac66c6e6571e'))

    # print(csc.send_document('lorem-ipsum.pdf', '/opt/educalegal/api_requests/lorem-ipsum.pdf'))

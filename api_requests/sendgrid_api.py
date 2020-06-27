# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Category, Attachment, FileContent, FileType, FileName, Disposition, CustomArg

message = Mail(
    from_email='sistemas@educalegal.com.br',
    to_emails='sistemas@educalegal.com.br',
    subject='Sending with Twilio SendGrid is Fun',
    html_content='<strong>and easy to do anywhere, even with Python</strong>')
message.category = Category("Desenvolvimento")
message.custom_arg
CustomArg("Cliente", "Educa Legal Desenvolvimento")
file_path = "lorem-ipsum.pdf"
with open(file_path, 'rb') as f:
    data = f.read()
    f.close()
encoded = base64.b64encode(data).decode()
attachment = Attachment()
attachment.file_content = FileContent(encoded)
attachment.file_type = FileType('application/pdf')
attachment.file_name = FileName('test_filename.pdf')
attachment.disposition = Disposition('attachment')
message.attachment = attachment

try:
    # sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    sg = SendGridAPIClient('SG.SwlqsxA_TtmrbqF3-iiJew.CYzzrPYQpwFrEOMIJ9Xw6arfV0mSo1m3qFe-sVHg6o')
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e)

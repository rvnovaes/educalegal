# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
import base64

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Category, Attachment, FileContent, FileType, FileName, Disposition


def send_email_sendgrid(from_email, to_emails, subject, html_content, category, file_path, file_name):
    # Sendgrid API returns 400 BAD REQUEST se você eviar emails duplicados. Por isso, convertemos a lista em conjunto e
    # novamente em lista
    if isinstance(to_emails, list):
        s1 = set(to_emails)
        to_emails = list(s1)

    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        html_content=html_content)

    message.category = Category(category)
    file_path = file_path
    with open(file_path, 'rb') as f:
        data = f.read()
        f.close()
    encoded = base64.b64encode(data).decode()
    attachment = Attachment()
    attachment.file_content = FileContent(encoded)
    attachment.file_type = FileType('application/pdf')
    attachment.file_name = FileName(file_name)
    attachment.disposition = Disposition('attachment')
    message.attachment = attachment

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        if response.status_code == 202:
            success_message = "E-mail enviado com sucesso!"
            return response.status_code, success_message
        else:
            error_message = "Hove falha no envio do e-mail..."
            return response.status_code, error_message
    except Exception as e:
        exception_status_code = 1
        return exception_status_code, str(e)


if __name__ == "__main__":
    send_email_sendgrid("sistemas@educalegal.com.br", "sistemas@educalegal.com.br", "TESTE", "<h1>Hello World",
                        "Desenvolvimento", "lorem-ipsum.pdf", "lorem-ipsum.pdf")

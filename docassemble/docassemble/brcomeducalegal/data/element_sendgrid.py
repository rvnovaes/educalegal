# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
import base64

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Category, Attachment, FileContent, FileType, FileName, Disposition, To, From, Bcc


def send_email_sendgrid(to_emails, subject, html_content, category, file_path, file_name):
    message = Mail(
        subject=subject,
        html_content=html_content)
    message.from_email = From("automacao@educalegal.com.br", "Educa Legal")
    message.bcc = Bcc("sistemas@educalegal.com.br", "Sistemas Educa Legal")
    to_emails_names = list()
    to_emails_deduplication = list()
    # Sendgrid API returns 400 BAD REQUEST se você eviar emails duplicados.
    # Por isso, testamos se o email esta na lista de deduplicacao
    for i in to_emails:
        current_email = i["email"]
        current_name = i["name"]
        if current_email not in to_emails_deduplication:
            recipient = To(current_email, current_name)
            to_emails_names.append(recipient)
        to_emails_deduplication.append(current_email)
    message.to = to_emails_names
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
        # sg = SendGridAPIClient('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')
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
    recipients = [{"email": "rvnovaes@gmail.com", "name": "Roberto"},
                  {"email": "rvnovaes@gmail.com", "name": "Roberto"},
                  {"email": "roberto.novaes@educalegal.com.br", "name": "Roberto EducaLegal"}]


    print(send_email_sendgrid(recipients, "TESTE", "<h1>Hello World",
                        "Desenvolvimento", "lorem-ipsum.pdf", "lorem-ipsum.pdf"))


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

import smtplib

import os
from dotenv import load_dotenv

load_dotenv()


class SendMail():
    def __init__(self) -> None:
        self.email_name = os.environ.get("EMAIL_NAME")
        self.email_from = os.environ.get("EMAIL_FROM")
        self.email_to = os.environ.get("EMAIL_TO")
        self.email_password = os.environ.get("EMAIL_PASSWORD")

        self.smtp_host = os.environ.get("SMTP_HOST")
        self.smtp_port = os.environ.get("SMTP_PORT")
        self.message = MIMEMultipart()
        self.server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)

    def send_mail(self, subject, body):
        self.message['From'] = formataddr(
            (str(Header(self.email_name, 'utf-8')), self.email_from))
        self.message['To'] = self.email_to
        self.message['Subject'] = subject

        self.message.attach(MIMEText(body, 'html', 'utf-8'))

        self.server.login(self.email_from, self.email_password)
        self.server.sendmail(
            self.message['From'], self.message['To'], self.message.as_string())
        self.server.quit()

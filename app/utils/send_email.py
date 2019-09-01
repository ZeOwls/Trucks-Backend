import os
import smtplib
import ssl
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders
from flask_login import current_user

# app pass is phsskkegbtqdnnfz
email_user = os.environ.get("EMAIL_USER")
email_pss = os.environ.get("EMAIL_PASS")

os.environ.get("EMAIL_PASS")

def pass_mail(password,receiver_email,name):
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(email_user, email_pss)
        print(name)
        subject = "Hello from trucks company"
        # body = f"Hello {name},\n\nWelcome to trucks company,here is your password: {password}.\nkeep it safe and be sure to remember it"
        body = "يا هلا يا هلا "
        msg = f"Subject: {subject}\n\n{body}".encode('UTF-8')
        smtp.sendmail(email_user, receiver_email, msg)


def file_mail(filename, name):
    # TODO uncomment that line in production
    receiver_email = 'a.nassar@zeowls.com'  # current_user.email
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(email_user, email_pss)
        message = MIMEMultipart()
        # receiver_email = "mahmoud14zamalek@gmail.com"
        message["From"] = email_user
        message["To"] = receiver_email  # current_user.email
        subject = f"Trucks | {name} Data file"
        body = f"Hello From trucks,\nWe attached {name} Data file as you request it before\n\n\nregards."
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        with open(os.path.join('app/utils/sentfiles', filename), "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )

        # Add attachment to message and convert message to string
        message.attach(part)
        text = message.as_string()

        smtp.sendmail(email_user, receiver_email, text)

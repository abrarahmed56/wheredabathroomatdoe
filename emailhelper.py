from constants import *
import smtplib
import socket
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart

def send_email(receiver, subject, body):
    HOST = "smtp.gmail.com"
    PORT = "587"
    socket.setdefaulttimeout(None)
    sender= "wheredabathroomatdoe@gmail.com"
    with open('emailpassword', 'r') as f:
        password = f.read().strip()
   
    msg = MIMEMultipart('alternative')    
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    html = MIMEText(body, 'html')
    msg.attach(html)

    server = smtplib.SMTP()
    server.connect(HOST, PORT)
    server.starttls()
    server.login(sender,password)
    server.sendmail(sender,receiver, msg.as_string())
    server.close()

def send_confirmation_email(receiver, first_name, url_id):
    global WEBSITE_URL_BASE
    if not first_name:
        first_name = "Anonymous"
    email_body_template = '''
    Dear %(name)s,<br><br>
    Please click <a href="%(url)s" target="_blank">here</a> to confirm your email address.<br>
    Alternatively, here is a direct link: %(url)s<br><br>
    Thank you for registering for wheredabathroomatdoe?!,<br><br>
    The wheredabathroomatdoe?! Team
    '''
    email_body = email_body_template%{ 'name': first_name
                                     , 'url':
                                     "%s/confirm/email/%s"%
                                     (WEBSITE_URL_BASE, url_id)
                                     }
    send_email(receiver, "wheredabathroomatdoe?! Account Confirmation", email_body)
    return True

def send_password_reset_email(receiver, first_name, url_id):
    global WEBSITE_URL_BASE
    if not first_name:
        first_name = "Anonymous"
    email_body_template = '''
    Dear %(name)s,<br><br>
    Please click <a href="%(url)s" target="_blank">here</a> to reset your password.<br>
    Alternatively, here is a direct link: %(url)s<br>
    If you have not requested a password reset, please disregard this message.<br><br>
    Thank you for using wheredabathroomatdoe?!,<br><br>
    The wheredabathroomatdoe?! Team
    '''
    email_body = email_body_template%{ 'name': first_name
                                     , 'url':
                                     "%s/passwordreset/%s"%
                                     (WEBSITE_URL_BASE, url_id)
                                     }
    send_email(receiver, "wheredabathroomatdoe?! Password Reset", email_body)
    return True

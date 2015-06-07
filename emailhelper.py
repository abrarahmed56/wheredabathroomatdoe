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
    email_body_template = '''
    Dear %(name)s,<br>
    Please click <a href="%(url)s target="_blank"">here</a> to confirm your email address.<br>
    Alternatively, here is a direct link: %(url)s<br>
    Thank you for registering for wheredabathroomatdoe?!
    '''
    email_body = email_body_template%{ 'name': first_name
                                     , 'url': "http://www.chesley.party:8000/confirm/email/%s"%url_id
                                     }
    send_email(receiver, "wheredabathroomatdoe Account Confirmation", email_body)


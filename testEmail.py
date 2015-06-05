import smtplib
import socket
from email.MIMEText import MIMEText

def send_email(receiver, subject, body):
    HOST = "smtp.gmail.com"
    PORT = "587"
    socket.setdefaulttimeout(None)
    sender= "wheredabathroomatdoe@gmail.com"
    with open('emailpassword', 'r') as f:
        password = f.read().strip()
   
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    server = smtplib.SMTP()
    server.connect(HOST, PORT)
    server.starttls()
    server.login(sender,password)
    server.sendmail(sender,receiver, msg.as_string())
    server.close()

send_email("erickolbusz@gmail.com","TEST1","hey its works bub")
send_email("trunkatedpig@gmail.com","TEST2","hey its still works bub")

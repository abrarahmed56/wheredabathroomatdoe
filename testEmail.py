import smtplib
import socket
from email.MIMEText import MIMEText

socket.setdefaulttimeout(None)
HOST = "smtp.gmail.com"
PORT = "587"
sender= "erickolbusz@gmail.com"
password = "#"
receiver= ""

msg = MIMEText("email body text")

msg['Subject'] = 'hey its works bub'
msg['From'] = sender
msg['To'] = receiver

server = smtplib.SMTP()
server.connect(HOST, PORT)
server.starttls()
server.login(sender,password)
server.sendmail(sender,receiver, msg.as_string())
server.close()

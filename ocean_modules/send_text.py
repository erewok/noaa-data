#!/usr/bin/python3 -tt

import smtplib
from email.mime.text import MIMEText

def _tsend(username, password, recipient, msg):

  message = MIMEText(msg, _charset="utf-8")
  email_text = """From: {}
    To: {}
    Subject: Weather
    {}""".format(username, recipient, message)

  server = smtplib.SMTP('smtp.gmail.com', 587)
  server.starttls()
  server.login(username, password)
  server.sendmail(username, recipient, email_text)
  server.quit()

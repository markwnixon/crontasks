import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import ntpath
import shutil
import os    
import numpy as np
import subprocess
import fnmatch
from collections import Counter
import datetime
from PyPDF2 import PdfFileReader

from CCC_system_setup import usernames, passwords, websites

def emailshipreport(tabdata):
    
    #newfile= ntpath.basename(mfile)
    #shutil.copy(mfile,newfile)

    emailfrom = usernames['mnix']
    #emailto = usernames['info']
    emailto = usernames['expo']
    #emailcc = usernames['expo']
    #fileToSend = tfile
    username = usernames['mnix']
    password = passwords['mnix']

    msg = MIMEMultipart()
    msg["From"] = emailfrom
    msg["To"] = emailto
    msg["Cc"] = emailcc
    msg["Subject"] = 'Ship Report'

    s1='<td>'
    s2='</td><td>'
    body = '<html><body><p>Here is status of FEL related Shipline Activity</p><p>Blue = arrived, Red = arrives in less than 10 days, Ordered by new arrival date</p>\n\n'
    body = body + "<table><tr align = 'center'>"
    body = body + '<td><b>Days<br>Away</b></td><td><b>Status</b></td><td><b>New Arrival Date</b></td><td><b>Release</b></td><td><b>Old Arrival Date</b></td><td><b>Booking</b></td><td><b>Container</b></td><td><b>BillTo</b></td><td><b>Exporter</b></td></tr>\n'
    for tab in tabdata:
        try:
            daway=int(tab[0])
            if daway<0:
                s1="<td style='color: blue'>"
                s2='</td>'+s1
            elif daway<11:
                s1="<td style='color: red'>"
                s2='</td>'+s1
            else:
                s1="<td>"
                s2='</td>'+s1
                
        except:
            err=1
                
        body=body+'<tr>'+s1+tab[0]+s2+tab[1]+s2+tab[2]+s2+tab[3]+s2+tab[4]+s2+tab[5]+s2+tab[6]+s2+tab[8]+s2+tab[9]+'</td></tr>\n'
   
    body=body+'</table></body></html>'
    msg.attach(MIMEText(body, 'html'))

    #attachment = open(fileToSend, "rb")
 
    #part = MIMEBase('application', 'octet-stream')
    #part.set_payload((attachment).read())
    #encoders.encode_base64(part)
    #part.add_header('Content-Disposition', "attachment; filename= %s" % fileToSend)
 
    #msg.attach(part)
    
    server = smtplib.SMTP(websites['mailserver'])
    #server.starttls()
    server.login(username,password)
    emailto = [emailto, emailcc]
    server.sendmail(emailfrom, emailto, msg.as_string())
    server.quit()
    

    
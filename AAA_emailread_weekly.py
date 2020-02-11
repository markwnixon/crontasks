import os
import shutil

import imaplib, email
import datetime
import numpy as np

from CCC_system_setup import addpath3, usernames, passwords, imap_url
from remote_db_connect import tunnel, db
from models import Autos


from fuelsorter import fuelsort

def unique(list1):
    x = np.array(list1)
    newlist=np.unique(x)
    return newlist

def get_bookings(longs):
    t=booking_p.findall(longs)
    return t

def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None,True)

def search(key,value,con):
    result,data=con.search(None,key,'"{}"'.format(value))
    return data

#(_, data) = CONN.search(None, '(SENTSINCE {0})'.format(date)), '(FROM {0})'.format("someone@yahoo.com") )
def search_from_date(key,value,con,datefrom):
    result,data=con.search( None, '(SENTSINCE {0})'.format(datefrom) , key, '"{}"'.format(value) )
    return data

def get_emails(result_bytes,con):
    msgs=[]
    for num in result_bytes[0].split():
        typ,data=con.fetch(num,'(RFC822)')
        msgs.append(data)
    return msgs

def get_attachments(msg):
    attachment_dir='/home/mark/alldocs/test'
    for part in msg.walk():
        if part.get_content_maintype()=='multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        file_Name=part.get_filename()
        if bool(file_Name):
            filePath=os.path.join(attachment_dir,file_Name)
            with open(filePath,'wb')as f:
                f.write(part.get_payload(decode=True))

def get_attachments_name(msg,this_name,att_dir):
    for part in msg.walk():
        if part.get_content_maintype()=='multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        file_Name=part.get_filename()
        if bool(file_Name):
            filePath=os.path.join(att_dir,this_name)
            with open(filePath,'wb')as f:
                f.write(part.get_payload(decode=True))

def get_attachments_pdf(msg,att_dir,type,contains):
    for part in msg.walk():
        if part.get_content_maintype()=='multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        file_Name=part.get_filename()

        if bool(file_Name):
            if type in file_Name.lower() and contains in file_Name:
                filePath=os.path.join(att_dir,file_Name)
                with open(filePath,'wb')as f:
                    f.write(part.get_payload(decode=True))

def get_attachment_filename(msg,type,contains):
    filehere=[]
    for part in msg.walk():
        if part.get_content_maintype()=='multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        file_Name=part.get_filename()
        if bool(file_Name):
            if type in file_Name.lower() and contains.lower() in file_Name.lower():
                filehere.append(file_Name)

    return filehere

def datename(data):
    for response_part in data:
        if isinstance(response_part, tuple):
            part = response_part[1].decode('utf-8')
            msg = email.message_from_string(part)
            date=msg['Date']
            print(date)
            date=date.split('-',1)[0]
            date=date.split('+',1)[0]
            date=date.strip()
            n=datetime.datetime.strptime(date , "%a, %d %b %Y %H:%M:%S")
            adder=str(n.year)+'_'+str(n.month)+'_'+str(n.day)+'_'+str(n.hour)+str(n.minute)+str(n.second)
    return adder

def get_date(data):
    for response_part in data:
        if isinstance(response_part, tuple):
            try:
                part = response_part[1].decode('utf-8')
                msg = email.message_from_string(part)
                date=msg['Date']
                date=date.split('-',1)[0]
                date=date.split('+',1)[0]
                date=date.strip()
                n=datetime.datetime.strptime(date , "%a, %d %b %Y %H:%M:%S")
                newdate=datetime.date(n.year,n.month,n.day)
            except:
                newdate=None
    return newdate

def get_subject(data):
    for response_part in data:
        if isinstance(response_part, tuple):
            part = response_part[1].decode('utf-8')
            msg = email.message_from_string(part)
            subject=msg['Subject']
    return subject

def get_body_text(data):
    for response_part in data:
        if isinstance(response_part, tuple):
            part = response_part[1].decode('utf-8')
            msg = email.message_from_string(part)
            text=msg['Text']
    return text

def checkdate(emaildate,filename,txtfile):
    returnval=0
    with open(txtfile) as f:
        for line in f:
            if filename in line:
                linelist=line.split()
                date=linelist[0]
                if date != 'None':
                    datedt=datetime.datetime.strptime(date, '%Y-%m-%d')
                    datedt=datedt.date()
                    if datedt<emaildate:
                        print('File needs to be updated',datedt,date,filename)
                        returnval=1
                else:
                    print('File found, but have no date to compare')
                    returnval=1
    return returnval


if 1==1:
#_____________________________________________________________________________________________________________
# Switches for routines
#_____________________________________________________________________________________________________________
    fleet=1
# 0 means do not run, 1 means run normal, 2 means create new baseline
#_____________________________________________________________________________________________________________

#_____________________________________________________________________________________________________________
# Subroutine for extracting new Fleet MultiService attachments from multiservice
#_____________________________________________________________________________________________________________


    if fleet>0:
        if fleet==1:
            usernamelist = [usernames['inf2']]
            password = passwords['inf2']
            dayback=14
        if fleet==2:
            usernamelist = [usernames['inf2']]
            password = passwords['inf2']
            dayback=90

        datefrom = (datetime.date.today() - datetime.timedelta(dayback)).strftime("%d-%b-%Y")
        print('Running Fleet from...',datefrom)
        att_dir=addpath3('emaildocs/msfleet')
        txt_file=addpath3('emaildocs/fleet.txt')

        for username in usernamelist:
            con = imaplib.IMAP4_SSL(imap_url)
            con.login(username,password)
            con.select('INBOX')
            msgs=get_emails(search_from_date('FROM','customer-service-msfleet@multiservice.com',con,datefrom),con)
            flist=os.listdir(att_dir)
            nbills=len(flist)
            fleetbillsadd=[]
            fleetbillsupdate=[]
            for j,msg in enumerate(msgs):
                raw=email.message_from_bytes(msg[0][1])
                thesefiles=get_attachment_filename(raw,'pdf','fleet_bill')
                thisdate=get_date(msg)
                for thisfile in thesefiles:
                    #print(thisdate,thisfile)
                    if fleet==2:
                        fleetbillsadd.append([thisdate,thisfile])
                        get_attachments_pdf(raw,att_dir,'pdf','fleet_bill')

                    if thisfile not in flist and fleet==1:
                        #print('Adding new file:',thisfile)
                        fleetbillsadd.append([thisdate,thisfile])
                        get_attachments_pdf(raw,att_dir,'pdf','fleet_bill')

                    elif fleet==1:
                        update=checkdate(thisdate,thisfile,txt_file)
                        #print(update)
                        if update:
                            fleetbillsupdate.append([thisdate,thisfile])
                            get_attachments_pdf(raw,att_dir,'pdf','fleet_bill')
                        else:
                            print('This file up to date: ',thisfile)

            if fleet==1:
                ot='a'
            if fleet==2:
                ot='w'

            with open(txt_file,ot) as f:
                for bill in fleetbillsadd:
                    try:
                        thisdate=bill[0].strftime('%Y-%m-%d')
                    except:
                        thisdate='None'

                    nbills=nbills+1
                    thisfile=bill[1]
                    newfile=thisfile.replace('.pdf','')
                    newfile=newfile.replace('.','')
                    newfile=newfile+'.pdf'
                    print('Adding',thisdate,thisfile)
                    f.write(thisdate+' '+thisfile+'\n')
                    newfile=addpath3('emaildocs/msfleet/'+newfile)
                    shutil.copy(addpath3('emaildocs/msfleet/'+thisfile),newfile)
                    fuelsort(thisdate,newfile,nbills)

tunnel.stop()
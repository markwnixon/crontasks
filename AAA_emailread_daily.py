import os
import shutil
import fnmatch
import subprocess

import imaplib, email
import datetime
import re
import numpy as np
from cronfuncs import newjo

from CCC_system_setup import addpath2, addpath3, websites, usernames, passwords, imap_url, scac, companydata
from remote_db_connect import tunnel, db
from models import Orders, OverSeas, People, Drops

#booking_p=re.compile('[159][0123456789]{8}')
booking_p=re.compile("[1259][0123456789]{8}|[E][BKG0123456789]{11}|[S0][PHL0123456789]{9}|[038VR][0123456789]{7}")

#_____________________________________________________________________________________________________________
# Switches for routines
#_____________________________________________________________________________________________________________
remit=0
gjob=1
gbook=1
kjob=0
cdata = companydata()
tcode= cdata[10]
# 0 means do not run, 1 means run normal, 2 means create new baseline
#_____________________________________________________________________________________________________________
# Subroutines to extract remittances coming in from Knight
#_____________________________________________________________________________________________________________

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

    if remit>0:

        msgs=get_emails(search('FROM','ReportServer@KnightTrans.com',con),con)
        att_dir='/home/mark/alldocs/emailextracted/knightremits'
        for j,msg in enumerate(msgs):
            adder=datename(msg)
            print(adder)
            this_name='Remittance'+'_'+adder+'.pdf'
            #print(get_body(email.message_from_bytes(msg[0][1])))
            raw=email.message_from_bytes(msg[0][1])
            get_attachments_name(raw,this_name,att_dir)

        for file2 in os.listdir(att_dir):
            if fnmatch.fnmatch(file2, '*.pdf'):
                #Check to see if already in database:
                base=os.path.splitext(file2)[0]
                tp=subprocess.check_output(['pdf2txt.py', '-o', os.path.join(att_dir,base+'.txt'), os.path.join(att_dir,file2)])


#_____________________________________________________________________________________________________________
# Subroutine for extracting new Maersk bookings attachments from Global
#_____________________________________________________________________________________________________________

    if gbook>0:
        if gbook==1:
            usernamelist=[usernames['info']]
            password = passwords['info']
            dayback=14
        if gbook==2:
            usernamelist=[usernames['info']]
            password = passwords['info']
            dayback=450

        datefrom = (datetime.date.today() - datetime.timedelta(dayback)).strftime("%d-%b-%Y")
        print('Running GBook from...',datefrom)

        att_dir=addpath3('emaildocs/globalbook')
        txt_file=addpath3('emaildocs/global_bookings.txt')

        for username in usernamelist:
            con = imaplib.IMAP4_SSL(imap_url)
            con.login(username,password)
            con.select('INBOX')
            msgs=get_emails(search_from_date('FROM','@gblna.com',con,datefrom),con)
            flist=os.listdir(att_dir)
            loadconsadd=[]
            loadconsupdate=[]
            bookcheck = []
            for j,msg in enumerate(msgs):
                raw=email.message_from_bytes(msg[0][1])
                thesefiles=get_attachment_filename(raw,'pdf','DB')
                thisdate=get_date(msg)
                subject = get_subject(msg)
                #print('The subject is:', subject)
                blist = get_bookings(subject)
                if blist:
                    bkhere = blist[0]
                    bkhere = bkhere.strip()
                    if bkhere not in bookcheck:
                        bookcheck.append(bkhere)
                        #print(bkhere)
                        odat = OverSeas.query.filter(OverSeas.Booking == bkhere).first()
                        if odat is not None:
                            print(f'Booking {bkhere} already in database')
                        else:
                            sdate = thisdate.strftime('%Y-%m-%d')
                            jtype = tcode + 'O'
                            nextjo = newjo(jtype, sdate)
                            input = OverSeas(Jo=nextjo, Pid=0, MoveType=None, Direction=None, Commodity=None,
                                             Pod=None, Pol=None, Origin=None, PuDate=sdate, ContainerType=None,
                                             Booking=bkhere, CommoList=0, ExportID=0, ConsigID=0, NotifyID=0,
                                             FrForID=0, PreCarryID=0, Estimate=None, Charge=None,
                                             Container=None,
                                             Dpath=None, Ipath=None, Apath=None, Cache=0, Status='000', Label=None,
                                             BillTo=None, Exporter=None, Consignee=None, Notify=None,
                                             FrFor=None, PreCarry=None, Driver=None, Seal=None,
                                             Description=None, RetDate=sdate, Tpath=None, Itotal='',
                                             RelType='Seaway Bill', AES='', ExpRef='', AddNote='')

                            db.session.add(input)
                            db.session.commit()
                            print(f'Booking {bkhere} has been added to database')

                for thisfile in thesefiles:
                    #print(thisdate,thisfile)
                    if gbook==2:
                        loadconsadd.append([thisdate,thisfile])

                    if thisfile not in flist and gbook==1:
                        #print('Adding new file:',thisfile)
                        loadconsadd.append([thisdate,thisfile])
                        get_attachments_pdf(raw,att_dir,'pdf','DB')

                    elif gbook==1:
                        update=checkdate(thisdate,thisfile,txt_file)
                        #print(update)
                        if update:
                            loadconsupdate.append([thisdate,thisfile])
                            get_attachments_pdf(raw,att_dir,'pdf','DB')
                        else:
                            print('This file up to date: ',thisfile)
            if gbook==1:
                filelines=[]
                for load in loadconsupdate:
                    try:
                        thisdate=load[0].strftime('%Y-%m-%d')
                    except:
                        thisdate='None'
                    thisfile=load[1]
                    print('Modifying',thisdate,thisfile)
                    with open(txt_file) as f:
                        for line in f:
                            if thisfile in line:
                                line = thisdate+' '+thisfile+'\n'
                            filelines.append(line)
                    shutil.copy(addpath3('emaildocs/globalbook/'+thisfile),addpath2('bookings/'+thisfile))
                    with open(txt_file,'w') as f:
                        for line in filelines:
                            f.write(line)
            if gbook==1:
                ot='a'
            if gbook==2:
                ot='w'

            with open(txt_file,ot) as f:
                for load in loadconsadd:
                    try:
                        thisdate=load[0].strftime('%Y-%m-%d')
                    except:
                        thisdate='None'
                    thisfile=load[1]
                    print('Adding',thisdate,thisfile)
                    f.write(thisdate+' '+thisfile+'\n')
                    if gbook==1:
                        shutil.copy(addpath3('emaildocs/globalbook/'+thisfile),addpath2('bookings/'+thisfile))
#_____________________________________________________________________________________________________________
# Subroutine for extracting new loads coming in from Knight
#_____________________________________________________________________________________________________________
    if kjob>0:
        if kjob==1:
            usernamelist=[usernames['inf2']]
            password = passwords['inf2']
            dayback=120
        if kjob==2:
            usernamelist = [usernames['info']]
            password = passwords['info']
            dayback=450
        datefrom = (datetime.date.today() - datetime.timedelta(dayback)).strftime("%d-%b-%Y")
        print(datefrom)
        att_dir=addpath3('emaildocs/knightloads')
        txt_file=addpath3('emaildocs/knight_loads.txt')

        for username in usernamelist:
            con = imaplib.IMAP4_SSL(imap_url)
            con.login(username,password)
            con.select('INBOX')
            msgs=get_emails(search_from_date('FROM','@knighttrans.com',con,datefrom),con)
            flist=os.listdir(att_dir)
            loadconsadd=[]
            loadconsupdate=[]
            for j,msg in enumerate(msgs):
                raw=email.message_from_bytes(msg[0][1])
                thesefiles=get_attachment_filename(raw,'pdf','LoadConfirmation')
                thisdate=get_date(msg)
                for thisfile in thesefiles:
                    #print(thisdate,thisfile)
                    if kjob==2:
                        loadconsadd.append([thisdate,thisfile])
                    if thisfile not in flist and kjob==1:
                        #print('Adding new file:',thisfile)
                        loadconsadd.append([thisdate,thisfile])
                        get_attachments_pdf(raw,att_dir,'pdf','LoadConfirmation')
                    elif kjob==1:
                        update=checkdate(thisdate,thisfile,txt_file)
                        #print(update)
                        if update:
                            loadconsupdate.append([thisdate,thisfile])
                            get_attachments_pdf(raw,att_dir,'pdf','LoadConfirmation')
                        else:
                            print('This file up to date: ',thisfile)

            if kjob==1:
                filelines=[]
                for load in loadconsupdate:
                    try:
                        thisdate=load[0].strftime('%Y-%m-%d')
                    except:
                        thisdate='None'
                    thisfile=load[1]
                    print('Modifying',thisdate,thisfile)
                    with open(txt_file) as f:
                        for line in f:
                            if thisfile in line:
                                line = thisdate+' '+thisfile+'\n'
                            filelines.append(line)
                    shutil.copy(addpath3('emaildocs/knightloads/'+thisfile),addpath2('orders/'+thisfile))
                    with open(txt_file,'w') as f:
                        for line in filelines:
                            f.write(line)

            if kjob==1:
                ot='a'
            if kjob==2:
                ot='w'
            with open(txt_file,ot) as f:
                for load in loadconsadd:
                    try:
                        thisdate=load[0].strftime('%Y-%m-%d')
                    except:
                        thisdate='None'
                    thisfile=load[1]
                    print('Adding',thisdate,thisfile)
                    f.write(thisdate+' '+thisfile+'\n')
                    if kjob==1:
                        shutil.copy(addpath3('emaildocs/knightloads/'+thisfile),addpath2('orders/'+thisfile))



#_____________________________________________________________________________________________________________
# Subroutine to grab bookings from ABE for Global work and put into the database on website
#_____________________________________________________________________________________________________________
    if gjob>0:
        if gjob==1:
            dayback=30
        if gjob==2:
            dayback=450
        datefrom = (datetime.date.today() - datetime.timedelta(dayback)).strftime("%d-%b-%Y")
        print(datefrom)
        username = usernames['infh']
        password = passwords['infh']
        con = imaplib.IMAP4_SSL(imap_url)
        con.login(username,password)
        con.select('INBOX')
        msgs=get_emails(search_from_date('FROM','@gblna.com',con,datefrom),con)
        # msgs=get_emails(search('FROM','aalsawi@gblna.com',con),con)
        con.close()
        con.logout()

        bookings=[]
        norepeat=[]
        for j,msg in enumerate(msgs):
            raw=email.message_from_bytes(msg[0][1])
            body=get_body(raw)
            getdate=get_date(msg)
            try:
                body=body.decode('utf-8')
                blist=get_bookings(body)
                if blist:
                    for b in blist:
                        b=b.strip()
                        if b not in norepeat:
                            booktriplet=[b,getdate,getdate]
                            bookings.append(booktriplet)
                            norepeat.append(b)
                        else:
                        #find the existing booking and replace the second date
                            for book in bookings:
                                if book[0]==b:
                                    book[2]=getdate

            except:
                print('Bad decode on',getdate)


        try:
            with open(addpath3('emaildocs/global_jobs.txt')) as f:
                longs=f.read()
            f.close()
        except:
            longs=''

        if gjob==1:
            ot='a'
        if gjob==2:
            ot='w'

        with open(addpath3('emaildocs/global_jobs.txt'),ot) as f:
            for book in bookings:
                b=book[0]
                d1=book[1].strftime('%Y-%m-%d')
                d2=book[2].strftime('%Y-%m-%d')
                if gjob==2:
                    print('Adding',b,d1,d2)
                    f.write(b+' '+d1+' '+d2+'\n')

                if gjob==1:
                    bdat=Orders.query.filter(Orders.Booking==b).first()
                    odat=OverSeas.query.filter(OverSeas.Booking==b).first()
                    pdat = People.query.filter(People.Company == 'Global Business Link').first()
                    bid = pdat.id
                    ldat = Drops.query.filter(Drops.Entity == 'Global Business Link').first()
                    lid = ldat.id
                    ddat = Drops.query.filter(Drops.Entity == 'Baltimore Seagirt').first()
                    did = ddat.id
                    if bdat is None and b not in longs and odat is None:
                        print('Adding',b,d1,d2)
                        f.write(b+' '+d1+' '+d2+'\n')
                        sdate=getdate.strftime('%Y-%m-%d')
                        jtype=tcode + 'T'
                        nextjo=newjo(jtype,sdate)
                        load='G'+nextjo[-5:]
                        order='G'+nextjo[-5:]
                        input = Orders(Status='A0', Jo=nextjo, Load=load,Order=order, Company='Global Business Link',Location=None,Booking=b,BOL=None,
                                        Container='TBD', Date=book[1], Driver=None, Company2='Baltimore Seagirt', Time=None, Date2=book[2], Time2=None,
                                        Seal=None, Pickup=None, Delivery=None, Amount='275.00', Path=None, Original=None,
                                        Description=None, Chassis=None, Detention='0', Storage='0', Release=0, Shipper='Global Business Link',
                                        Type=None, Time3=None, Bid=bid, Lid=lid, Did=did, Label=None, Dropblock1='Global Business Link\n4000 Coolidge Ave K\nBaltimore, MD 21229',
                                        Dropblock2='Baltimore Seagirt\n2600 Broening Hwy\nBaltimore, MD 21224',Commodity='Auto',Packing='Each',Links=None,
                                        Hstat=-1,Istat=-1,Proof=None,Invoice=None,Gate=None,Package=None,Manifest=None,Scache=0,Pcache=0,Icache=0,Mcache=0,Pkcache=0, QBi=0, InvoTotal='275.00')
                        db.session.add(input)
                        db.session.commit()
                    else:
                        print('                Skipping',book[0],book[1],book[2])

tunnel.stop()
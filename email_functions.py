import os

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
import email
import imaplib
import numpy as np
import re
import datetime
import subprocess
import fnmatch
import shutil
import os
from bs4 import BeautifulSoup as soup

import time
from datetime import timedelta

from pyvirtualdisplay import Display
from selenium import webdriver
from scrapers import vinscraper

from CCC_system_setup import addpath2, websites, usernames, passwords, mycompany, addpaths
co = mycompany()
if co == 'FELA':
    from CCC_FELA_remote_db_connect import tunnel, db
    from CCC_FELA_models import Autos, Accounts, People
elif co == 'OSLM':
    from CCC_OSLM_remote_db_connect import tunnel, db
    from CCC_OSLM_models import Autos, Accounts, People


class Cars:

    def __init__(self, jo, year, make, model, color, vin, empweight, value, towcostea):
        self.jo = jo
        self.year = year
        self.make = make
        self.model = model
        self.color = color
        self.vin = vin
        self.empweight = empweight
        self.towcostea = towcostea
        self.value = value


class Tow:

    def __init__(self, orderid, towcompany, addr1, addr2, phone, towcost, date1, date2, pufrom, delto, ncars, fn):
        self.orderid = orderid
        self.towcompany = towcompany
        self.addr1 = addr1
        self.addr2 = addr2
        self.phone = phone
        self.towcost = towcost
        self.date1 = date1
        self.date2 = date2
        self.pufrom = pufrom
        self.delto = delto
        self.ncars = ncars
        self.fn = fn


def unique(list1):
    x = np.array(list1)
    newlist = np.unique(x)
    return newlist


def get_bookings(longs):
    t1 = booking_p1.findall(longs)
    t2 = booking_p2.findall(longs)
    return t1+t2


def get_links(longs):
    t1 = 'Nothing'
    longs = longs.splitlines()
    for line in longs:
        if 'https' in line and 'protected' in line:
            t1 = line.strip()
    return t1


def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)


def search(key, value, con):
    result, data = con.search(None, key, '"{}"'.format(value))
    return data

# (_, data) = CONN.search(None, '(SENTSINCE {0})'.format(date)), '(FROM {0})'.format("someone@yahoo.com") )


def search_from_date(key, value, con, datefrom):
    result, data = con.search(None, '(SENTSINCE {0})'.format(datefrom), key, '"{}"'.format(value))
    return data


def get_emails(result_bytes, con):
    msgs = []
    for num in result_bytes[0].split():
        typ, data = con.fetch(num, '(RFC822)')
        msgs.append(data)
    return msgs


def get_attachments(msg):
    attachment_dir = '/home/mark/alldocs/test'
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        file_Name = part.get_filename()
        if bool(file_Name):
            filePath = os.path.join(attachment_dir, file_Name)
            with open(filePath, 'wb')as f:
                f.write(part.get_payload(decode=True))


def get_attachments_name(msg, this_name, att_dir):
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        file_Name = part.get_filename()
        if bool(file_Name):
            filePath = os.path.join(att_dir, this_name)
            with open(filePath, 'wb')as f:
                f.write(part.get_payload(decode=True))


def get_attachments_pdf(msg, att_dir, type, contains):
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        file_Name = part.get_filename()

        if bool(file_Name):
            if type in file_Name.lower() and contains in file_Name:
                filePath = os.path.join(att_dir, file_Name)
                with open(filePath, 'wb')as f:
                    f.write(part.get_payload(decode=True))


def get_attachment_filename(msg, type, contains):
    filehere = []
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        file_Name = part.get_filename()
        if bool(file_Name):
            if type in file_Name.lower() and contains.lower() in file_Name.lower():
                filehere.append(file_Name)

    return filehere


def datename(data):
    for response_part in data:
        if isinstance(response_part, tuple):
            part = response_part[1].decode('utf-8')
            msg = email.message_from_string(part)
            date = msg['Date']
            print(date)
            date = date.split('-', 1)[0]
            date = date.split('+', 1)[0]
            date = date.strip()
            n = datetime.datetime.strptime(date, "%a, %d %b %Y %H:%M:%S")
            adder = str(n.year)+'_'+str(n.month)+'_'+str(n.day) + \
                '_'+str(n.hour)+str(n.minute)+str(n.second)
    return adder


def get_date(data):
    for response_part in data:
        if isinstance(response_part, tuple):
            try:
                part = response_part[1].decode('utf-8')
                msg = email.message_from_string(part)
                date = msg['Date']
                date = date.split('-', 1)[0]
                date = date.split('+', 1)[0]
                date = date.strip()
                n = datetime.datetime.strptime(date, "%a, %d %b %Y %H:%M:%S")
                newdate = datetime.date(n.year, n.month, n.day)
            except:
                newdate = None
    return newdate


def get_subject(data):
    for response_part in data:
        if isinstance(response_part, tuple):
            part = response_part[1].decode('utf-8')
            msg = email.message_from_string(part)
            subject = msg['Subject']
    return subject


def get_body_text(data):
    for response_part in data:
        if isinstance(response_part, tuple):
            part = response_part[1].decode('utf-8')
            msg = email.message_from_string(part)
            text = msg['Text']
    return text


def checkdate(emaildate, filename, txtfile):
    returnval = 0
    with open(txtfile) as f:
        for line in f:
            if filename in line:
                linelist = line.split()
                date = linelist[0]
                if date != 'None':
                    datedt = datetime.datetime.strptime(date, '%Y-%m-%d')
                    datedt = datedt.date()
                    if datedt < emaildate:
                        print('File needs to be updated', datedt, date, filename)
                        returnval = 1
                else:
                    print('File found, but have no date to compare')
                    returnval = 1
    return returnval


if 1 == 1:
    # _____________________________________________________________________________________________________________
    # Switches for routines
    # _____________________________________________________________________________________________________________
    dispatch = 1
# 0 means do not run, 1 means run normal, 2 means create new baseline
    if dispatch > 0:
        paths = addpaths()
        if dispatch == 1:
            dayback = 5
        if dispatch == 2:
            dayback = 14

        datefrom = (datetime.date.today() - datetime.timedelta(dayback)).strftime("%d-%b-%Y")
        print('Running Dispatch from...', datefrom)
        usernamelist = [usernames['infh']]
        password = passwords['infh']
        #att_dir = addpath2('alldocs/emailextracted/dispatch')
        #txt_file = addpath2('alldocs/autocompares/dispatch.txt')
        dispatch_links = []
        dispatch_subjs = []
        dispatch_dates = []
        orderlist = []
        companylist = []
        for username in usernamelist:
            con = imaplib.IMAP4_SSL(websites['serversite'])
            con.login(username, password)
            con.select('INBOX')
            msgs = get_emails(search_from_date('FROM', '@centraldispatch.com', con, datefrom), con)
            for j, msg in enumerate(msgs):
                raw = email.message_from_bytes(msg[0][1])
                body = get_body(raw)
                subject = get_subject(msg)
                thisdate = get_date(msg)
                if 'ACCEPTED' in subject:
                    print('From raw email: ',subject, thisdate)
                    try:
                        body = body.decode('utf-8')
                        pdflinks = get_links(body)
                        dispatch_links.append(pdflinks)
                        dispatch_subjs.append(subject)
                        dispatch_dates.append(thisdate.strftime('%Y-%m-%d'))
                        order=subject.split('Order ID:',1)[1]
                        order=order.split()
                        order=order[0]
                        orderlist.append(order.strip())
                        company=subject.split('ACCEPTED by',1)[1]
                        companylist.append(company.strip())
                    except:
                        print('Bad decode on', getdate)


    txt_file=addpath2('tmp/dispatches.txt')
    print('txt_file=',txt_file)
    print('Initial Orderlist: ',orderlist)
    if dispatch==2:
        ot='w+'
        with open(txt_file,ot) as f:
            for j,mylink in enumerate(dispatch_links):
                print('Adding',mylink)
                f.write(dispatch_dates[j]+' '+dispatch_subjs[j]+'\n')
    if dispatch==1:
        poplist=[]
        with open(txt_file,'w+') as f:
            for line in f:
                for j,order in enumerate(orderlist):
                    company=companylist[j]
                    if order in line and company in line:
                        print('This order already processed: ',order)
                        poplist.append(j)
        poplist.sort(reverse=True) #need list in reverse order to avoid reindex issues
        for i in poplist:
            orderlist.pop(i)
            dispatch_links.pop(i)
            dispatch_subjs.pop(i)
            dispatch_dates.pop(i)

        # Now have only the new email data in list and can append to write the new info
        ot='a'
        with open(txt_file,ot) as f:
            for j,mylink in enumerate(dispatch_links):
                print('Adding',mylink)
                f.write(dispatch_dates[j]+' '+dispatch_subjs[j]+'\n')

    print('New dispatch links: ',dispatch_links)



if len(dispatch_links)>0:
    linktest = dispatch_links[0]
    username = usernames['disp']
    password = passwords['disp']
    paths = addpaths()
    #outpath = addpath2('dispatch/')

    print('Entering Firefox')
    yesterday = datetime.datetime.strftime(datetime.datetime.now() - timedelta(2), '%m/%d/%Y')
    today = datetime.datetime.today()
    print('This run made at: ', today)
    todaystr = datetime.datetime.today().strftime('%m/%d/%Y')
    startdate = yesterday
    enddate = todaystr

    # for j,startdate in enumerate(startdates):
    # enddate=enddates[j]
    with Display():
    #if 1 == 1:
        success = 0
        iter = 0
        print('profile at:', paths[4])
        #browser = webdriver.Firefox()
        while success == 0 and iter < 20:
            browser = webdriver.Firefox(firefox_profile=paths[4])
            url1 = websites['disp']
            browser.get(linktest)
            print(f'Got url1 {url1}')
            time.sleep(2)
            print('Done Sleeping')
            print('Getting xpath')
            selectElem = browser.find_element_by_xpath('//*[@id="pageUsername"]')
            print(f'Got xpath for Username {username}')
            selectElem.clear()
            selectElem.send_keys(username)
            selectElem = browser.find_element_by_xpath('//*[@id="pagePassword"]')
            print(f'Got xpath for Password {password}')
            selectElem.clear()
            selectElem.send_keys(password)
            selectElem.submit()
            try:
                browser.switch_to_frame(browser.find_elements_by_tag_name("iframe")[0])
                selectElem = browser.find_element_by_xpath('//*[@id="recaptcha-anchor"]/div[1]').click()
                time.sleep(1)
                selectElem = browser.find_element_by_xpath('//*[@id="keepLoggedIn"]').click()
                time.sleep(1)
                selectElem = browser.find_element_by_xpath('//*[@id="button"]').click()
            except:
                print('Did not succeed')
            time.sleep(2)
            newurl = browser.current_url
            print(newurl)
            if 'login' not in newurl:
                success = 1
                print('It Worked...Moving Forward....')
                time.sleep(1)
                browser.switch_to_default_content()

            else:
                iter = iter+1
                print('Did not succeed on iter', iter)
                # browser.switch_to_default_content()
                browser.quit()

        tow = [0]*len(dispatch_links)
        car = [0]*3*len(dispatch_links)
        i = 0
        for j, link in enumerate(dispatch_links):
            browser.get(link)
            time.sleep(2)
            page_data = browser.page_source
            page_soup = soup(page_data, 'html.parser')

            tow[j] = Tow(None, None, None, None, None, None, None, None, None, None, None, None)

            namelist = page_soup.findAll('div', {'class': 'panel-body'})

            towblock = namelist[0].address.text.splitlines()
            towcomp = []
            phone = namelist[0].a.text.strip()
            for line in towblock:
                line = line.strip()
                if len(line) > 3:
                    towcomp.append(line)
            towcomp = towcomp[0:3]+[phone]
            print(towcomp)
            tow[j].towcompany = towcomp[0]
            tow[j].addr1 = towcomp[1]
            tow[j].addr2 = towcomp[2]
            tow[j].phone = phone

            print('towdatahere',tow[j])

            dates = namelist[1].div.div.p.text.splitlines()
            for date in dates:
                if 'Pickup' in date:
                    tow[j].date1 = date.split(':', 1)[1].strip()
                    tow[j].date1 = datetime.datetime.strptime(tow[j].date1, "%m/%d/%Y").date()
                if 'Delivery' in date:
                    tow[j].date2 = date.split(':', 1)[1].strip()
                    tow[j].date2 = datetime.datetime.strptime(tow[j].date2, "%m/%d/%Y").date()

            namelist = page_soup.findAll('div', {'class': 'col-xs-12 col-sm-6'})
            dolblock = namelist[3].text.splitlines()
            for line in dolblock:
                line = line.strip()
                if 'Total Payment' in line:
                    line = line.split('Carrier:', 1)[1]
                    line = line.strip()
                    tow[j].towcost = line.replace('$', '')
                    print(tow[j].towcost)

            cdata = page_soup.findAll('span', {'class': 'pull-right'})
            orderid = cdata[0].text
            orderid = orderid.split(':', 1)[1]
            tow[j].orderid = orderid.strip()
            ncar = cdata[1].text
            ncar = ncar.split(':', 1)[1]
            tow[j].ncars = ncar.strip()
            ncars = int(tow[j].ncars)
            print('Ncars=', ncars)
            cost = float(tow[j].towcost)
            costea = cost/ncars

            headerlist = []
            tablist = page_soup.findAll('th', {'class': 'hidden-xs'})
            for tab in tablist:
                header = tab.text
                header = header.strip()
                headerlist.append(header)
            print(towcomp)
            print(headerlist)
            slicer = len(headerlist)

            publock = []
            pudata = page_soup.findAll('div', {'class': 'col-xs-12 col-sm-6 col-md-4'})
            puaddress = pudata[2].address.text
            lines = puaddress.splitlines()
            for line in lines:
                line = line.strip()
                if len(line) > 3 and 'contact' not in line.lower():
                    publock.append(line)
            print(publock)
            tow[j].pufrom = publock

            delblock = []
            deladdress = pudata[3].address.text
            lines = deladdress.splitlines()
            for line in lines:
                line = line.strip()
                if len(line) > 3 and 'contact' not in line.lower():
                    delblock.append(line)
            print(delblock)
            tow[j].delta = delblock

            for k in range(ncars):
                car[i] = Cars(None, None, None, None, None, None, None, None, None)
                datalist = []
                tablist = page_soup.findAll('td', {'class': 'hidden-xs'})
                for tab in tablist:
                    data = tab.text
                    data = data.strip()
                    datalist.append(data)
                print(datalist)
                car[i].year = datalist[0]
                car[i].make = datalist[1]
                car[i].model = datalist[2]
                car[i].color = datalist[4]
                car[i].vin = datalist[6]
                car[i].towcostea = costea
                i = i+1

        # Save all the files in temp directory as they will need to be renamed later
        for j, link in enumerate(dispatch_links):
            browser.get(link)
            time.sleep(3)
            selectElem = browser.find_element_by_link_text('Print').click()
            time.sleep(3)
            try:
                tow[j].fn = 'DISP_'+tow[j].orderid+'.pdf'
                newfile = paths[1]+'tmp/'+tow[j].fn
                shutil.move(paths[1]+'tmp/DispatchSheet.pdf', newfile)
                time.sleep(1)
            except OSError:
                print('File not found')
            # Note: with browser set to download pdf files the print button does download
            # and do not need remainer of this section:
            # time.sleep(2)
            # browser.switch_to_window(browser.window_handles[1])
            # time.sleep(2)
            #selectElem = browser.find_element_by_id("download").click()
            # browser.close()
            # browser.switch_to_window(browser.window_handles[0])

    browser.quit()
    print(len(dispatch_links), i-1)
    ncartotal = i
    for i in range(ncartotal):
        vin = car[i].vin
        if len(vin) == 17:
            year, make, model, wt, value, navg = vinscraper(vin)
            value = value.replace('$', '')
            car[i].year = year
            car[i].make = make
            car[i].model = model
            car[i].empweight = wt
            car[i].value = value
        attrs = vars(car[i])
        print(', '.join("%s: %s" % item for item in attrs.items()))
    # Now ready to place in database:
    for jx, link in enumerate(dispatch_links):
        ncars = int(tow[jx].ncars)
        for iy in range(ncars):
            #print(tow[j].orderid,car[i].year,car[i].make,car[i].model,car[i].vin,car[i].empweight,car[i].value)
            #print(tow[j].towcompany,tow[j].towcost,car[i].towcostea,tow[j].fn,tow[j].date1,tow[j].date2,tow[j].pufrom,tow[j].delto,tow[j].ncars)
            print('just here',tow[jx].towcompany,tow[jx].addr1,tow[jx].addr2,tow[jx].phone)#input = Autos(Jo=orderid, Hjo=None, Year=year, Make=make, Model=model, Color=color, VIN=vin, Title=None, State=None, EmpWeight=wt, Dispatched='Horizon Motors', Value=value,
            adat = Autos.query.filter(Autos.Orderid == tow[jx].orderid).first()
            if adat is None:
                print("This is a new tow order so we need to add it to the database")
                vin=car[iy].vin
                pulist=tow[jx].pufrom
                if pulist is not None:
                    puloc=pulist[-1]
                else:
                    puloc=''
                delist=tow[jx].delto
                if delist is not None:
                    deloc=delist[-1]
                else:
                    deloc='FEL'
                bdat = Autos.query.filter(Autos.VIN == vin).first()
                if bdat is None:
                    print("Entering data in Autos database")
                    input = Autos(Jo=tow[jx].orderid, Hjo=None, Year=car[iy].year, Make=car[iy].make, Model=car[iy].model, Color=car[iy].color, VIN=car[iy].vin, Title=None, State=None, EmpWeight=car[iy].empweight, Dispatched='Horizon Motors', Value=car[iy].value,
                                  TowCompany=tow[jx].towcompany, TowCost=tow[jx].towcost, TowCostEa=car[iy].towcostea, Original=tow[jx].fn, Status='New', Date1=tow[jx].date1, Date2=tow[jx].date2, Pufrom=puloc, Delto=deloc, Ncars=tow[jx].ncars, Orderid=tow[jx].orderid)
                    db.session.add(input)
                    db.session.commit()

                    pdat = People.query.filter((People.Ptype == 'TowCo') &
                                               (People.Company == tow[jx].towcompany)).first()
                    tdat = Accounts.query.filter(Accounts.Name.contains('Tow')).first()
                    if tdat is not None:
                        towacct = tdat.Name
                        towid = tdat.id
                    else:
                        towacct = None
                        towid = None
                    if pdat is not None:
                        pdat.Temp1 = 'Updated'
                        db.session.commit()
                    else:
                        print('input for:', tow[jx].towcompany, tow[jx].addr1, tow[jx].addr2, tow[jx].phone)
                        input = People(Ptype='TowCo', Company=tow[jx].towcompany, First='', Middle='', Last='', Addr1=tow[jx].addr1, Addr2=tow[jx].addr2, Addr3='', Idtype='', Idnumber='', Telephone=tow[jx].phone,
                                       Email='', Associate1=towacct, Associate2='', Date1=tow[jx].date1, Date2=None, Original='',Temp1='',Temp2='', Accountid = towid)
                        db.session.add(input)
                        db.session.commit()
        try:
            newfile = paths[1]+'tmp/'+tow[jx].fn
            copyline = f'scp {newfile} {websites["ssh_data"]+"vdispatch"}'
            os.system(copyline)
            os.remove(newfile)
        except:
            print("Copy of original document not successful")
tunnel.stop()

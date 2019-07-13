from systemfunc import addpath2, emailvals, addpaths
import email
import imaplib
#  from models import FELVehicles, Storage, Invoices, JO, Income, Orders, FELBills, Accounts, Bookings, OverSeas, Autos, People, Interchange, Drivers, ChalkBoard, Proofs, Services, Drops
# from viewfuncs import parseline, tabdata, tabdataR, popjo, jovec, newjo, timedata, nonone, nononef, init_truck_zero, dropupdate
import numpy as np
import re
import datetime
import subprocess
import fnmatch
import shutil
import os
# from felrun import db
import sys
# from scrape_dispatch import dispatch_finder
# ___________________________________________
# import sys
# sys.path.append('/home/mnixon/felrun')

from bs4 import BeautifulSoup as soup

import time
from datetime import timedelta
# import datetime

from pyvirtualdisplay import Display
from selenium import webdriver
#from cronpaths import addpath2
from scrapers import vinscraper
#from remote_db_connect import hiddendata
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


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
    dispatch = 2
# 0 means do not run, 1 means run normal, 2 means create new baseline
    if dispatch > 0:
        em, pw, ourserver = emailvals()
        if dispatch == 1:
            usernames = [em[5]]
            dayback = 14
        if dispatch == 2:
            usernames = [em[5]]
            dayback = 14

        datefrom = (datetime.date.today() - datetime.timedelta(dayback)).strftime("%d-%b-%Y")
        print('Running Dispatch from...', datefrom)
        password = pw[5]
        print(ourserver)
        #att_dir = addpath2('alldocs/emailextracted/dispatch')
        #txt_file = addpath2('alldocs/autocompares/dispatch.txt')

        for username in usernames:
            con = imaplib.IMAP4_SSL("az1-ss7.a2hosting.com")
            con.login(username, password)
            con.select('INBOX')
            msgs = get_emails(search_from_date('FROM', '@centraldispatch.com', con, datefrom), con)
            dispatch_links = []
            for j, msg in enumerate(msgs):
                raw = email.message_from_bytes(msg[0][1])
                body = get_body(raw)
                subject = get_subject(msg)
                getdate = get_date(msg)
                if 'ACCEPTED' in subject:
                    print(subject, getdate)
                    try:
                        body = body.decode('utf-8')
                        pdflinks = get_links(body)
                        dispatch_links.append(pdflinks)
                    except:
                        print('Bad decode on', getdate)
            print(dispatch_links)

linktest = dispatch_links[0]

if 1 == 1:
    #emails, passwds, ourserver = hiddendata()
    username = em[6]
    password = pw[6]
    path1, path2, path3 = addpaths()
    #outpath = addpath2('dispatch/')

    print('Entering Firefox')
    yesterday = datetime.datetime.strftime(datetime.datetime.now() - timedelta(2), '%m/%d/%Y')
    today = datetime.datetime.today()
    print('This run made at: ', today)
    todaystr = datetime.datetime.today().strftime('%m/%d/%Y')
    startdate = yesterday
    enddate = todaystr
    consets = []

    # for j,startdate in enumerate(startdates):
    # enddate=enddates[j]
    # with Display():
    if 1 == 1:
        success = 0
        iter = 0
        print('profile at', path3)
        browser = webdriver.Firefox(firefox_profile=path3)
        #browser = webdriver.Firefox()
        while success == 0 and iter < 20:
            url1 = 'https://www.centraldispatch.com/login'
            browser.get(linktest)
            print('Got url1')
            time.sleep(2)
            print('Done Sleeping')
            print('Getting xpath')
            selectElem = browser.find_element_by_xpath('//*[@id="pageUsername"]')
            print('Got xpath for Username')
            selectElem.clear()
            selectElem.send_keys(username)
            selectElem = browser.find_element_by_xpath('//*[@id="pagePassword"]')
            print('Got xpath for Password')
            selectElem.clear()
            selectElem.send_keys(password)
            selectElem.submit()
            try:
                browser.switch_to_frame(browser.find_elements_by_tag_name("iframe")[0])
                selectElem = browser.find_element_by_xpath('//*[@id="recaptcha-anchor"]').click()
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
            time.sleep(2)
            selectElem = browser.find_element_by_link_text('Print').click()
            time.sleep(2)
            try:
                tow[j].fn = 'DISP'+tow[j].orderid+'.pdf'
                newfile = path2+'/tmp/'+tow[j].fn
                shutil.move(path2+'/tmp/DispatchSheet.pdf', newfile)
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
    attrs = vars(car[0])
    print(', '.join("%s: %s" % item for item in attrs.items()))
# Now ready to place in database:

#selectElem = browser.find_element_by_xpath('//*[@id="download"]').click()
# browser.quit()

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

from selenium import webdriver
from scrapers import vinscraper

from CCC_system_setup import addpath1, websites, usernames, passwords, addpaths, companydata
from remote_db_connect import tunnel, db
from models import Autos, Accounts, People, Bills
from cronfuncs import newjo
from utils import d2s
from pyvirtualdisplay import Display

cdata = companydata()

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
def limit_text(input):
    if input is not None:
        if len(input)>50: input = input[0:49]
    return input

def addauto(cardata):
    pu = cardata[0].title()
    de = cardata[1]
    od = cardata[3]
    mo = cardata[4].replace('$', '')
    print(mo)
    dt = cardata[5]
    dt = datetime.datetime.strptime(dt, '%m/%d/%y')
    dt = dt.date()
    ncars = cardata[6]
    towcolist = cardata[7].splitlines()
    towco = limit_text(towcolist[0])
    year = cardata[9]
    make = cardata[10].title()
    model = cardata[11].title()
    color = cardata[12].title()
    vin = cardata[13].upper()

    input = Autos(Jo=od, Hjo=None, Year=year, Make=make, Model=model, Color=color, VIN=vin, Title=None, State=None,
                  EmpWeight=None, Dispatched='Horizon Motors', Value=None,
                  TowCompany=towco, TowCost=mo, TowCostEa=mo, Original=None, Status='New', Date1=dt,
                  Date2=None, Pufrom=pu, Delto=de, Ncars=ncars, Orderid=od)
    db.session.add(input)
    db.session.commit()

def addtowco(cardata):
    dt = cardata[5]
    dt = datetime.datetime.strptime(dt, '%m/%d/%y')
    dt = dt.date()
    towcolist = cardata[7].splitlines()
    towco = limit_text(towcolist[0])
    addr1 = towcolist[1].title()
    addr2 = towcolist[2]
    phone = cardata[8]
    input = People(Company=towco, First=None, Middle=None, Last=None, Addr1=addr1,
                   Addr2=addr2, Addr3=None,
                   Idtype=None, Idnumber=None, Telephone=phone, Email=None,
                   Associate1=None,
                   Associate2=None, Date1=dt, Ptype='TowCo', Date2=None, Original=None, Temp1=None,
                   Temp2="New", Accountid=None)
    db.session.add(input)
    db.session.commit()

def addbill(cardata):
    print(cardata)
    pu = cardata[0]
    de = cardata[1]
    od = cardata[3]
    mo = cardata[4].replace('$', '')
    print(mo)
    dt = cardata[5]
    dt = datetime.datetime.strptime(dt, '%m/%d/%y')
    dt = dt.date()
    print(dt)
    ncars = cardata[6]
    towcolist = cardata[7].splitlines()
    towco = limit_text(towcolist[0])
    addr1 = towcolist[1]
    addr2 = towcolist[2]
    print(towco, addr1, addr2)
    phone = cardata[8]
    year = cardata[9]
    make = cardata[10]
    model = cardata[11]
    color = cardata[12]
    vin = cardata[13]
    print(vin)

    today_str = dt.strftime('%Y-%m-%d')
    ckmemo = 'Towing for Dealership Car Purchase'
    bdesc = f'Tow VIN {vin} from {pu} to {de}'
    bamt = d2s(mo)

    nextjo = newjo('HB', today_str)

    pdat = People.query.filter( (People.Ptype == 'TowCo') & (People.Company == towco) ).first()
    if pdat is not None: pid = pdat.id
    else: pid = 0


    input = Bills(Jo=nextjo, Pid=pid, Company=towco, Memo=ckmemo, Description=bdesc, bAmount=bamt, Status='Unpaid',
                  Cache=0, Original='',
                  Ref=None, bDate=dt, pDate=None, pAmount=None, pMulti=None, pAccount=None, bAccount='Towing Horizon Sales',
                  bType='Expense',
                  bCat='Direct', bSubcat='Car Sales', Link=pu, User='Agent', Co='H', Temp1=None, Temp2=od,
                  Recurring=0, dDate=dt,
                  pAmount2='0.00', pDate2=None, Code1=None, Code2=None, CkCache=0, QBi=0, iflag=0, PmtList=None,
                  PacctList=None, RefList=None, MemoList=None, PdateList=None, CheckList=None, MethList=None)

    db.session.add(input)
    db.session.commit()


if 1 == 1:
    username = usernames['disp']
    password = passwords['disp']
    paths = addpaths()
    #outpath = addpath1('dispatch/')

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
        browser = webdriver.Firefox(firefox_profile=paths[4])
        url1 = websites['disp']
        browser.get(url1)
        time.sleep(2)
        try:
            keepgoing = 1
            selectElem = browser.find_element_by_xpath('//*[@id="Username"]')
            selectElem.send_keys(username)
            selectElem.clear()
            selectElem.send_keys(username)
            selectElem = browser.find_element_by_xpath('//*[@id="password"]')
            print(f'Got xpath for Password {password}')
            selectElem.clear()
            selectElem.send_keys(password)
            selectElem = browser.find_element_by_xpath('//*[@id="loginButton"]').click()
            time.sleep(2)
            selectElem = browser.find_element_by_xpath('//*[@id="primary-navbar-collapse"]/ul/li[1]/a').click()
            selectElem = browser.find_element_by_xpath('//*[@id="navMyVehicles"]').click()
            time.sleep(2)
        except:
            keepgoing=0
            print('Could not log onto system and navigate to my vehicles')

        if keepgoing == 1:

            cases = [3,5] #3 is Dispatched and 5 is Delivered
            for case in cases:

                jxlist = []
                cardata = []
                newcardata = []

                try:
                    selectElem = browser.find_element_by_xpath(f'/html/body/view/div/ul/li[{case}]/a').click()
                    time.sleep(2)
                    dispatch_url = browser.current_url

                    selectElem = browser.find_element_by_xpath('/html/body/view/div/div[3]/div[2]')
                    con = selectElem.text
                    res = [int(i) for i in con.split() if i.isdigit()]
                    print(res)
                    ntows = res[0]

                    for ix in range(ntows):
                        jx = ix+1

                        selectElem = browser.find_element_by_xpath(f'/html/body/view/div/form/div/table/tbody/tr[{jx}]/td[3]/a')
                        pickup = selectElem.text
                        print(pickup)

                        selectElem = browser.find_element_by_xpath(f'/html/body/view/div/form/div/table/tbody/tr[{jx}]/td[4]/a')
                        delivery = selectElem.text
                        print(delivery)

                        selectElem = browser.find_element_by_xpath(f'/html/body/view/div/form/div/table/tbody/tr[{jx}]/td[5]/div[1]')
                        car = selectElem.text
                        print(car)

                        selectElem = browser.find_element_by_xpath(f'/html/body/view/div/form/div/table/tbody/tr[{jx}]/td[5]/span')
                        orderid = selectElem.text
                        print(orderid)

                        selectElem = browser.find_element_by_xpath(f'/html/body/view/div/form/div/table/tbody/tr[{jx}]/td[6]/a[1]')
                        towco = limit_text(selectElem.text)
                        print(towco)

                        selectElem = browser.find_element_by_xpath(f'/html/body/view/div/form/div/table/tbody/tr[{jx}]/td[6]/span[3]/span[1]')
                        amount = selectElem.text
                        print(amount)

                        selectElem = browser.find_element_by_xpath(f'/html/body/view/div/form/div/table/tbody/tr[{jx}]/td[7]/strong/span')
                        shipped = selectElem.text
                        print(shipped)

                        dt = datetime.datetime.strptime(shipped, '%m/%d/%y')
                        dt = dt.date()
                        print(dt)

                        adat = Autos.query.filter( (Autos.TowCompany==towco) & (Autos.Date1==dt) ).first()
                        if adat is None:
                            list1 = [pickup, delivery, car, orderid, amount, shipped]
                            cardata.append(list1)
                            jxlist.append(jx)
                        else:
                            print('The tow is already in the system')
                            print(' ')
                except:
                    print(f'No dispataches for case {case}')

                print('jxlist',case,jxlist)
                print('cardata',case,cardata)
                ix = 0
                for jx in jxlist:

                    selectElem = browser.find_element_by_xpath(f'/html/body/view/div/form/div/table/tbody/tr[{jx}]/td[8]/a[2]').click()
                    time.sleep(2)

                    list1 = cardata[ix]
                    ix += 1

                    selectElem = browser.find_element_by_xpath('//*[@id="sheetBottom"]/div[1]/div[1]/h4/span')
                    con = selectElem.text
                    res = [int(i) for i in con.split() if i.isdigit()]
                    try:
                        ncars = res[0]
                    except:
                        ncars = 0
                    print(ncars)
                    list1.append(ncars)


                    selectElem = browser.find_element_by_xpath('//*[@id="sheetDetails"]/div[1]/div[1]/div[2]/div/div[1]/address')
                    address = selectElem.text
                    print(address)
                    list1.append(address)

                    selectElem = browser.find_element_by_xpath('//*[@id="sheetDetails"]/div[1]/div[1]/div[2]/div/div[2]/a[1]')
                    phone = selectElem.text
                    print(phone)
                    list1.append(phone)
                    ilist = [2, 3, 4, 6, 8]

                    if ncars == 1:
                        for kx in ilist:
                            selectElem = browser.find_element_by_xpath(f'//*[@id="sheetBottom"]/div[1]/div[2]/table/tbody/tr/td[{kx}]')
                            item = selectElem.text
                            print(item)
                            list1.append(item)
                        newcardata.append(list1)

                    if ncars > 1:
                        for mx in range(1,ncars+1):
                            thislist = list1
                            for kx in ilist:
                                selectElem = browser.find_element_by_xpath(f'//*[@id="sheetBottom"]/div[1]/div[2]/table/tbody/tr[{mx}]/td[{kx}]')
                                item = selectElem.text
                                print(item)
                                thislist.append(item)

                            newcardata.append(thislist)

                    browser.get(dispatch_url)
                    time.sleep(2)


                #Now update the database:
                for cardata in newcardata:
                    print(cardata)
                    pu=cardata[0]
                    de=cardata[1]
                    od=cardata[3]
                    mo=cardata[4].replace('$','')
                    print(mo)
                    dt=cardata[5]
                    dt = datetime.datetime.strptime(dt, '%m/%d/%y')
                    dt = dt.date()
                    print(dt)
                    ncars = cardata[6]
                    towcolist = cardata[7].splitlines()
                    towco = limit_text(towcolist[0])
                    addr1 = towcolist[1]
                    addr2 = towcolist[2]
                    print(towco,addr1,addr2)
                    phone = cardata[8]
                    year = cardata[9]
                    make = cardata[10]
                    model = cardata[11]
                    color = cardata[12]
                    vin = cardata[13]
                    print(vin)

                    adat = Autos.query.filter( (Autos.TowCompany==towco) & (Autos.Date1==dt) ).first()
                    if adat is None:
                        addauto(cardata)

                    pdat = People.query.filter( (People.Ptype == 'TowCo') & (People.Company == towco) ).first()
                    if pdat is None:
                        addtowco(cardata)

                    bdat = Bills.query.filter( (Bills.Company==towco) & (Bills.bDate == dt) ).first()
                    if bdat is None:
                        addbill(cardata)


tunnel.stop()

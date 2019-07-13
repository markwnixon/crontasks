import pdfkit
import sys
# sys.path.append('/home/mnixon/felrun')

from bs4 import BeautifulSoup as soup

import time
from datetime import datetime, timedelta
import os

from pyvirtualdisplay import Display
from selenium import webdriver
from cronpaths import addpath2
from remote_db_connect import hiddendata


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

     def __init__(self, orderid, towcompany, addr1, addr2, phone, towcost, date1, date2, pufrom, delto, ncars):
        self.orderid=orderid
        self.towcompany=towcompany
        self.addr1=addr1
        self.addr2=addr2
        self.phone=phone
        self.towcost=towcost
        self.date1=date1
        self.date2=date2
        self.pufrom=pufrom
        self.delto=delto
        self.ncars=ncars



def dispatch_finder(dispatch_links):

    emails, passwds, ourserver = hiddendata()
    username = emails[5]
    password = passwds[5]
    outpath = addpath2('dispatch/')
    print('Entering Firefox')
    yesterday = datetime.strftime(datetime.now() - timedelta(2), '%m/%d/%Y')
    today = datetime.today()
    print('This run made at: ', today)
    todaystr = datetime.today().strftime('%m/%d/%Y')
    startdate = yesterday
    enddate = todaystr
    datasets = []
    url_link = dispatch_links[0]
    # for j,startdate in enumerate(startdates):
    # enddate=enddates[j]
    # with Display():
    if 1 == 1:
        success = 0
        iter = 0
        while success == 0 and iter < 20:
            url1 = 'https://www.centraldispatch.com/login'
            browser = webdriver.Firefox()
            browser.get(url_link)
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
                browser.quit()

    for link in dispatch_links:
        browser.get(link)
        time.sleep(2)
        page_data = browser.page_source
        page_soup = soup(page_data, 'html.parser')

        namelist = page_soup.findAll('div', {'class': 'col-xs-12 col-sm-6'})
        towblock = namelist[0].text.splitlines()
        towcomp = []
        phone = ''
        for line in towblock:
            line = line.strip()
            if 'phone' in line.lower():
                line = line.split('hone:', 1)[1]
                phone = line
            if len(line) > 3:
                towcomp.append(line)
        towcomp = towcomp[0:3]+[phone]

        dolblock = namelist[3].text.splitlines()
        for line in dolblock:
            line = line.strip()
            if 'Total Payment' in line:
                line = line.split('Carrier:', 1)[1]
                cost = line.strip()
                cost = cost.replace('$', '')
                print(cost)

        ncardat = page_soup.findAll('span', {'class': 'pull-right'})
        for ndat in ncardat:
            ncar = ndat.text.strip()
            if 'Vehicles' in ncar:
                ncar = ncar.split(':', 1)[1]
                ncar = ncar.strip()
        ncars = int(ncar)
        print('Ncars=', ncars)

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

        delblock = []
        deladdress = pudata[3].address.text
        lines = deladdress.splitlines()
        for line in lines:
            line = line.strip()
            if len(line) > 3 and 'contact' not in line.lower():
                delblock.append(line)
        print(delblock)

        datalist = [0]*ncars
        basedata = [0]*ncars
        for i in range(ncars):
            datalist[i] = []
            tablist = page_soup.findAll('td', {'class': 'hidden-xs'})
            for tab in tablist:
                data = tab.text
                data = data.strip()
                datalist[i].append(data)
            print(datalist[i])
            basedata[i] = [orderid, None, year, make, model, color, vin, None, None, None, 'Horizon Motors', None, carrier, towcost, towcost_each, original, 'New', pudate, deldate, pufrom, 'FEL', orderid']

    browser.quit()

    bdat = Autos.query.filter(Autos.VIN == vin).first()
    if bdat is None or vin == 'NoVIN':
        print("Entering data in Autos database")
        input = Autos(Jo=orderid, Hjo=None, Year=year, Make=make, Model=model, Color=color,
                      VIN=vin, Title=None, State=None, EmpWeight=wt, Dispatched='Horizon Motors', Value=value,
                      TowCompany=carrier, TowCost=payment, TowCostEa=each, Original=original, Status='New',
                      Date1=date1, Date2=date2, Pufrom=pufrom, Delto='FEL', Ncars=ncars, Orderid=orderid)
        db.session.add(input)
        db.session.commit()
        print('This auto not in database, adding to records...')
        print(orderid, year, make, model, color, vin, wt, value,
              carrier, payment, each, ncars, pufrom, original)
        print(' ')

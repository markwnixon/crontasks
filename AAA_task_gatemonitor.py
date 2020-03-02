import sys
from bs4 import BeautifulSoup as soup

import time
from datetime import datetime, timedelta
import os

from pyvirtualdisplay import Display
from selenium import webdriver
import pdfkit

from CCC_system_setup import addpath3, websites, usernames, passwords
from remote_db_connect import tunnel, db
from models import Interchange

printif = 0

runat = datetime.now()
print(' ')
print('_____________________________________________________')
print('This sequence run at ', runat)
print('_____________________________________________________')
print(' ')


# startdates=['4/8/2019','4/9/2019','4/10/2019','4/11/2019','4/12/2019'] #7am
# enddates=['4/9/2019','4/10/2019','4/11/2019','4/12/2019','4/13/2019']#5pm


def gatescraper(printif):

    username = usernames['gate']
    password = passwords['gate']
    print('username,password=',username,password)

    outpath = addpath3('interchange/')
    print('Entering Firefox') if printif == 1 else 1
    yesterday = datetime.strftime(datetime.now() - timedelta(1), '%m/%d/%Y')
    #todaystr = datetime.strftime(datetime.now() - timedelta(4), '%m/%d/%Y')
    today = datetime.today()
    cutoff = datetime.now() - timedelta(10)
    cutoff = cutoff.date()
    todaystr = datetime.today().strftime('%m/%d/%Y')
    startdate = yesterday
    enddate = todaystr
    consets = []

    # for j,startdate in enumerate(startdates):
    # enddate=enddates[j]
    with Display():


        url1 = websites['gate']
        browser = webdriver.Firefox()
        browser.get(url1)
        print('Got url1') if printif == 1 else 1
        time.sleep(4)
        print('Done Sleeping') if printif == 1 else 1
        print('Getting xpath') if printif == 1 else 1
        selectElem = browser.find_element_by_xpath('//*[@id="UserName"]')
        print('Got xpath for Username') if printif == 1 else 1
        selectElem.clear()
        selectElem.send_keys(username)

        selectElem = browser.find_element_by_xpath('//*[@id="Password"]')
        print('Got xpath for Password') if printif == 1 else 1
        selectElem.clear()
        selectElem.send_keys(password)
        time.sleep(1)
        selectElem.submit()
        time.sleep(2)
        newurl = browser.current_url
        print('newurl=', newurl, flush=True) if printif == 1 else 1
        newurl = newurl+'#/Report/GateActivity'

        if 2 == 2:

            browser.get(newurl)
            time.sleep(2)
            print('newurl=', newurl, flush=True) if printif == 1 else 1

            selectElem = browser.find_element_by_xpath('//*[@id="StartDate"]')
            selectElem.clear()
            selectElem.send_keys(startdate)
            selectElem = browser.find_element_by_xpath('//*[@id="EndDate"]')
            selectElem.clear()
            selectElem.send_keys(enddate)

            time.sleep(1)
            selectElem.submit()
            time.sleep(7)

            try:
                contentstr = f'//*[@id="completed"]/div/div[1]'
                selectElem = browser.find_element_by_xpath(contentstr)
                con = selectElem.text
                res = [int(i) for i in con.split() if i.isdigit()]
            except:
                res = [0]
                print('No gate transactions reported')
            if len(res) > 0:
                numrec = int(res[0])
            else:
                numrec = 0
            print('Number of Elements in Table = ',numrec) if printif == 1 else 1

            #containers = browser.find_elements_by_xpath('//a[contains(@href,"ticket")]')
            conrecords = []
            for i in range(1,numrec+1):
                cr = []
                for j in range(1,12):
                    contentstr = f'//*[@id="completed"]/div/div[3]/table/tbody/tr[{i}]/td[{j}]'
                    selectElem = browser.find_element_by_xpath(contentstr)
                    con = selectElem.text
                    if j==1:
                        movetyp = selectElem.text.strip()
                        movetyp = movetyp.replace('Full','Load')
                        movetyp = movetyp.replace('Export Dray-Off','Load Out')
                        con = movetyp
                    cr.append(con)
                    if j==3:
                        nc = browser.find_element_by_xpath(f'//*[@id="completed"]/div/div[3]/table/tbody/tr[{i}]/td[{j}]/a')
                        clink = nc.get_attribute('href')
                        cr.append(clink)
                        thiscon = selectElem.text.strip()

                print(cr) if printif == 1 else 1
                dpt = cr[1].split()
                print('dpt=', dpt) if printif == 1 else 1
                mydate = datetime.strptime(dpt[0], '%m/%d/%Y')
                mydate = mydate.date()
                mytime = f'{dpt[1]} {dpt[2]}'
                mytimedt = datetime.strptime(mytime, '%I:%M %p')
                mytime = mytimedt.strftime('%H:%M')
                print('mytime =', mytime) if printif == 1 else 1
                print('cutoff =',cutoff) if printif == 1 else 1
                idat = Interchange.query.filter( (Interchange.Container == thiscon) & (Interchange.Type == movetyp) & (Interchange.Date > cutoff) ).first()
                if idat is None:

                    contype = f'{cr[4]} {cr[5]} {cr[6]}'
                    input = Interchange(Container=thiscon, TruckNumber='NAY', Driver='NAY', Chassis=cr[8],
                                        Date=mydate, Release=cr[11], GrossWt='NAY', Seals='NAY', ConType=contype, CargoWt='NAY',
                                        Time=mytime, Status='AAAAAA', Original='NAY', Path=cr[7], Type=movetyp, Jo='NAY', Company='NAY', Other=None)
                    db.session.add(input)
                    db.session.commit()
                    print(f'***Adding {thiscon} {movetyp} on {mydate} at {mytime} to database')
                    conrecords.append(cr)
                else:
                    print(f'Record for {thiscon} {movetyp} on {mydate} at {mytime} already in database')

            #These are the records that will be put in database
            for rec in conrecords:

                thiscon = rec[2]
                movetyp = rec[0]
                clink = rec[3]
                browser.get(clink)
                time.sleep(2)
                conset = {}
                con_data = browser.page_source
                page_soup = soup(con_data, 'html.parser')
                keys = ['TRUCK NUMBER:', 'Chassis:','SCALE WT:', 'GROSS WT:', 'CARGO WT:', 'Seals:']
                namelist = page_soup.findAll('span', {'class': 'info-item-label'})
                itemlist = page_soup.findAll('span', {'class': 'info-item-value'})
                for key in keys:
                    for j, name in enumerate(namelist):
                        thisname = name.text.strip()
                        if thisname == key:
                            item = itemlist[j].text.strip()
                            if len(item) > 1:
                                newkey = key.replace(':', '').replace(' ', '_')
                                conset.update({newkey: item})
                                print(key, item) if printif == 1 else 1
                            else:
                                print('Not valid:', key, item) if printif == 1 else 1

                idat = Interchange.query.filter(
                    (Interchange.Container == thiscon) & (Interchange.Type == movetyp)).first()

                if idat is not None:

                    type = movetyp.upper()
                    type = type.replace(' ', '_')
                    viewfile = thiscon + '_' + type + '.pdf'

                    idat.Chassis = conset.get("Chassis")
                    idat.TruckNumber = conset.get("TruckNumber")
                    idat.GrossWt = conset.get("GrossWt")
                    idat.CargoWt = conset.get("CargoWt")
                    idat.Seals = conset.get("Seals")
                    idat.Original = viewfile

                    db.session.commit()

                    pdfkit.from_string(con_data, outpath+viewfile)
                    outpath = addpath3('interchange/')
                    newfile = outpath + viewfile
                    copyline = f'scp {newfile} {websites["ssh_data"]+"vinterchange"}'
                    print('copyline=',copyline)
                    os.system(copyline)
                    os.remove(newfile)

        browser.quit()
    return


gatescraper(printif)
tunnel.stop()
#sys.exit('Gatescraping completed and interchange insert executed...')

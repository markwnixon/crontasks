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

import pdfkit

# startdates=['4/8/2019','4/9/2019','4/10/2019','4/11/2019','4/12/2019'] #7am
# enddates=['4/9/2019','4/10/2019','4/11/2019','4/12/2019','4/13/2019']#5pm


def gatescraper():

    emails, passwds, ourserver = hiddendata()
    username = emails[0]
    password = passwds[0]
    outpath = addpath2('interchange/')
    print('Entering Firefox')
    yesterday = datetime.strftime(datetime.now() - timedelta(2), '%m/%d/%Y')
    today = datetime.today()
    print('This run made at: ', today)
    todaystr = datetime.today().strftime('%m/%d/%Y')
    startdate = yesterday
    enddate = todaystr
    consets = []

    # for j,startdate in enumerate(startdates):
    # enddate=enddates[j]
    with Display():

        url1 = 'https://voyagertrack.portsamerica.com/'
        browser = webdriver.Firefox()
        browser.get(url1)
        print('Got url1')
        time.sleep(2)
        print('Done Sleeping')
        print('Getting xpath')
        selectElem = browser.find_element_by_xpath('//*[@id="UserName"]')
        print('Got xpath for Username')
        selectElem.clear()
        selectElem.send_keys(username)

        selectElem = browser.find_element_by_xpath('//*[@id="Password"]')
        print('Got xpath for Password')
        selectElem.clear()
        selectElem.send_keys(password)
        time.sleep(1)
        selectElem.submit()
        time.sleep(2)
        newurl = browser.current_url
        print('newurl=', newurl, flush=True)
        newurl = newurl+'#/Report/GateActivity'

        if 2 == 2:

            browser.get(newurl)
            time.sleep(2)
            print('newurl=', newurl, flush=True)

            selectElem = browser.find_element_by_xpath('//*[@id="StartDate"]')
            selectElem.clear()
            selectElem.send_keys(startdate)
            selectElem = browser.find_element_by_xpath('//*[@id="EndDate"]')
            selectElem.clear()
            selectElem.send_keys(enddate)

            time.sleep(1)
            selectElem.submit()
            time.sleep(7)
            # selectElem=browser.find_element_by_xpath('//select[@id="completed"]/option[text()=')
            # //*[@id="completed"]/div/div[4]/div/ul[1]/li/select

            # b.find_element_by_xpath("//select[@name='element_name']/option[text()='option_text']").click()
        # selectList=browser.find_elements_by_xpath('//*[@id="completed"]')
        #hrefs = browser.find_elements_by_tag_name('a')
        # for href in hrefs:
            # print(href.text)
            clinks = []
            containers = browser.find_elements_by_xpath('//a[contains(@href,"ticket")]')
            for container in containers:
                if len(container.text) == 11:
                    clink = container.get_attribute('href')
                    clinks.append(clink)
                    print('For Container:', container.text, 'Link=', clink)

            print(' ')
            print('Number of tickets in pile: ', len(clinks))
            print(' ')

            for clink in clinks:
                print(' ')
                print(' ')

                browser.get(clink)
                time.sleep(2)
                con_data = browser.page_source
                page_soup = soup(con_data, 'html.parser')
                item = page_soup.find('div', {'class': 'quarterpage header-normal'})
                movetype = item.text
                conset = {'Type': movetype}
                print('Movetype=', movetype)
                item = page_soup.find(
                    'div', {'class': 'quarterpage header-normal header-time-title'})
                try:
                    dandt = item.text.split()
                    mydate = dandt[0]
                    mytime = dandt[1]
                except:
                    mydate = 'NA'
                    mytime = 'NA'
                print('Date=', mydate)
                print('Time=', mytime)
                conset.update({'Date': mydate})
                conset.update({'Time': mytime})
                keys = ['RELEASE:', 'CONTAINER:', 'SIZE/TYPE:', 'TRUCK NUMBER:', 'CHASSIS:',
                        'SCALE WT:', 'GROSS WT:', 'CARGO WT:', 'SEALS:', 'IN TIME:', 'DRIVER:']
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
                                print(key, item)
                            else:
                                print('Not valid:', key, item)

                container = conset.get("CONTAINER")
                type = conset.get("Type")
                type = type.replace(' ', '_')
                viewfile = container+'_'+type+'.pdf'
                # If file exists then we dont need another copy:
                exists = os.path.isfile(outpath+viewfile)
                if not exists:
                    pdfkit.from_string(con_data, outpath+viewfile)
                conset.update({'Viewfile': viewfile})
                consets.append(conset)

        browser.quit()
        print(consets)
    return consets


def interchange_insert(consets):

    from remote_db_connect import db, tunnel
    from models2 import Interchange

    for obj in consets:
                # Search for things that are the keywords:
        driverlist = ['Ghanem', 'Davis', 'Alameh', 'Tibbs', 'Khoder']
        obj.update({'DRIVER': 'NFI'})

        chassis = obj.get("CHASSIS")
        if chassis == 'NFI':
            chassis = 'OWN'

        trucknum = obj.get("TRUCK_NUMBER")
        if '87' in trucknum:
            driver = 'Hassan Khoder'
            trucknum = '870F36'
        else:
            driver = 'Darrell Tibbs'

        type = obj.get("Type")
        typedef = 'Empty Out'
        if type == 'EMPTY IN':
            typedef = 'Empty In'
        elif type == 'LOAD IN':
            typedef = 'Load In'
        elif type == 'LOAD OUT':
            typedef = 'Load Out'

        container = obj.get("CONTAINER")
        #print('Looking in Database for....',container,typedef)

        idat = Interchange.query.filter(
            (Interchange.CONTAINER == container) & (Interchange.TYPE == typedef)).first()
        if idat is None:
            # Check to see if this file is in database already
            input = Interchange(CONTAINER=container, TRUCK_NUMBER=trucknum, DRIVER=driver, CHASSIS=chassis,
                                Date=obj.get("Date"), RELEASE=obj.get("RELEASE"), GROSS_WT=obj.get("GROSS_WT"), SEALS=obj.get("SEALS"),
                                CONTYPE=obj.get("SIZE/TYPE"), CARGO_WT=obj.get("CARGO_WT"),
                                Time=obj.get("Time"), Status='AAAAAA', Original=obj.get("Viewfile"), Path='NFI', TYPE=typedef, Jo='NAY', Company='NAY')
           # if missing is None:
            print('Data is being added to database: interchange data for container:',
                  container, ' ', typedef)
            db.session.add(input)
            db.session.commit()
            error = 0
        else:
            print('This container and move are in database already: ', container, ' ', typedef)
            error = 0

        original = obj.get("Viewfile")
        outpath = addpath2('interchange/')
        newfile = outpath+original
        pythonline = ' mnixon@ssh.pythonanywhere.com:/home/mnixon/felrun/tmp/data/vinterchange'
        copyline = 'scp '+newfile+pythonline
        if idat is None:
            os.system(copyline)
        os.remove(newfile)
    tunnel.stop()
    return


consets = gatescraper()
interchange_insert(consets)
sys.exit('Gatescraping completed and interchange insert executed...')

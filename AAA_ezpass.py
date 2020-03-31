from CCC_system_setup import scac, mycompany, usernames, passwords, websites
from remote_db_connect import tunnel, db
from models import Tolls, Vehicles

import time
import datetime
import os

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from random import randint

from pytesseract import image_to_string
from PIL import Image

tdata = Vehicles.query.filter(Vehicles.Ezpassxponder != None).all()
for tdat in tdata:
    print(tdat.Unit, tdat.Ezpassxponder)


printif = 0

with Display():
#if 1 == 1:
    url1 = websites['ezpass']
    driver = webdriver.Firefox()
    driver.set_window_size(1920,1080)
    driver.get(url1)
    time.sleep(7)

    # find part of the page you want image of
    element = driver.find_element_by_xpath('//*[@id="templatecontent"]/div/form/span/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[8]/td[4]/span/img')
    location = element.location
    size = element.size
    driver.save_screenshot('screenshot.png')
    im = Image.open('screenshot.png')
    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']
    im = im.crop((left, top, right, bottom))  # defines crop points
    im.save('screenshotj.png')
    captcha_text = image_to_string(Image.open('screenshotj.png'))
    print(captcha_text)

    user_id = driver.find_element_by_xpath('//*[@id="templatecontent"]/div/form/span/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[4]/td[7]/input')
    user_id.clear()
    user_id.send_keys(usernames['ezpass'])

    password = driver.find_element_by_xpath('//*[@id="templatecontent"]/div/form/span/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[5]/td[7]/input')
    password.clear()
    password.send_keys(passwords['ezpass'])

    captcha = driver.find_element_by_xpath('//*[@id="templatecontent"]/div/form/span/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[8]/td[7]/input')
    captcha.clear()
    captcha.send_keys(captcha_text)
    driver.find_element_by_xpath('//*[@id="btnLogin"]').click()

    time.sleep(7)
    driver.find_element_by_xpath('//*[@id="menu"]/ul/li[10]/a').click()
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="menu"]/ul/li[12]/a').click()
    time.sleep(1)

    # Select a tolls cutoff date
    # Uncomment these lines as needed to search way back:
    #startdate = datetime.datetime(2020, 1, 1)
    #enddate = startdate + datetime.timedelta(7)message

    #Use these lines for daily updates script
    enddate = datetime.datetime.today()
    startdate = enddate - datetime.timedelta(7)

    if enddate > datetime.datetime.today():
        enddate = datetime.datetime.today()
    sdate, edate = startdate.date(), enddate.date()
    sds, eds = sdate.strftime("%m/%d/%Y"), edate.strftime("%m/%d/%Y")

    while sdate < datetime.date.today():

        for tdat in tdata:
            unit = tdat.Unit
            tran = tdat.Ezpassxponder

            # Default for website is posting date.  Have to use posting date for daily updates
            # Because it takes so long for some transaction to post
            #datetype = Select(driver.find_element_by_xpath('//*[@id="tr_dateType"]/td[4]/select'))
            #datetype.select_by_visible_text('Transaction Date')

            datestart = driver.find_element_by_xpath('//*[@title="Start Date"]')
            datestart.clear()
            datestart.send_keys(sds)

            datestop= driver.find_element_by_xpath('//*[@title="End Date"]')
            datestop.clear()
            datestop.send_keys(eds)

            datestop= driver.find_element_by_xpath('//*[@title="Transponder Number"]')
            datestop.clear()
            datestop.send_keys(tran)

            driver.find_element_by_xpath('//*[@id="btnSearch"]').click()

            time.sleep(3)

            try:

                contentstr = '/html/body/div/table/tbody/tr[5]/td[2]/table/tbody/tr[2]/td/div/form/span/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[3]/td[2]/span/table/thead/tr/td/table/tbody/tr/td[2]/table/tbody/tr/td[3]'
                selectElem = driver.find_element_by_xpath(contentstr)
                num_records = selectElem.text
                num_records = int(num_records.replace(' items','').replace(' item',''))
                print(num_records)
            except:
                print('No Transactions Found')
                num_records = 0

            if num_records > 0:

                for jx in range(2, 2+num_records):
                #if 1 == 2:
                    contentstr = f'/html/body/div/table/tbody/tr[5]/td[2]/table/tbody/tr[2]/td/div/form/span/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[3]/td[2]/span/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[{jx}]/td[2]/div'
                    selectElem = driver.find_element_by_xpath(contentstr)
                    mydate = selectElem.text

                    contentstr = f'/html/body/div/table/tbody/tr[5]/td[2]/table/tbody/tr[2]/td/div/form/span/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[3]/td[2]/span/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[{jx}]/td[9]/div'
                    selectElem = driver.find_element_by_xpath(contentstr)
                    mytime = selectElem.text

                    contentstr = f'/html/body/div/table/tbody/tr[5]/td[2]/table/tbody/tr[2]/td/div/form/span/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[3]/td[2]/span/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[{jx}]/td[10]/div'
                    selectElem = driver.find_element_by_xpath(contentstr)
                    plaza = selectElem.text

                    contentstr = f'/html/body/div/table/tbody/tr[5]/td[2]/table/tbody/tr[2]/td/div/form/span/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[3]/td[2]/span/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr[{jx}]/td[13]'
                    selectElem = driver.find_element_by_xpath(contentstr)
                    amount = selectElem.text.strip()
                    amount = amount[1:]
                    amount = amount.replace('$','')

                    dstring = mydate + 'T' + mytime
                    dt_time = datetime.datetime.strptime(dstring, "%m/%d/%YT%H:%M:%S")
                    tdate = dt_time.date()

                    print('Found: ',jx,unit,mydate,mytime,plaza,amount,dt_time)
                    tolldat = Tolls.query.filter( (Tolls.Datetm == dt_time) & (Tolls.Unit==unit) ).first()
                    if tolldat is None:
                        print('Adding: ', jx, unit, mydate, mytime, plaza, amount, dt_time)
                        input=Tolls(Date = tdate,Datetm=dt_time,Plaza = plaza,Amount=amount,Unit=unit)
                        db.session.add(input)
                        db.session.commit()

            # Cycle for next Unit
            driver.find_element_by_xpath('//*[@id="menu"]/ul/li[12]/a').click()
            time.sleep(1)

        startdate = startdate + datetime.timedelta(8)
        enddate = enddate + datetime.timedelta(8)
        if enddate > datetime.datetime.today():
            enddate = datetime.datetime.today()
        sdate, edate = startdate.date(), enddate.date()
        sds, eds = sdate.strftime("%m/%d/%Y"), edate.strftime("%m/%d/%Y")
        print(sds, eds)



driver.quit()
tunnel.stop()
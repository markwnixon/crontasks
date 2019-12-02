from pyvirtualdisplay import Display
from selenium import webdriver

#import bs4
#from urllib.request import urlopen as ureq
from bs4 import BeautifulSoup as soup
import datetime
import time
import operator

from email_reports import emailshipreport

from CCC_system_setup import mycompany
co = mycompany()
if co == 'FELA':
    from CCC_FELA_remote_db_connect import tunnel, db
    from CCC_FELA_models import Bookings, OverSeas, FELBills
elif co == 'OSLM':
    from CCC_OSLM_remote_db_connect import tunnel, db
    from CCC_OSLM_models import Bookings, OverSeas

today=datetime.date.today()
fromday=today-datetime.timedelta(days=60)
futureday=today+datetime.timedelta(days=10)
#bookings=Bookings.query.filter((Bookings.SailDate<advday) & (Bookings.EstArr>dragday)).order_by(Bookings.EstArr).all()
odata=OverSeas.query.filter((OverSeas.PuDate<futureday) & (OverSeas.PuDate>fromday)).all()

def convert_date_dt(indate,inform):
    adate = indate[0:11]
    adate = adate.strip()
    adatedt = datetime.datetime.strptime(adate, inform)
    return adatedt.date()

def convert_date(indate,inform):
    adate = indate[0:11]
    adate = adate.strip()
    adatedt = datetime.datetime.strptime(adate, inform)
    adatedt = adatedt.date()
    delta = adatedt - today
    daysaway = delta.days
    date1str = adatedt.strftime('%Y-%m-%d')

    return date1str, daysaway


with Display():
#if 1 == 1:
    browser = webdriver.Firefox()
    browser.set_window_size(1920, 1080)
    tabdata=[]

    for odat in odata:
        bk = odat.Booking
        container = odat.Container
        container = container[0:11]  # in case we added letters to designate street turn
        container = container.strip()
        try:
            lcon = len(container)
        except:
            lcon = 0

        book = Bookings.query.filter(Bookings.Booking == bk).first()
        if book is not None:
            adate='Not Found'
            seastatus='Unknown'
            portstatus='Unknown'
            daysaway=0
            date2dt = book.EstArr
            depdate_dt = book.SailDate
            date2str = date2dt.strftime('%Y-%m-%d')
            bk = book.Booking
            shipline = book.Line

            time.sleep(2)
            if shipline == 'Maersk' and lcon > 9:
                print(f'Looking for {container}')
                #browser = webdriver.Firefox()
                #browser.set_window_size(1920, 1080)
                url='https://www.maersk.com/tracking/#tracking/'+container
                browser.get(url)
                time.sleep(3)
                try:
                    contentstr = '//*[@id="table_id"]/tbody/tr/td[3]/span[4]'
                    selectElem = browser.find_element_by_xpath(contentstr)
                    adate = selectElem.text
                    print(f'Container {container} arrives on {adate}')
                except:
                    print('Could not find element')
                try:
                    date1str, daysaway = convert_date(adate,'%d %b %Y')
                    arrdate_dt = convert_date_dt(adate, '%d %b %Y')
                except:
                    try:
                        date1str, daysaway = convert_date(adate2, '%d %b %Y')
                        arrdate_dt = convert_date_dt(adate2, '%d %b %Y')
                    except:
                        daysaway = 0
                        date1str = date2str
                        arrdate_dt = book.EstArr
                checkdate = arrdate_dt - book.EstArr
                checkdate = checkdate.days


                allstatus = 'Not Left Yet'
                if today > depdate_dt:
                    allstatus = 'At Sea'
                if today >= arrdate_dt:
                    allstatus = 'Arrived'

            elif shipline == 'Hoegh':

                url='https://www.hoeghautoliners.com/my-cargo'
                browser.get(url)
                time.sleep(2)

                booksend = browser.find_element_by_xpath('//*[@id="booking-or-bl"]')
                booksend.send_keys(bk)
                time.sleep(1)

                browser.find_element_by_xpath('//*[@id="btn-send"]').click()

                time.sleep(1)

                contentstr = f'//*[@id="my-cargo-result"]/ul/li[1]/div[1]'
                selectElem = browser.find_element_by_xpath(contentstr)
                selectElem.click()

                time.sleep(1)

                contentstr = f'//*[@id="my-cargo-result"]/ul/li[1]/div[2]/table/tbody/tr[2]/td[2]'
                selectElem = browser.find_element_by_xpath(contentstr)
                voyage = selectElem.text

                contentstr = f'//*[@id="my-cargo-result"]/ul/li[1]/div[2]/table/tbody/tr[3]/td[2]'
                selectElem = browser.find_element_by_xpath(contentstr)
                lport = selectElem.text

                contentstr = f'//*[@id="my-cargo-result"]/ul/li[1]/div[2]/table/tbody/tr[5]/td[2]'
                selectElem = browser.find_element_by_xpath(contentstr)
                depdate = selectElem.text
                depdate_dt = convert_date_dt(depdate, '%d.%m.%Y')

                contentstr = f'//*[@id="my-cargo-result"]/ul/li[1]/div[2]/table/tbody/tr[6]/td[2]'
                selectElem = browser.find_element_by_xpath(contentstr)
                disport = selectElem.text

                contentstr = f'//*[@id="my-cargo-result"]/ul/li[1]/div[2]/table/tbody/tr[7]/td[2]'
                selectElem = browser.find_element_by_xpath(contentstr)
                arrdate = selectElem.text
                date1str, daysaway = convert_date(arrdate, '%d.%m.%Y')
                arrdate_dt = convert_date_dt(arrdate, '%d.%m.%Y')

                checkdate = arrdate_dt - book.EstArr
                checkdate = checkdate.days

                allstatus = 'Not Left Yet'
                if today > depdate_dt:
                    allstatus = 'At Sea'
                if today >= arrdate_dt:
                    allstatus = 'Arrived'

                print(voyage, lport, depdate, disport, arrdate)

                # This site will not allow refresh or resubmit of URL.  Must quit to clear so can get another book.
                browser.quit()
                browser = webdriver.Firefox()
                browser.set_window_size(1920, 1080)

            # Get payment status:
            bdat = Bills.query.filter( (Bills.Memo.contains(bk)) | (Bills.Description.contains(bk)) ).first()
            if bdat is not None:
                pay = 'Paid'
            else:
                pay = 'Pmt Due'

            if (shipline == 'Hoegh' or (shipline == 'Maersk' and lcon > 9)) and daysaway > -10 and checkdate < 40:
                tabdata.append([str(daysaway),allstatus,date1str,pay,date2str,bk,container,book.Vessel,odat.BillTo,odat.Exporter])



    print('Days','Status','ArriveUpdate','Release Pmt', 'PlannedArrive','Booking','Container','Vessel','BillTo','Exporter')
    newtabdata = sorted(tabdata, key = operator.itemgetter(2))
    for tab in newtabdata:
        print(tab[:10])
    emailshipreport(newtabdata)

browser.quit()
tunnel.stop()
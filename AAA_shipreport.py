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
    try:
        adate = indate[0:11]
        adate = adate.strip()
        adatedt = datetime.datetime.strptime(adate, inform)
        adatedt = adatedt.date()
        delta = adatedt - today
        daysaway = delta.days
        date1str = adatedt.strftime('%Y-%m-%d')
    except:
        daysaway = 0
        date1str = date2str

    return date1str, daysaway


with Display():
#if 1 == 1:

    tabdata=[]

    for odat in odata:
        bk = odat.Booking
        container = odat.Container
        container = container[0:11]  # in case we added letters to designate street turn
        container = container.strip()

        book = Bookings.query.filter(Bookings.Booking == bk).first()
        if book is not None:
            adate='Not Found'
            seastatus='Unknown'
            portstatus='Unknown'
            daysaway=0
            date2dt = book.EstArr
            date2str = date2dt.strftime('%Y-%m-%d')
            bk = book.Booking
            shipline = book.Line

            time.sleep(2)
            if shipline == 'Maersk':
                browser = webdriver.Firefox()
                browser.set_window_size(1920, 1080)
                url='https://www.maersk.com/tracking/#tracking/'+container
                browser.get(url)
                time.sleep(1)
                site_data=browser.page_source
                page_soup=soup(site_data,'html.parser')
                allspans=[item.get_text(strip=True) for item in page_soup.select("span")]
                for j,span in enumerate(allspans):
                    #print(j,span)
                    if 'Estimated arrival' in span:
                        adate=allspans[j+1]
                        seastatus='At Sea'
                        portstatus='Left Port'
                    if 'Arrival date' in span:
                        adate=allspans[j+1]
                        seastatus='Has Arrived'
                        portstatus='Has Arrived'
                    if 'Load' in span:
                        adate2=allspans[j+1]
                        portstatus='Left Port'
                    if 'Gate in' in span:
                        adate2=allspans[j+1]
                        portstatus='Still at Port'
                        seastatus='Still at Port'

                    date1str, daysaway = convert_date(adate,'%d %b %Y')

                    if portstatus=='Has Arrived':
                        allstatus='Arrived'
                    elif portstatus=='Left Port' and seastatus=='At Sea':
                        allstatus='At Sea'
                    elif portstatus=='Still at Port':
                        allstatus='Not Left Yet'
                    else:
                        allstatus = 'Unknown'

                browser.quit()

            elif shipline == 'Hoegh':
                browser = webdriver.Firefox()
                browser.set_window_size(1920, 1080)
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
                allstatus = 'Not Left Yet'
                if today > depdate_dt:
                    allstatus = 'At Sea'
                if today >= arrdate_dt:
                    allstatus = 'Arrived'

                print(voyage, lport, depdate, disport, arrdate)

                browser.quit()

            # Get payment status:
            bdat = FELBills.query.filter( (FELBills.Memo.contains(bk)) | (FELBills.Description.contains(bk)) ).first()
            if bdat is not None:
                pay = 'Paid'
            else:
                pay = 'Pmt Due'

            if (shipline == 'Hoegh' or shipline == 'Maersk') and daysaway > -5:
                tabdata.append([str(daysaway),allstatus,date1str,pay,date2str,bk,container,book.Vessel,odat.BillTo,odat.Exporter])



    print('Days','Status','ArriveUpdate','Release Pmt', 'PlannedArrive','Booking','Container','Vessel','BillTo','Exporter')
    newtabdata = sorted(tabdata, key = operator.itemgetter(2))
    for tab in newtabdata:
        print(tab[:10])
    #emailshipreport(tabdata)

    
tunnel.stop()
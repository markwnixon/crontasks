from pyvirtualdisplay import Display
from selenium import webdriver

#import bs4
#from urllib.request import urlopen as ureq
from bs4 import BeautifulSoup as soup
import datetime
import time

from email_reports import emailshipreport

from CCC_system_setup import mycompany
co = mycompany()
if co == 'FELA':
    from CCC_FELA_remote_db_connect import tunnel, db
    from CCC_FELA_models import Bookings, OverSeas
elif co == 'OSLM':
    from CCC_OSLM_remote_db_connect import tunnel, db
    from CCC_OSLM_models import Bookings, OverSeas

today=datetime.date.today()
dragday=today-datetime.timedelta(days=20)
advday=today+datetime.timedelta(days=20)
bookings=Bookings.query.filter((Bookings.SailDate<advday) & (Bookings.EstArr>dragday)).order_by(Bookings.EstArr).all()
    
if 1==1:
    print('Running Ship Script',flush=True)
    with Display():
        browser = webdriver.Firefox()
        tabdata=[]

        for book in bookings:
            adate='Not Found'
            seastatus='Unknown'
            portstatus='Unknown'
            daysaway=0
            odat=OverSeas.query.filter(OverSeas.Booking==book.Booking).first()
            if odat is not None:
                container=odat.Container
                container=container[0:11] # in case we added letters to designate street turn
                container=container.strip()
                time.sleep(2)
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
                        
                    try:
                        adate=adate[0:11]
                        adate=adate.strip()
                        adatedt=datetime.datetime.strptime(adate, '%d %b %Y')
                        adatedt=adatedt.date()
                        delta=adatedt-today
                        daysaway=delta.days
                        date1str=adatedt.strftime('%Y-%m-%d')
                    except:
                        daysaway=0
                        date1str='None'
                        
                    date2dt=book.EstArr
                    date2str=date2dt.strftime('%Y-%m-%d')
                    
                    if portstatus=='Has Arrived':
                        allstatus='Arrived'
                    elif portstatus=='Left Port' and seastatus=='At Sea':
                        allstatus='At Sea'
                    elif portstatus=='Still at Port':
                        allstatus='Not Left Yet'
                    else:
                        allstatus = 'Unknown'
                        
                tabdata.append([str(daysaway),allstatus,date1str,date2str,book.Booking,container,book.Vessel,odat.BillTo,odat.Exporter])
    #arrivals=page_soup.findAll('span',{'class':'pseudo-header--data-key'})
    #for arrive in arrivals:
        #print(arrive.text)
    
    
    #print(browser.title) #this should print "Google"

    #finally:
    browser.quit()
    print('Days','Status','ArriveUpdate','PlannedArrive','Booking','Container','Vessel','BillTo','Exporter')
    for tab in tabdata:
        print(tab[:9])
    emailshipreport(tabdata)
    
    
tunnel.stop()
        #print([x for x in tab[:9]])
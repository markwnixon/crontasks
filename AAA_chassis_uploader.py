import time
import datetime
import os

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from random import randint

from statistics import mean
from CCC_system_setup import mycompany, usernames, passwords, websites

co = mycompany()
if co == 'FELA':
    from CCC_FELA_remote_db_connect import tunnel, db
    from CCC_FELA_models import Chassis, Interchange
elif co == 'OSLM':
    from CCC_OSLM_remote_db_connect import tunnel, db
    from CCC_OSLM_models import Chassis, Interchange

from selenium.webdriver.common.action_chains import ActionChains

def chassis_insert(company,datedt,invonum,total,con,cha,amt,days,dateout,datein,booking,rate):
    
    # Check if chassis has been billed (has an invonum) or is an active status update (invo = Not Created)
    adat = Chassis.query.filter((Chassis.InvoNum == 'Not Created') & (Chassis.Chass == cha)).first()
    if adat is not None:
        adat.Date = datedt
        adat.InvoNum = invonum
        adat.Days = days
        adat.Datein = datein
        adat.Dateout = dateout
        adat.Container = con
        if invonum != 'Not Created':
            adat.Total = total
            adat.Amount = amt
            adat.Rate = rate
        db.session.commit()
                 
    cdat = Chassis.query.filter((Chassis.InvoNum == invonum) & (Chassis.Chass == cha)).first()
    if cdat is None:
        input = Chassis(Jo = None, Company = company, Date = datedt, InvoNum = invonum, Total = total, Container = con, Chass = cha, Amount = amt, Days = days, Dateout = dateout, Datein = datein, Booking = booking, Rate = rate, Status = '0', Match = '0')
        db.session.add(input)
        db.session.commit()
        #print('Looking in Database for....',container,typedef)

# Select an invoice cutoff date
today = datetime.datetime.today()
today = today.date()
dt = datetime.datetime.now() - datetime.timedelta(7)
dt = dt.date()
print(dt)
printif = 0

#dt = datetime.datetime(2018,1,1).date()
with Display():
#if 1 == 1:

    url1 = websites['dcli']
    browser = webdriver.Firefox()
    browser.set_window_size(1920,1080)
    
    
    browser.get(url1)
    print('Got url1') if printif == 1 else 1
    time.sleep(7)
    selectElem = browser.find_element_by_xpath('//*[@id="loginLinkATag"]').click()
    time.sleep(5)

    selectElem = browser.find_element_by_xpath('//*[@id="username"]')
    selectElem.clear()
    selectElem.send_keys(usernames['dcli'])

    selectElem = browser.find_element_by_xpath('//*[@id="password"]')
    selectElem.clear()
    selectElem.send_keys(passwords['dcli'])

    selectElem = browser.find_element_by_xpath('//*[@id="loginForm"]/section[4]/div/div[1]/input')
    selectElem.click()

    time.sleep(7)

    # Now we are on the invoice page and need to go through each invoice listed.
    # Lets start by getting the date for each invoice so we can decide which invoices we want to collect

    contentstr = f'//*[@id="content"]/div[1]/div/div[2]/div[5]/span[2]'
    selectElem = browser.find_element_by_xpath(contentstr)
    num_invoices = int(selectElem.text)
    print(num_invoices) if printif == 1 else 1

    for i in range(1,num_invoices+1):

        try:
            contentstr = f'//*[@id="content"]/div[1]/div/div[2]/div[4]/div[2]/div/div[2]/div[{i}]'
            selectElem = browser.find_element_by_xpath(contentstr)
            thisdate = selectElem.text
            #Keep the table scrolling down so we can capture everything    
            print(thisdate) if printif == 1 else 1
            dlist = thisdate.split()
            datestr = dlist[0]
            datedt=datetime.datetime.strptime(datestr,'%m/%d/%Y')
            datedt = datedt.date()
            
            if datedt > dt:
                
                # Get the invoice amount:
                contentstr = f'//*[@id="content"]/div[1]/div/div[2]/div[4]/div[2]/div/div[4]/div[{i}]'
                selectElem = browser.find_element_by_xpath(contentstr)
                iamount = selectElem.text
                
                # Get the invoice number (get this last so we can click on it:
                contentstr = f'//*[@id="content"]/div[1]/div/div[2]/div[4]/div[2]/div/div[3]/div[{i}]'
                selectElem = browser.find_element_by_xpath(contentstr)
                invoicenum = selectElem.text
                           
                #Go to details page
                print(f'Getting details for invoice {i} from date {datestr} with invoice number {invoicenum} for {iamount}') if printif == 1 else 1
                
                #Click on invoicenum and then click for details:
                selectElem.click()
                button = browser.find_element_by_xpath('//*[@id="content"]/div[1]/div/div[2]/div[2]/div[2]/div[1]/button')
                button.click()
                time.sleep(5)
                
                #Now grab the details...
                contentstr = f'//*[@id="content"]/div[1]/div[3]/div[6]/span[2]'
                selectElem = browser.find_element_by_xpath(contentstr)
                num_records = int(selectElem.text)
                print('num_records =',num_records ) if printif == 1 else 1
                for j in range(1,num_records+1):
                    try:
                        contentstr = f'//*[@id="content"]/div[1]/div[3]/div[5]/div[2]/div/div[2]/div[{j}]'
                        selectElem = browser.find_element_by_xpath(contentstr)
                        con = selectElem.text
                        
                        contentstr = f'//*[@id="content"]/div[1]/div[3]/div[5]/div[2]/div/div[3]/div[{j}]'
                        selectElem = browser.find_element_by_xpath(contentstr)
                        cha = selectElem.text
                        cha = cha.strip()
                        cha = cha.replace(' ','')
                        
                        contentstr = f'//*[@id="content"]/div[1]/div[3]/div[5]/div[2]/div/div[4]/div[{j}]'
                        selectElem = browser.find_element_by_xpath(contentstr)
                        amt = selectElem.text
                        
                        contentstr = f'//*[@id="content"]/div[1]/div[3]/div[5]/div[2]/div/div[13]/div[{j}]'
                        selectElem = browser.find_element_by_xpath(contentstr)
                        days = selectElem.text
                        
                        contentstr = f'//*[@id="content"]/div[1]/div[3]/div[5]/div[2]/div/div[16]/div[{j}]'
                        selectElem = browser.find_element_by_xpath(contentstr)
                        dateout = selectElem.text
                        
                        contentstr = f'//*[@id="content"]/div[1]/div[3]/div[5]/div[2]/div/div[15]/div[{j}]'
                        selectElem = browser.find_element_by_xpath(contentstr)
                        datein = selectElem.text
                        
                        contentstr = f'//*[@id="content"]/div[1]/div[3]/div[5]/div[2]/div/div[14]/div[{j}]'
                        selectElem = browser.find_element_by_xpath(contentstr)
                        rate = selectElem.text
                        
                        contentstr = f'//*[@id="content"]/div[1]/div[3]/div[5]/div[2]/div/div[19]/div[{j}]'
                        selectElem = browser.find_element_by_xpath(contentstr)
                        booking = selectElem.text
                        
                        print(f'Invoice {invoicenum} Total Amt {iamount} Container is {con} Chassis is {cha} and Charge is {amt} for Days: {days}')
                        print(f'Chassis {con} went out on {dateout} and returned on {datein} on booking {booking} at rate {rate}')
                        print(' ')
                        chassis_insert('DCLI',datedt,invoicenum,iamount,con,cha,amt,days,dateout,datein,booking,rate)
                        
                    except:
                        print('Failed')
                        break
                        
                selectElem = browser.find_element_by_xpath('//*[@id="content"]/div[1]/ol/li[1]/a').click()
                time.sleep(5)
                
                #Now have to click on 
        except:
            print('Cannot find this element, so loop is broken')
            break
        
        
    selectElem = browser.find_element_by_xpath('//*[@id="activityTab"]/a')
    selectElem.click()
    time.sleep(3)

    #Now grab the details of recent activity

    try:
        contentstr = f'//*[@id="activitiesTabContent"]/div[3]/div[5]/span[2]'
        selectElem = browser.find_element_by_xpath(contentstr)
        num_records = int(selectElem.text)
        print('num_unbilled_records =', num_records)

        for j in range(1, num_records+1):

            try:
                contentstr = f'//*[@id="activitiesTabContent"]/div[3]/div[4]/div[2]/div/div[4]/div[{j}]'
                selectElem = browser.find_element_by_xpath(contentstr)
                con = selectElem.text

                contentstr = f'//*[@id="activitiesTabContent"]/div[3]/div[4]/div[2]/div/div[5]/div[{j}]'
                selectElem = browser.find_element_by_xpath(contentstr)
                cha = selectElem.text
                cha = cha.strip()
                cha = cha.replace(' ', '')

                contentstr = f'//*[@id="activitiesTabContent"]/div[3]/div[4]/div[2]/div/div[8]/div[{j}]'
                selectElem = browser.find_element_by_xpath(contentstr)
                type = selectElem.text

                contentstr = f'//*[@id="activitiesTabContent"]/div[3]/div[4]/div[2]/div/div[12]/div[{j}]'
                selectElem = browser.find_element_by_xpath(contentstr)
                days = selectElem.text

                contentstr = f'//*[@id="activitiesTabContent"]/div[3]/div[4]/div[2]/div/div[13]/div[{j}]'
                selectElem = browser.find_element_by_xpath(contentstr)
                dateout = selectElem.text

                contentstr = f'//*[@id="activitiesTabContent"]/div[3]/div[4]/div[2]/div/div[14]/div[{j}]'
                selectElem = browser.find_element_by_xpath(contentstr)
                datein = selectElem.text

                contentstr = f'//*[@id="activitiesTabContent"]/div[3]/div[4]/div[2]/div/div[15]/div[{j}]'
                selectElem = browser.find_element_by_xpath(contentstr)
                booking = selectElem.text

                #Sometimes website does not provide all the numbers in a container here.  Double check and get elsewhere
                lcon = len(con)
                if lcon < 11:
                    idat = Interchange.query.filter(Interchange.RELEASE == booking).first()
                    if idat is not None:
                        con = idat.CONTAINER
                    else:
                        idat2 = Interchange.query.filter(Interchange.CONTAINER.contains(con)).first()
                        if idat2 is not None:
                            con = idat2.CONTAINER

                if len(datein)<5:
                    datein = 'Still Out'
                print(f'Current Unbilled Activity: Container is {con} Chassis is {cha} Days: {days}')
                print(f'Chassis {con} went out on {dateout} and returned on {datein} on booking {booking} at rate {rate}')
                print(' ')
                chassis_insert('DCLI',today,'Not Created','0.00',con,cha,'0.000',days,dateout,datein,booking,type)


            except:
                print('Cannot find element so loop is broken')
                break
    except:
        print('No recent activity reported here')

    browser.quit()

tunnel.stop()
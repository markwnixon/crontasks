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
    from CCC_FELA_models import Chassis, Interchange, FELBills, People
elif co == 'OSLM':
    from CCC_OSLM_remote_db_connect import tunnel, db
    from CCC_OSLM_models import Chassis, Interchange

from selenium.webdriver.common.action_chains import ActionChains

def chassis_insert(company,datedt,invonum,total,con,cha,amt,days,dateout,datein,booking,rate):

    cdat = Chassis.query.filter((Chassis.InvoNum == invonum) & (Chassis.Date == datedt) ).first()
    if cdat is None:
        input = Chassis(Jo = None, Company = company, Date = datedt, InvoNum = invonum, Total = total, Container = con, Chass = cha, Amount = amt, Days = days, Dateout = dateout, Datein = datein, Booking = booking, Rate = rate, Status = '0', Match = '0')
        db.session.add(input)
        db.session.commit()

def bills_insert(co, datedt, datedue, invonum, invoamt, status):

    bdat = FELBills.query.filter((FELBills.bDate == datedt) & (FELBills.bAmount == invoamt)).first()
    if bdat is None:
        pdat = People.query.filter(People.Company == co).first()
        company = pdat.Company
        aid = pdat.id
        billno = invonum
        memo = invonum
        bdesc = 'Monthly Chassis Rentals'
        input = FELBills(Jo=billno, Pid=aid, Company=co, Memo=memo, Description=bdesc, bAmount=invoamt, Status='Unpaid',
                         Cache=0, Original=None,
                         Ref='', bDate=datedt, pDate=None, pAmount='0.00', pMulti=None, pAccount='FEL Citibank',
                         bAccount='Equipment Rental', bType='Expensse',
                         bCat='Direct', bSubcat='Trucking', Link=None, User='Robot', Co='F', Temp1=None, Temp2=None,
                         Recurring=0, dDate=datedue, pAmount2='0.00', pDate2=None)
        db.session.add(input)
        db.session.commit()
        # Now change the bill number:
        bdat = FELBills.query.filter(FELBills.Jo == billno).first()
        newbillno = 'B' + str(bdat.id)
        bdat.Jo = newbillno
        db.session.commit()
    else:
        bdat.dDate = datedue
        bdat.Memo = invonum
        bdat.Description = 'Monthly Chassis Rentals'
        bstat = bdat.Status
        if status == 'Paid' and bstat == 'Unpaid':
            bdat.pAmount = bdat.bAmount
            bdat.Status = status
            ref = bdat.Ref
            bdat.Ref = 'Epay'
            bdat.pDate = datedue
            print(f'Found {bdat.id} with {bdat.bAmount} and Reference {bdat.Ref}')
        elif status == 'Paid' and bstat == 'Paid':
            if 'epay' in bdat.Ref or bdat.Ref == None or bdat.Ref == '' or bdat.Ref == ' ':
                bdat.Ref = 'Epay'
            if bdat.pAccount == None or bdat.pAccount == '':
                bdat.pAccount = 'FEL Citibank'

        db.session.commit()



# Select an invoice cutoff date
today = datetime.datetime.today()
today = today.date()
dt = datetime.datetime.now() - datetime.timedelta(60)
dt = dt.date()
datedt = dt
print(dt)
printif = 0
page = 1

#dt = datetime.datetime(2018,1,1).date()
#with Display():
if 1 == 1:

    url1 = websites['flexivan']
    browser = webdriver.Firefox()
    browser.set_window_size(1920,1080)
    
    
    browser.get(url1)
    print('Got url1') if printif == 1 else 1
    time.sleep(5)

    selectElem = browser.find_element_by_xpath('//*[@id="txtvusername"]')
    selectElem.clear()
    selectElem.send_keys(usernames['flexivan'])

    selectElem = browser.find_element_by_xpath('//*[@id="txtvpassword"]')
    selectElem.clear()
    selectElem.send_keys(passwords['flexivan'])

    selectElem = browser.find_element_by_xpath('//*[@id="btnSign"]')
    selectElem.click()

    time.sleep(5)

    #Pay a Bill Button
    selectElem = browser.find_element_by_xpath('//*[@id="btnPayABill"]')
    selectElem.click()

    time.sleep(2)

    # Select to see the Invoices on Ribbon
    selectElem = browser.find_element_by_xpath('/html/body/nav/div[3]/div/div/div[2]/ul/li[2]')
    selectElem.click()

    time.sleep(2)

    # Now we are on the invoice page and need to go through each invoice listed.
    # This website does not define number of returns, but always shows 5 in table.
    num_invoices = 5

    while datedt >= dt and page > 0:
        for ix in range(1,num_invoices+1):

            if 1 == 1:
                print(f'Working on invoice {ix} of {num_invoices}')
                contentstr = f'/html/body/div[2]/div/div/div/div/div[2]/div/form/table/tbody/tr[{ix}]/td[3]'
                selectElem = browser.find_element_by_xpath(contentstr)
                invonum = selectElem.text

                contentstr = f'/html/body/div[2]/div/div/div/div/div[2]/div/form/table/tbody/tr[{ix}]/td[4]'
                selectElem = browser.find_element_by_xpath(contentstr)
                date1 = selectElem.text
                datedt= datetime.datetime.strptime(date1,'%m/%d/%Y')
                datedue = datedt + datetime.timedelta(30)
                datedt = datedt.date()
                datedue = datedue.date()

                contentstr = f'/html/body/div[2]/div/div/div/div/div[2]/div/form/table/tbody/tr[{ix}]/td[5]'
                selectElem = browser.find_element_by_xpath(contentstr)
                invoamt = selectElem.text
                invoamt = invoamt.replace('$','').replace(',','')

                contentstr = f'/html/body/div[2]/div/div/div/div/div[2]/div/form/table/tbody/tr[{ix}]/td[6]'
                selectElem = browser.find_element_by_xpath(contentstr)
                invodue = selectElem.text
                invodue = invodue.replace('$', '').replace(',', '')

                contentstr = f'/html/body/div[2]/div/div/div/div/div[2]/div/form/table/tbody/tr[{ix}]/td[7]'
                selectElem = browser.find_element_by_xpath(contentstr)
                status = selectElem.text

                if datedt > dt:
                    cha = None
                    con = 'Pool'
                    days = None
                    booking = None
                    rate = None
                    dateout = None
                    datein = None

                    print(f'Date:{datedt} Invoice:{invonum} Amount:{invoamt} BalDue:{invodue} Status:{status}')
                    print(' ')
                    chassis_insert('Flexivan',datedt,invonum,invoamt,con,cha,invoamt,days,dateout,datein,booking,rate)
                    bills_insert('Flexi-Van Leasing Inc', datedt, datedue, invonum, invoamt, status)


        # Go to the next page:
        if page == 1:
            selectElem = browser.find_element_by_xpath('/html/body/div[2]/div/div/div/div/div[2]/div/form/div[2]/ul/li[2]/a').click()
            page = page + 1
            time.sleep(5)
        else:
            try:
                selectElem = browser.find_element_by_xpath(f'/html/body/div[2]/div/div/div/div/div[2]/div/form/div[2]/ul/li[{page+1}]/a').click()
                page = page + 1
                time.sleep(5)
            except:
                #There are no more pages...
                page = 0

    browser.quit()

tunnel.stop()
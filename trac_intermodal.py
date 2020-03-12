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
    from CCC_FELA_models import Chassis, Interchange, Bills, People
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

def bills_insert(co, datedt, datedue, invonum, invoamt, status, comment):

    bdat = Bills.query.filter((Bills.Memo == invonum) & (Bills.bAmount == invoamt)).first()
    if bdat is None:
        pdat = People.query.filter(People.Company == co).first()
        company = pdat.Company
        aid = pdat.id
        billno = invonum
        memo = comment
        bdesc = 'Monthly Chassis Rentals'
        if status == 'Paid':
            pamt = invoamt
        else:
            pamt = '0.00'
        input = Bills(Jo=billno, Pid=aid, Company=co, Memo=memo, Description=bdesc, bAmount=invoamt, Status=status,
                         Cache=0, Original=None,
                         Ref='', bDate=datedt, pDate=None, pAmount=pamt, pMulti=None, pAccount='FEL Citibank',
                         bAccount='Equipment Rental', bType='Expensse',
                         bCat='Direct', bSubcat='Trucking', Link=None, User='Robot', Co='F', Temp1=None, Temp2=None,
                         Recurring=0, dDate=datedue, pAmount2='0.00', pDate2=None, iflag = 0, PmtList=None,
                             PacctList=None, RefList=None, MemoList=None, PdateList=None, CheckList=None)
        db.session.add(input)
        db.session.commit()
        # Now change the bill number:
        bdat = Bills.query.filter(Bills.Jo == billno).first()
        newbillno = 'B' + str(bdat.id)
        bdat.Jo = newbillno
        db.session.commit()
    else:
        bdat.dDate = datedue
        bdat.Memo = invonum
        bdat.Description = 'Monthly Chassis Rentals'
        bstat = bdat.Status
        if status == 'Paid' and bstat == 'Unpaid':
            bdat.pAmount = invoamt
            bdat.Status = status
            ref = bdat.Ref
            bdat.Ref = comment
            bdat.pDate = datedue
            print(f'Found {bdat.id} with {bdat.bAmount} and Reference {bdat.Ref}')
        elif status == 'Paid' and bstat == 'Paid':
            if 'epay' in bdat.Ref or bdat.Ref == None or bdat.Ref == '' or bdat.Ref == ' ':
                bdat.Ref = 'Epay'
            if '2766' in comment:
                bdat.pAccount = 'FEL Industrial Bank'
            else:
                bdat.pAccount = 'FEL Citibank'
            if '6542' in comment:
                bdat.pAccount = 'FEL US Bank VISA'
            bdat.Ref = comment
            bdat.pDate = datedt

        db.session.commit()



# Select an invoice cutoff date
today = datetime.datetime.today()
today = today.date()
dt = datetime.datetime.now() - datetime.timedelta(30)
dt = dt.date()
datedt = dt
print(dt)
printif = 0
page = 1

#dt = datetime.datetime(2018,1,1).date()
with Display():
#if 1 == 1:

    url1 = websites['trac']
    browser = webdriver.Firefox()
    browser.set_window_size(1920,1080)
    
    
    browser.get(url1)
    print('Got url1') if printif == 1 else 1
    time.sleep(5)

    selectElem = browser.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_txtAccountNumber"]')
    selectElem.clear()
    selectElem.send_keys(usernames['trac'])

    selectElem = browser.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_txtInvoiceNumber"]')
    selectElem.clear()
    selectElem.send_keys(passwords['trac'])

    selectElem = browser.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_bSubmit"]')
    selectElem.click()

    time.sleep(5)

    #Select Invoices Button
    selectElem = browser.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_cmdNext"]')
    selectElem.click()

    time.sleep(5)

    # Now we are on the invoice page and need to go through each invoice listed.
    # This website does not define number of returns, but always shows 5 in table.
    num_invoices = 20

    for ix in range(1,num_invoices+1):

        print(f'Working on invoice {ix} of {num_invoices}')

        try:
            contentstr = f'/html/body/form/div[3]/ul/li[4]/table/tbody/tr/td[2]/table[2]/tbody/tr[{ix+1}]/td[4]/span'
            selectElem = browser.find_element_by_xpath(contentstr)
            invonum = selectElem.text

            contentstr = f'/html/body/form/div[3]/ul/li[4]/table/tbody/tr/td[2]/table[2]/tbody/tr[{ix+1}]/td[7]/span'
            selectElem = browser.find_element_by_xpath(contentstr)
            date1 = selectElem.text
            datedt= datetime.datetime.strptime(date1,'%m/%d/%Y')
            datedue = datedt + datetime.timedelta(30)
            datedt = datedt.date()
            datedue = datedue.date()

            contentstr = f'/html/body/form/div[3]/ul/li[4]/table/tbody/tr/td[2]/table[2]/tbody/tr[{ix+1}]/td[9]/span'
            selectElem = browser.find_element_by_xpath(contentstr)
            invoamt = selectElem.text
            invoamt = invoamt.replace('$','').replace(',','')

            if datedt > dt:
                cha = None
                con = 'Pool'
                days = None
                booking = None
                rate = None
                dateout = None
                datein = None

                print(f'Date:{datedt} Invoice:{invonum} Amount:{invoamt} BalDue:{invoamt}')
                print(' ')
                chassis_insert('Trac Intermodal',datedt,invonum,invoamt,con,cha,invoamt,days,dateout,datein,booking,rate)
                bills_insert('Trac Intermodal', datedt, datedue, invonum, invoamt, 'Unpaid', invonum)
        except:
            print('No More Invoices to Process')
            break


    # Go to payment history:

    selectElem = browser.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_hlinkPayHistory"]').click()
    time.sleep(5)

    browser.get('https://trac.accelpayonline.com/ViewPayments.aspx')
    time.sleep(2)

    num_invoices = 50
    for ix in range(1, num_invoices + 1):

        try:

            contentstr = f'/html/body/form/div[3]/ul/li[4]/table/tbody/tr/td[2]/table[2]/tbody/tr[{ix+1}]/td[1]/span'
            selectElem = browser.find_element_by_xpath(contentstr)
            date1 = selectElem.text
            datedt = datetime.datetime.strptime(date1, '%m/%d/%Y')
            datedue = datedt + datetime.timedelta(30)
            datedt = datedt.date()
            datedue = datedue.date()

            contentstr = f'/html/body/form/div[3]/ul/li[4]/table/tbody/tr/td[2]/table[2]/tbody/tr[{ix+1}]/td[2]/span'
            selectElem = browser.find_element_by_xpath(contentstr)
            invoamt = selectElem.text
            invoamt = invoamt.replace('$','').replace(',','')

            contentstr = f'/html/body/form/div[3]/ul/li[4]/table/tbody/tr/td[2]/table[2]/tbody/tr[{ix+1}]/td[3]/span'
            selectElem = browser.find_element_by_xpath(contentstr)
            invonum = selectElem.text

            contentstr = f'/html/body/form/div[3]/ul/li[4]/table/tbody/tr/td[2]/table[2]/tbody/tr[{ix+1}]/td[5]/span'
            selectElem = browser.find_element_by_xpath(contentstr)
            comment = selectElem.text

            print(f'ix{ix} datedt{datedt} amt{invoamt} invonum{invonum} comment{comment}')
            if datedt > dt:
                cha = None
                con = 'Pool'
                days = None
                booking = None
                rate = None
                dateout = None
                datein = None
                chassis_insert('Trac Intermodal',datedt,invonum,invoamt,con,cha,invoamt,days,dateout,datein,booking,rate)
                bills_insert('Trac Intermodal', datedt, datedue, invonum, invoamt, 'Paid', comment)

        except:
            print('No More Invoices to Process')
            break

    #browser.quit()

tunnel.stop()
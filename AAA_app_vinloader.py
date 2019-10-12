import datetime

from pyvirtualdisplay import Display
from selenium import webdriver
import time

from bs4 import BeautifulSoup as soup
from random import randint
from statistics import mean
import os

from CCC_system_setup import mycompany, usernames, passwords, websites, addpath2, from_phone

sid = os.environ['TWILIO_ACCOUNT_SID']
token = os.environ['TWILIO_AUTH_TOKEN']
print(sid)
print(token)
print(from_phone)

co = mycompany()
if co == 'FELA':
    from CCC_FELA_remote_db_connect import tunnel, db
    from CCC_FELA_models import Autos
elif co == 'OSLM':
    from CCC_OSLM_remote_db_connect import tunnel, db
    from CCC_OSLM_models import Autos

from twilio.rest import Client

today = datetime.date.today()


def carfax(vin, tsec):
    with Display():
        url1 = 'https://www.carfax.com/vehicle-history-reports/'
        browser = webdriver.Firefox()
        browser.get(url1)
        print('Got url1')
        time.sleep(tsec)
        print('Getting xpath')
        selectElem = browser.find_element_by_xpath('//*[@id="vin-input"]')
        print('Got xpath')
        selectElem.clear()
        selectElem.send_keys(vin)
        selectElem.submit()
        time.sleep(tsec)
        newurl = browser.current_url
        browser.quit()
    return newurl


def curbweight(year, make, model):
    with Display():
        browser = webdriver.Firefox()
        url2 = 'https://www.google.com/search?q=curb+weight+of+a+'+year+'+'+make+'+'+model
        browser.get(url2)
        time.sleep(1)
        site_data = browser.page_source
        page_soup = soup(site_data, 'html.parser')
        weightcells = page_soup.findAll('div', {'class': 'Z0LcW'})
        wtot = 0.00
        nw = 0.00
        for weight in weightcells:
            wall = weight.text
            wall = wall.split()
            wlow = wall[0]
            wlow = wlow.replace(',', '')
            try:
                wlow = float(wlow)
            except:
                wlow = 0.00
            if wlow > 0.01:
                wtot = wtot + wlow
                nw = nw + 1.0
        try:
            wavg = int(wtot/nw)
        except:
            wavg = 0
        browser.quit()
    return wavg


def carprice(year, make, model):
    with Display():
        browser = webdriver.Firefox()
        url3 = 'https://www.carmax.com/cars/'+make.lower()+'/'+model.lower()+'?year='+year
        browser.get(url3)
        time_delay = randint(1, 2)
        time.sleep(time_delay)
        site_data = browser.page_source

        page_soup = soup(site_data, 'html.parser')
        prices = page_soup.findAll('span', {'class': 'car-price'})
        pall = []
        for j, price in enumerate(prices):
            pamt = price.text
            pamt = pamt.replace('$', '').replace(',', '').replace('*', '')
            try:
                pf = float(pamt)
                pall.append(pf)
            except:
                err = 1
        pavg = mean(pall)
        pavg = int(pavg)
        pstr = '$'+str(pavg)+'.00'
        print('Avg Price =', pstr)
        browser.quit()
    return pstr, j


def quickvinscraper(vin):
    print('Entering vinscraper')
    issue1 = ''
    issue2 = ''
    issue3 = ''
    err = 'All is well'

    error = 0

    try:
        newurl = carfax(vin, 1)
        print('newurl=', newurl, flush=True)
        if newurl == 'https://www.carfax.com/vehicle-history-reports/':
            print('Failed first try...adding time')
            newurl = carfax(vin, 2)
            print('newurl=', newurl, flush=True)
        if newurl == 'https://www.carfax.com/vehicle-history-reports/':
            print('Failed second try...adding more time...last try')
            newurl = carfax(vin, 3)
            print('newurl=', newurl, flush=True)
        if newurl == 'https://www.carfax.com/vehicle-history-reports/':
            error = 1
    except:
        error = 1
        newurl = 'failed'

    print(error, newurl)

    if error == 0:
        year = newurl.split('year=', 1)[1]
        year = year.split('&', 1)[0]

        make = newurl.split('make=', 1)[1]
        make = make.split('&', 1)[0]
        make = make.strip()

        model = newurl.split('model=', 1)[1]
        model = model.split('&', 1)[0]
        if '%' in model:
            model = model.split('%', 1)[0]
        if '/' in model:
            model = model.split('/', 1)[0]
        model = model.strip()
        # model=model.split('%',1)[0]
        if model == '300C' or model == '300c':
            model = '300'
        print(year, make, model)
    else:
        err = 'Failed on year,make,model url'
        year = ''
        make = ''
        model = ''

    return year, make, model, err


def quickvinloader(vin):
    print(len(vin))
    if len(vin) == 18:
        vin = vin[1:18]
    if len(vin) == 17:
        year, make, model, error = quickvinscraper(vin)
    else:
        year = '0'
        make = '0'
        model = '0'
        error = 'VIN not correct'

    return year, make, model, error


# Main part of running code
client = Client()
try:
    longs = open('incoming/whatsapp/vins.txt').read()
    vlist = longs.split()
    os.remove('incoming/whatsapp/vins.txt')
    sessionph = vlist[0]
    vlist.remove(sessionph)
except IOError:
    vlist = []
    file1 = open(addpath2('whatsapp/vinrun.txt'), 'a+')
    file1.write('Error in opening incoming/vins.txt\n')
    file1.close()

for vin in vlist:
    message = client.messages.create(body=f'Looking up VIN: {vin}', from_=from_phone, to=sessionph)

    now = datetime.datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    file1 = open(addpath2('whatsapp/vinrun.txt'), 'a+')
    file1.write('At '+date_time+' running task for VIN:'+vin+'\n')
    file1.close()

    year, make, model, error = quickvinloader(vin)
    message = client.messages.create(body=f'Found...\nYear: {year}\nMake: {make}\nModel: {model}\n...getting weight and price...', from_=from_phone, to=sessionph)
    if error == 'All is well':
        weight = curbweight(year, make, model)
        price, navg = carprice(year, make, model)

        adat = Autos.query.filter(Autos.VIN == vin).first()
        if adat is not None:
            error = 'Already in database'
            print(error)
        else:
            error = 'Placing in database'
            print(error)
            price = price.replace('$', '')
            lvin = len(vin)
            orderid = 'N' + vin[-5:]
            input = Autos(Jo=orderid,Hjo=None,Year=year,Make=make,Model=model,Color='',VIN=vin,Title='',State='',EmpWeight=weight,Dispatched=None,Value=price,TowCompany=None,TowCost=None,TowCostEa=' ',Original=None,Status='New',Date1=today,Date2=today,Pufrom='',Delto='',Ncars=1,Orderid=orderid)
            db.session.add(input)
            db.session.commit()

        file1 = open(addpath2('vinrun.txt'), 'a+')
        output = f'VIN:{vin} Year:{year} Make:{make} Model:{model} Weight:{weight} Price:{price} Msg:{error}\n'
        tw_output = f'*{vin}*\nYear: *{year}*\nMake: *{make}*\nModel: *{model}*\nWeight: *{weight}*\nPrice: *{price}*\nMsg: _{error}_\n'
        file1.write(output)
        file1.close()
        print('Done with', year, make, model, weight, price)

        print(sid)
        print(token)



        print(f'Sent from {from_phone}')
        print(f'Sent to {sessionph}')

        message = client.messages.create(body=tw_output,from_=from_phone,to=sessionph)


tunnel.stop()

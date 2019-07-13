import bs4
from urllib.request import urlopen as ureq
from bs4 import BeautifulSoup as soup

import time
import datetime
import os

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from random import randint

from statistics import mean


def carfax(vin, tsec):
    with Display():
        url1 = 'https://www.carfax.com/vehicle-history-reports/'
        #chromedriver = '/home/mark/fel/chromedriver'
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
        for weight in weightcells:
            wall = weight.text
            wall = wall.split()
            wlow = wall[0]
            whigh = wall[2]
            wlow = wlow.replace(',', '')
            whigh = whigh.replace(',', '')
            print(wlow, whigh)
        browser.quit()
    return wlow


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


def vinscraper(vin):
    print('Entering vinscraper')
    issue1 = ''
    issue2 = ''
    issue3 = ''

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
        issue1 = 'Failed on year,make,model url'
        year = ''
        make = ''
        model = ''

    print(year, make, model, 'error=', error, 'issue1=', issue1)

    if error == 0:
        try:
            wlow = curbweight(year, make, model)
        except:
            issue2 = 'Could not get curb weight'
            wlow = ''

    if error == 0:
        try:
            pstr, j = carprice(year, make, model)
        except:
            pstr = ''
            j = ''
            issue3 = 'Could not determine price'

    return year, make, model, wlow, pstr, j

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
    from CCC_FELA_models import Autos, Drivers, Vehicles
elif co == 'OSLM':
    from CCC_OSLM_remote_db_connect import tunnel, db
    from CCC_OSLM_models import Autos, Drivers, Vehicles

from twilio.rest import Client

today = datetime.date.today()

tdata = Vehicles.query.filter(Vehicles.Status == 'active').all()

ddata = Drivers.query.filter(Drivers.Truck == 'active').all()
for ddat in ddata:
    sessionph = 'whatsapp:+1' + ddat.Phone
    print('This sessionph=', sessionph)
    print('This message from',from_phone)
    driver = ddat.Name
    driverlist = driver.split()
    driver = driverlist[0]
    newmessage = f'Hello {driver}\nGood morning!\nWhat truck are you driving today? Enter bold label:\n*t1:*  918F33\n*t2:* 920F90\n*tn:* Not driving today'
    #newmessage = f'Hello {driver}\nGood morning!\nWhat truck are you driving today? Enter bold label:\n'
    for tdat in tdata:
        make = tdat.Make
        if len(make) > 5:
            make = make[0:5]
        #newmessage = newmessage + f'*t{str(tdat.id)}:* {tdat.Year} {make} {tdat.Plate}\n'
    #newmessage = newmessage + '*tn:* Not driving today'
    client = Client()
    message = client.messages.create(body=newmessage, from_=from_phone, to=sessionph)


tunnel.stop()

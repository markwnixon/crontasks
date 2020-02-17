from CCC_system_setup import addpath2, addpath3, websites, usernames, passwords, imap_url, scac
from remote_db_connect import tunnel, db
from models import Interchange, Orders


import requests
import json
import datetime
from datetime import timedelta
from math import sqrt
from cronfuncs import dropupdate, d1s, d2s


today = datetime.datetime.today()
#today = today.date()
print(today, scac)
cutoff = datetime.datetime.now() - timedelta(120)
cutoff = cutoff.date()

#Do Global Section
i40 = 1
i20 = 0
iglobal = 0
trial = 1
if iglobal == 1 and i20 == 0:
    next_container = 'CLHU9078790'
    label = 'GBL Chassis'
    chassislist = []
elif i20 == 0 and i40 == 0:
    chassislist = ['GBL Chassis','FDAZ408834-8', 'FDAZ430496-1','FDAZ430575-7', 'FDAZ454547-0', 'FDAZ454583-A']
    next_container = 'MNBU3353999'
    label = 'FDAZ454666-7'

elif i20 == 1:
    idata = Interchange.query.filter( (Interchange.CONTYPE.contains('20')) & (Interchange.Date > cutoff) ).all()
    for idat in idata:
        chassis = idat.CHASSIS
        print(f'Chassis for {idat.CONTAINER} is {chassis}')
        if chassis is None:
            print('chassis none')
        elif 'OWN' in chassis or 'Own' in chassis or 'FELA' in chassis or 'NONUM' in chassis or 'NONE' in chassis:
            print(chassis)
            idat.CHASSIS = 'FELA020'
    db.session.commit()

elif i40 == 1:
    idata = Interchange.query.filter( (Interchange.CONTYPE.contains('40')) & (Interchange.Date > cutoff) ).all()
    for idat in idata:
        chassis = idat.CHASSIS
        print(f'Chassis for {idat.Company} and {idat.CONTAINER} on {idat.Date} is {chassis}')
        if chassis is None:
            print('chassis none')
        elif 'OWN' in chassis or 'Own' in chassis or 'FELA' in chassis or 'NONUM' in chassis or 'NONE' in chassis or 'MDVC' in chassis or '5210' in chassis:
            print(chassis)
            idat.CHASSIS = 'FELA001'
    db.session.commit()


if i20 == 0 and i40 == 0:
    idat = Interchange.query.filter( (Interchange.CONTAINER==next_container) & (Interchange.TYPE.contains('out')) ).first()
    if idat is not None:
        print(f'{idat.RELEASE} {idat.CONTAINER} {idat.Date} {idat.Time}')
        if trial == 0:
            chassis = idat.CHASSIS
            if chassis not in chassislist:
                idat.CHASSIS = label

    while next_container is not None:
        jdat = Interchange.query.filter( (Interchange.CONTAINER==next_container) & (Interchange.TYPE.contains('in')) ).first()
        if jdat is not None:
            print(f'{jdat.RELEASE} {jdat.CONTAINER} {jdat.Date} {jdat.Time}')
            if trial == 1: print(f'Current Chassis is: {jdat.CHASSIS}')
            if trial == 0:
                chassis = jdat.CHASSIS
                if chassis not in chassislist:
                    jdat.CHASSIS = label
                else:
                    print(f'Duplicate chassis on {jdat.CONTAINER}')
            if iglobal == 1:
                odat = Orders.query.filter( (Orders.Container == next_container) & (Orders.Booking == jdat.RELEASE) ).first()
                if odat is not None:
                    print(odat.Shipper)
                    odat.BOL = label
            kdat = Interchange.query.filter( (Interchange.Date==jdat.Date) & (Interchange.Time==jdat.Time) & (Interchange.TYPE.contains('out')) ).first()
            if kdat is not None:
                print(f'{kdat.RELEASE} {kdat.CONTAINER} {kdat.Date} {kdat.Time}')
                if trial == 1: print(f'Current Chassis is: {kdat.CHASSIS}')
                if trial == 0:
                    if chassis not in chassislist:
                        kdat.CHASSIS = label
                    else:
                        print(f'Duplicate chassis on {kdat.CONTAINER}')
                next_container = kdat.CONTAINER
            else:
                next_container = None
        else:
            next_container = None

    if trial == 0: db.session.commit()

tunnel.stop()


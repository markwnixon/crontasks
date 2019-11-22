import requests
import json
import datetime
import calendar
from math import sqrt
from cronfuncs import dropupdate, d1s, d2s
from datetime import timedelta


daybackfrom = 50
daybackto = 0
printif = 0
# (daybackto=0 is today; from 1 to 0 is yesterday and today)


today = datetime.datetime.today()
#today = today.date()
print(today) if printif == 1 else 1

from CCC_system_setup import co

if co == 'FELA':
    from CCC_FELA_remote_db_connect import tunnel, db
    from CCC_FELA_models import Orders, Interchange

elif co == 'OSLM':
    from CCC_OSLM_remote_db_connect import tunnel, db
    from CCC_OSLM_models import Orders, Interchange

odata = Orders.query.filter(Orders.Shipper == 'Global Business Link').order_by(Orders.Date).all()

if 1 == 1:
    num_dups = 0
    for odat in odata:
        bk = odat.Booking
        cn = odat.Container
        if cn == 'TBD':
            cn = 'NOM'
        tid = odat.id
        bdat = Orders.query.filter( ((Orders.Booking == bk) | (Orders.Container == cn)) & (Orders.id != tid) ).first()
        if bdat is not None:
            num_dups = num_dups + 1
            print(f'Have duplicate with {bk} and/or {cn}')
    print(f'Found {num_dups} duplicates')
if 1 == 2:
    # Now make report of global jobs that have been invoiced.
    for jx, odat in enumerate(odata):
        status = odat.Status
        ck = int(status[1])
        if ck >= 1:
            dt = odat.Date
            bk = odat.Booking
            cn = odat.Container
            print(f'{jx+1} {dt} {bk} | {cn} already invoiced')

if 1 == 2:
    # Now make report of global jobs that have been invoiced.
    jx = 0
    for odat in odata:
        status = odat.Status
        ck1 = int(status[0])
        ck2 = int(status[1])
        if ck1 == 2 and ck2 ==0:
            jx = jx+1
            dt = odat.Date
            dt2 = odat.Date2
            bk = odat.Booking
            cn = odat.Container
            print(f'{jx} Out:{dt} In:{dt2} Bk:{bk} | Cn:{cn} Not Invoiced')


tunnel.stop()
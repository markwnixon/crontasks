import requests
import json
import datetime
from math import sqrt
from cronfuncs import dropupdate, d1s, d2s


today = datetime.datetime.today()
#today = today.date()
print(today)

from CCC_system_setup import addpath3, addpath4, websites, usernames, passwords, mycompany, addpaths, imap_url, quartix_customer_id, quartix_app
co = mycompany()

if co == 'FELA':
    from CCC_FELA_remote_db_connect import tunnel, db
    from CCC_FELA_models import Trucklog, Drivers
    uname = usernames['quartix']
    password = passwords['quartix']

elif co == 'OSLM':
    from CCC_OSLM_remote_db_connect import tunnel, db
    from CCC_OSLM_models import Trucklog, Drivers
    uname = usernames['quartix']
    password = passwords['quartix']

pstart = datetime.date(2019,10,14)
pstop = pstart + datetime.timedelta(14)
wk1 = pstart + datetime.timedelta(7)
print(pstart,pstop)

# Date id tags began
ddata = Drivers.query.filter((Drivers.Start <= pstart) & (Drivers.End >= pstart)).all()
for dat in ddata:
    driver = dat.Name
    hdata = Trucklog.query.filter( (Trucklog.Driver == driver) & (Trucklog.Date >= pstart) & (Trucklog.Date <= pstop)).all()
    tot1 = 0
    tot2 = 0
    for hdat in hdata:
        print(f'Driver {driver} on Date {hdat.Date} drove {hdat.Shift} hrs')
        if hdat.Date <= wk1:
            tot1 = tot1 + float(hdat.Shift)
        else:
            tot2 = tot2 + float(hdat.Shift)

    if tot1 > 40.0:
        ot1 = tot1 - 40.0
        tot1 = 40.0
    else:
        ot1 = 0.0

    if tot2 > 40.0:
        ot2 = tot2 - 40.0
        tot2 = 40.0
    else:
        ot2 = 0.0

    reg_hours = tot1 + tot2
    ot_hours = ot1 + ot2

    print(f'Summary for {driver}: {d1s(reg_hours)} regular hours and {d1s(ot_hours)} OT')
    print(' ')


tunnel.stop()
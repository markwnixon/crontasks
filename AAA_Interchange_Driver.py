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
    from CCC_FELA_models import Trucklog, Drivers, Driverlog, Interchange, FELVehicles
    uname = usernames['quartix']
    password = passwords['quartix']

elif co == 'OSLM':
    from CCC_OSLM_remote_db_connect import tunnel, db
    from CCC_OSLM_models import Trucklog, Drivers, Driverlog, Interchange
    uname = usernames['quartix']
    password = passwords['quartix']

cutoff = datetime.date(2019,10,1)
idata = Interchange.query.filter( (Interchange.Path != 'V') & (Interchange.Date > cutoff) ).all()
for idat in idata:
    idate = idat.Date
    tn = idat.TRUCK_NUMBER
    trk = FELVehicles.query.filter(FELVehicles.Plate == tn).first()
    if trk is not None:
        unit = trk.Unit
    else:
        print(idat.CONTAINER, 'No Unit')
        unit = 'NAY'

    ddata = Driverlog.query.filter( (Driverlog.Date == idate) & (Driverlog.Truck == unit) ).all()
    if len(ddata) == 1:
        ddat = ddata[0]
        print(idat.CONTAINER, unit, ddat.Driver)
    else:
        for ddat in ddata:
            print('**',idat.CONTAINER, unit, ddat.Driver)

tunnel.stop()


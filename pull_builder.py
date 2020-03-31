from CCC_system_setup import scac, addpath1, addpath5, machine, websites, addpath2, addpath3
from remote_db_connect import tunnel, db
from models import Orders, Interchange
print(f'Running company {scac}')

import datetime
from datetime import timedelta
from viewfuncs import stripper, newjo, hasinput
import os

movem = 0

daybackfrom = 10
daybackto = 0
printif = 0
today = datetime.datetime.today()
cutoffdate = today - timedelta(3)

print(f'Running pdf builder for SCAC {scac} off Machine {machine}')
print(addpath1('tmp/'))



odata = Orders.query.filter(Orders.Date > cutoffdate).all()
for odat in odata:
    if hasinput(odat.Container):
        idata = Interchange.query.filter(Interchange.Container == odat.Container).all()
        for idat in idata:
            print(idat.Container, idat.Original)
            if movem == 1:
                pythonline = websites['ssh_data'] + f'vinterchange/{idat.Original}'
                placefile = addpath3(f'interchange/{idat.Original}')
                copyline1 = f'scp {pythonline} {placefile}'
                print(copyline1)
                os.system(copyline1)

tunnel.stop()


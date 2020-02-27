from CCC_system_setup import scac
from remote_db_connect import tunnel, db
from models import Interchange, Orders

import datetime
from datetime import timedelta

today = datetime.datetime.today()
print(today, scac)
cutoff = datetime.datetime.now() - timedelta(30)
cutoff = cutoff.date()

#Attempt to Chain the Global Chassis

gdata = Interchange.query.filter( (Interchange.CHASSIS == 'GBL Chassis') & (Interchange.TYPE.contains('out')) & (Interchange.Date > cutoff) ) .all()
gdat = gdata[-3]
if gdat is not None:
    next_container = gdat.CONTAINER
    print(f'Starting with Global Chassis Container {next_container}')
    label = 'GBL Chassis'

    idat = Interchange.query.filter((Interchange.CONTAINER == next_container) & (Interchange.TYPE.contains('out'))).first()
    if idat is not None:
        print(f'{idat.RELEASE} {idat.CONTAINER} {idat.Date} {idat.Time}')
        idat.CHASSIS = label

    while next_container is not None:
        jdat = Interchange.query.filter((Interchange.CONTAINER == next_container) & (Interchange.TYPE.contains('in'))).first()
        if jdat is not None:
            print(f'{jdat.RELEASE} {jdat.CONTAINER} {jdat.Date} {jdat.Time}')
            jdat.CHASSIS = label
            odat = Orders.query.filter(Orders.Container == next_container).first()
            if odat is not None:
                odat.BOL = label

            kdat = Interchange.query.filter((Interchange.Date == jdat.Date) & (Interchange.Time == jdat.Time) & (Interchange.TYPE.contains('out'))).first()
            if kdat is not None:
                print(f'{kdat.RELEASE} {kdat.CONTAINER} {kdat.Date} {kdat.Time}')
                kdat.CHASSIS = label
                next_container = kdat.CONTAINER
            else:
                next_container = None
        else:
            next_container = None

    db.session.commit()

#Clean up our 20' chassis

gdata = Interchange.query.filter( (Interchange.CHASSIS == 'FELA020') & (Interchange.TYPE.contains('out')) & (Interchange.Date > cutoff) ) .all()
gdat = gdata[-1]
if gdat is not None:
    lookback = gdat.Date
    idata = Interchange.query.filter( (Interchange.CONTYPE.contains('20')) & (Interchange.Date >= lookback) ).all()
    for idat in idata:
        chassis = idat.CHASSIS
        print(f'Chassis for {idat.CONTAINER} is {chassis}')
        if chassis is None:
            print('chassis none')
        elif 'OWN' in chassis or 'Own' in chassis or 'FELA' in chassis or 'NONUM' in chassis or 'NONE' in chassis:
            idat.CHASSIS = 'FELA020'
    db.session.commit()

#Clean up our 40' chassis

gdata = Interchange.query.filter( (Interchange.CHASSIS == 'FELA001') & (Interchange.TYPE.contains('out')) & (Interchange.Date > cutoff) ) .all()
gdat = gdata[-1]
if gdat is not None:
    lookback = gdat.Date
    idata = Interchange.query.filter( (Interchange.CONTYPE.contains('40')) & (Interchange.Date >= lookback) ).all()
    for idat in idata:
        chassis = idat.CHASSIS
        print(f'Chassis for {idat.CONTAINER} is {chassis}')
        if chassis is None:
            print('chassis none')
        elif 'OWN' in chassis or 'Own' in chassis or 'FELA' in chassis or 'NONUM' in chassis or 'NONE' in chassis:
            idat.CHASSIS = 'FELA001'
    db.session.commit()

tunnel.stop()


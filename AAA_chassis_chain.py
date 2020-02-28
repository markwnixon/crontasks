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

gdata = Interchange.query.filter( (Interchange.Chassis == 'GBL Chassis') & (Interchange.Type.contains('out')) & (Interchange.Date > cutoff) ) .all()
gdat = gdata[-1]
if gdat is not None:
    next_container = gdat.Container
    print(f'Starting with Global Chassis Container {next_container}')
    label = 'GBL Chassis'

    idat = Interchange.query.filter((Interchange.Container == next_container) & (Interchange.Type.contains('out'))).first()
    if idat is not None:
        print(f'{idat.Release} {idat.Container} {idat.Date} {idat.Time}')
        idat.Chassis = label

    while next_container is not None:
        jdat = Interchange.query.filter((Interchange.Container == next_container) & (Interchange.Type.contains('in'))).first()
        if jdat is not None:
            print(f'{jdat.Release} {jdat.Container} {jdat.Date} {jdat.Time}')
            jdat.Chassis = label
            odat = Orders.query.filter((Orders.Container == next_container) & (Orders.Booking == jdat.Release)).first()
            if odat is not None:
                odat.BOL = label

            kdat = Interchange.query.filter((Interchange.Date == jdat.Date) & (Interchange.Time == jdat.Time) & (Interchange.Type.contains('out'))).first()
            if kdat is not None:
                print(f'{kdat.Release} {kdat.Container} {kdat.Date} {kdat.Time}')
                kdat.Chassis = label
                next_container = kdat.Container
            else:
                next_container = None
        else:
            next_container = None

    db.session.commit()

#Clean up our 20' chassis

gdata = Interchange.query.filter( (Interchange.Chassis == 'FELA020') & (Interchange.Type.contains('out')) & (Interchange.Date > cutoff) ) .all()
gdat = gdata[-1]
if gdat is not None:
    lookback = gdat.Date
    idata = Interchange.query.filter( (Interchange.ConType.contains('20')) & (Interchange.Date >= lookback) ).all()
    for idat in idata:
        chassis = idat.Chassis
        print(f'Chassis for {idat.Container} is {chassis}')
        if chassis is None:
            print('chassis none')
        elif 'OWN' in chassis or 'Own' in chassis or 'FELA' in chassis or 'NONUM' in chassis or 'NONE' in chassis:
            idat.Chassis = 'FELA020'
    db.session.commit()

#Clean up our 40' chassis

gdata = Interchange.query.filter( (Interchange.Chassis == 'FELA001') & (Interchange.Type.contains('out')) & (Interchange.Date > cutoff) ) .all()
gdat = gdata[-1]
if gdat is not None:
    lookback = gdat.Date
    idata = Interchange.query.filter( (Interchange.ConType.contains('40')) & (Interchange.Date >= lookback) ).all()
    for idat in idata:
        chassis = idat.Chassis
        print(f'Chassis for {idat.Container} is {chassis}')
        if chassis is None:
            print('chassis none')
        elif 'OWN' in chassis or 'Own' in chassis or 'FELA' in chassis or 'NONUM' in chassis or 'NONE' in chassis:
            idat.Chassis = 'FELA001'
    db.session.commit()

tunnel.stop()


import datetime
from datetime import timedelta
today = datetime.datetime.today()
print(today)
cutoff = datetime.datetime.now() - timedelta(21
                                             )

from remote_db_connect import tunnel, db
from models import Interchange, DriverAssign, Vehicles, Trucklog

idata = Interchange.query.filter(Interchange.Date > cutoff).all()
for idat in idata:
    idate = idat.Date
    tn = idat.TruckNumber
    trk = Vehicles.query.filter(Vehicles.Plate == tn).first()
    if trk is not None:
        unit = trk.Unit
        if unit is not None:
            adat = DriverAssign.query.filter( (DriverAssign.Date==idate) & (DriverAssign.UnitStart == unit) ).first()
            if adat is not None:
                print(adat.Driver)
                idat.Driver = adat.Driver
            else:
                idat.Driver = 'NAY'
        else:
            idat.Driver = 'NAY'
    else:
        idat.Driver = 'NAY'

db.session.commit()

idata = Interchange.query.filter( (Interchange.Date > cutoff) & (Interchange.Driver == 'NAY') ).all()
for idat in idata:
    idate = idat.Date
    tn = idat.TruckNumber
    trk = Vehicles.query.filter(Vehicles.Plate == tn).first()
    if trk is not None:
        unit = trk.Unit
        if unit is not None:
            adat = Trucklog.query.filter( (Trucklog.Date==idate) & (Trucklog.Unit == unit) ).first()
            if adat is not None:
                d1 = adat.DriverStart
                d2 = adat.DriverEnd
                if d1 is None:
                    driver = d2
                else:
                    driver = d1
                print('Second Set:',driver)
                idat.Driver = driver
            else:
                idat.Driver = 'NAY'
        else:
            idat.Driver = 'NAY'
    else:
        idat.Driver = 'NAY'

db.session.commit()


tunnel.stop()


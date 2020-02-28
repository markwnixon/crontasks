import requests
import json
import datetime
import calendar
from math import sqrt
from cronfuncs import dropupdate, d1s, d2s
from datetime import timedelta

printif = 0
today = datetime.datetime.today()
#today = today.date()
print(today) if printif == 1 else 1

#response = requests.post("https://qws.quartix.com/v2/api/auth", params=parameters)

from CCC_system_setup import addpath3, addpath4, websites, usernames, passwords, mycompany, addpaths, imap_url, quartix_customer_id, quartix_app
co = mycompany()

if co == 'FELA':
    from CCC_FELA_remote_db_connect import tunnel, db
    from CCC_FELA_models import Chassis, Interchange, Invoices, Truckcost

elif co == 'OSLM':
    from CCC_OSLM_remote_db_connect import tunnel, db
    from CCC_OSLM_models import Chassis, Interchange, Invoices

thisyear = datetime.datetime.now().year
print(thisyear)
numcalday = today - datetime.datetime(thisyear, 1, 1)
numcalday = numcalday.days
print(numcalday)

obase = 2
for tday in range(1,numcalday):
    xdate = datetime.datetime(thisyear, 1, 1) + timedelta(tday)
    xdate = xdate.date()
    print(xdate)
    outs = Interchange.query.filter( (Interchange.Date == xdate) & (Interchange.Type.contains('Out')) ).all()
    ins = Interchange.query.filter( (Interchange.Date == xdate) & (Interchange.Type.contains('In')) ).all()
    netout = len(outs) - len(ins) + obase
    print(xdate,netout)


ytamt = 0.0
ynumc = 0
yiamt = 0.0
ydays = 0
for month in range(1,13):
    days = calendar.monthrange(thisyear,month)[1]
    xdfrom = datetime.datetime(thisyear, month, 1)
    xdto = datetime.datetime(thisyear,month,days)
    xdret = xdto + timedelta(30)
    print(f'From:{xdfrom}-{xdto} with RET to {xdret}')
    m3 = calendar.month_abbr[month]
    print(m3)

    cdata = Chassis.query.filter( (Chassis.Date >= xdfrom) & (Chassis.Date <= xdto)).all()
    mtamt = 0.0
    for cd in cdata:
        amt = cd.Amount
        amt = amt.replace('$','').replace(',','')
        amt = float(amt)
        mtamt = mtamt + amt

    numdays = 0
    condata = Interchange.query.filter( (Interchange.Date >= xdfrom) & (Interchange.Date <= xdto) & (Interchange.Type.contains('Out')) ).all()
    for cd in condata:
        condata2 = Interchange.query.filter( (Interchange.Date >= xdfrom) & (Interchange.Date <= xdret) & (Interchange.Container == cd.Container) & (Interchange.Type.contains('In')) ).first()
        if condata2 is not None:
            d1 = cd.Date
            d2 = condata2.Date
            mydays = d2 - d1
            mydays = (mydays.days) + 1
            if mydays > 6:
                print(mydays,cd.Container)
            numdays = numdays + mydays
        else:
            print(f'Container {cd.Container} no return match')
    numc = len(condata)

    idata = Invoices.query.filter( (Invoices.Date >= xdfrom) & (Invoices.Date <= xdto) & (Invoices.Service == 'Chassis Fees') ).all()
    miamt = 0.0
    for id in idata:
        amt = id.Amount
        amt = float(amt)
        miamt = miamt + amt

    jdol = 0.0
    jdata = Interchange.query.filter( (Interchange.Date >= xdfrom) & (Interchange.Date <= xdto) & ( (Interchange.Chassis.contains('jay')) | (Interchange.Company.contains('Jays')) )  & (Interchange.Type.contains('In')) ).all()
    for jdat in jdata:
        jout = Interchange.query.filter( (Interchange.Container == jdat.Container) & (Interchange.Type.contains('Out')) ).first()
        d1 = jdat.Date
        d2 = jout.Date
        mydays = d1 - d2
        mydays = (mydays.days) + 1
        #print(f'jdays:{mydays}')
        jdol = jdol + mydays * 30.0
    #print(jdol)
    miamt = miamt + jdol



    if numdays > 0:
        tavg = mtamt/float(numdays)
        iavg = miamt/float(numdays)
        cavg = mtamt/float(numc)
        ciavg = miamt/float(numc)
        cdavg = float(numdays)/float(numc)
    else:
        tavg = None
        iavg = None
        cavg = None
        ciavg = None
        cdavg = None

    print(f'Month:{month} Chassis$:{d2s(mtamt)} ChasDays{numdays} ConOut:{numc} Chas$/Day:{d2s(tavg)} Chas$/Con:{d2s(cavg)} Days/Con:{d2s(cdavg)}')
    ytamt = ytamt + mtamt
    ynumc = ynumc + numc
    ydays = ydays + numdays
    yiamt = yiamt + miamt

    tcon = Truckcost.query.filter(Truckcost.Cost == 'Containers').first()
    ebase = f'tcon.{m3} = str({numc})'
    print(ebase)
    exec(ebase)
    db.session.commit()

    tcon = Truckcost.query.filter(Truckcost.Cost == 'ChassisDays').first()
    ebase = f'tcon.{m3} = str({numdays})'
    print(ebase)
    exec(ebase)
    db.session.commit()

    tcon = Truckcost.query.filter(Truckcost.Cost == 'Chassis').first()
    ebase = f'tcon.{m3} = str({d2s(mtamt)})'
    print(ebase)
    exec(ebase)
    db.session.commit()


ytavg = ytamt/float(ydays)
yiavg = yiamt/float(ydays)
print(f'Year Avg for Year:{thisyear} Chassis$:{d2s(ytamt)} Cons:{ynumc} ChasPay$/Day:{d2s(ytavg)}  ChasPay$/Con:{d2s(ytamt/float(ynumc))} Days/Con:{d2s(ydays/ynumc)}')
print(f'Year Avg for Year:{thisyear} ChasInc$:{d2s(yiamt)} Cons:{ynumc} ChasInc$/Day:{d2s(yiavg)}  ChasInc$/Con:{d2s(yiamt/float(ynumc))}')

tcon = Truckcost.query.filter(Truckcost.Cost == 'Containers').first()
tcon.Ytd = d2s(ynumc)
tcon.PerCon = '1'
tcon.PerChasDay = d2s(float(ynumc)/float(ydays))
tcon.PerDay = d2s(float(ynumc)/float(numcalday))
db.session.commit()

tcon = Truckcost.query.filter(Truckcost.Cost == 'ChassisDays').first()
tcon.Ytd = d2s(ydays)
tcon.PerCon = d2s(float(ydays)/float(ynumc))
tcon.PerChasDay = '1'
tcon.PerDay = d2s(float(ydays)/float(numcalday))
db.session.commit()

tcon = Truckcost.query.filter(Truckcost.Cost == 'Chassis').first()
tcon.Ytd = d2s(ytamt)
tcon.PerCon = d2s(ytamt/float(ynumc))
tcon.PerChasDay = d2s(ytamt/float(ydays))
tcon.PerDay = d2s(float(ytamt)/float(numcalday))
db.session.commit()





tunnel.stop()
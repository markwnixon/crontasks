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

#response = requests.post("https://qws.quartix.com/v2/api/auth", params=parameters)

from CCC_system_setup import addpath3, addpath4, websites, usernames, passwords, mycompany, addpaths, imap_url, quartix_customer_id, quartix_app
co = mycompany()

if co == 'FELA':
    from CCC_FELA_remote_db_connect import tunnel, db
    from CCC_FELA_models import Trucklog, Drivers, Driverlog, Portlog, Interchange, Tolls, Truckcost, FELBills, Payroll
    uname = usernames['quartix']
    password = passwords['quartix']

elif co == 'OSLM':
    from CCC_OSLM_remote_db_connect import tunnel, db
    from CCC_OSLM_models import Trucklog, Drivers, Driverlog, Portlog, Interchange
    uname = usernames['quartix']
    password = passwords['quartix']

def get_port(sd,ed):
    pdata = Portlog.query.filter( (Portlog.Date >= sd) & (Portlog.Date <= ed)).all()
    port_time, port_miles, port_entries = 0.0, 0.0, 0.0
    port_time_withcust, port_entries_withcust, port_time_without, port_entries_without = 0.0, 0.0, 0.0, 0.0
    for pdat in pdata:
        timein = float(pdat.PortTime)
        miles = float(pdat.Portmiles)
        custtime = float(pdat.CustTime)
        if timein > .2:
            port_time += timein
            port_entries += 1
            port_miles += miles
            if custtime > 0.0:
                port_time_withcust += timein
                port_entries_withcust += 1
            else:
                port_time_without += timein
                port_entries_without +=1
    return port_time, port_miles, port_entries, port_time_withcust, port_entries_withcust, port_time_without, port_entries_without

def get_pay(ptype,sd,ed):
    nt=0.00
    amt=0.00
    tdata = Payroll.query.filter( (Payroll.Date >= sd) & (Payroll.Date <= ed) & (Payroll.Function == ptype) ).all()
    for tdat in tdata:
        amt += float(tdat.FullCost)
        nt += float(tdat.TotHours)
    return amt,nt

def get_tolls(sd,ed):
    nt=0
    amt=0.00
    tdata = Tolls.query.filter( (Tolls.Date >= sd) & (Tolls.Date <= ed) ).all()
    for tdat in tdata:
        amt += float(tdat.Amount)
        nt += 1
    return amt,nt

def get_fuel(sd,ed):
    amt=0.00
    tdata = FELBills.query.filter( (FELBills.bDate >= sd) & (FELBills.bDate <= ed) & ( (FELBills.bAccount.contains('Fuel')) | (FELBills.bCat.contains('Fuel')) ) ).all()
    for tdat in tdata:
        amt += float(tdat.bAmount)
    return amt

def get_tmiles(sd,ed):
    nt=0
    amt=0.00
    tdata = Trucklog.query.filter( (Trucklog.Date >= sd) & (Trucklog.Date <= ed) ).all()
    for tdat in tdata:
        amt += float(tdat.Distance)
        nt += 1
    return amt,nt

def put_cost(item,m3,amt,dig):
    if dig == 2:
        amt = d2s(amt)
    elif dig == 1:
        amt = d1s(amt)
    elif dig == 0:
        amt = str(int(amt))
    tcon = Truckcost.query.filter(Truckcost.Cost == item).first()
    ebase = f'tcon.{m3} = str({amt})'
    exec(ebase)
    db.session.commit()

thisyear = datetime.datetime.now().year
print(thisyear)


#Perform Year to Date Costs:
xdfrom = datetime.datetime(thisyear,1,1)
xdto = datetime.datetime.now()
sd = xdfrom.date()
ed = xdto.date()

tmiles,ntrips = get_tmiles(sd,ed)
put_cost('TruckMiles','Ytd',tmiles,1)
put_cost('TruckDays','Ytd',ntrips,0)

fuelcost = get_fuel(sd,ed)
put_cost('FuelCost','Ytd',fuelcost,1)

m3 = 'Ytd'
port_time, port_miles, port_entries, port_time_withcust, port_entries_withcust, port_time_without, port_entries_without = get_port(sd, ed)
put_cost('PortTime', m3, port_time, 1)
put_cost('PortMiles', m3, port_miles, 1)
put_cost('PortEntries', m3, port_entries, 0)
put_cost('PortTimeCustoms', m3, port_time_withcust, 1)
put_cost('PortEntriesCustoms', m3, port_entries_withcust, 0)
put_cost('PortTimeNoCust', m3, port_time_without, 1)
put_cost('PortEntriesNoCust', m3, port_entries_without, 0)

condat = Truckcost.query.filter(Truckcost.Cost == 'Containers').first()
numcon = float(condat.Ytd)
numwithcust = port_entries_withcust
numwithout = numcon - numwithcust
put_cost('ConWithCust', m3, numwithcust, 0)
put_cost('ConNoCust', m3, numwithout, 0)

toll_amt, toll_num = get_tolls(sd, ed)
print(f'{sd}-{ed} Tolls:${d2s(toll_amt)} #Tolls:{toll_num}')
try:
    tperc = toll_amt/numcon
except:
    tperc = 0.00

put_cost('Tolls', 'Ytd', toll_amt, 2)
put_cost('NumTolls','Ytd',toll_num,0)
put_cost('TollsPerCon','Ytd',tperc,2)

driverpay, driverhrs = get_pay('Driver', sd, ed)
try:
    burdrate = driverpay/driverhrs
except:
    burdrate = None
put_cost('DriverFullCost',m3,driverpay,2)
put_cost('DriverHours',m3,driverhrs,2)
put_cost('DriverBurdRate',m3,burdrate,2)

#######################################################################
dat = Truckcost.query.filter(Truckcost.Cost == 'DriverBurdRate').first()
ebase = f'rate = dat.{m3} '
exec(ebase)
try:
    rate = float(rate)
except:
    rate = 0.00

dat = Truckcost.query.filter(Truckcost.Cost == 'PortTime').first()
ebase = f'ptime = dat.{m3} '
exec(ebase)
try:
    ptime = float(ptime)
except:
    ptime = 0.00

try:
    pdrvcost = rate * ptime / numcon
except:
    pdrvcost = 0.00

put_cost('PortDriverCost', m3, pdrvcost, 2)
##############################################################

dat = Truckcost.query.filter(Truckcost.Cost == 'PortMiles').first()
ebase = f'pmiles = dat.{m3} '
exec(ebase)
try:
    pmiles = float(pmiles)
except:
    pmiles = 0.00

dat = Truckcost.query.filter(Truckcost.Cost == 'TruckMiles').first()
ebase = f'tmiles = dat.{m3} '
exec(ebase)
try:
    tmiles = float(tmiles)
except:
    tmiles = 0.00

dat = Truckcost.query.filter(Truckcost.Cost == 'DriverFullCost').first()
ebase = f'dcost = dat.{m3} '
exec(ebase)
try:
    dcost = float(dcost)
except:
    dcost = 0.00

dat = Truckcost.query.filter(Truckcost.Cost == 'FuelCost').first()
ebase = f'fcost = dat.{m3} '
exec(ebase)
try:
    fcost = float(fcost)
except:
    fcost = 0.00

#Calc Net driver cost when not in port
mvdcost = dcost - (ptime * rate)

#Calc Net truck miles when not in port
mvmiles = tmiles - pmiles

try:
    drvc1 = rate / 30.0  # InnerCity Avg Vel
    drvc2 = rate / 38.0  # InnerMetro Avg Vel
    drvc3 = rate / 47.0  # MetroOut Avg Vel
    fuelcostpermile = fcost / tmiles
    portfuelcost = fuelcostpermile * pmiles + 0.8 * ptime * 3.0  # 2nd paart account for idling at .8galperhour
    pfcpercon = portfuelcost / numcon
    fcpm = (fcost - portfuelcost) / mvmiles
except:
    pfcpercon = 0.00
    fcpm = 0.00
    drivercostpermile = 0.00

put_cost('PortFuelCost', m3, pfcpercon, 2)
put_cost('DriverCPMMetro', m3, drvc1, 2)
put_cost('DriverCPMInterMetro', m3, drvc2, 2)
put_cost('DriverCPMMetroAway', m3, drvc3, 2)
put_cost('FuelCPM', m3, fcpm, 2)






for month in range(1,13):
    days = calendar.monthrange(thisyear,month)[1]
    xdfrom = datetime.datetime(thisyear, month, 1)
    xdto = datetime.datetime(thisyear,month,days)
    sd = xdfrom.date()
    ed = xdto.date()

    m3 = calendar.month_abbr[month]
    toll_amt, toll_num = get_tolls(sd,ed)
    print(f'{sd}-{ed} Tolls:${d2s(toll_amt)} #Tolls:{toll_num}')
    put_cost('Tolls',m3,toll_amt,2)
    put_cost('NumTolls', m3, toll_num, 0)

    tmiles, ntrips = get_tmiles(sd, ed)
    put_cost('TruckMiles', m3, tmiles, 1)
    put_cost('TruckDays', m3, ntrips, 0)

    fuelcost = get_fuel(sd, ed)
    put_cost('FuelCost', m3, fuelcost, 2)

    port_time, port_miles, port_entries, port_time_withcust, port_entries_withcust, port_time_without, port_entries_without = get_port(sd,ed)
    put_cost('PortTime', m3, port_time, 1)
    put_cost('PortMiles', m3, port_miles, 1)
    put_cost('PortEntries', m3, port_entries, 0)
    put_cost('PortTimeCustoms', m3, port_time_withcust, 1)
    put_cost('PortEntriesCustoms', m3, port_entries_withcust, 0)
    put_cost('PortTimeNoCust', m3, port_time_without, 1)
    put_cost('PortEntriesNoCust', m3, port_entries_without, 0)

    condat = Truckcost.query.filter(Truckcost.Cost == 'Containers').first()
    ebase = f'numcon = condat.{m3} '
    exec(ebase)
    numcon = float(numcon)
    numwithcust = port_entries_withcust
    numwithout = numcon - numwithcust
    put_cost('ConWithCust', m3, numwithcust, 0)
    put_cost('ConNoCust', m3, numwithout, 0)

    driverpay, driverhrs = get_pay('Driver', sd, ed)
    try:
        burdrate = driverpay / driverhrs
    except:
        burdrate = None
    put_cost('DriverFullCost', m3, driverpay, 2)
    put_cost('DriverHours', m3, driverhrs, 2)
    put_cost('DriverBurdRate', m3, burdrate, 2)

    ######## Update the Key Cost Metrics ##########
    ######### PORT ################################
    ###PortDriverCost is $perContainer spent on driver in port
    dat = Truckcost.query.filter(Truckcost.Cost == 'DriverBurdRate').first()
    ebase = f'rate = dat.{m3} '
    exec(ebase)
    try:
        rate = float(rate)
    except:
        rate = 0.00

    dat = Truckcost.query.filter(Truckcost.Cost == 'PortTime').first()
    ebase = f'ptime = dat.{m3} '
    exec(ebase)
    try:
        ptime = float(ptime)
    except:
        ptime = 0.00

    try:
        pdrvcost = rate * ptime / numcon
    except:
        pdrvcost = 0.00

    put_cost('PortDriverCost', m3, pdrvcost, 2)

    ##############################################################

    dat = Truckcost.query.filter(Truckcost.Cost == 'PortMiles').first()
    ebase = f'pmiles = dat.{m3} '
    exec(ebase)
    try:
        pmiles = float(pmiles)
    except:
        pmiles = 0.00

    dat = Truckcost.query.filter(Truckcost.Cost == 'TruckMiles').first()
    ebase = f'tmiles = dat.{m3} '
    exec(ebase)
    try:
        tmiles = float(tmiles)
    except:
        tmiles = 0.00

    dat = Truckcost.query.filter(Truckcost.Cost == 'DriverFullCost').first()
    ebase = f'dcost = dat.{m3} '
    exec(ebase)
    try:
        dcost = float(dcost)
    except:
        dcost = 0.00

    dat = Truckcost.query.filter(Truckcost.Cost == 'FuelCost').first()
    ebase = f'fcost = dat.{m3} '
    exec(ebase)
    try:
        fcost = float(fcost)
    except:
        fcost = 0.00

    # Calc Net driver cost when not in port
    mvdcost = dcost - (ptime * rate)

    # Calc Net truck miles when not in port
    mvmiles = tmiles - pmiles

    try:
        drvc1 = rate / 30.0 #InnerCity Avg Vel
        drvc2 = rate / 38.0  # InnerMetro Avg Vel
        drvc3 = rate / 47.0  # MetroOut Avg Vel
        fuelcostpermile = fcost / tmiles
        portfuelcost = fuelcostpermile * pmiles + 0.8 * ptime * 3.0  # 2nd paart account for idling at .8galperhour
        pfcpercon = portfuelcost / numcon
        fcpm = (fcost - portfuelcost) / mvmiles
    except:
        pfcpercon = 0.00
        fcpm = 0.00
        drivercostpermile = 0.00

    put_cost('PortFuelCost', m3, pfcpercon, 2)
    put_cost('DriverCPMMetro', m3, drvc1, 2)
    put_cost('DriverCPMInterMetro', m3, drvc2, 2)
    put_cost('DriverCPMMetroAway', m3, drvc3, 2)
    put_cost('FuelCPM', m3, fcpm, 2)
    ##############################################################



tunnel.stop()
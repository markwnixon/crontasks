import requests
import json
import datetime
from math import sqrt
from cronfuncs import dropupdate, d1s, d2s
from datetime import timedelta


daybackfrom = 7
daybackto = 1
printif = 0
printlog = 1
# (daybackto=0 is today; from 1 to 0 is yesterday and today)

runat = datetime.datetime.now()
print(' ') if printlog == 1 else 1
print('______________________________________________________________________') if printlog == 1 else 1
print('This sequence of AAA_quartix.py run at ', runat) if printlog == 1 else 1
print('______________________________________________________________________') if printlog == 1 else 1
print(' ') if printlog == 1 else 1


today = datetime.datetime.today()
#today = today.date()
print(today) if printif == 1 else 1

#response = requests.post("https://qws.quartix.com/v2/api/auth", params=parameters)

from CCC_system_setup import usernames, passwords, quartix_customer_id, quartix_app
from remote_db_connect import tunnel, db
from models import Trucklog, Drivers, Driverlog, Portlog, Interchange
uname = usernames['quartix']
password = passwords['quartix']

def driver_find(tdate,unit,driverid):
    driver = 'NAY'
    ddat = Drivers.query.filter((Drivers.JobStart <= tdate) & (Drivers.JobEnd >= tdate) & (Drivers.Tagid == driverid)).first()
    if ddat is not None:
        driver = ddat.Name
    else:
        ddat = Drivers.query.filter( (Drivers.JobStart <= tdate) & (Drivers.JobEnd >= tdate) & (Drivers.Truck == unit)).first()
        if ddat is not None:
            driver = ddat.Name
    return driver

def get_odometer(vid, distance):
    parameters = {'VehicleIDList': [vid]}
    API_ENDPOINT = "https://qws.quartix.com/v2/api/vehicles/odometer"
    r = s.get(url=API_ENDPOINT, params=parameters)
    dataret = r.json()['Data']
    if dataret:
        dataret = dataret[0]
        ostart = dataret['OdoEstimateKm'] * .62137
        ostop = ostart + distance
        ostart = int(ostart)
        ostop = int(ostop)
    else:
        ostart = 0
        ostop = 0

    return ostart, ostop

def insert_driverbase(datehere, driver, vid, sdt, edt, distance, sloc, eloc, ids, units):
    if distance > 0:
        ostart, ostop = get_odometer(vid, distance)
    else:
        ostart = 0
        ostop = 0

    for idx, id in enumerate(ids):
        if id == vid:
            unit = units[idx]

    shift = str(edt - sdt)
    try:
        (hr, min, sec) = shift.split(':')
        shift_time = round(float(int(hr) * 3600 + int(min) * 60 + int(sec)) / 3600.0, 2)
    except:
        shift_time = 0

    tdat = Driverlog.query.filter((Driverlog.Date == datehere) & (Driverlog.Truck == unit)).first()
    if tdat is None:
        print(f'Adding to Driverlog for Date:{datehere} and Driver:{driver} in Unit:{unit}') if printlog == 1 else 1
        input = Driverlog(Date=datehere, Driver=driver, GPSin=sdt, GPSout=edt,Odomstart=str(ostart), Odomstop=str(ostop), Truck=unit,Locationstart = sloc, Locationstop = eloc, Shift = d1s(shift_time), Status='0')
        db.session.add(input)
        db.session.commit()
    else:
        print(f'Data Already Exists in Driverlog for Date:{datehere} and Driver:{driver} in Unit:{unit}')

def insert_portdata(datehere,portstart,portstop,porttime,custtime,thisunit,portmiles):
    pdat = Portlog.query.filter( (Portlog.Date == datehere) & (Portlog.GPSin==portstart)).first()
    if pdat is None:
        if 1 == 1:
            pt = str(porttime)
            print(pt) if printif == 1 else 1
            (hr, min, sec) = pt.split(':')
            portdec = round(float(int(hr) * 3600 + int(min) * 60 + int(sec)) / 3600.0, 2)
        try:
            ct = str(custtime)
            (hr, min, sec) = ct.split(':')
            custdec = round(float(int(hr) * 3600 + int(min) * 60 + int(sec)) / 3600.0, 2)
        except:
            custdec = 0

        idata = Interchange.query.filter(Interchange.Date == datehere).all()
        cin = None
        cout = None
        pcheck = portstart - timedelta(minutes=10)
        for idat in idata:
            datehere_s = (datetime.date.today() - datetime.timedelta(thisback)).strftime("%d-%b-%Y")
            time = idat.Time
            try:
                dstring = datehere_s + 'T' + time
                dt_time = datetime.datetime.strptime(dstring, "%d-%b-%YT%H:%M")
            except:
                dt_time = datetime.datetime.strptime(datehere_s, "%d-%b-%Y")
            print('idat',time,dt_time) if printif == 1 else 1
            type = idat.Type

            if dt_time >= pcheck and dt_time <= portstop:
                if 'In' in type:
                    cin = idat.Container
                elif 'Out' in type:
                    cout = idat.Container

        print(f'Adding to Portlog for Date:{datehere} in Unit:{thisunit}') if printlog == 1 else 1
        input = Portlog(Date=datehere,Unit=thisunit,Driver=None,GPSin=portstart,GPSout=portstop,PortTime=d2s(portdec),CustTime=d2s(custdec),ConIn=cin,ConOut=cout,Status='0',Portmiles=d2s(portmiles))
        db.session.add(input)
        db.session.commit()

def in_box(lat,lon,pts):
    if lat > pts[0] and lat < pts[2] and lon > pts[1] and lon < pts[3]:
        return 1
    else:
        return 0

def linelen(pts):
    pblat, pblon, ptlat, ptlon = pts[0], pts[1], pts[2], pts[3]
    dx, dy = ptlon - pblon, ptlat - pblat
    return sqrt(dx*dx+dy*dy)

def linemiles(pts):
    pblat, pblon, ptlat, ptlon = pts[0], pts[1], pts[2], pts[3]
    dx, dy = ptlon - pblon, ptlat - pblat
    #Simplified conversion of lat, lon to miles, lon only good at Baltimore lat
    dxm, dym = dx*53.0, dy*69.0
    return sqrt(dxm*dxm+dym*dym)


def near_line(lat,lon,pts):
    pblat, pblon, ptlat, ptlon = pts[0], pts[1], pts[2], pts[3]
    l3 = linelen(pts)
    l2 = linelen([pblat,pblon,lat,lon])
    l1 = linelen([ptlat, ptlon, lat, lon])
    yd = (l1*l1 + l3*l3 - l2*l2)/(2*l3)
    xd = sqrt(l1*l1 - yd*yd)

    return xd



s = requests.Session()

data = {'CustomerID':quartix_customer_id,
        'UserName':uname,
        'Password':password,
        'Application':quartix_app
        }

API_ENDPOINT = "https://qws.quartix.com/v2/api/auth"

#r = requests.post(url = API_ENDPOINT, data = data)
s.post(url = API_ENDPOINT, data = data)
print(s.cookies) if printif == 1 else 1

parameters = {}
API_ENDPOINT = "https://qws.quartix.com/v2/api/groups"
r = s.get(url = API_ENDPOINT)
dataret = r.json()['Data'][0]
print(dataret) if printif == 1 else 1
groupid = dataret['GroupID']
print(groupid)


parameters = {'GroupID':groupid}
API_ENDPOINT = "https://qws.quartix.com/v2/api/vehicles"
r = s.get(url = API_ENDPOINT, params = parameters)
dataret = r.json()['Data']
ids = []
vins = []
units = []
print(dataret) if printif == 1 else 1
for dat in dataret:
    ids.append(dat['VehicleId'])
    vins.append(dat['RegistrationNumber'])
    units.append(dat['VehicleInitials'])

print(ids) if printif == 1 else 1
print(vins) if printif == 1 else 1
print(units) if printif == 1 else 1
print(' ') if printif == 1 else 1
print(' ') if printif == 1 else 1



#Prepare for date extractions
delta = daybackfrom - daybackto
for jback in range(delta+1):
    thisback = daybackfrom - jback
    print(thisback) if printif == 1 else 1
    datehere_s = (datetime.date.today() - datetime.timedelta(thisback)).strftime("%d-%b-%Y")
    datehere = datetime.date.today() - datetime.timedelta(thisback)
    print(datehere) if printif == 1 else 1

    for jid, vid in enumerate(ids):

        thisunit = units[jid]

        #Define geolocation parameters:
        portbox = [39.243, -76.55376, 39.264, -76.52198]

        if thisunit == '437':
            entryline = [39.25605, -76.53826, 39.25794, -76.53753]
            exitline = [39.256, -76.53826, 39.25749, -76.53753]
            exit_criteria = .000210

        elif thisunit == '436':
            entryline = [39.25605, -76.53826, 39.25794, -76.53753]
            exitline = [39.256, -76.53826, 39.25749, -76.53753]
            exit_criteria = .000242

        elif thisunit == '435':
            entryline = [39.25605, -76.53826, 39.25850, -76.53730]
            exitline = [39.256, -76.53826, 39.25749, -76.53753]
            exit_criteria = .000210

        else:
            entryline = [39.25605, -76.53826, 39.25850, -76.53730]
            exitline = [39.256, -76.53826, 39.25749, -76.53753]
            exit_criteria = .000210

        print(f'Grabbing Data for Unit:{thisunit} VIN:{vins[jid]} on Date{datehere_s}') if printif == 1 else 1
        print('') if printif == 1 else 1

        parameters = {
                      'VehicleID':vid,
                      'StartDay':datehere_s
                      }

        API_ENDPOINT = "https://qws.quartix.com/v2/api/vehicles/route"
        r = s.get(url = API_ENDPOINT, params=parameters)
        dataret = r.json()['Data']['Summary']

        #Calculate time in port:
        otherset = r.json()['Data']['Trips']
        #print('Otherset',otherset)
        inport, custtime, cstart, cstop = 0, 0, 0, 0
        customs = 'no'
        for kdx, tset in enumerate(otherset):
            print(f'Trip No. {kdx}') if printif == 1 else 1
            routes = tset['Route']

            for rout in routes:
                #print('###Route###',rout)
                etype, head, dtnow = rout['EventType'], rout['Heading'], rout['EventDateTime']
                if etype != 'Distance':
                    locat = rout['Location']
                else:
                    locat = 'None'
                tstamp = dtnow[0:16]
                timehere = datetime.datetime.strptime(tstamp, '%Y-%m-%dT%H:%M')
                lat, lon = rout['Latitude'],   rout['Longitude']

                if in_box(lat,lon,portbox):
                    #Now we look at the details within:
                    #Save this value in case we need it later...
                    last_box = timehere

                    # Look for customs only if currently inside port:
                    if inport == 1:
                        geolon = -(lon + 76.536)
                        if geolon < 0.0 and customs == 'no':
                            customs = 'yes'
                            cstart = timehere
                            cstop = 0
                        elif geolon > 0.0 and customs == 'yes':
                            cstop = timehere
                            custtime = timehere - cstart
                            customs = 'comp'

                        disttohere = linemiles([latlast, lonlast, lat, lon])
                        portmiles = portmiles + disttohere
                        latlast = lat
                        lonlast = lon
                        #print(f'Port run on and lat {lat}, lon {lon} miles {portmiles}')


                    #Look for entrance into port only if not inside port already:
                    if etype == 'Distance':
                        if inport == 0 and lat<entryline[2] and lat>entryline[0]:
                            crit_entry = near_line(lat, lon, entryline)
                            print('Route', locat, timehere, lat, lon, head,crit_entry) if printif == 1 else 1
                            if crit_entry < .001 and (head > 170 and head < 260):
                                #We are entering port, see if new port entry:
                                #print('***Port Entry***', locat, timehere, lat, lon, geolat, geolon)
                                print(' ') if printif == 1 else 1
                                print('%%%%%%In PORT Clicked ON%%%%%%%') if printif == 1 else 1
                                print(' ') if printif == 1 else 1
                                portstart = timehere
                                latlast,lonlast = lat, lon
                                portmiles = 0.0
                                inport = 1

                        elif inport == 1 and lat<exitline[2] and lat>exitline[0]:
                            crit_exit = near_line(lat, lon, exitline)
                            print('Route', locat, timehere, lat, lon, head, crit_exit) if printif == 1 else 1
                            if crit_exit < exit_criteria and (head > 300 or head < 40):
                                #print('###Port Exit###',timehere,geolat,geolon)
                                customs = customs.replace('comp', 'yes')
                                print(' ') if printif == 1 else 1
                                print('%%%%%%PORT Clicked OFF%%%%%%%') if printif == 1 else 1
                                print(' ') if printif == 1 else 1
                                portstop = timehere
                                porttime = timehere - portstart
                                print(f'****Time in port start:{portstart} end:{timehere} time in:{porttime} and customs:{customs}') if printif == 1 else 1
                                if customs == 'yes':
                                    print(f'Customs start:{cstart} and stop:{cstop} for total time of {custtime}') if printif == 1 else 1
                                else:
                                    custtime = 0
                                insert_portdata(datehere, portstart, portstop, porttime, custtime, thisunit, portmiles)
                                inport = 0
                                portstart = 0
                                portmiles = 0.0
                                customs = 'no'
                                custtime = 0
                                cstart = 0
                                cstop = 0
                        else:
                            # We are in the port, but not at the beginning or end so calculate distance run
                            crit_exit = near_line(lat, lon, exitline)
                            print('Route in portbox only', locat, timehere, lat, lon, head, crit_exit) if printif == 1 else 1

        if inport == 1:
            # Have an end to a day and showing still inport, close down using last_box
            porttime = last_box - portstart
            insert_portdata(datehere, portstart, last_box, porttime, custtime, thisunit, portmiles)





                #print('***Route***',locat, timehere, lat, lon, geolat, geolon)


        print(dataret) if printif == 1 else 1
        trips = dataret['NumberOfTrips']
        distance = dataret['Distance']*.62137

        print('Summary Data from /route') if printif == 1 else 1
        if distance > 0:
            print(f'#Trips:{trips}') if printif == 1 else 1
            print(f'Distance:{distance} miles') if printif == 1 else 1
        else:
            print('Vehicle Not Active') if printif == 1 else 1

        print('') if printif == 1 else 1


        parameters = {'GroupID':groupid,
                      'VehicleIDList':[vid],
                      'StartDay':datehere_s,
                      'EndDay':datehere_s
                      }

        API_ENDPOINT = "https://qws.quartix.com/v2/api/vehicles/trips"
        r = s.get(url = API_ENDPOINT, params=parameters)
        dataret = r.json()['Data']
        didlist = []
        if dataret:
            total_optime = 0.0
            print('Data from Trips:') if printif == 1 else 1
            for j,dr in enumerate(dataret):
                print(dr) if printif == 1 else 1
                # Grab the key data:
                start = dr['StartDateTime']
                loc1 = dr['StartLocation']
                if j == 0:
                    slat = dr['StartLat']
                    slon = dr['StartLong']
                    rm_max = 0.0
                    loc_max = loc1
                    start = start[0:16]
                    start_dt = datetime.datetime.strptime(start, '%Y-%m-%dT%H:%M')
                    loc_start = dr['StartLocation']
                    if trips == 1:
                        rm_max = distance/2

                driverid = dr['DriverID']
                didlist.append(driverid)
                ended = dr['EndDateTime']
                ended = ended[0:16]
                loc2 = dr['EndLocation']
                elat = dr['EndLat']
                elon = dr['EndLong']
                print(ended) if printif == 1 else 1
                ttime = dr['TravelTime'] * 24
                itime = dr['IdlingTime'] * 24
                optime = ttime + itime
                total_optime = total_optime + optime

                ended_dt = datetime.datetime.strptime(ended,'%Y-%m-%dT%H:%M')
                print(ended_dt) if printif == 1 else 1
                print(f'{driverid} started at {loc1} on {start}, lat:{slat} lon:{slon}') if printif == 1 else 1
                print(f'{driverid} ended at {loc2} on {ended}, lat:{elat} lon:{elon}') if printif == 1 else 1
                dlat = (slat-elat)*69
                dlon = (slon-elon)*53
                radialmiles = sqrt(dlat*dlat + dlon*dlon)
                if radialmiles > rm_max:
                    rm_max = radialmiles
                    loc_max = loc2
                print(f'At end of trip {j} radialmiles from base={radialmiles}') if printif == 1 else 1

            if distance > 0:
                ostart, ostop = get_odometer(vid, distance)
            else:
                ostart = 0
                ostop = 0

            shift = str(ended_dt - start_dt)
            try:
                (hr, min, sec) = shift.split(':')
                shift_time = round(float( int(hr) * 3600 + int(min) * 60 + int(sec) )/3600.0, 2)
            except:
                shift_time = 0
            tag = vins[jid]
            for did in didlist:
                if did != 0:
                    driverid = did
            unit = units[jid]
            driver = driver_find(datehere,unit,driverid)
            print(shift_time) if printif == 1 else 1
            print('Items for Database:') if printif == 1 else 1
            print(f'Date:{datehere}') if printif == 1 else 1
            print(start_dt) if printif == 1 else 1
            print(ended_dt) if printif == 1 else 1
            print(f'Unit:{unit}') if printif == 1 else 1
            print(f'Tag/Vin:{tag}') if printif == 1 else 1
            print(f'Distance:{distance}') if printif == 1 else 1
            print(f'Maximum radial miles {rm_max} at {loc_max}') if printif == 1 else 1
            print(f'OdomStart:{ostart}') if printif == 1 else 1
            print(f'OdomStop:{ostop}') if printif == 1 else 1
            print(f'Oper_Time:{total_optime}') if printif == 1 else 1
            print(f'Driver:{driverid}') if printif == 1 else 1
            print(f'Driver:{driver}') if printif == 1 else 1
            print(f'LocStart:{loc_start}') if printif == 1 else 1
            print(f'LocStop:{loc2}') if printif == 1 else 1

            di = d1s(distance)

            tdat = Trucklog.query.filter((Trucklog.Date == datehere) & (Trucklog.Tag == tag)).first()
            if tdat is None:
                print(f'Adding to Trucklog for Date:{datehere} and Unit:{units[jid]}') if printlog == 1 else 1
                input = Trucklog(Date=datehere, Unit=units[jid], Tag = tag, GPSin=start_dt, GPSout=ended_dt, Shift=d2s(shift_time), Distance=di,
                                 Gotime=d2s(total_optime), Rdist=d2s(rm_max), Rloc=loc_max, Odomstart=str(ostart), Odomstop=str(ostop), Odverify=None,
                                 DriverStart=driver, Maintrecord='None', Locationstart=loc_start, DriverEnd=driver,
                                 Locationstop=loc2, Maintid=str(driverid), Status='0')
                db.session.add(input)
                db.session.commit()
            else:
                print(f'Data Already Exists in Trucklog for Date:{datehere} and Unit:{units[jid]}') if printlog == 1 else 1

            pdata = Portlog.query.filter( (Portlog.Date == datehere) & (Portlog.Unit == units[jid]) ).all()
            for pdat in pdata:
                pdat.Driver = driver
                db.session.commit()

        else:
            print('No data here for truck') if printif == 1 else 1


    # Get a list of active drivers and their id tags on this date
    didlist = []
    drlist = []
    # Date id tags began
    ddata = Drivers.query.filter((Drivers.JobStart <= datehere) & (Drivers.JobEnd >= datehere)).all()
    for dat in ddata:
        driver = dat.Name
        did = dat.Tagid
        didlist.append(did)
        drlist.append(driver)


    for jdx,tid in enumerate(didlist):
        driver = drlist[jdx]
        parameters = {
                      'DriverIDList':[int(tid)],
                      'StartDay':datehere_s,
                      'EndDay':datehere_s
                      }

        API_ENDPOINT = "https://qws.quartix.com/v2/api/drivers/trips"
        r = s.get(url = API_ENDPOINT, params=parameters)
        dataret = r.json()['Data']
        print(f'Attempting to get return on ID {tid} Driver {driver}') if printif == 1 else 1
        #print(dataret)
        if dataret:
            vidlist=[]
            distance = 0.0
            for jdx,dr in enumerate(dataret):
                print(dr) if printif == 1 else 1
                dist = dr['Distance'] * .62137
                distance = distance + dist
                # Grab the key data:
                start = dr['StartDateTime']
                loc1 = dr['StartLocation']
                if jdx == 0:
                    slat = dr['StartLat']
                    slon = dr['StartLong']
                    rm_max = 0.0
                    loc_max = loc1
                    vstart = start[0:16]
                    vstart_dt = datetime.datetime.strptime(vstart, '%Y-%m-%dT%H:%M')
                    vloc_start = dr['StartLocation']
                    if trips == 1:
                        rm_max = distance/2

                vehicleid = dr['VehicleID']
                vidlist.append(vehicleid)
                # Check to see if changed vehicles:
                if jdx > 0:
                    if vidlist[jdx] != vidlist[jdx-1]:
                        vid = vidlist[jdx-1]
                        print(f'In vehicle unit {vid}') if printif == 1 else 1
                        print(f'Shift started {vstart} at {vloc_start}') if printif == 1 else 1
                        print(f'Shift stopped {ended} at {loc2}') if printif == 1 else 1
                        insert_driverbase(datehere, driver, vid, vstart_dt, ended_dt, distance, vloc_start, loc2, ids, units)

                        # Now set new start for next truck before we get the new values:
                        vstart = ended[0:16]
                        vstart_dt = datetime.datetime.strptime(vstart, '%Y-%m-%dT%H:%M')
                        vloc_start = loc2
                        distance = 0


                ended = dr['EndDateTime']
                ended = ended[0:16]
                loc2 = dr['EndLocation']
                elat = dr['EndLat']
                elon = dr['EndLong']
                print(ended) if printif == 1 else 1
                ttime = dr['TravelTime'] * 24
                itime = dr['IdlingTime'] * 24
                optime = ttime + itime
                total_optime = total_optime + optime

                ended_dt = datetime.datetime.strptime(ended,'%Y-%m-%dT%H:%M')
                print(ended_dt) if printif == 1 else 1
                #print(f'{driverid} started at {loc1} on {start}, lat:{slat} lon:{slon}')
                #print(f'{driverid} ended at {loc2} on {ended}, lat:{elat} lon:{elon}')
                dlat = (slat-elat)*69
                dlon = (slon-elon)*53
                radialmiles = sqrt(dlat*dlat + dlon*dlon)
                if radialmiles > rm_max:
                    rm_max = radialmiles
                    loc_max = loc2
                #print(f'At end of trip {j} radialmiles from base={radialmiles}')


            shift = str(ended_dt - start_dt)
            try:
                (hr, min, sec) = shift.split(':')
                shift_time = round(float(int(hr) * 3600 + int(min) * 60 + int(sec)) / 3600.0, 2)
            except:
                shift_time = 0

            print(f'In vehicle unit {vehicleid}') if printif == 1 else 1
            print(f'Shift started {vstart} at {vloc_start}') if printif == 1 else 1
            print(f'Shift stopped {ended} at {loc2}') if printif == 1 else 1

            insert_driverbase(datehere, driver, vehicleid, vstart_dt, ended_dt, distance, vloc_start, loc2, ids, units)


tunnel.stop()
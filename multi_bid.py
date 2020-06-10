from datetime import datetime, timedelta
from CCC_system_setup import scac, addpath1, apikeys, companydata
from remote_db_connect import tunnel, db
from models import Drivers, Vehicles, DriverAssign, Trucklog, KeyInfo
from utils import d2s, d1s
import os
import xlrd, xlwt
from requests import get
import math

API_KEY_GEO = apikeys['gkey']
API_KEY_DIS = apikeys['dkey']
cdata = companydata()

def roundup(x):
    return int(math.ceil(x / 10.0)) * 10

def checkcross(lam,la_last,la,lom,lo_last,lo):
    lacross = 0
    locross = 0
    if (la_last<lam and la>lam) or (la_last>lam and la<lam):
        lacross = 1
    if (lo_last<lom and lo>lom) or (lo_last>lom and lo<lom):
        locross = 1
    return lacross, locross

def direct_resolver(json):
    di, du, ht, la, lo = [],[],[],[],[]
    t1 = json['routes'][0]['legs'][0]['steps']
    for t2 in t1:
        di.append(t2['distance']['text'])
        du.append(t2['duration']['text'])
        ht.append(t2['html_instructions'])
        la.append(t2['end_location']['lat'])
        lo.append(t2['end_location']['lng'])

    return di, du, ht, la, lo

def get_directions(start,end):
    dists, duras, lats, lons = [], [], [], []
    tot_dist = 0.0
    tot_dura = 0.0
    start = start.replace(" ", "+")
    end = end.replace(" ", "+")
    url = f'https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}'
    url = url + f'&key={API_KEY_DIS}'
    #print(url)
    response = get(url)
    dis, dus, hts, las, los  = direct_resolver(response.json())

    #Convert all mixed units to miles, hours and convert from text to floats
    for di in dis:
        if 'mi' in di:
            nu = float(di.replace('mi',''))
        elif 'ft' in di:
            nu = float(di.replace('ft',''))/5280.0
        else:
            nu = 0.0
        dists.append(nu)
        tot_dist += nu

    for du in dus:
        dul = du.split()
        if len(dul) == 4:
            hr = float(dul[0])
            min = float(dul[2])
            hrs = hr + min/60.0
        elif len(dul) == 2:
            if 'hr' in du:
                hrs = float(dul[0])
            elif 'min' in du:
                hrs = float(dul[0])/60.0
            else:
                hrs = 0.0
        duras.append(hrs)
        tot_dura += hrs

    for la in las:
        lats.append(float(la))
    for lo in los:
        lons.append(float(lo))

    return dists, duras, lats, lons, hts, tot_dist, tot_dura

#Set location of xls file to read from
# Give the location of the file
loc = ("/home/mark/Documents/Maersk Bid Sheet2.xlsx")

# To open Workbook
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(3)
sheet.cell_value(0, 0)

from xlwt import Workbook

wbout = Workbook()
sheet1 = wbout.add_sheet('Baltimore')
imili = 1



# Extracting number of rows and columns
print(f'The data sheet has {sheet.nrows} rows')
print(f'The data sheet has {sheet.ncols} cols')
print(f'The header for columns are:')
for i in range(sheet.ncols):
    print(f'Column {i}: {sheet.cell_value(7, i)}')
#for mx in range(1,sheet.nrows):

for mx in range(8,867):
    if imili == 1:
        id = str(sheet.cell_value(mx, 2))
        region = str(sheet.cell_value(mx, 3))
        locfrom = str(sheet.cell_value(mx, 4))
        locto = str(sheet.cell_value(mx, 5))
        movetype = str(sheet.cell_value(mx, 6))
        equiptype = str(sheet.cell_value(mx, 7))
        haz = str(sheet.cell_value(mx, 8))
        ratetype = str(sheet.cell_value(mx, 9))
    else:
        id = str(sheet.cell_value(mx, 2))
        locfrom = str(sheet.cell_value(mx, 3))
        locto = str(sheet.cell_value(mx, 4))
        movetype = str(sheet.cell_value(mx, 5))
        equiptype = str(sheet.cell_value(mx, 6))
        haz = str(sheet.cell_value(mx, 7))
        ratetype = str(sheet.cell_value(mx, 8))
    tollmat = []
    if 'seagirt' in locfrom.lower(): locfrom = 'Seagirt Marine Terminal, Baltimore, MD 21224'
    if 'seagirt' in locto.lower(): locto = 'Seagirt Marine Terminal, Baltimore, MD 21224'

    print(f'Running row {mx+1} for {id} {locfrom} {locto} {movetype} {equiptype} {haz} {ratetype}')

    if haz != 'Y' and ('seagirt' in locfrom.lower() or 'seagirt' in locto.lower()):

        try:
            miles, hours, lats, lons, dirdata, tot_dist, tot_dura = get_directions(locfrom,locto)
        except:
            try:
                if ',' not in locfrom: locfrom = locfrom + ', MD'
                if ',' not in locto: locto = locto + ', MD'
                miles, hours, lats, lons, dirdata, tot_dist, tot_dura = get_directions(locfrom, locto)
            except:
                try:
                    if ',' not in locfrom: locfrom = locfrom.replace('MD','PA')
                    if ',' not in locfrom: locfrom = locfrom.replace('MD','PA')
                    miles, hours, lats, lons, dirdata, tot_dist, tot_dura = get_directions(locfrom, locto)
                except:
                    try:
                        if ',' not in locfrom: locfrom = locfrom.replace('PA', 'VA')
                        if ',' not in locfrom: locfrom = locfrom.replace('PA', 'VA')
                        miles, hours, lats, lons, dirdata, tot_dist, tot_dura = get_directions(locfrom, locto)
                    except:
                        print('City find failure')




        # Calculate road tolls
        tollroadlist = ['I-76', 'NJ Tpke']
        tollroadcpm = [.784, .275]
        legtolls = len(dirdata) * [0.0]
        legcodes = len(dirdata) * ['None']
        for lx, mi in enumerate(miles):
            for nx, tollrd in enumerate(tollroadlist):
                if tollrd in dirdata[lx]:
                    legtolls[lx] = tollroadcpm[nx] * mi
                    legcodes[lx] = tollrd

        # Calculate plaza tolls
        fm_tollbox = [39.267757, -76.610192, 39.261248, -76.563158]
        bht_tollbox = [39.259962, -76.566240, 39.239063, -76.603324]
        fsk_tollbox = [39.232770, -76.502453, 39.202279, -76.569906]
        bay_tollbox = [39.026893, -76.417512, 38.964938, -76.290104]
        sus_tollbox = [39.585193, -76.142883, 39.552328, -76.033975]
        new_tollbox = [39.647121, -75.774523, 39.642613, -75.757187]  # Newark Delaware Toll Center
        dmb_tollbox = [39.702146, -75.553479, 39.669730, -75.483284]
        tollcodes = ['FM', 'BHT', 'FSK', 'BAY', 'SUS', 'NEW', 'DMB']
        tollboxes = [fm_tollbox, bht_tollbox, fsk_tollbox, bay_tollbox, sus_tollbox, new_tollbox, dmb_tollbox]

        for jx, lat in enumerate(lats):
            stat1 = 'ok'
            stat2 = 'ok'
            stat3 = 0
            stat4 = 0
            tollcode = 'None'
            la = float(lat)
            lo = float(lons[jx])
            for kx, tollbox in enumerate(tollboxes):
                lah = max([tollbox[0], tollbox[2]])
                lal = min([tollbox[0], tollbox[2]])
                loh = max([tollbox[1], tollbox[3]])
                lol = min([tollbox[1], tollbox[3]])
                if la > lal and la < lah:
                    stat1 = 'toll'
                    if lo > lol and lo < loh:
                        stat2 = 'toll'
                        tollcode = tollcodes[kx]
                        #Only cross plaza one time:
                        if tollcode not in legcodes:
                            legtolls[jx] = 24.00
                            legcodes[jx] = tollcode
                if jx > 0:
                    lam = (lah + lal) / 2.0
                    lom = (loh + lol) / 2.0
                    la_last = float(lats[jx - 1])
                    lo_last = float(lons[jx - 1])
                    stat3, stat4 = checkcross(lam, la_last, la, lom, lo_last, lo)
                    if stat3 == 1 and stat4 == 1:
                        tollcode = tollcodes[kx]
                        if tollcode not in legcodes:
                            legtolls[jx] = 24.00
                            legcodes[jx] = tollcode
            ##print(lat,lons[jx],stat1, stat2, stat3, stat4, tollcode)

        tot_tolls = 0.00
        ex_drv = 27.41
        ex_fuel = .48
        ex_toll = 24.00
        ex_insur = 4.00
        ex_rm = .22
        ex_misc = .04
        ex_ga = 15
        expdata = [d2s(ex_drv), d2s(ex_fuel), d2s(ex_toll), d2s(ex_insur), d2s(ex_rm), d2s(ex_misc), d2s(ex_ga)]

        porttime = 1.4
        loadtime = 2.0
        triptime = tot_dura * 2.0
        glidetime = 1.0 + triptime * .01
        tottime = porttime + loadtime + triptime + glidetime
        timedata = [d1s(triptime), d1s(porttime), d1s(loadtime), d1s(glidetime), d1s(tottime)]

        tripmiles = tot_dist * 2.0
        portmiles = .4
        glidemiles = 10 + .005 * tripmiles
        totmiles = tripmiles + portmiles + glidemiles
        distdata = [d1s(tripmiles), d1s(portmiles), '0.0', d1s(glidemiles), d1s(totmiles)]

        newdirdata = []
        for lx, aline in enumerate(dirdata):
            tot_tolls += legtolls[lx]
            aline = aline.replace('<div style="font-size:0.9em">Toll road</div>', '')
            aline = aline.strip()
            # print(aline)
            # print(f'Dist:{d1s(miles[lx])}, Time:{d1s(hours[lx])}, ')
            if legtolls[lx] < .000001:
                newdirdata.append(f'{d1s(miles[lx])} MI {d2s(hours[lx])} HRS {aline}')
            else:
                newdirdata.append(
                    f'{d1s(miles[lx])} MI {d2s(hours[lx])} HRS {aline} Tolls:${d2s(legtolls[lx])}, TollCode:{legcodes[lx]}')

        # Cost Analysis:
        #Charge $10 per day for chassis
        if tot_dura < 4.0:
            our_chassis = 10.0
        else:
            our_chassis = 20.00

        #Slight increase for reefer
        if equiptype == 'REEF':
            reefer = 20.00
        else:
            reefer = 0.00

        cost_drv = tottime * ex_drv
        cost_fuel = totmiles * ex_fuel
        cost_tolls = 2.0 * tot_tolls

        cost_insur = tottime * ex_insur
        cost_rm = totmiles * ex_rm
        cost_misc = totmiles * ex_misc

        cost_direct = cost_drv + cost_fuel + cost_tolls + cost_insur + cost_rm + cost_misc
        cost_ga = cost_direct * ex_ga / 100.0
        cost_total = cost_direct + cost_ga
        costdata = [d2s(cost_drv), d2s(cost_fuel), d2s(cost_tolls), d2s(cost_insur), d2s(cost_rm), d2s(cost_misc),
                    d2s(cost_ga), d2s(cost_direct), d2s(cost_total)]

        bid_base = cost_total * 1.2 + our_chassis + reefer
        haul_no_tolls = bid_base - cost_tolls
        fsc = haul_no_tolls *.13
        m_bid = bid_base - cost_tolls - fsc
        m_bid = float(int(m_bid))
        cost_tolls = float(int(cost_tolls))
        bid = m_bid + cost_tolls + fsc


        if ratetype == 'One Way':
            cost_of_bobtail = 1. * tot_dist + 65 * tot_dura
            m_bid = m_bid/2.0 + cost_of_bobtail
            m_bid = float(int(m_bid))
            bid = m_bid + cost_tolls + fsc

        print(f'Row {mx+1}: Bid = {d2s(m_bid)} Tolls:{d2s(cost_tolls)} Fuel Surcharge:{d2s(fsc)} Chassis:{d2s(our_chassis)} Total: {d2s(bid)}')
        sheet1.write(mx, 0, id)
        sheet1.write(mx, 1, locfrom)
        sheet1.write(mx, 2, locto)
        sheet1.write(mx, 3, movetype)
        sheet1.write(mx, 4, equiptype)
        sheet1.write(mx, 5, haz)
        sheet1.write(mx, 6, ratetype)
        sheet1.write(mx,7,d2s(m_bid))
        sheet1.write(mx,8,d2s(cost_tolls))
        sheet1.write(mx, 9, ' ')
        sheet1.write(mx, 10, d2s(fsc))
        sheet1.write(mx, 11, d2s(our_chassis))
        sheet1.write(mx, 12, d2s(reefer))
        sheet1.write(mx, 13, d2s(bid))


        if cost_tolls > 48:
            print(f'TollMat:{legtolls}')
            print(f'TollCodes:{legcodes}')
        print(' ')

    else:
        if haz == 'Y': print('Decline because hazardous')
        if 'baltimore' not in locfrom and 'baltimore' not in locto: print('Not a Baltimore related trip')
        sheet1.write(mx, 0, id)
        sheet1.write(mx, 1, locfrom)
        sheet1.write(mx, 2, locto)
        sheet1.write(mx, 3, movetype)
        sheet1.write(mx, 4, equiptype)
        sheet1.write(mx, 5, haz)
        sheet1.write(mx, 6, ratetype)




wbout.save('/home/mark/Documents/mexample.xls')



tunnel.stop()
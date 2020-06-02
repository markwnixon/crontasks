from datetime import datetime, timedelta
from CCC_system_setup import scac, addpath1, apikeys, companydata
from remote_db_connect import tunnel, db
from models import Drivers, Vehicles, DriverAssign, Trucklog, KeyInfo
from utils import d2s, d1s
import os
import xlrd
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
loc = ("/home/mark/test.xls")

# To open Workbook
wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)
sheet.cell_value(0, 0)

# Extracting number of rows and columns
print(f'The data sheet has {sheet.nrows} rows')
print(f'The data sheet has {sheet.ncols} colss')
print(f'The header for columns are:')
for i in range(sheet.ncols):
    print(f'Column {i}: {sheet.cell_value(0, i)}')

for i in range(1,sheet.nrows):
    id = str(int(sheet.cell_value(i, 0)))
    locfrom = str(sheet.cell_value(i, 1))
    locto = str(sheet.cell_value(i, 2))
    method = str(sheet.cell_value(i, 3))
    print(f'Running case {i} for {id} {locfrom} {locto} {method}')

    miles, hours, lats, lons, dirdata, tot_dist, tot_dura = get_directions(locfrom,locto)

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

    bid = cost_total * 1.2
    bid13 = cost_total *.13
    m_bid = bid - cost_tolls - bid13

    print(f'Case {i}: Bid = {d2s(m_bid)} Tolls:{d2s(cost_tolls)} Fuel Surcharge:{d2s(bid13)} Total: {d2s(bid)}')
    print(' ')








tunnel.stop()
from requests import get
from pprint import pprint
from json import dump
from CCC_system_setup import apikeys
from csv import QUOTE_ALL, DictWriter
from cronfuncs import d2s, d1s, db, tunnel

print(apikeys)
API_KEY_GEO = apikeys['gkey']
API_KEY_DIS = apikeys['dkey']

def extract_values(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []
    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results

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

def route_resolver(json):
    print(json)
    final = json['rows']
    final = final[0]
    next = final['elements']
    next = next[0]
    bi = next['distance']
    ci = next['duration']
    di = bi['text']
    du = ci['text']
    return di, du

def address_resolver(json):
    final = {}
    if json['results']:
        data = json['results'][0]
        for item in data['address_components']:
            for category in item['types']:
                data[category] = {}
                data[category] = item['long_name']
        final['street'] = data.get("route", None)
        final['state'] = data.get("administrative_area_level_1", None)
        final['city'] = data.get("locality", None)
        final['county'] = data.get("administrative_area_level_2", None)
        final['country'] = data.get("country", None)
        final['postal_code'] = data.get("postal_code", None)
        final['neighborhood'] = data.get("neighborhood",None)
        final['sublocality'] = data.get("sublocality", None)
        final['housenumber'] = data.get("housenumber", None)
        final['postal_town'] = data.get("postal_town", None)
        final['subpremise'] = data.get("subpremise", None)
        final['latitude'] = data.get("geometry", {}).get("location", {}).get("lat", None)
        final['longitude'] = data.get("geometry", {}).get("location", {}).get("lng", None)
        final['location_type'] = data.get("geometry", {}).get("location_type", None)
        final['postal_code_suffix'] = data.get("postal_code_suffix", None)
        final['street_number'] = data.get('street_number', None)
    return final

def checkcross(lam,la_last,la,lom,lo_last,lo):
    lacross = 0
    locross = 0
    if (la_last<lam and la>lam) or (la_last>lam and la<lam):
        lacross = 1
    if (lo_last<lom and lo>lom) or (lo_last>lom and lo<lom):
        locross = 1
    return lacross, locross


def get_address_details(address):
    url = 'https://maps.googleapis.com/maps/api/geocode/json?'
    url = url + 'address='+ address.replace(" ","+")
    url = url + f'&key={API_KEY_GEO}'
    print(url)
    response = get(url)
    data  = address_resolver(response.json())
    data['address'] = address
    lat = data['latitude']
    lon = data['longitude']
    print(lat,lon)
    return data

def get_distance(start,end):
    start = start.replace(" ", "+")
    end = end.replace(" ", "+")
    url = f'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins={start}&destinations={end}'
    url = url + f'&key={API_KEY_DIS}'
    print(url)
    response = get(url)
    print(response)
    data = route_resolver(response.json())
    return data

def get_directions(start,end):
    dists, duras, lats, lons = [], [], [], []
    tot_dist = 0.0
    tot_dura = 0.0
    start = start.replace(" ", "+")
    end = end.replace(" ", "+")
    url = f'https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}'
    url = url + f'&key={API_KEY_DIS}'
    print(url)
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

if 1 == 2:
    """
    Provide the address via csv or paste it here 
    """
    # address_to_search = list(DictReader("path/to/csv/file"))
    address_to_search = ['71 Pilgrim Avenue Chevy Chase, MD 20815']
    data = []
    for i in address_to_search:
        data.append(get_address_details(i))
        print(get_address_details(i))

start = '2600 Broening Highway, Baltimore, MD'
end = 'Manassas, VA'
if 1 == 2:
    dist,dura = get_distance(start,end)
    print(dist,dura)
    dist = dist.replace('mi','')
    duralist = dura.split()
    if len(duralist) == 4:
        hrs = float(duralist[0])
        mins = float(duralist[2])
    if len(duralist) == 2:
        hrs = 0.0
        mins = float(duralist[0])

    tothrs = hrs + mins/60.0
    drvcost = tothrs * 27.0
    fuelcost = float(dist)/6.0*2.78
    print(tothrs,drvcost,dist,fuelcost)


####################################  Directions Section  ######################################
miles, hours, lats, lons, dirdata, tot_dist, tot_dura = get_directions(start,end)
print(f'Total distance {d1s(tot_dist)} miles and total duration {d1s(tot_dura)} hours')

#Calculate road tolls
tollroadlist = ['I-76','NJ Tpke']
tollroadcpm = [.784, .275]
legtolls = len(dirdata)*[0.0]
legcodes = len(dirdata)*['None']
for lx,mi in enumerate(miles):
    for nx,tollrd in enumerate(tollroadlist):
        if tollrd in dirdata[lx]:
            legtolls[lx] = tollroadcpm[nx]*mi
            legcodes[lx] = tollrd

#Calculate plaza tolls
fm_tollbox =  [39.267757, -76.610192, 39.261248, -76.563158]
bht_tollbox = [39.259962, -76.566240, 39.239063, -76.603324]
fsk_tollbox = [39.232770, -76.502453, 39.202279, -76.569906]
bay_tollbox = [39.026893, -76.417512, 38.964938, -76.290104]
sus_tollbox = [39.585193, -76.142883, 39.552328, -76.033975]
new_tollbox = [39.647121, -75.774523, 39.642613, -75.757187] #Newark Delaware Toll Center
dmb_tollbox = [39.702146, -75.553479, 39.669730, -75.483284]
tollcodes = ['FM', 'BHT', 'FSK', 'BAY', 'SUS', 'NEW', 'DMB']
tollboxes = [fm_tollbox, bht_tollbox, fsk_tollbox, bay_tollbox, sus_tollbox, new_tollbox, dmb_tollbox]

for jx,lat in enumerate(lats):
    stat1 = 'ok'
    stat2 = 'ok'
    stat3 = 0
    stat4 = 0
    tollcode = 'None'
    la = float(lat)
    lo = float(lons[jx])
    for kx, tollbox in enumerate(tollboxes):
        lah = max([tollbox[0],tollbox[2]])
        lal = min([tollbox[0], tollbox[2]])
        loh = max([tollbox[1],tollbox[3]])
        lol = min([tollbox[1], tollbox[3]])
        if la > lal and la < lah:
            stat1 = 'toll'
            if lo > lol and lo < loh:
                stat2 = 'toll'
                tollcode = tollcodes[kx]
                legtolls[jx] = 24.00
                legcodes[jx] = tollcode
        if jx > 0:
            lam = (lah + lal)/2.0
            lom = (loh + lol)/2.0
            la_last = float(lats[jx-1])
            lo_last= float(lons[jx-1])
            stat3, stat4 = checkcross(lam,la_last,la,lom,lo_last,lo)
            if stat3 == 1 and stat4 ==1:
                tollcode = tollcodes[kx]
                legtolls[jx] = 24.00
                legcodes[jx] = tollcode
    #print(lat,lons[jx],stat1, stat2, stat3, stat4, tollcode)


tot_tolls = 0.00
for lx,aline in enumerate(dirdata):
    tot_tolls += legtolls[lx]
    print(aline)
    print(f'Dist:{d1s(miles[lx])}, Time:{d1s(hours[lx])}, Tolls:${d2s(legtolls[lx])}, TollCode:{legcodes[lx]}')
bid = tot_dist*2.0*2.10 + tot_tolls*2 + 250.
cma_bid = bid/1.13
print('Summary')
print(f'Driver Cost: ${d2s(tot_dura*2*27.00)}')
print(f'Fuel Cost: ${d2s(tot_dist*2*.47)}')
print(f'Toll Cost: ${d2s(tot_tolls*2)}')
print(f'Recommended Bid: ${d2s(bid)}')
print(f'Recommended CMA Bid: ${d2s(cma_bid)} plus fuel')

tunnel.stop()
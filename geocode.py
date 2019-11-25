from requests import get
from pprint import pprint
from json import dump
from CCC_system_setup import apikeys
from csv import QUOTE_ALL, DictWriter

print(apikeys)
API_KEY_GEO = apikeys['gkey']
API_KEY_DIS = apikeys['dkey']

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
end = 'Hagerstown, MD'
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


if 1 == 2:
    with open("data.csv",'w') as csvfile:
        csvwriter = DictWriter(csvfile, fieldnames=data[0].keys(), quoting=QUOTE_ALL)
        csvwriter.writeheader()
        csvwriter.writerows(data)
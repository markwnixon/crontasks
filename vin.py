import requests
import json
import datetime
from math import sqrt
from cronfuncs import dropupdate, d1s, d2s
from datetime import timedelta
from CCC_system_setup import apikeys


def getvindata(vintoget):
    url = "https://vindecoder.p.rapidapi.com/decode_vin"
    querystring = {"vin":vintoget}

    headers = {
        'x-rapidapi-host': "vindecoder.p.rapidapi.com",
        'x-rapidapi-key': apikeys['vinkey']
        }


    r = requests.request("GET", url, headers=headers, params=querystring)
    r = requests.request("GET", url, headers=headers, params=querystring)
    dataret = r.json()
    print(dataret)
    testret = dataret['success']
    print(testret)
    specs = dataret['specification']
    vin = specs['vin']
    year = specs['year']
    make = specs['make']
    model = specs['model']
    trim = specs['trim_level']
    engine = specs['engine']
    style = specs['style']
    height = specs['overall_height']
    length = specs['overall_length']
    width = specs['overall_width']

return r.text

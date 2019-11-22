from requests import Session
from requests.auth import HTTPBasicAuth  # or HTTPDigestAuth, or OAuth1, etc.
from zeep import Client
from zeep.transports import Transport

from CCC_system_setup import mycompany, apiservers, usernames, passwords, websites, addpath2, from_phone
co = mycompany()
if co == 'FELA':
    from CCC_FELA_remote_db_connect import tunnel, db
    from CCC_FELA_models import Magaccts
elif co == 'OSLM':
    from CCC_OSLM_remote_db_connect import tunnel, db
    from CCC_OSLM_models import Autos, Drivers, Vehicles

import xml.etree.ElementTree as ET

import logging.config

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'zeep.transports': {
            'propagate': True,
            'handlers': ['console'],
        },
    }
})

#Practice and Test Creating a Session
if 1 == 1:
    session = Session()
    session.auth = HTTPBasicAuth(usernames['magaya'], passwords['magaya'])
    magaya_wsdl_url = apiservers['magaya']
    client = Client(magaya_wsdl_url, transport=Transport(session=session))
    token = client.service.StartSession(usernames['magaya'], passwords['magaya'])
    key = token['access_key']

    ret = client.service.GetTransRangeByDate(key,'BI','2019-10-01','2019-11-30',0)
    ret_xml = ret['trans_list_xml']

def getp(child,lev,acctlist):
    lb1 = '    '
    tag = child.tag
    tag = tag.replace('{http://www.magaya.com/XMLSchema/V1}', '')
    txt = child.text
    att = child.attrib
    if txt is None:
        lev = lev+1
        for nc in child:
            getp(nc,lev,acctlist)
        lev = lev-1
    if lev==1 or lev == 2:
        print(lb1*lev,f'{tag} {txt}')
        acctlist.append(txt)
    return tag,txt,att,acctlist

def get_item_from_itemlist(xml):
    for child in root:
        tag,att,txt = getp(child,0)

def pxml(xml):
    print('***************Start of ET xml recital*******************')
    root = ET.fromstring(xml)
    masterlist = []
    for child in root:
        tag,att,txt,acctlist = getp(child,0,[])
        masterlist.append(acctlist)
    print(masterlist)
    print('***************End of ET xml recital*******************')

pxml(ret_xml)


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

if 1 == 1:
    #Practice creating an xml file via the xsd format
    ##################################
    root=ET.Element('Quotation', xmlns="http://www.magaya.com/XMLSchema/V1", Type="QT", GUID='37b7ff17-dee4-41d7-89ae-a8d55cc2fd76')
    ET.SubElement(root,'CreatedOn').text='2019-10-14T15:36:48-05:00'
    ET.SubElement(root,'Number').text = 'MarkQT0080'
    ET.SubElement(root,'CreatedByName').text = 'John Doe'

    ET.SubElement(root, 'Version').text = '104'
    ET.SubElement(root, 'IssuedByName').text = 'First Eagle Logistics, Inc.'
    ib = ET.SubElement(root, 'IssuedBy', GUID='3f72abdc-3e03-4e99-bf9a-71ebdfae8631')

    ET.SubElement(ib, 'Type').text = 'ForwardingAgent'
    ET.SubElement(ib, 'Name').text = 'First Eagle Logistics, Inc.'
    ET.SubElement(ib, 'CreatedOn').text = '2019-08-20T15:06:24-05:00'

    ab = ET.SubElement(ib, 'Address')
    ET.SubElement(ab, 'Street').text = '505 Hampton Park Blvd'
    ET.SubElement(ab, 'Street').text = 'Suite TTTTO'
    ET.SubElement(ab, 'City').text = 'Capitol Heights'
    ET.SubElement(ab, 'State').text = 'MD'
    ET.SubElement(ab, 'ZipCode').text = '20743'
    ET.SubElement(ab, 'Country', Code='US').text = 'United States'
    #SubElement(root, '').text = ''

if 1 == 1:
    part1 = '<?xml version="1.0" encoding="utf-8"?>'
    xmlsend = part1 + ET.tostring(root).decode('utf-8')
    print(xmlsend)
    ret4 = client.service.SetTransaction(key,'QT',0,xmlsend)
    print(ret4)

tunnel.stop()
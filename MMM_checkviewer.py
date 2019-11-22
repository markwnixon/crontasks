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


#Practice and Test Creating a Session
if 1 == 1:
    session = Session()
    session.auth = HTTPBasicAuth(usernames['magaya'], passwords['magaya'])
    magaya_wsdl_url = apiservers['magaya']
    client = Client(magaya_wsdl_url, transport=Transport(session=session))
    token = client.service.StartSession(usernames['magaya'], passwords['magaya'])
    key = token['access_key']

    ret = client.service.GetTransaction(key,'CK',0,'2369')
    ret_xml = ret['trans_xml']
    print(ret_xml)

    #ret = client.service.GetTransRangeByDate(key,'CK','2019-10-01','2019-11-30',0)
    #ret_xml = ret['trans_list_xml']

def getp(child,lev):
    lb1 = '    '
    tag = child.tag
    tag = tag.replace('{http://www.magaya.com/XMLSchema/V1}', '')
    txt = child.text
    att = child.attrib
    print(lb1 * lev, f'{tag} {att} = {txt}')
    if txt is None:
        #print(lb1 * lev, f'{tag} {att} = {txt}')
        lev = lev+1
        for nc in child:
            getp(nc,lev)
        lev = lev-1
    #print(lb1*lev,f'{tag} {att} = {txt}')
    return tag,txt,att

def get_item_from_itemlist(xml):
    for child in root:
        tag,att,txt = getp(child,0)

def pxml(xml):
    print('***************Start of ET xml recital*******************')
    root = ET.fromstring(xml)
    print(root.tag, root.attrib, root.text)
    for child in root:
        tag,att,txt = getp(child,0)
    print('***************End of ET xml recital*******************')

pxml(ret_xml)

tunnel.stop()
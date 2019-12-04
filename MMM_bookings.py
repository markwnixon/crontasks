from requests import Session
from requests.auth import HTTPBasicAuth  # or HTTPDigestAuth, or OAuth1, etc.
from zeep import Client
from zeep.transports import Transport

from CCC_system_setup import mycompany, apiservers, usernames, passwords, websites, addpath2, from_phone
co = mycompany()
if co == 'FELA':
    from CCC_FELA_remote_db_connect import tunnel, db
    from CCC_FELA_models import Magaccts, OverSeas, Bookings
elif co == 'OSLM':
    from CCC_OSLM_remote_db_connect import tunnel, db
    from CCC_OSLM_models import Autos, Drivers, Vehicles

from datetime import datetime, timedelta
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
            'level': 'DEBUG',
            'propagate': True,
            'handlers': ['console'],
        },
    }
})

def get_dt_date(input):
    try:
        datestr = input[0:10]
        datedt = datetime.strptime(datestr,'%Y-%m-%d')
        return datedt.date()
    except:
        return None

def getput(nm,os):
    cdat = People.query.filter(People.Company == nm[0]).first()
    if cdat is None:
        input = People(Company=nm[0], First=None, Middle=None, Last=None, Addr1=nm[1], Addr2=nm[2], Addr3=nm[3],
                       Idtype=None, Idnumber=None,
                       Telephone=nm[4], Email=nm[5], Associate1=None, Associate2=None, Date1=today, Ptype=os,
                       Date2=None, Original=None, Temp1=None, Temp2=None, Accountid=None)
        db.session.add(input)
        db.session.commit()
        print(f'Adding {name} to {os} Database with {addr1} {addr2} {tel} {email}')
        newdat = People.query.filter(People.Company == name).first()
        return newdat.id
    else:
        print(f'Found {name}')
        return cdat.id



session = Session()
session.auth = HTTPBasicAuth(usernames['magaya'], passwords['magaya'])
magaya_wsdl_url = apiservers['magaya']
client = Client(magaya_wsdl_url, transport=Transport(session=session))
token = client.service.StartSession(usernames['magaya'], passwords['magaya'])
key = token['access_key']

ret = client.service.GetTransRangeByDate(key,'BK','2019-10-01','2019-11-27',0)
ret_xml = ret['trans_list_xml']

root = ET.fromstring(ret_xml)
print(root[0])
for child in root:
    print(child.tag, child.text)
print('end of ET')

def get_address_block(nc1):
    block = []
    name = 'NAY'
    addr1 = 'NAY'
    addr2 = 'NAY'
    city = 'NAY'
    cou = 'NAY'
    phone = 'NAY'
    email = 'NAY'
    for nc2 in nc1:
        tag2, txt2 = nc2.tag, nc2.text
        tag2 = tag2.replace('{http://www.magaya.com/XMLSchema/V1}', '').strip()
        #print('Address Block',tag2,txt2)
        if tag2 == 'Name':
            name = txt2
        if tag2 == 'Email':
            email = txt2
        if tag2 == 'Phone':
            phone = txt2
        if tag2 == 'Address':
            for nc3 in nc2:
                tag3, txt3 = nc3.tag, nc3.text
                tag3 = tag3.replace('{http://www.magaya.com/XMLSchema/V1}', '').strip()
                #print('Address Block 3', tag3, txt3)
                if tag3 == 'Street':
                    if addr1 == 'NAY':
                        addr1 = txt3
                    else:
                        addr2 = txt3
                if tag3 == 'City':
                    city = txt3
                if tag3 == 'State':
                    city = txt3
                if tag3 == 'ZipCode':
                    city = txt3
                if tag3 == 'Country':
                    cou = txt3
    block = [name,addr1,addr2,f'{city}, {cou}',phone,email]
    return block

def get_address_block1(nc1):
    block = []
    typea = 'NAY'
    cycle = 0
    name = 'NAY'
    addr1 = 'NAY'
    addr2 = 'NAY'
    city = 'NAY'
    cou = 'NAY'
    phone = 'NAY'
    email = 'NAY'
    while email == 'NAY':
        for nc2 in nc1:
            tag2, txt2 = nc2.tag, nc2.text
            tag2 = tag2.replace('{http://www.magaya.com/XMLSchema/V1}', '').strip()
            #print('Address Block',tag2,txt2)
            if tag2 == 'Type':
                typea = txt2
            if tag2 == 'Name':
                name = txt2
            if tag2 == 'Email':
                email = txt2
            if tag2 == 'Phone':
                phone = txt2
            if tag2 == 'Address':
                for nc3 in nc2:
                    tag3, txt3 = nc3.tag, nc3.text
                    tag3 = tag3.replace('{http://www.magaya.com/XMLSchema/V1}', '').strip()
                    #print('Address Block 3', tag3, txt3)
                    if tag3 == 'Street':
                        if addr1 == 'NAY':
                            addr1 = txt3
                        else:
                            addr2 = txt3
                    if tag3 == 'City':
                        city = txt3
                    if tag3 == 'State':
                        city = txt3
                    if tag3 == 'ZipCode':
                        city = txt3
                    if tag3 == 'Country':
                        cou = txt3
    block = [typea,name,addr1,addr2,f'{city}, {cou}',phone,email]
    return block



tlist = ret['trans_list_xml']
itemstofind = ['BookingNumber', 'Number', 'NotifyPartyName', 'ShipperName', 'EstimatedDepartureDate',
               'EstimatedArrivalDate', 'PickupDate', 'CutoffDate', 'ConsigneeName',
               'ContainersNumbers', 'VehicleID', 'ModelYear', 'Make', 'Model', 'TotalPieces', 'DescriptionOfGoods',
               'OnCarriageBy']
if 1 == 1:
    xml = ET.fromstring(tlist)
    #print('Xml=',xml)
    for child in xml:
        if 'OceanBooking' in child.tag:
            itemsfound = ['None'] * len(itemstofind)
            #print(f'The child tag is {child.tag} = {child.text}')
            for nc1 in child:
                tag, txt = nc1.tag, nc1.text
                tag = tag.replace('{http://www.magaya.com/XMLSchema/V1}','').strip()
                #print(f'The nc1 tag is {tag} = {txt}')
                if tag in itemstofind:
                    #print(f'Have {tag} is {txt}')
                    for jx, item in enumerate(itemstofind):
                        if item == tag:
                            #print(jx,itemsfound)
                            itemsfound[jx] = txt
                if tag == 'NotifyParty':
                    try:
                        not_block = get_address_block(nc1)
                        print('notblock', not_block)
                    except:
                        not_block = []
                if tag == 'Consignee':
                    con_block = get_address_block(nc1)
                if tag == 'Shipper':
                    shi_block = get_address_block(nc1)
                if tag == 'IssuedBy':
                    iss_block = get_address_block(nc1)

            #print(itemsfound)

            print('conblock',con_block)
            print('shiblock', shi_block)
            print('issblock', iss_block)
            if 1 == 1:
                booking = itemsfound[0]
                odat = OverSeas.query.filter(OverSeas.Booking==booking).first()
                bdat = Bookings.query.filter(Bookings.Booking == booking).first()
                if odat is None or bdat is None:
                    print(f'Adding booking {booking}')
                    itemstofind = ['BookingNumber', 'Number', 'NotifyPartyName', 'ShipperName', 'EstimatedDepartureDate',
                                   'EstimatedArrivalDate', 'PickupDate', 'CutoffDate', 'ConsigneeName',
                                   'ContainersNumbers', 'VehicleID', 'ModelYear', 'Make', 'Model', 'TotalPieces', 'DescriptionOfGoods',
                                   'OnCarriageBy']
                    jo = itemsfound[1]
                    notify = itemsfound[2]
                    shipper = itemsfound[3]
                    depdate = get_dt_date(itemsfound[4])
                    arrdate = get_dt_date(itemsfound[5])
                    pudate = get_dt_date(itemsfound[6])
                    codate = get_dt_date(itemsfound[7])
                    consignee = itemsfound[8]
                    container = itemsfound[9]
                    print(f'Jo: {jo} Booking: {booking} Container:{container} Shipper:{shipper}, Consignee:{consignee}, Notify:{notify}')
                    print(f'Depart:{depdate} Arrive:{arrdate} Earliest:{pudate} Cutoff:{codate}')
                    if odat is None:
                        cindex = getput(con_block, 'OverSeas2')
                        sindex = getput(shi_block, 'OverSeas')
                        nindex = getput(not_block, 'OverSeas2')
                        findex = getput(iss_block, 'OverSeas')
                        input = OverSeas(Jo=jo, Pid=0, MoveType='Ocean', Direction='Export', Commodity=None, Pod=None, Pol=None,
                                         Origin=None, PuDate=pudate, ContainerType=None,
                                         Booking=booking, CommoList=0, ExportID=sindex, ConsigID=cindex, NotifyID=nindex, FrForID=findex,
                                         PreCarryID=0, Estimate=None, Charge=None, Container=container,
                                         Dpath=None, Ipath=None, Apath=None, Cache=0, Status='000', Label=None,
                                         BillTo=shipper, Exporter=shipper, Consignee=consignee, Notify=notify,
                                         FrFor=None, PreCarry=None, Driver=None, Seal=None, Description= 'Magaya API',
                                         RetDate=None, Tpath=None, Itotal='',
                                         RelType='Seaway Bill', AES='', ExpRef='', AddNote='')
                        db.session.add(input)
                        db.session.commit()
                    if bdat is None:
                        input = Bookings(Jo=jo, Booking=booking, ExportRef=None, Line=None, Vessel=None,
                                         PortCut=None,
                                         DocCut=None, SailDate=depdate, EstArr=arrdate,
                                         RelType=None, AES=None, Original=None, Amount=None,
                                         LoadPort=None, Dest=None, Status="New")
                        db.session.add(input)
                        db.session.commit()

#ret = client.service.EndSession(token)
#print(ret)
tunnel.stop()
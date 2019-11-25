from requests import Session
from requests.auth import HTTPBasicAuth  # or HTTPDigestAuth, or OAuth1, etc.
from zeep import Client
from zeep.transports import Transport
from address_parser import Parser
import usaddress

from CCC_system_setup import mycompany, apiservers, usernames, passwords, websites, addpath2, from_phone
co = mycompany()
if co == 'FELA':
    from CCC_FELA_remote_db_connect import tunnel, db
    from CCC_FELA_models import Magaccts, FELBills, Accounts, People

import xml.etree.ElementTree as ET
import datetime
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

def getp(child,lev):
    lb1 = '    '
    tag = child.tag
    tag = tag.replace('{http://www.magaya.com/XMLSchema/V1}', '')
    txt = child.text
    att = child.attrib
    print(lb1 * lev, f'{tag} {att} = {txt}')
    if txt is None:
        lev = lev+1
        for nc in child:
            getp(nc,lev)
        lev = lev-1
    return tag,txt,att

def getpfind(child,lev,tagfind,txtfound,status):
    tag = child.tag
    tag = tag.replace('{http://www.magaya.com/XMLSchema/V1}', '')
    txt = child.text
    att = child.attrib
    if tag == tagfind:
        txtfound = txt
        status = 1
        return tag, txt, att, txtfound, status
    if txt is None:
        lev = lev+1
        for nc in child:
            tag,txt,att,txtfound,status = getpfind(nc,lev,tagfind, txtfound, status)
        lev = lev-1
    return tag,txt,att, txtfound, 1

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

def find_xml(xml,tagfind):
    status = 0
    root = ET.fromstring(xml)
    print(root.tag, root.attrib, root.text)
    for child in root:
        tag,txt,att,txtfound,status = getpfind(child,0,tagfind,'',0)
        if status == 1:
            return txtfound

def addr2break(addr1, addr2):
    addressinput = addr1 + ' ' + addr2
    testpart = usaddress.parse(addressinput)
    ecity, estate, ezip = '', '', ''
    #print(testpart)
    for te in testpart:
        #print(te[0],te[1])
        if te[1] == 'PlaceName':
            ecity = ecity + te[0] + ' '
        if te[1] == 'StateName':
            estate = te[0]
        if te[1] == 'ZipCode':
            ezip = te[0]
    ecity = ecity.replace(',','')
    ecity = ecity.strip()
    return ecity, estate, ezip


def rectify(btry):
    btry = btry.lower()
    cklist = ['container', 'towing', 'taxes', 'fuel', 'overseas', 'insurance', 'maint', 'prof', 'rent', 'utilities', 'hm:', 'trucking:payroll', 'credit card', 'adv-mark', 'trucking:other', 'office', 'other']
    rklist = ['Containers/Overseas Shipments', 'Towing Costs', 'Taxes Licenses Fees', 'Fuel', 'Containers/Overseas Shipments', 'Insurance for Trucking', 'Building Repairs and Maint', 'Professional Fees', 'Building Rent', 'Utilities', 'Horizon', 'Trucking Payroll', 'Credit Card', 'Advertising', 'Medical and Screening', 'Office Supplies', 'Office Payroll']
    for jx, ck in enumerate(cklist):
        if ck in btry:
            return rklist[jx]

def fixbaccount(ctry,bid):
    cklist = ['Shareholder Norma Ghanem', 'Jay Settlement Account', 'Norma Ghanem', 'FEL VISA 2419']
    rklist = ['Shareholder Norma Ghanem', 'Contracted Labor', 'Office Payroll', 'FEL VISA 2419']
    for jx, ck in enumerate(cklist):
        if ck == ctry:
            cdat = FELBills.query.get(bid)
            cdat.bAccount = rklist[jx]
            db.session.commit()

            return rklist[jx]

# Turn Tasks on or Off for Error Checking...
#mcon = 0 to Turn Off Writing to Magaya
mcon = 1
error = 0
testcase = 1

#Create Session
if mcon == 1 or mcon == 0:
    session = Session()
    session.auth = HTTPBasicAuth(usernames['magaya'], passwords['magaya'])
    magaya_wsdl_url = apiservers['magaya']
    client = Client(magaya_wsdl_url, transport=Transport(session=session))
    token = client.service.StartSession(usernames['magaya'], passwords['magaya'])
    key = token['access_key']

# Sequence through each Bank Account:
banks = ['FEL CitiBank', 'FEL Industrial Bank', 'HM Citibank']
banknums = ['9108648598', '1312766', '9108648846']
for kx, bank in enumerate(banks):
    banknum = banknums[kx]

    # Cycle through the FELBills to get Check Numbers
    fdata = FELBills.query.filter((FELBills.pAccount==bank) & (FELBills != 'Unpaid') ).order_by(FELBills.Ref).all()
    for fdat in fdata:
        if testcase < 2000:
            checknum = fdat.Ref
            bid = fdat.id

            try:
                icknum = int(checknum)
            except:
                checknum = 'EP'+str(bid)

            if len(checknum) == 4 or 'EP' in checknum:

                testcase = testcase + 1
                #See if check already moved into Magaya
                retm = client.service.GetTransaction(key, 'CK', 0, checknum)
                errfind = retm['return']

                if errfind == 'no_error':
                    print(f'Check {checknum} already in Magaya')
                elif 'EP' in checknum and fdat.Status == 'Paid-M':
                    print(f'Check {checknum} part of a multipart check')
                elif len(checknum) == 4 or fdat.Status == 'Paid':
                    print(errfind)

                    if fdat.Status == 'Paid-M':
                        amount = fdat.pMulti
                    else:
                        amount = fdat.bAmount
                    baccount = fdat.bAccount
                    if baccount is None:
                        company = fdat.Company
                        ai = fixbaccount(company, bid)
                        btry = fdat.bCat
                        baccount = rectify(fdat.bCat)
                    if baccount is not None:
                        adat = Accounts.query.filter(Accounts.Name == baccount).first()
                        if adat is not None:
                            aid = adat.id
                            mdat = Magaccts.query.filter( (Magaccts.Mapid1==aid) | (Magaccts.Mapid2==aid) | (Magaccts.Mapid3==aid) ).first()
                            if mdat is not None:
                                typecat = mdat.TypeA
                                namecat = mdat.Name
                            else:
                                print(f'For check {checknum} Magaya account not found to match {str(aid)}')
                        else:
                            print(f'For check {checknum} FEL account not found to match {baccount}')
                    else:
                        print(f'No category account data for BillID:{bid} check {checknum}')

                    memo = fdat.Memo
                    ckdate = fdat.pDate
                    try:
                        ddate = ckdate.strftime("%Y-%m-%d")
                    except:
                        ckdate = fdat.bDate
                        try:
                            ddate = ckdate.strftime("%Y-%m-%d")
                        except:
                            print(f'Bad Date for Bill {bid}')

                    datestr = f'{ddate}T00:00:20-01:00'
                    #print(datestr)
                    desc = fdat.Description

                    #Entity section
                    ename = fdat.Company
                    edat = People.query.filter(People.Company == ename).first()
                    if edat is not None:
                        ptype = edat.Ptype
                        if ptype == 'TowCo':
                            etype = 'Carrier'
                        else:
                            etype = 'Vendor'
                        estreet = edat.Addr1
                        estreet = estreet.strip()
                        ecity, estate, ezip = addr2break(edat.Addr1, edat.Addr2)
                        ephone = edat.Telephone
                        e_email = edat.Email

                    if error == 0:
                        print(f'CkNo:{checknum} Amount:{amount} Date:{datestr} Bank:{bank} AcctNo:{banknum} MagayaCat[Type:{typecat} Name:{namecat}]')
                        print(f'Type:{etype} {ename}')
                        print(f'Street: {estreet}')
                        print(f'City/State/ZIP: {ecity}, {estate}  {ezip}')
                        print(f'Phone/Email: {ephone} {e_email}')
                        print(' ')

                    #Section to put all vendors and towco into Magaya
                    ret3 = client.service.GetEntities(key, 0, ename)
                    try:
                        ret_xml = ret3['entity_list_xml']
                        pxml(ret_xml)

                        root = ET.fromstring(ret_xml)
                        #print(f'Tag:{root[0][1].tag}, Attrib:{root[0][1].attrib}, Text:{root[0][1].text}')
                        try:
                            ename = root[0][1].text
                        except:
                            print('Cannot obtain check name')
                        etype = root[0].tag
                        etype = etype.replace('{http://www.magaya.com/XMLSchema/V1}','')
                        eguid = root[0].attrib['GUID']
                        if etype == 'Carrier':
                            ecode = find_xml(ret_xml, 'CarrierTypeCode')

                            if error == 0:
                                print(f'Found etype={etype} eguid={eguid} ecode={ecode}')
                            inputtype = 1
                        else:
                            inputtype = 2
                    except:
                        inputtype = 0


                    #Section to send checks into Magaya
                    if mcon == 1:
                        #part1 = '<?xml version="1.0" encoding="utf-8"?>'
                        #xmlsend = part1 + ET.tostring(root).decode('utf-8')
                        part = [0]*15
                        part[0] = '<?xml version="1.0" encoding="utf-8"?><Check xmlns="http://www.magaya.com/XMLSchema/V1" Type="CK">'
                        part[1] = f'<Type>ExpenseCheck</Type><Number>{checknum}</Number><CreatedBy GUID="c2a36b6c-dc56-4cfc-aa8d-f4ec775c805f"><Type>Employee</Type><Name>Mark Nixon</Name><EntityID>MN001</EntityID>'
                        part[2] = f'<CreatedOn>{datestr}</CreatedOn>'
                        part[3] = '<Address><ContactPhone>301-816-300</ContactPhone><ContactPhoneExtension>103</ContactPhoneExtension><ContactEmail>mnixon@firsteaglelogistics.com</ContactEmail></Address><BillingAddress><ContactPhone>301-816-300</ContactPhone><ContactPhoneExtension>103</ContactPhoneExtension><ContactEmail>mnixon@firsteaglelogistics.com</ContactEmail></BillingAddress><Email>mnixon@firsteaglelogistics.com</Email><Phone>301-816-300</Phone><PhoneExtension>103</PhoneExtension><CountryOfCitizenship Code="US">United States</CountryOfCitizenship><IsPrepaid>true</IsPrepaid><MobilePhone>757-897-3266</MobilePhone></CreatedBy>'
                        part[4] = '<IssuedBy GUID="3f72abdc-3e03-4e99-bf9a-71ebdfae8631"><Type>ForwardingAgent</Type><Name>First Eagle Logistics, Inc.</Name><CreatedOn>2019-08-15T15:06:24-05:00</CreatedOn><Address><Street>505 Hampton Park Blvd</Street><Street>Suite O</Street><City>Capitol Heights</City><State>MD</State><ZipCode>20743</ZipCode><Country Code="US">United States</Country><ContactName>Nadav Kalai</ContactName><ContactPhone>301-516-3000</ContactPhone><ContactFax>301-516-1515</ContactFax><ContactEmail>info@firsteaglelogistics.com</ContactEmail></Address><BillingAddress><Street>505 Hampton Park Blvd, Ste O</Street><City>Capitol Heights</City><State>MD</State><ZipCode>20743</ZipCode><Country Code="US">United States</Country><ContactName>Nadav Kalai</ContactName><ContactPhone>301-516-3000</ContactPhone><ContactFax>301-516-1515</ContactFax><ContactEmail>info@firsteaglelogistics.com</ContactEmail><PortCode>Z2A</PortCode></BillingAddress><Email>info@firsteaglelogistics.com</Email><Website>http://www.firsteaglelogistics.com</Website><Phone>301-516-3000</Phone><Fax>301-516-1515</Fax><ContactFirstName>Nadav</ContactFirstName><ContactLastName>Kalai</ContactLastName><ExporterID>472363625</ExporterID><ExporterIDType>EIN</ExporterIDType><NetworkID>36520</NetworkID><IsKnownShipper>true</IsKnownShipper><IsPrepaid>true</IsPrepaid><AgentInfo><SCACNumber>FELA</SCACNumber></AgentInfo></IssuedBy>'
                        part[5] = f'<BankAccount><Type>BankAccount</Type><Name>{bank}</Name><Number>{banknum}</Number><Currency Code="USD"><Name>United States Dollar</Name><ExchangeRate>1.00</ExchangeRate><DecimalPlaces>2</DecimalPlaces><IsHomeCurrency>true</IsHomeCurrency></Currency><ParentAccount><Type>BankAccount</Type><Name>Bank Account</Name><Currency Code="USD"><Name>United States Dollar</Name><ExchangeRate>1.00</ExchangeRate><DecimalPlaces>2</DecimalPlaces><IsHomeCurrency>true</IsHomeCurrency></Currency></ParentAccount></BankAccount>'
                        #If we found the entity in Mayaga:
                        if inputtype == 1:
                            part[6] = f'<Entity GUID="{eguid}"><Type>{etype}</Type><Name>{ename}</Name><CarrierInfo><CarrierTypeCode>{ecode}</CarrierTypeCode></CarrierInfo></Entity>'
                        elif inputtype == 2:
                            part[6] = f'<Entity GUID="{eguid}"><Type>{etype}</Type><Name>{ename}</Name></Entity>'
                        else:
                            part[6] = f'<Entity><Type>{etype}</Type><Name>{ename}</Name><CreatedOn>{datestr}</CreatedOn>'
                            part[6] = part[6] + f'<Address><Street>{estreet}</Street><City>{ecity}</City><State>{estate}</State><ZipCode>{ezip}</ZipCode><Country>United States</Country><ContactPhone>{ephone}</ContactPhone><ContactEmail>{e_email}</ContactEmail></Address>'
                            part[6] = part[6] + f'<CarrierInfo><CarrierTypeCode>Ground</CarrierTypeCode></CarrierInfo></Entity>'
                        part[7] = f'<CreatedOn>{datestr}</CreatedOn>'
                        part[8] = f'<TotalAmount Currency="USD">{amount}</TotalAmount><HomeCurrency Code="USD"><Name>United States Dollar</Name><ExchangeRate>1.00</ExchangeRate><DecimalPlaces>2</DecimalPlaces><IsHomeCurrency>true</IsHomeCurrency></HomeCurrency><Currency Code="USD"><Name>United States Dollar</Name><ExchangeRate>1.00</ExchangeRate><DecimalPlaces>2</DecimalPlaces><IsHomeCurrency>true</IsHomeCurrency></Currency><ExchangeRate>1.00</ExchangeRate><TotalAmountInCurrency Currency="USD">{amount}</TotalAmountInCurrency>'
                        if 'FEL' in bank:
                            part[9] = '<Division GUID="5a7e69b6-96d3-45a5-b09d-95772d3efb53"><Type>Division</Type><Name>First Eagle Logistics, Inc.</Name><CreatedOn>2019-08-16T16:46:48-05:00</CreatedOn><Address><Street>505 Hampton Park Blvd, Ste O</Street><City>Capitol Heights</City><State>MD</State><ZipCode>20743</ZipCode><Country Code="US">United States</Country><PortCode>Z2A</PortCode></Address><Email>info@firsteaglelogistics.com</Email><Phone>301-516-3000</Phone><Fax>301-516-1515</Fax><AccountNumber>        </AccountNumber><IsPrepaid>true</IsPrepaid><DivisionInfo><UseInHeaders>true</UseInHeaders></DivisionInfo></Division>'
                        else:
                            part[9] = '<Division GUID="698ed9ba-291b-45ed-a8c9-994fb95f61b9"><Type>Division</Type><Name>Horizon Motors, Inc.</Name><CreatedOn>2019-08-16T16:48:20-05:00</CreatedOn><Address><Street>505 Hampton Park Blvd, Ste N</Street><City>Capitol Heights</City><State>MD</State><ZipCode>20743</ZipCode><Country Code="US">United States</Country><PortCode>BAL</PortCode></Address><Email>info@horizonmotors1.com</Email><Phone>301-909-1819</Phone><AccountNumber>        </AccountNumber><IsPrepaid>true</IsPrepaid><DivisionInfo><UseInHeaders>true</UseInHeaders></DivisionInfo></Division>'
                        part[10] = f'<Notes>{memo}</Notes><IsPrinted>false</IsPrinted><CheckLines><CheckLine>'
                        part[11] = f'<Account><Type>{typecat}</Type><Name>{namecat}</Name>'
                        part[12] = '<Currency Code="USD"><Name>United States Dollar</Name><ExchangeRate>1.00</ExchangeRate><DecimalPlaces>2</DecimalPlaces><IsHomeCurrency>true</IsHomeCurrency></Currency>'
                        part[13] = f'<ParentAccount><Type>{typecat}</Type><Name>{namecat}</Name><Currency Code="USD"><Name>United States Dollar</Name><ExchangeRate>1.00</ExchangeRate><DecimalPlaces>2</DecimalPlaces><IsHomeCurrency>true</IsHomeCurrency></Currency></ParentAccount></Account><AmountPaid Currency="USD">{amount}</AmountPaid><AmountPaidInCurrency Currency="USD">{amount}</AmountPaidInCurrency>'
                        part[14] = f'<Description>{desc}</Description></CheckLine></CheckLines><HasAttachments>false</HasAttachments></Check>'
                        testsend = ''
                        for ptxt in part:
                            testsend = testsend + ptxt

                        print(testsend)
                        ret4 = client.service.SetTransaction(key,'CK',0,testsend)
                        print(ret4)
                        errplug = ret4['return']
                        if errplug == 'invalid_xml' or 'error' in errplug:
                            with open('checksummary.txt','a+') as fp:
                                fp.write(f'CkNo:{checknum} Amount:{amount} Date:{datestr} Bank:{bank} AcctNo:{banknum} MagayaCat[Type:{typecat} Name:{namecat}]\n')
                                fp.write(f'Type:{etype} {ename}\n')
                                fp.write(f'Street: {estreet}\n')
                                fp.write(f'City/State/ZIP: {ecity}, {estate}  {ezip}\n')
                                fp.write(f'Phone/Email: {ephone} {e_email}\n\n\n')

            else:
                # print(f'Bill ID:{bid} has no ref number: sees {checknum}')
                continue

tunnel.stop()
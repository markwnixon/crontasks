from requests import Session
from requests.auth import HTTPBasicAuth  # or HTTPDigestAuth, or OAuth1, etc.
from zeep import Client
from zeep.transports import Transport

from CCC_system_setup import mycompany, apiservers, usernames, passwords, websites, addpath2, from_phone
co = mycompany()
if co == 'FELA':
    from CCC_FELA_remote_db_connect import tunnel, db
    from CCC_FELA_models import Magaccts, FELBills, Accounts

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

#Practice and Test Creating a Session
if 1 == 2:
    session = Session()
    session.auth = HTTPBasicAuth(usernames['magaya'], passwords['magaya'])
    magaya_wsdl_url = apiservers['magaya']
    client = Client(magaya_wsdl_url, transport=Transport(session=session))
    token = client.service.StartSession(usernames['magaya'], passwords['magaya'])
    key = token['access_key']

# Cycle through the FELBills to get Check Numbers
fdata = FELBills.query.filter(FELBills.pAccount=='FEL CitiBank').all()
for fdat in fdata:
    checknum = fdat.Ref
    if len(checknum) == 4:
        amount = fdat.bAmount
        baccount = fdat.bAccount
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
            print(f'No category account data for check {checknum}')
        typecat = 'CostOfGoodsSold'
        namecat = 'Freight Cost'
        bank = 'FEL CitiBank'
        banknum = '9108648598'
        memo = 'Here is a memo'
        today = datetime.datetime.today()
        ddate = today.strftime("%Y-%m-%d")
        datestr = f'{ddate}T00:00:20-01:00'
        #print(datestr)
        desc = 'Here is a checkline description'

        entityGUID="bd713dad-03be-47f1-8795-6c12aa8e188c"
        etype = 'Carrier'
        ename = 'My New Tow Carrier'
        estreet = 'Street'
        ecity = 'Mycity'
        estate = 'Mystate'
        ezip = 'Myzip'
        ephone = '222-222-2222'
        e_email = 'newemail@special.com'
    else:
        continue





if 1 == 2:
    #part1 = '<?xml version="1.0" encoding="utf-8"?>'
    #xmlsend = part1 + ET.tostring(root).decode('utf-8')
    part = [0]*15
    part[0] = '<?xml version="1.0" encoding="utf-8"?><Check xmlns="http://www.magaya.com/XMLSchema/V1" Type="CK">'
    part[1] = f'<Type>ExpenseCheck</Type><Number>{checknum}</Number><CreatedBy GUID="c2a36b6c-dc56-4cfc-aa8d-f4ec775c805f"><Type>Employee</Type><Name>Mark Nixon</Name><EntityID>MN001</EntityID>'
    part[2] = f'<CreatedOn>{datestr}</CreatedOn>'
    part[3] = '<Address><ContactPhone>301-816-300</ContactPhone><ContactPhoneExtension>103</ContactPhoneExtension><ContactEmail>mnixon@firsteaglelogistics.com</ContactEmail></Address><BillingAddress><ContactPhone>301-816-300</ContactPhone><ContactPhoneExtension>103</ContactPhoneExtension><ContactEmail>mnixon@firsteaglelogistics.com</ContactEmail></BillingAddress><Email>mnixon@firsteaglelogistics.com</Email><Phone>301-816-300</Phone><PhoneExtension>103</PhoneExtension><CountryOfCitizenship Code="US">United States</CountryOfCitizenship><IsPrepaid>true</IsPrepaid><MobilePhone>757-897-3266</MobilePhone></CreatedBy>'
    part[4] = '<IssuedBy GUID="3f72abdc-3e03-4e99-bf9a-71ebdfae8631"><Type>ForwardingAgent</Type><Name>First Eagle Logistics, Inc.</Name><CreatedOn>2019-08-15T15:06:24-05:00</CreatedOn><Address><Street>505 Hampton Park Blvd</Street><Street>Suite O</Street><City>Capitol Heights</City><State>MD</State><ZipCode>20743</ZipCode><Country Code="US">United States</Country><ContactName>Nadav Kalai</ContactName><ContactPhone>301-516-3000</ContactPhone><ContactFax>301-516-1515</ContactFax><ContactEmail>info@firsteaglelogistics.com</ContactEmail></Address><BillingAddress><Street>505 Hampton Park Blvd, Ste O</Street><City>Capitol Heights</City><State>MD</State><ZipCode>20743</ZipCode><Country Code="US">United States</Country><ContactName>Nadav Kalai</ContactName><ContactPhone>301-516-3000</ContactPhone><ContactFax>301-516-1515</ContactFax><ContactEmail>info@firsteaglelogistics.com</ContactEmail><PortCode>Z2A</PortCode></BillingAddress><Email>info@firsteaglelogistics.com</Email><Website>http://www.firsteaglelogistics.com</Website><Phone>301-516-3000</Phone><Fax>301-516-1515</Fax><ContactFirstName>Nadav</ContactFirstName><ContactLastName>Kalai</ContactLastName><ExporterID>472363625</ExporterID><ExporterIDType>EIN</ExporterIDType><NetworkID>36520</NetworkID><IsKnownShipper>true</IsKnownShipper><IsPrepaid>true</IsPrepaid><AgentInfo><SCACNumber>FELA</SCACNumber></AgentInfo></IssuedBy>'
    part[5] = f'<BankAccount><Type>BankAccount</Type><Name>{bank}</Name><Number>{banknum}</Number><Currency Code="USD"><Name>United States Dollar</Name><ExchangeRate>1.00</ExchangeRate><DecimalPlaces>2</DecimalPlaces><IsHomeCurrency>true</IsHomeCurrency></Currency><ParentAccount><Type>BankAccount</Type><Name>Bank Account</Name><Currency Code="USD"><Name>United States Dollar</Name><ExchangeRate>1.00</ExchangeRate><DecimalPlaces>2</DecimalPlaces><IsHomeCurrency>true</IsHomeCurrency></Currency></ParentAccount></BankAccount>'
    part[6] = f'<Entity><Type>{etype}</Type><Name>{ename}</Name><CreatedOn>2019-09-30T19:15:04-05:00</CreatedOn><Address><Street>{estreet}</Street><City>{ecity}</City><State>{estate}</State><ZipCode>{ezip}</ZipCode><Country>United States</Country><ContactPhone>{ephone}</ContactPhone><ContactEmail>{e_email}</ContactEmail></Address><IsPrepaid>true</IsPrepaid><CarrierInfo><CarrierTypeCode>Ground</CarrierTypeCode></CarrierInfo></Entity>'
    part[7] = '<CreatedOn>2019-11-21T15:38:31-05:00</CreatedOn>'
    part[8] = f'<TotalAmount Currency="USD">{amount}</TotalAmount><HomeCurrency Code="USD"><Name>United States Dollar</Name><ExchangeRate>1.00</ExchangeRate><DecimalPlaces>2</DecimalPlaces><IsHomeCurrency>true</IsHomeCurrency></HomeCurrency><Currency Code="USD"><Name>United States Dollar</Name><ExchangeRate>1.00</ExchangeRate><DecimalPlaces>2</DecimalPlaces><IsHomeCurrency>true</IsHomeCurrency></Currency><ExchangeRate>1.00</ExchangeRate><TotalAmountInCurrency Currency="USD">{amount}</TotalAmountInCurrency>'
    part[9] = '<Division GUID="5a7e69b6-96d3-45a5-b09d-95772d3efb53"><Type>Division</Type><Name>First Eagle Logistics, Inc.</Name><CreatedOn>2019-08-16T16:46:48-05:00</CreatedOn><Address><Street>505 Hampton Park Blvd, Ste O</Street><City>Capitol Heights</City><State>MD</State><ZipCode>20743</ZipCode><Country Code="US">United States</Country><PortCode>Z2A</PortCode></Address><Email>info@firsteaglelogistics.com</Email><Phone>301-516-3000</Phone><Fax>301-516-1515</Fax><AccountNumber>        </AccountNumber><IsPrepaid>true</IsPrepaid><DivisionInfo><UseInHeaders>true</UseInHeaders></DivisionInfo></Division>'
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

tunnel.stop()
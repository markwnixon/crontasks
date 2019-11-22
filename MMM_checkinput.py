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
    root=ET.Element('Check', xmlns="http://www.magaya.com/XMLSchema/V1", Type="CK")
    ET.SubElement(root, 'Type').text = 'ExpenseCheck'
    ET.SubElement(root, 'Number').text = '2500'

if 1 == 1:
    ia = ET.SubElement(root,'CreatedBy')
    ET.SubElement(ia,'Type').text='Employee'
    ET.SubElement(ia, 'Name').text = 'Mark Nixon'
    ET.SubElement(ia, 'EntityID').text = 'MN001'
    ET.SubElement(ia,'CreatedOn').text='2019-10-14T15:36:48-05:00'

    ib = ET.SubElement(root, 'BankAccount')
    ET.SubElement(ib, 'Type').text = 'BankAccount'
    ET.SubElement(ib, 'Name').text = 'FEL CitiBank'
    ET.SubElement(ib, 'Number').text = '9108648598'

    ic = ET.SubElement(root, 'Entity')
    ET.SubElement(ic, 'Type').text = 'Carrier'
    ET.SubElement(ic, 'Name').text = 'A&T Carriers Inc'
    ET.SubElement(ic, 'CreatedOn').text = '2019-09-30T19:15:04-05:00'

    id = ET.SubElement(ic, 'Address')
    ET.SubElement(id, 'Street').text = '6615 Bluebottle Lane'
    ET.SubElement(id, 'City').text = 'Catonsville'
    ET.SubElement(id, 'State').text = 'MD'
    ET.SubElement(id, 'ZipCode').text = '20933'
    ET.SubElement(id, 'Country').text = 'United States'

    ET.SubElement(root, 'TotalAmount', Currency = 'USD').text = '90.00'

if 1 == 1:
    part1 = '<?xml version="1.0" encoding="utf-8"?>'
    xmlsend = part1 + ET.tostring(root).decode('utf-8')
    part1 = '<?xml version="1.0" encoding="utf-8"?><Check xmlns="http://www.magaya.com/XMLSchema/V1" Type="CK">'
    part2 = '<Type>ExpenseCheck</Type><Number>2604</Number>'
    part3 = '<CreatedBy GUID="c2a36b6c-dc56-4cfc-aa8d-f4ec775c805f"><Type>Employee</Type><Name>Mark Nixon</Name><EntityID>MN001</EntityID><CreatedOn>2019-08-16T10:09:19-05:00</CreatedOn><Address><ContactPhone>301-816-300</ContactPhone><ContactPhoneExtension>103</ContactPhoneExtension><ContactEmail>mnixon@firsteaglelogistics.com</ContactEmail></Address><BillingAddress><ContactPhone>301-816-300</ContactPhone><ContactPhoneExtension>103</ContactPhoneExtension><ContactEmail>mnixon@firsteaglelogistics.com</ContactEmail></BillingAddress><Email>mnixon@firsteaglelogistics.com</Email><Phone>301-816-300</Phone><PhoneExtension>103</PhoneExtension><CountryOfCitizenship Code="US">United States</CountryOfCitizenship><IsPrepaid>true</IsPrepaid><MobilePhone>757-897-3266</MobilePhone></CreatedBy>'
    part4 = '<IssuedBy GUID="3f72abdc-3e03-4e99-bf9a-71ebdfae8631"><Type>ForwardingAgent</Type><Name>First Eagle Logistics, Inc.</Name><CreatedOn>2019-08-15T15:06:24-05:00</CreatedOn><Address><Street>505 Hampton Park Blvd</Street><Street>Suite O</Street><City>Capitol Heights</City><State>MD</State><ZipCode>20743</ZipCode><Country Code="US">United States</Country><ContactName>Nadav Kalai</ContactName><ContactPhone>301-516-3000</ContactPhone><ContactFax>301-516-1515</ContactFax><ContactEmail>info@firsteaglelogistics.com</ContactEmail></Address><BillingAddress><Street>505 Hampton Park Blvd, Ste O</Street><City>Capitol Heights</City><State>MD</State><ZipCode>20743</ZipCode><Country Code="US">United States</Country><ContactName>Nadav Kalai</ContactName><ContactPhone>301-516-3000</ContactPhone><ContactFax>301-516-1515</ContactFax><ContactEmail>info@firsteaglelogistics.com</ContactEmail><PortCode>Z2A</PortCode></BillingAddress><Email>info@firsteaglelogistics.com</Email><Website>http://www.firsteaglelogistics.com</Website><Phone>301-516-3000</Phone><Fax>301-516-1515</Fax><ContactFirstName>Nadav</ContactFirstName><ContactLastName>Kalai</ContactLastName><ExporterID>472363625</ExporterID><ExporterIDType>EIN</ExporterIDType><NetworkID>36520</NetworkID><IsKnownShipper>true</IsKnownShipper><IsPrepaid>true</IsPrepaid><AgentInfo><SCACNumber>FELA</SCACNumber></AgentInfo></IssuedBy>'
    part5 = '<BankAccount><Type>BankAccount</Type><Name>FEL CitiBank</Name><Number>9108648598</Number><Currency Code="USD"><Name>United States Dollar</Name><ExchangeRate>1.00</ExchangeRate><DecimalPlaces>2</DecimalPlaces><IsHomeCurrency>true</IsHomeCurrency></Currency><ParentAccount><Type>BankAccount</Type><Name>Bank Account</Name><Currency Code="USD"><Name>United States Dollar</Name><ExchangeRate>1.00</ExchangeRate><DecimalPlaces>2</DecimalPlaces><IsHomeCurrency>true</IsHomeCurrency></Currency></ParentAccount></BankAccount>'
    part6 = '<Entity GUID="bd713dad-03be-47f1-8795-6c12aa8e188c"><Type>Carrier</Type><Name>A&amp;T Carriers Inc</Name><CreatedOn>2019-09-30T19:15:04-05:00</CreatedOn><Address><Street>6615 Bluebottle Lane</Street><City>Katy</City><State>TX</State><ZipCode>77449</ZipCode><Country>United States</Country></Address><IsPrepaid>true</IsPrepaid><CarrierInfo><CarrierTypeCode>Ground</CarrierTypeCode></CarrierInfo></Entity>'
    part7 = '<CreatedOn>2019-11-21T15:38:31-05:00</CreatedOn>'
    part8 = '<TotalAmount Currency="USD">95.67</TotalAmount><HomeCurrency Code="USD"><Name>United States Dollar</Name><ExchangeRate>1.00</ExchangeRate><DecimalPlaces>2</DecimalPlaces><IsHomeCurrency>true</IsHomeCurrency></HomeCurrency><Currency Code="USD"><Name>United States Dollar</Name><ExchangeRate>1.00</ExchangeRate><DecimalPlaces>2</DecimalPlaces><IsHomeCurrency>true</IsHomeCurrency></Currency><ExchangeRate>1.00</ExchangeRate><TotalAmountInCurrency Currency="USD">95.67</TotalAmountInCurrency>'
    part9 = '<Division GUID="5a7e69b6-96d3-45a5-b09d-95772d3efb53"><Type>Division</Type><Name>First Eagle Logistics, Inc.</Name><CreatedOn>2019-08-16T16:46:48-05:00</CreatedOn><Address><Street>505 Hampton Park Blvd, Ste O</Street><City>Capitol Heights</City><State>MD</State><ZipCode>20743</ZipCode><Country Code="US">United States</Country><PortCode>Z2A</PortCode></Address><Email>info@firsteaglelogistics.com</Email><Phone>301-516-3000</Phone><Fax>301-516-1515</Fax><AccountNumber>        </AccountNumber><IsPrepaid>true</IsPrepaid><DivisionInfo><UseInHeaders>true</UseInHeaders></DivisionInfo></Division>'
    part10 = '<Notes>Tow Cost</Notes><IsPrinted>false</IsPrinted><CheckLines><CheckLine><Account><Type>CostOfGoodsSold</Type><Name>Ground Freight Cost</Name><Currency Code="USD"><Name>United States Dollar</Name><ExchangeRate>1.00</ExchangeRate><DecimalPlaces>2</DecimalPlaces><IsHomeCurrency>true</IsHomeCurrency></Currency><ParentAccount><Type>CostOfGoodsSold</Type><Name>Freight Cost</Name><Currency Code="USD"><Name>United States Dollar</Name><ExchangeRate>1.00</ExchangeRate><DecimalPlaces>2</DecimalPlaces><IsHomeCurrency>true</IsHomeCurrency></Currency></ParentAccount></Account><AmountPaid Currency="USD">95.67</AmountPaid><AmountPaidInCurrency Currency="USD">95.67</AmountPaidInCurrency></CheckLine></CheckLines><HasAttachments>false</HasAttachments>'
    close =  '</Check>'
    testsend = part1 + part2 + part3 + part4 + part5 + part6 + part7 + part8 + part10 + close

    print(xmlsend)
    ret4 = client.service.SetTransaction(key,'CK',0,testsend)
    print(ret4)

tunnel.stop()
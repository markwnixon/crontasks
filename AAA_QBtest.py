import datetime

from CCC_FELA_remote_db_connect import db
#from CCC_remote_db_QBconnect import db
from CCC_FELA_models import Orders, People
from CCC_QB_models import QB_Invoices, QB_Accounts, QB_Bills, QB_Customers

class qbinvoitem:
    def __init__(self,name,qty,price):
        self.name = name
        self.qty = qty
        self.price = price

    def restate(self):
        print(f'We created {self.name} with Qty {self.qty} and {self.price} ')

item1 = qbinvoitem('Storage', '1', '35.00')
item1.restate()

item2 = qbinvoitem('Trucking:Drayage', '1','42.00')
item2.restate()

itemlist  = [item1,item2]


def qbinvoitem(item,qty,price):
    output = f'<Row><ItemName>{item}</ItemName><ItemQuantity>{qty}</ItemQuantity><ItemAmount>{price}</ItemAmount></Row>'
    return output

def qbinvoice(itemlist):
    output = '<InvoiceLineItems>'
    for item in itemlist:
        name = item.name
        qty = item.qty
        price = item.price
        output = output + qbinvoitem(name,qty,price)
    output = output + '</InvoiceLineItems>'
    return output

odat = Orders.query.first()
print('My order from database is', odat.Company)


sender = qbinvoice(itemlist)
print(sender)

if 1 == 2:
    qdata = QB_Accounts.query.all()
    for qdat in qdata:
        print(f'Quickbooks Account Name: {qdat.Name}  Type:{qdat.Type}')
if 1 == 2:
    bdata = QB_Bills.query.all()
    for bdat in bdata:
        print(f'Quickbooks Bills  Date: {bdat.Date}  Vendor:{bdat.VendorName} Amount:{bdat.Amount}')
if 1 == 2:
    cdata = QB_Customers.query.all()
    for cdat in cdata:
        print(f'Quickbooks Customers: {cdat.Name}')
        print(f'Line1: {cdat.BillingLine1}')
        print(f'Line2: {cdat.BillingLine2}')
        print(f'Line3: {cdat.BillingLine3}')
        print(f'Line4: {cdat.BillingLine4}')
        print(f'Line5: {cdat.BillingLine5}')
        print(f'Phone:{cdat.Phone}')
        print(f'Email:{cdat.Email}')

mycust = People.query.filter(People.Ptype == 'Trucking').first()
co = mycust.Company
addr1 = mycust.Addr1
addr2 = mycust.Addr2
addr3 = mycust.Addr3
phone = mycust.Telephone
email = mycust.Email

print(f'Entering {co} {addr1}')
input = QB_Customers(Name = co, Company = co, BillingLine1 = co, BillingLine2 = addr1, BillingLine3 = addr2, BillingLine4 = addr3, Phone = phone, Email = email,
                     BillingAddress = None, BillingLine5 = None, BillingCity = None, BillingState = None, BillingPostalCode = None, ShippingAddress = None)
db.session.add(input)
db.session.commit()

#input = QB_Invoices(CustomerName='Test1',ItemAggregate=sender)
#db.session.add(input)
#db.session.commit()

print('This run started at: ', datetime.datetime.now())
#print(co, websites)

tunnel.stop()

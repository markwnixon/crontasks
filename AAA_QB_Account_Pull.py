import datetime

from CCC_system_setup import scac
from remote_db_connect import tunnel, db

print(f'Running company {scac}')

from QB_models import QB_Invoices, QB_Accounts, QB_Bills, QB_Customers
from models import Orders, People, QBaccounts, Accttypes, Taxmap

def parent_check(qb):
    parent = qb.ParentName
    if parent:
        try:
            name, sub1 = parent.split(':')
            sub2 = qb.Name
        except:
            name = parent
            sub1 = qb.Name
            sub2 = None
    else:
        name = qb.Name
        sub1 = None
        sub2 = None
    return name,sub1,sub2

skiplist = ['Bank Accounts', 'Credit Cards', 'Ask My Accountant', 'Estimates', 'Purchase Orders']

if 1 == 1:
    qbacct = QB_Accounts.query.all()
    for qb in qbacct:

        if qb.Type == 'BANK':
            # First check for new Bank Accounts and Credit Card Accounts, which quickbooks treats a subaccounts of Bank Accounts...
            bankdat = QBaccounts.query.filter( (QBaccounts.Name == qb.Name) & (QBaccounts.Type == 'Bank') ).first()
            if bankdat is None and qb.Name not in skiplist:
                print(f'Need to Add Quickbooks Bank Account {qb.Name} of Type {qb.Type}')
                input = QBaccounts(Name=qb.Name,Type='Bank',Sub1=None,Sub2=None,Co='F')
                db.session.add(input)

        elif qb.Type == 'CREDITCARD' and qb.Name not in skiplist:
            ccdat = QBaccounts.query.filter((QBaccounts.Name == qb.Name) & (QBaccounts.Type == 'Credit Card')).first()
            if ccdat is None:
                print(f'Need to Add Quickbooks Credit Card Account {qb.Name} of Type {qb.Type}')
                input = QBaccounts(Name=qb.Name,Type='Credit Card',Sub1=None,Sub2=None,Co='F')
                db.session.add(input)

        elif qb.Type == 'INCOME':
            name,sub1,sub2 = parent_check(qb)
            if name not in skiplist and sub1 not in skiplist and sub2 not in skiplist:
                qdat = QBaccounts.query.filter( (QBaccounts.Name == name) & (QBaccounts.Sub1 == sub1) & (QBaccounts.Sub2 == sub2) ).first()
                if qdat is None:
                    print(f'Need to Add Quickbooks Account {qb.Name} of Type {qb.Type}')
                    input = QBaccounts(Name=name, Type='Income', Sub1=sub1, Sub2=sub2, Co='F')
                    db.session.add(input)

        elif qb.Type == 'COSTOFGOODSSOLD':
            name,sub1,sub2 = parent_check(qb)
            if name not in skiplist and sub1 not in skiplist and sub2 not in skiplist:
                qdat = QBaccounts.query.filter( (QBaccounts.Name == name) & (QBaccounts.Sub1 == sub1) & (QBaccounts.Sub2 == sub2) ).first()
                if qdat is None:
                    print(f'Need to Add Quickbooks Account {qb.Name} of Type {qb.Type}')
                    input = QBaccounts(Name=name, Type='Cost of Goods Sold', Sub1=sub1, Sub2=sub2, Co='F')
                    db.session.add(input)

        elif qb.Type == 'EXPENSE':
            name,sub1,sub2 = parent_check(qb)
            if name not in skiplist and sub1 not in skiplist and sub2 not in skiplist:
                qdat = QBaccounts.query.filter( (QBaccounts.Name == name) & (QBaccounts.Sub1 == sub1) & (QBaccounts.Sub2 == sub2) ).first()
                if qdat is None:
                    print(f'Need to Add Quickbooks Account {qb.Name} of Type {qb.Type}')
                    input = QBaccounts(Name=name, Type='Expense', Sub1=sub1, Sub2=sub2, Co='F')
                    db.session.add(input)

        else:
            name,sub1,sub2 = parent_check(qb)
            if name not in skiplist and sub1 not in skiplist and sub2 not in skiplist:
                qdat = QBaccounts.query.filter( (QBaccounts.Name == name) & (QBaccounts.Sub1 == sub1) & (QBaccounts.Sub2 == sub2) ).first()
                if qdat is None:
                    print(f'Need to Add Quickbooks Account {qb.Name} of Type {qb.Type}')
                    input = QBaccounts(Name=name, Type=qb.Type, Sub1=sub1, Sub2=sub2, Co='F')
                    db.session.add(input)

    db.session.commit()



tunnel.stop()

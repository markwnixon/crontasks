from remote_db_connect import tunnel, db
from models import Divisions, Focusareas, Accounts, Gledger, IEroll

from datetime import date
from datetime import datetime
from cronfuncs import d2s

today = datetime.today()

mon = today.month
yer = today.year
print(mon)
prev12 = []
year12 = []
dfr = []
dto = []
monlabel = []
nmonths = 12
for ix in range(nmonths+1):
    if mon < 1:
        mon = 12
        yer = yer-1
    prev12.append(mon)
    year12.append(yer)
    monthname = date(1900, mon, 1).strftime('%b')
    monlabel.append(f'{monthname} {str(yer)}')
    print(date(yer,mon,1), monthname)
    dfr.append(date(yer,mon,1))
    mon = mon - 1

dto = dfr[0:nmonths]
dfr = dfr[1:nmonths+1]
print(prev12)
print(year12)
print(dfr)
print(dto)
def writemonth(mo):
    idat = IEroll.query.filter( IEroll.Name == 'MonthLabel' ).first()
    if idat is None:
        input = IEroll(Name='MonthLabel', Category=None, Subcategory=None, Type=None, Co=None,
                       C1=None, C2=None,
                       C3=None, C4=None, C5=None, C6=None, C7=None, C8=None, C9=None, C10=None, C11=None, C12=None,
                       C13=None, C14=None, C15=None,
                       C16=None, C17=None, C18=None, C19=None, C20=None, C21=None, C22=None, C23=None, C24=None)
        db.session.add(input)
        db.session.commit()
        idat = IEroll.query.filter(IEroll.Name == 'MonthLabel').first()
    setattr(idat, f'C{ix}', mo)

ix = 0
for (df,dt) in zip(dfr,dto):
    ix += 1
    print(df, dt)
    writemonth(monlabel[ix])
    divdata = Divisions.query.all()
    for divdat in divdata:
        divtotal = 0.00
        divco = divdat.Co
        divname = divdat.Name

        #Collect the G-A Expenses for the Div
        gatotal = 0.0
        adata = Accounts.query.filter((Accounts.Type == 'Expense') & (Accounts.Category == 'G-A')).all()
        for adat in adata:
            total = 0
            expname = adat.Name
            thiscat = adat.Category
            thissub = adat.Subcategory
            gdata = Gledger.query.filter( (Gledger.Date >= df) & (Gledger.Date < dt) & (Gledger.Account == expname) ).all()
            for gdat in gdata:
                total = total + gdat.Debit
            print(f'Total Expenses for Account {expname} {ix} {df} to {dt} is {d2s(total)}')
            idat = IEroll.query.filter( (IEroll.Name == adat.Name) & (IEroll.Co == adat.Co) ).first()
            if idat is None:
                input = IEroll(Name=adat.Name, Category=adat.Category, Subcategory=adat.Subcategory,Type=adat.Type,Co=adat.Co, C1=None, C2 = None,
                               C3=None,C4=None,C5=None,C6=None,C7=None,C8=None,C9=None,C10=None,C11=None,C12=None,C13=None,C14=None,C15=None,
                               C16=None,C17=None,C18=None,C19=None,C20=None,C21=None,C22=None,C23=None,C24=None)
                db.session.add(input)
                db.session.commit()
                idat = IEroll.query.filter( (IEroll.Name == adat.Name) & (IEroll.Co == adat.Co) ).first()
            setattr(idat, f'C{ix}', d2s(total/100.))
            gatotal = gatotal + total / 100.

        ganame = f'{divco} G-A Expense Totals'
        print(f'Total G-A Expenses for Company {divname} {ix} {df} to {dt} is {d2s(gatotal)}')

        #G-A Totals
        gdat = IEroll.query.filter( (IEroll.Name == ganame) & (IEroll.Co == divco) ).first()
        if gdat is None:
            input = IEroll(Name=ganame, Category=thiscat, Subcategory=thissub,Type='Expense',Co=divco, C1=None, C2 = None,
                           C3=None,C4=None,C5=None,C6=None,C7=None,C8=None,C9=None,C10=None,C11=None,C12=None,C13=None,C14=None,C15=None,
                           C16=None,C17=None,C18=None,C19=None,C20=None,C21=None,C22=None,C23=None,C24=None)
            db.session.add(input)
            db.session.commit()
            gdat = IEroll.query.filter( (IEroll.Name == ganame) & (IEroll.Co == divco) ).first()
        setattr(gdat,f'C{ix}',d2s(gatotal))

        divtotal = divtotal + gatotal

        # Now Get the focus area direct expenses
        fdata = Focusareas.query.filter(Focusareas.Co == divco).all()
        for fdat in fdata:
            foctotal = 0.00
            focarea = fdat.Name
            adata = Accounts.query.filter((Accounts.Type == 'Expense') & (Accounts.Subcategory == focarea)).all()
            for adat in adata:
                total = 0
                expname = adat.Name
                thiscat = adat.Category
                thissub = adat.Subcategory
                gdata = Gledger.query.filter( (Gledger.Date >= df) & (Gledger.Date < dt) & (Gledger.Account == expname) ).all()
                for gdat in gdata:
                    total = total + gdat.Debit
                print(f'Total Expenses for Account {expname} {ix} {df} to {dt} is {d2s(total)}')
                idat = IEroll.query.filter( (IEroll.Name == adat.Name) & (IEroll.Co == adat.Co) ).first()
                if idat is None:
                    input = IEroll(Name=adat.Name, Category=adat.Category, Subcategory=adat.Subcategory,Type=adat.Type,Co=adat.Co, C1=None, C2 = None,
                                   C3=None,C4=None,C5=None,C6=None,C7=None,C8=None,C9=None,C10=None,C11=None,C12=None,C13=None,C14=None,C15=None,
                                   C16=None,C17=None,C18=None,C19=None,C20=None,C21=None,C22=None,C23=None,C24=None)
                    db.session.add(input)
                    db.session.commit()
                    idat = IEroll.query.filter( (IEroll.Name == adat.Name) & (IEroll.Co == adat.Co) ).first()
                setattr(idat, f'C{ix}', d2s(total/100.))
                foctotal = foctotal + total / 100.

            focname = focarea + ' Expense Totals'
            print(f'Total Expenses for Focus Area {focname} {ix} {df} to {dt} is {d2s(foctotal)}')

            #Focus area Totals and Subtotal Creation
            fdat = IEroll.query.filter( (IEroll.Name == focname) & (IEroll.Co == divco) ).first()
            if fdat is None:
                input = IEroll(Name=focname, Category=thiscat, Subcategory=thissub,Type='Expense',Co=divco, C1=None, C2 = None,
                               C3=None,C4=None,C5=None,C6=None,C7=None,C8=None,C9=None,C10=None,C11=None,C12=None,C13=None,C14=None,C15=None,
                               C16=None,C17=None,C18=None,C19=None,C20=None,C21=None,C22=None,C23=None,C24=None)
                db.session.add(input)
                db.session.commit()
                fdat = IEroll.query.filter( (IEroll.Name == focname) & (IEroll.Co == divco) ).first()
            setattr(fdat,f'C{ix}',d2s(foctotal))

            divtotal = divtotal + foctotal

        divnametit = divname + ' Expense Totals'
        print(f'Total Expenses for Company {divname} {ix} {df} to {dt} is {d2s(divtotal)}')

        # Focus area Totals and Subtotal Creation
        ddat = IEroll.query.filter((IEroll.Name == divnametit) & (IEroll.Co == divco)).first()
        if ddat is None:
            input = IEroll(Name=divnametit, Category='All', Subcategory=thissub, Type='Expense', Co=divco, C1=None,
                           C2=None, C3=None, C4=None, C5=None, C6=None, C7=None, C8=None, C9=None, C10=None, C11=None, C12=None,
                           C13=None, C14=None, C15=None, C16=None, C17=None, C18=None, C19=None, C20=None, C21=None, C22=None, C23=None, C24=None)
            db.session.add(input)
            db.session.commit()
            ddat = IEroll.query.filter((IEroll.Name == divnametit) & (IEroll.Co == divco)).first()
        setattr(ddat, f'C{ix}', d2s(divtotal))

    db.session.commit()

total = 0.00
foctotal = 0.00
divtotal = 0.00

ix = 0
for (df,dt) in zip(dfr,dto):
    ix += 1
    print(df, dt)
    divdata = Divisions.query.all()
    for divdat in divdata:
        divtotal = 0.00
        divco = divdat.Co
        divname = divdat.Name
        fdata = Focusareas.query.filter(Focusareas.Co == divco).all()
        for fdat in fdata:
            foctotal = 0.00
            focarea = fdat.Name
            adata = Accounts.query.filter((Accounts.Type == 'Income') & (Accounts.Subcategory == focarea)).all()
            for adat in adata:
                total = 0
                incname = adat.Name
                thiscat = adat.Category
                thissub = adat.Subcategory
                gdata = Gledger.query.filter( (Gledger.Date >= df) & (Gledger.Date < dt) & (Gledger.Account == incname) ).all()
                for gdat in gdata:
                    total = total + gdat.Credit
                print(f'Total Income for Account {incname} {ix} {df} to {dt} is {d2s(total)}')
                idat = IEroll.query.filter( (IEroll.Name == adat.Name) & (IEroll.Co == adat.Co) ).first()
                if idat is None:
                    input = IEroll(Name=adat.Name, Category=adat.Category, Subcategory=adat.Subcategory,Type=adat.Type,Co=adat.Co, C1=None, C2 = None,
                                   C3=None,C4=None,C5=None,C6=None,C7=None,C8=None,C9=None,C10=None,C11=None,C12=None,C13=None,C14=None,C15=None,
                                   C16=None,C17=None,C18=None,C19=None,C20=None,C21=None,C22=None,C23=None,C24=None)
                    db.session.add(input)
                    db.session.commit()
                    idat = IEroll.query.filter( (IEroll.Name == adat.Name) & (IEroll.Co == adat.Co) ).first()
                setattr(idat, f'C{ix}', d2s(total/100.))
                foctotal = foctotal + total / 100.

            focname = focarea + ' Income Totals'
            print(f'Total Income for Focus Area {focname} {ix} {df} to {dt} is {d2s(foctotal)}')

            #Focus area Totals and Subtotal Creation
            fdat = IEroll.query.filter( (IEroll.Name == focname) & (IEroll.Co == divco) ).first()
            if fdat is None:
                input = IEroll(Name=focname, Category=thiscat, Subcategory=thissub,Type='Income',Co=divco, C1=None, C2 = None,
                               C3=None,C4=None,C5=None,C6=None,C7=None,C8=None,C9=None,C10=None,C11=None,C12=None,C13=None,C14=None,C15=None,
                               C16=None,C17=None,C18=None,C19=None,C20=None,C21=None,C22=None,C23=None,C24=None)
                db.session.add(input)
                db.session.commit()
                fdat = IEroll.query.filter( (IEroll.Name == focname) & (IEroll.Co == divco) ).first()
            setattr(fdat,f'C{ix}',d2s(foctotal))

            divtotal = divtotal + foctotal

        divnametit = divname + ' Income Totals'
        print(f'Total Income for Company {divname} {ix} {df} to {dt} is {d2s(divtotal)}')

        # Focus area Totals and Subtotal Creation
        ddat = IEroll.query.filter((IEroll.Name == divnametit) & (IEroll.Co == divco)).first()
        if ddat is None:
            input = IEroll(Name=divnametit, Category='All', Subcategory=thissub, Type='Income', Co=divco, C1=None,
                           C2=None, C3=None, C4=None, C5=None, C6=None, C7=None, C8=None, C9=None, C10=None, C11=None, C12=None,
                           C13=None, C14=None, C15=None, C16=None, C17=None, C18=None, C19=None, C20=None, C21=None, C22=None, C23=None, C24=None)
            db.session.add(input)
            db.session.commit()
            ddat = IEroll.query.filter((IEroll.Name == divnametit) & (IEroll.Co == divco)).first()
        setattr(ddat, f'C{ix}', d2s(divtotal))

    db.session.commit()

tunnel.stop()
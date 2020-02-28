import sys
from bs4 import BeautifulSoup as soup

from datetime import datetime, timedelta


from CCC_system_setup import scac
from remote_db_connect import tunnel, db
from models import Interchange, Orders, OverSeas


printif = 0

runat = datetime.now()
today = runat.date()
lookback = runat - timedelta(30)
lbdate = lookback.date()
print(' ')
print('________________________________________________________')
print(f'This sequence run at {runat} with look back to {lbdate}')
print('________________________________________________________')
print(' ')

#Make sure all the booking and container numbers for orders have upper case:
#These correction made only once, using Release...set to 1 after corrections
jdata = Orders.query.filter( (~Orders.Status.endswith('3')) & (Orders.Date > lbdate) & (Orders.Release == 0) ).all()
for jdat in jdata:
    bk = jdat.Booking
    bk = bk.upper()
    con = jdat.Container
    con = con.upper()
    bk = bk.strip()
    con = con.strip()
    jdat.Booking = bk
    jdat.Container = con
    jdat.Release = 1
    db.session.commit()

#Sometimes we return container with different booking number, so we need to get the container number to the job whether it is an In or and Out:
jdata = Orders.query.filter( (~Orders.Status.endswith('3')) & (Orders.Date > lbdate)).all()
for jdat in jdata:
    con = jdat.Container
    if con == 'TBD':
        bk = jdat.Booking
        if len(bk) > 7:
            idat = Interchange.query.filter( (Interchange.Release == bk) & (Interchange.Date > lbdate) ).first()
            if idat is not None:
                jdat.Container = idat.Container
                db.session.commit()

#Make sure there are no doubled up Global Jobs
jdata = Orders.query.filter( (Orders.Shipper == 'Global Business Link') & (~Orders.Status.endswith('3')) & (Orders.Date > lbdate)).all()
for jdat in jdata:

    bk = jdat.Booking
    con = jdat.Container

    # Do not want to include container matches if they are TBD
    if con == 'TBD' or len(con) < 9:
        con = 'XXX'
    if len(bk) < 6:
        bk = 'YYY'
    print(f'Global Job {jdat.Booking} and {jdat.Container} with Status {jdat.Status}')

    #First see if there is an Overseas container matching to Global Job:
    if scac == 'FELA':
        odat = OverSeas.query.filter( (OverSeas.PuDate > lbdate) & (OverSeas.Booking == bk) | (OverSeas.Container == con) ).first()
        if odat is not None:
            # Have a duplicate with overseas booking or container: delete the Global Job
            print(f'Have Global duplicate with OverSeas {bk} | {con}')
            killid = jdat.id
            print(f'Have Global duplicate with Order {bk} | {con}')
            Orders.query.filter(Orders.id == killid).delete()
            db.session.commit()

            #Now refranchise the Interchange Tickets just in Case they have Global Label:
            idata = Interchange.query.filter( ((Interchange.Container == con) | (Interchange.Release == bk)) & (Interchange.Date > lbdate) ).all()
            for idat in idata:
                idat.Jo = odat.Jo
                idat.Company = odat.BillTo
                db.session.commit()

    #Now see if there are trucking jobs of other companies that got mixed up with Global:
    tdat = Orders.query.filter( (Orders.id != jdat.id) & (Orders.Date > lbdate) & ((Orders.Booking == bk) | (Orders.Container == con)) ).first()
    if tdat is not None:
        # Have a duplicate with order booking or container: delete the Global Job
        killid = jdat.id
        print(f'Have Global duplicate with Order {bk} | {con}')
        Orders.query.filter(Orders.id == killid).delete()
        db.session.commit()

        # Now refranchise the Interchange Tickets just in Case they have Global Label:
        idata = Interchange.query.filter(((Interchange.Container == con) | (Interchange.Release == bk)) & (Interchange.Date > lbdate)).all()
        for idat in idata:
            idat.Jo = tdat.Jo
            idat.Company = tdat.Shipper
            db.session.commit()

# Match up the containers that can be matched up IN to OUT matching
idata = Interchange.query.filter( (Interchange.Type.contains('Out') & (Interchange.Date > lbdate)) ).all()
for idat in idata:
    con = idat.Container
    if len(con) < 9:
        con = 'XXX'
    bk = idat.Release
    if len(bk) < 6:
        bk = 'YYY'
    sta = idat.Status
    print(f'Container {idat.Container} has Type {idat.Type} and Status {idat.Status}')
    imat = Interchange.query.filter( ((Interchange.Container == con) | (Interchange.Release == bk)) & (Interchange.Type.contains('In')) & (Interchange.Date > lbdate) ).first()
    if imat is not None:
        imat.Status = 'IO'
        idat.Status = 'IO'
    else:
        idat.Status = 'BBBBBB'
    db.session.commit()

def checkon(con,bk):
    if con == 'TBD' or len(con) < 9:
        con = 'XXX'
    else:
        retcon = con
    if len(bk) < 6:
        bk = 'YYY'
    else:
        retbk = bk
    return con, bk




# Move Jobs Along the Status Path for Containers:
jdata = Orders.query.filter((Orders.Hstat < 2) & (Orders.Date > lbdate)).all()
for jdat in jdata:
    con, bk = checkon(jdat.Container,jdat.Booking)
    stat = jdat.Hstat
    idat = Interchange.query.filter( ((Interchange.Container == con) | (Interchange.Release == bk)) & (Interchange.Type.contains('Out')) & (Interchange.Date > lbdate) ).first()
    if idat is not None:
        istat = idat.Status
        if istat == 'IO':
            jdat.Hstat = 2
        else:
            jdat.Hstat = 1
    else:
        jdat.Hstat = 0
    db.session.commit()


#Make a match of all Jobs with Container Data:
jdata = Orders.query.filter( (Orders.Hstat < 4) & (Orders.Date > lbdate)).all()
for jdat in jdata:
    con, bk = checkon(jdat.Container, jdat.Booking)
    idat = Interchange.query.filter(((Interchange.Container == con) | (Interchange.Release == bk)) & (Interchange.Type.contains('Out')) & (Interchange.Date > lbdate)).first()
    if idat is not None:
        #print(f'Match to truck job {idat.Order} and {idat.Container}')
        jdat.Container = idat.Container
        jdat.Type = idat.ConType
        jdat.Date = idat.Date
        idat.Company = jdat.Shipper
        idat.Jo = jdat.Jo

        imat = Interchange.query.filter(((Interchange.Container == con) | (Interchange.Release == bk)) & (Interchange.Type.contains('In')) & (Interchange.Date > lbdate)).first()
        if imat is not None:
            jdat.Date2 = imat.Date
            imat.Jo = jdat.Jo
            imat.Company = jdat.Shipper
        else:
            finishdate = jdat.Date2
            if today > finishdate:
                jdat.Date2 = today

        db.session.commit()

tunnel.stop()
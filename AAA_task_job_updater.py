import sys
from bs4 import BeautifulSoup as soup

from datetime import datetime, timedelta


from CCC_system_setup import addpath4, websites, usernames, passwords, mycompany
co = mycompany()

if co == 'FELA':
    from CCC_FELA_remote_db_connect import tunnel, db
    from CCC_FELA_models import Interchange, Orders, OverSeas
elif co == 'OSLM':
    from CCC_OSLM_remote_db_connect import tunnel, db
    from CCC_OSLM_models import Interchange, Orders

printif = 0

runat = datetime.now()
today = runat.date()
lookback = runat - timedelta(60)
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
            idat = Interchange.query.filter( (Interchange.RELEASE == bk) & (Interchange.Date > lbdate) ).first()
            if idat is not None:
                jdat.Container = idat.CONTAINER
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
    if co == 'FELA':
        odat = OverSeas.query.filter( (OverSeas.PuDate > lbdate) & (OverSeas.Booking == bk) | (OverSeas.Container == con) ).first()
        if odat is not None:
            # Have a duplicate with overseas booking or container: delete the Global Job
            print(f'Have Global duplicate with OverSeas {bk} | {con}')
            killid = jdat.id
            print(f'Have Global duplicate with Order {bk} | {con}')
            Orders.query.filter(Orders.id == killid).delete()
            db.session.commit()

            #Now refranchise the Interchange Tickets just in Case they have Global Label:
            idata = Interchange.query.filter( ((Interchange.CONTAINER == con) | (Interchange.RELEASE == bk)) & (Interchange.Date > lbdate) ).all()
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
        idata = Interchange.query.filter(((Interchange.CONTAINER == con) | (Interchange.RELEASE == bk)) & (Interchange.Date > lbdate)).all()
        for idat in idata:
            idat.Jo = tdat.Jo
            idat.Company = tdat.Shipper
            db.session.commit()

# Match up the containers that can be matched up IN to OUT matching
idata = Interchange.query.filter( (Interchange.TYPE.contains('Out') & (Interchange.Date > lbdate)) ).all()
for idat in idata:
    con = idat.CONTAINER
    if len(con) < 9:
        con = 'XXX'
    bk = idat.RELEASE
    if len(bk) < 6:
        bk = 'YYY'
    sta = idat.Status
    print(f'Container {idat.CONTAINER} has Type {idat.TYPE} and Status {idat.Status}')
    imat = Interchange.query.filter( ((Interchange.CONTAINER == con) | (Interchange.RELEASE == bk)) & (Interchange.TYPE.contains('In')) & (Interchange.Date > lbdate) ).first()
    if imat is not None:
        imat.Status = 'IO'
        idat.Status = 'IO'
    else:
        idat.Status = 'BBBBBB'
    db.session.commit()

# Move Jobs Along the Status Path for Containers:
jdata = Orders.query.filter((~Orders.Status.startswith('3')) & (Orders.Date > lbdate)).all()
for jdat in jdata:
    con = jdat.Container
    bk = jdat.Booking
    if con == 'TBD' or len(con) < 9:
        con = 'XXX'
    if len(bk) < 6:
        bk = 'YYY'
    stat = jdat.Status
    d1 = stat[1]
    idat = Interchange.query.filter( ((Interchange.CONTAINER == con) | (Interchange.RELEASE == bk)) & (Interchange.TYPE.contains('Out')) & (Interchange.Date > lbdate) ).first()
    if idat is not None:
        istat = idat.Status
        if istat == 'IO':
            d0 = '2'
        else:
            d0 = '1'
    else:
        d0 = '0'

    jdat.Status = d0 + d1
    db.session.commit()


#Make a match of all Jobs with Container Data:
jdata = Orders.query.filter( (~Orders.Status.endswith('3')) & (Orders.Date > lbdate)).all()
for jdat in jdata:
    bk = jdat.Booking
    con = jdat.Container
    if con == 'TBD' or len(con) < 9:
        con = 'XXX'
    if len(bk) < 6:
        bk = 'YYY'

    idat = Interchange.query.filter(((Interchange.CONTAINER == con) | (Interchange.RELEASE == bk)) & (Interchange.TYPE.contains('Out')) & (Interchange.Date > lbdate)).first()
    if idat is not None:
        #print(f'Match to truck job {idat.Order} and {idat.Container}')
        jdat.Container = idat.CONTAINER
        jdat.Type = idat.CONTYPE
        jdat.Date = idat.Date
        idat.Company = jdat.Shipper
        idat.Jo = jdat.Jo

        imat = Interchange.query.filter(((Interchange.CONTAINER == con) | (Interchange.RELEASE == bk)) & (Interchange.TYPE.contains('In')) & (Interchange.Date > lbdate)).first()
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
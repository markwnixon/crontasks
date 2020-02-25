from remote_db_connect import tunnel, db
from models import Divisions, Focusareas, Accounts, Gledger, Broll, People, Bills

from datetime import date
from datetime import datetime
from cronfuncs import d2s
import enchant

today = datetime.today()

mon = today.month
yer = today.year
print(mon)
prev12 = []
year12 = []
dfr = []
dto = []
nmonths = 24
for ix in range(nmonths+1):
    if mon < 1:
        mon = 12
        yer = yer-1
    prev12.append(mon)
    year12.append(yer)
    print(date(yer,mon,1))
    dfr.append(date(yer,mon,1))
    mon = mon - 1

dto = dfr[0:nmonths]
dfr = dfr[1:nmonths+1]
print(prev12)
print(year12)
print(dfr)
print(dto)

def correct(company):
    companylist = company.split(' ')
    newname=None
    for comp in companylist:
        #This if removes extra spaces between words...
        if comp != '' and comp !=' ':
            sl = len(comp)
            if sl>1 and sl < 5:
                d = enchant.Dict("en_US")
                if d.check(comp):
                    if comp.lower() in ['and', 'the', 'of', 'in', 'for']:
                        comp = comp.lower()
                    elif comp.lower() in ['usa','md','ad','iq', 'visa', 'us', 'dat', 'rr', 'alp']:
                        comp = comp.upper()
                    else:
                        comp = comp.title()
                else:
                    comp = comp.upper()
            else:
                if comp.lower() not in ['(usa)', 'inarme', 'myeld20', 'ezpass', 'msfleet']:
                    comp = comp.title()
            if newname is None:
                newname = comp
            else:
                newname = newname + ' ' + comp
    return newname




if 1 == 2:
    pidlist = []
    #First must fix duplicate companies if such has been entered:
    bdata = Bills.query.filter(Bills.bType == 'Expense').all()
    for bdat in bdata:
        pid = bdat.Pid
        if pid is not None:
            pdat = People.query.get(pid)
            if pdat is not None:
                if pid not in pidlist:
                    pidlist.append(pid)
            else:
                print(f'Problem with bill id {bdat.id}, Company with id {pid} does not exist')
        else:
            print(f'Bill {bdat.id} has no vendor reference')

    for pid in pidlist:
        pdat = People.query.get(pid)
        if pdat is not None:
            company = pdat.Company
            newcompany = correct(company)
            if pdat.Date2 is None:
                print(f'Company:{company} becomes:{newcompany}')
                pdat.Company = newcompany
                pdat.Date2 = today
        else:
            print(f'Company with id {pid} does not exist')
    db.session.commit()

# Fix any company drops for bills
if 1 == 2:
    bdata = Bills.query.filter(Bills.Co == None).all()
    for bdat in bdata:
        print(bdat.id)
        jo = bdat.Jo
        co = jo[0]
        bdat.Co = co
    db.session.commit()



if 1 == 2:
    ix = 0
    for (df,dt) in zip(dfr,dto):
        ix += 1
        print(df, dt)
        divdata = Divisions.query.all()
        for divdat in divdata:
            divtotal = 0.00
            divco = divdat.Co

            bdata = Bills.query.filter( (Bills.bDate >= df) & (Bills.bDate < dt) & (Bills.Co == divco) & (Bills.bType == 'Expense') ).all()
            company_list = []
            for bdat in bdata:
                pid = bdat.Pid
                if pid is not None:
                    cdat = People.query.get(pid)
                    if cdat is not None:
                        company = cdat.Company
                        if company is not None:
                            if company not in company_list:
                                company_list.append(company)
                        else:
                            print(f'Company with id {pid} does not exist')
                    else:
                        print(f'Pid {pid} does not exist from Bill {bdat.id}')
                else:
                    print(f'Bill {bdat.id} has no vendor reference')


            if 1 == 1:
                for company in company_list:
                    tot = 0.00
                    gtot = 0.00
                    pdata = People.query.filter(People.Company == company).all()
                    for pdat in pdata:
                        pid = pdat.id
                        bpdata = Bills.query.filter((Bills.bDate >= df) & (Bills.bDate < dt) & (Bills.Co == divco) & (Bills.bType == 'Expense') & (Bills.Pid == pid)).all()
                        for bpdat in bpdata:
                            bamt = float(bpdat.bAmount)
                            tot = tot + bamt
                            jo = bpdat.Jo
                            bcat = bpdat.bSubcat
                            bsub = bpdat.bAccount
                            gdat = Gledger.query.filter( (Gledger.Tcode == jo) & (Gledger.Type == 'ED') ).first()
                            if gdat is not None:
                                gamt = float(gdat.Debit)/100.0
                                gtot = gtot + gamt
                                if int(bamt) != int(gamt):
                                    print(f'Gledger amt is {gamt} while Bill Amount is {bamt}')
                            else:
                                print(f'Bill {jo} for {company} and amount {bamt} is not recorded')


                    idatB = Broll.query.filter( (Broll.Name == company) & (Broll.Co == divco) & (Broll.Type == 'Expense-B') ).first()
                    if idatB is None:
                        input = Broll(Name=company, Category=bcat, Subcategory=bsub,Type='Expense-B',Co=divco, Tot = 0, C1=None, C2 = None,
                                       C3=None,C4=None,C5=None,C6=None,C7=None,C8=None,C9=None,C10=None,C11=None,C12=None,C13=None,C14=None,C15=None,
                                       C16=None,C17=None,C18=None,C19=None,C20=None,C21=None,C22=None,C23=None,C24=None)
                        db.session.add(input)
                        db.session.commit()
                        idatB = Broll.query.filter( (Broll.Name == company) & (Broll.Co == divco) & (Broll.Type == 'Expense-B') ).first()

                    setattr(idatB, f'C{ix}', d2s(tot))

                    idatG = Broll.query.filter( (Broll.Name == company) & (Broll.Co == divco) & (Broll.Type == 'Expense-G') ).first()
                    if idatG is None:
                        input = Broll(Name=company, Category=bcat, Subcategory=bsub,Type='Expense-G',Co=divco, Tot=0, C1=None, C2 = None,
                                       C3=None,C4=None,C5=None,C6=None,C7=None,C8=None,C9=None,C10=None,C11=None,C12=None,C13=None,C14=None,C15=None,
                                       C16=None,C17=None,C18=None,C19=None,C20=None,C21=None,C22=None,C23=None,C24=None)
                        db.session.add(input)
                        db.session.commit()
                        idatG = Broll.query.filter( (Broll.Name == company) & (Broll.Co == divco) & (Broll.Type == 'Expense-G') ).first()

                    setattr(idatG, f'C{ix}', d2s(gtot))

    db.session.commit()

if 1 == 1:
    idata = Broll.query.filter(Broll.Type == 'Expense-B').all()
    for idat in idata:
        tot = 0.00
        for ix in range(1,25):
            dat = getattr(idat, f'C{ix}')
            if dat is not None:
                tot = tot + float(dat)
        itot = int(tot*100)
        print(itot)
        idat.Tot = itot
    db.session.commit()

tunnel.stop()
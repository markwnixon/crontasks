import datetime

from cronfuncs import d2s, nonone, nodollar
from scrapers import vinscraper

from CCC_system_setup import mycompany

co = mycompany()
if co == 'FELA':
    from CCC_FELA_remote_db_connect import tunnel, db
    from CCC_FELA_models import OverSeas, Orders, People, Autos
elif co == 'OSLM':
    from CCC_OSLM_remote_db_connect import tunnel, db
    from CCC_OSLM_models import OverSeas, Orders, People, Autos

today = datetime.date.today()


def vinfind(fout):
    # fout is a textfile created from a Dispatch pdf file
    allvins = []
    longs = open(fout).read()
    longsp = longs.split()
    for j, s in enumerate(longsp):
        if s == 'VIN:':
            vin = longsp[j+1]
            if vin == 'Lot':
                vin = 'NoVIN'
            if vin not in allvins:
                allvins.append(vin)

    return allvins


def dispatchfind(fout):
    def resetvals():
        year = ''
        make = ''
        model = ''
        color = 'NoCOLOR'
        vin = 'NoVIN'
        return year, make, model, color, vin
    year, make, model, color, vin = resetvals()
    ncars = 0
    carlist = []
    yearlist = [str(e) for e in range(1950, 2025)]
    with open(fout) as openfile:
        for line in openfile:
            if 'Vehicle Information' in line:
                carinfo = next(openfile)
                for k in range(1, 13):
                    nextline = next(openfile)
                    if 'Pickup Information' in nextline:
                        break
                    else:
                        carinfo = carinfo+nextline

    # print(carinfo)
    clist = carinfo.split()
    nfind = 0
    for j, c in enumerate(clist):
        if c == 'Vehicles:':
            ncars = clist[j+1]
        if c in yearlist:
            # this is new car so create new element in the car list
            nfind = nfind+1
            if nfind > 1:
                carlist.append([year, make, model, color, vin])
                year, make, model, color, vin = resetvals()
            year = c
            make = clist[j+1]
            make = make.title()
            model = clist[j+2]
            model = model.title()
            # print(year,make,model)
        if c == 'Color:':
            color = clist[j+1]
            color = color.title()
            if color == 'Plate:':
                color = 'NoCOLOR'
        if c == 'VIN:':
            vin = clist[j+1]
            vin = vin.upper()
            if vin == 'Lot':
                vin = 'NoVIN'

    if nfind > 0:
        carlist.append([year, make, model, color, vin])

    return nfind, carlist


def carrierfind(fout):
    endings = ['INC', 'Inc', 'inc', 'LLC', 'Llc', 'llc', 'Co.', 'company', 'Company']
    with open(fout) as openfile:
        carrier = ''
        addr1 = ''
        addr2 = ''
        phone = ''
        for line in openfile:
            if 'Carrier' in line:
                for k in range(8):
                    nextline = next(openfile)
                    if 'Carrier:' in nextline:
                        carrier = nextline.split(':', 1)[1]

                        for end in endings:
                            if end in carrier:
                                carrier = carrier.split(end, 1)[0]
                                carrier = carrier+end

                        carrier = carrier.strip()
                        addr1 = next(openfile)
                        addr2 = next(openfile)

                        mod = ''
                        for word in addr1.split():
                            if len(word) == 2:
                                word = word.upper()
                            else:
                                word = word.title()
                            mod = mod+' '+word
                        mod = ''
                        for word in addr2.split():
                            if len(word) == 2:
                                word = word.upper()
                            else:
                                word = word.title()
                            mod = mod+' '+word
                        addr2 = mod.strip()
                break

                for k in range(12):
                    nextline = next(openfile)
                    if 'Phone:' in nextline:
                        phone = nextline.split(':', 1)[1]
                        phone = phone.strip()

    return carrier, addr1, addr2, phone


def orderinfo(fout):

    with open(fout) as openfile:
        pudate = ''
        deldate = ''
        price = ''
        for line in openfile:
            if 'Order Information' in line:
                for k in range(5):
                    nextline = next(openfile)
                    if 'Pickup' in nextline:
                        pudate = nextline.split(':', 1)[1]
                        pudate = pudate.strip()
                    if 'Delivery' in nextline:
                        deldate = nextline.split(':', 1)[1]
                        deldate = deldate.strip()
            if 'Price Listed' in line:
                for k in range(5):
                    nextline = next(openfile)
                    if 'Total Payment' in nextline:
                        price = nextline.split(':', 1)[1]
                        price = price.strip()

    return pudate, deldate, price


def comefrom(fout):

    with open(fout) as openfile:
        pickup = ''
        for line in openfile:
            if 'Pickup Information' in line:
                nextline1 = next(openfile)
                for k in range(10):
                    nextline2 = next(openfile)
                    if 'Phone' in nextline2:
                        pickup = nextline1.strip()
                        break
                    else:
                        nextline1 = nextline2
        modpu = ''
        for word in pickup.split():
            if len(word) == 2:
                word = word.upper()
            else:
                word = word.title()
            modpu = modpu+' '+word
            modpu = modpu.strip()

    return modpu


def autofind(p5s, txtfile, srcfile):

    wt = None
    value = None
    fout = p5s+txtfile
    error = 1

    vinlist = vinfind(fout)
    nvins = len(vinlist)
    # print(vinlist)

    carrier, addr1, addr2, phone = carrierfind(fout)
    # print(carrier,addr1,addr2,phone)

    pudate, deldate, payment = orderinfo(fout)
    pufrom = comefrom(fout)
    # print(pudate,deldate,payment,pufrom)

    ncars, carlist = dispatchfind(fout)
    # print(nvins,ncars,len(carlist))

    try:
        date1 = datetime.datetime.strptime(pudate, "%m/%d/%Y")
    except:
        date1 = None
    try:
        date2 = datetime.datetime.strptime(deldate, "%m/%d/%Y")
    except:
        date2 = None

    payment = d2s(payment)
    try:
        total = float(payment)
        each = total/float(ncars)
        each = str(each)
        each = d2s(each)
    except:
        each = '0.00'

    adata = Autos.query.all()
    lauto = len(adata)-1
    for j, adat in enumerate(adata):
        if j == lauto:
            thisid = adat.id
            nextid = thisid+1

    newfile = 'DISP'+str(nextid)+'.pdf'
    original = 'tmp/vdispatch/'+newfile
    orderid = 'disp'+str(nextid)

    adat = Autos.query.filter(Autos.Orderid == orderid).first()
    if adat is None:
        print("This is a new tow order so we need to add it to the database")
        error = 0
        for car in carlist:
            # carlist.append([year,make,model,color,vin])
            vin = car[4]
            year = car[0]
            make = car[1]
            model = car[2]
            color = car[3]
            wt = '0'
            value = '0'
            if len(vin) == 17:
                try:
                    year, make, model, wt, value, navg = vinscraper(vin)
                    value = value.replace('$', '')
                except:
                    wt = 'Bad Vin'
                    value = 'Bad Vin'
            else:
                vin = 'NoVIN'

            bdat = Autos.query.filter(Autos.VIN == vin).first()
            if bdat is None or vin == 'NoVIN':
                print("Entering data in Autos database")
                input = Autos(Jo=orderid, Hjo=None, Year=year, Make=make, Model=model, Color=color, VIN=vin, Title=None, State=None, EmpWeight=wt, Dispatched='Horizon Motors', Value=value,
                              TowCompany=carrier, TowCost=payment, TowCostEa=each, Original=original, Status='New', Date1=date1, Date2=date2, Pufrom=pufrom, Delto='FEL', Ncars=ncars, Orderid=orderid)
                db.session.add(input)
                db.session.commit()
                print('This auto not in database, adding to records...')
                print(orderid, year, make, model, color, vin, wt, value,
                      carrier, payment, each, ncars, pufrom, original)
                print(' ')
            else:
                print('This auto already in the database')
                print('Modifying and updating records...')
                print(orderid, year, make, model, color, vin, wt, value,
                      carrier, payment, each, ncars, pufrom, original)
                print(' ')
                bdat.EmpWeight = wt
                bdat.Value = value
                bdat.TowCompany = carrier
                bdat.TowCost = payment
                bdat.TowCostEa = each
                bdat.Ncars = ncars
                bdat.Pufrom = pufrom
                bdat.Delto = 'FEL'
                db.session.commit()

            pdat = People.query.filter((People.Ptype == 'TowCo') &
                                       (People.Company == carrier)).first()
            if pdat is None:
                input = People(Company=carrier, First='', Middle='', Last='', Addr1=addr1, Addr2=addr2, Addr3='', Idtype='', Idnumber='', Telephone=phone,
                               Email='', Associate1='', Associate2='', Date1=today, Date2=None, Original='', Ptype='TowCo', Temp1='', Temp2='')
                db.session.add(input)
                db.session.commit()
    tunnel.stop()
    return newfile, error

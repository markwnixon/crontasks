import datetime

from CCC_system_setup import addpath3, addpath4, websites, usernames, passwords, mycompany, addpaths
co = mycompany()
if co == 'FELA':
    from CCC_FELA_remote_db_connect import db
    from CCC_FELA_models import JO
elif co == 'OSLM':
    from CCC_OSLM_remote_db_connect import db
    from CCC_OSLM_models import JO

today = datetime.date.today()


def nodollar(infloat):
    outstr = "%0.2f" % infloat
    return outstr


def dollar(infloat):
    outstr = '$'+"%0.2f" % infloat
    return outstr


def avg(in1, in2):
    out = (in1+in2)/2
    return out


def stat_update(status, newval, i):
    a = list(status)
    a[i] = newval
    b = ''.join(a)
    return b


def nonone(input):
    if input is not None:
        output = int(input)
    else:
        output = 0
    return output


def d2s(instr):
    try:
        instr = instr.replace('$', '').replace(',', '')
    except:
        instr = str(instr)
    try:
        infloat = float(instr)
        outstr = "%0.2f" % infloat
    except:
        outstr = instr
    return outstr

def newjo(jtype,sdate):
    dt = datetime.datetime.strptime(sdate, '%Y-%m-%d')
    year= str(dt.year)
    day=str(dt.day)
    month=str(dt.month)
    lv=JO.query.get(1)
    nextid=lv.nextid
    eval=str(nextid%100).zfill(2)
    day2="{0:0=2d}".format(int(day))
    if month=='10':
        month='X'
    if month=='11':
        month='Y'
    if month=='12':
        month='Z'
    if jtype=='H':
        nextjo='HM'+month+day2+year[3]+eval
    else:
        nextjo='F'+jtype+month+day2+year[3]+eval
    input2 = JO(jo=nextjo, nextid=0, date=sdate, status=1)
    db.session.add(input2)
    lv.nextid=nextid+1
    return nextjo

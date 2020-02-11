import datetime
import re

from remote_db_connect import tunnel, db
from models import Interchange


def interparse(inpath, infile, imfile):

    error = 1

    today = datetime.datetime.today()
    year = str(today.year)
    month = str(today.month)
    day = str(today.day)
    datestr = month+'/'+day+'/'+year

    pyr = year[2]+year[3]
    # print(pyr)

    date_stdtxt1 = re.compile(
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s?\d{1,2},?\s?\d{4}')
    date_stdtxt2 = re.compile(
        r'(?:January|February|March|April|June|July|August|September|October|November|December)\s?\d{1,2},?\s?\d{4}')
    date_y2 = re.compile(r'(?:0[1-9]|[12][0-9]|3[01])[/](?:0[1-9]|[12][0-9]|3[01])[/]\d{2}')
    date_y4 = re.compile(r'(?:0[1-9]|[12][0-9]|3[01])[/](?:0[1-9]|[12][0-9]|3[01])[/]\d{4}')
    date_ny4 = re.compile(r'\d{4}-\d{2}-\d{2}')
    date_mil2 = re.compile(r'\d{1,2}\s?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s?\d{2}')
    date_mil4 = re.compile(r'\d{1,2}\s?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s?\d{4}')
    date_y2mdns = re.compile(r'\s'+pyr+'(?:0[1-9]|1[012])(?:0[1-9]|[12][0-9]|3[01])')
    date_int = re.compile(r'\d{1,2}\s?(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s?\d{4}')
    car_year = re.compile(r'(?:19|20)\d{2}')

    container_p = re.compile(r'[A-Za-z]{4}\s?[Ool0123456789]{7}')
    container_p2 = re.compile(r'[A-Za-z]{4}\s?[Ool0123456789]{6}\s[Ool0123456789]')
    container_p3 = re.compile(r'[A-Za-z]{4}\s?[Ool0123456789]{6}-[Ool0123456789]')
    book1 = re.compile(r'[A-Z0-9]{10}')
    book2 = re.compile(r'[A-Z0-9]{11}')
    book3 = re.compile(r'[A-Z0-9]{12}')
    bol1 = re.compile(r'\d{8}')
    bol2 = re.compile(r'[A-Z][0-9]{5}')
    bol3 = re.compile(r'[Ool0123456789]{7}')
    order_p = re.compile(r'[Ool0123456789]{6}')
    time_p24 = re.compile(r'(?:[1-9]|0[1-9]|1[0-9]|2[01234])[:](?:0[0-9]|[12345][0-9])')
    vin_p = re.compile(r'[Ool0123456789]{11}')

    longs = open(inpath+infile).read()
    ss = longs.lower()

    typedef = 'Empty Out'
    if 'empty in' in ss:
        typedef = 'Empty In'
    elif 'load in' in ss:
        typedef = 'Load In'
    elif 'load out' in ss:
        typedef = 'Load Out'

    tdate = datetime.datetime.strptime(datestr, '%m/%d/%Y').strftime('%Y/%m/%d')
    thistime = '00:01'
    container = 'NFI'

    ilist = ['TRUCK NUMBER', 'CHASSIS', 'RELEASE', 'SEALS', 'GROSS WT', 'CARGO WT', 'SIZE/TYPE']
    obj = {}
    for i in ilist:
        obj.update({i: 'NFI'})
        match = re.search(i+':?\s?\s?(\w*)', longs)
        if match:
            test = match.group(1)
            if len(test) > 0:
                nratio = len(re.sub("\D", "", test))/len(test)
                if nratio > .4:
                    obj.update({i: test})

    datef = date_int.findall(longs)
    dateg = date_ny4.findall(longs)
    print('dateg=', dateg)
    if datef:
        fix = re.sub(" ", "", datef[0])
        try:
            tdate = datetime.datetime.strptime(fix, '%d%b%Y').strftime('%Y/%m/%d')
        except:
            err = 1
    if dateg:
        fix = re.sub(" ", "", dateg[0])
        if 1 == 1:  # try:
            tdate = datetime.datetime.strptime(fix, '%Y-%m-%d').strftime('%Y/%m/%d')
            print('tdate=', tdate)
        if 1 == 2:  # except:
            err = 1

    timeat = time_p24.findall(longs)
    if timeat:
        thistime = timeat[0]

    t1 = container_p.findall(longs)
    t2 = container_p2.findall(longs)
    t3 = container_p3.findall(longs)
    t4 = t1+t2+t3
    if t4:
        fix = t4[0].strip()
        fix = fix.replace(' ', '')
        fix = fix.replace('-', '')
        back7 = fix[-7:]
        back7 = back7.replace('O', '0')
        back7 = back7.replace('o', '0')
        back7 = back7.replace('l', '1')
        front4 = fix[0]+fix[1]+fix[2]+fix[3]
        container = front4.upper()+back7
        print(container)

    # Search for things that are the keywords:
    driverlist = ['Ghanem', 'Davis', 'Alameh', 'Tibbs', 'Khoder']
    obj.update({'DRIVER': 'NFI'})
    for i in driverlist:
        match = re.search(i.lower(), ss)
        if match:
            obj.update({'DRIVER': i})

    print(obj)

    if tdate is not None:
        thisdate = datetime.datetime.strptime(tdate, '%Y/%m/%d')
    else:
        thisdate = today

    chassis = obj.get("CHASSIS")
    if chassis == 'NFI':
        chassis = 'OWN'

    trucknum = obj.get("TRUCK NUMBER")
    if '87' in trucknum:
        driver = 'Hassan Khoder'
        trucknum = '870F36'
    else:
        driver = 'Darrell Tibbs'

    idat = Interchange.query.filter(Interchange.Original == imfile).first()
    if idat is None:
            # Check to see if this file is in database already
        input = Interchange(CONTAINER=container, TRUCK_NUMBER=trucknum, DRIVER=driver, CHASSIS=chassis,
                            Date=thisdate, RELEASE=obj.get("RELEASE"), GROSS_WT=obj.get("GROSS WT"), SEALS=obj.get("SEALS"),
                            CONTYPE=obj.get("SIZE/TYPE"), CARGO_WT=obj.get("CARGO WT"),
                            Time=thistime, Status='AAAAAA', Original=imfile, Path='NFI', TYPE=typedef, Jo='NAY', Company='NAY')
        # if missing is None:
        print('Data is being added to database: interchange')
        db.session.add(input)
        db.session.commit()
        error = 0
    else:
        print('This picture original found in database already: ', imfile)
        error = 0

    tunnel.stop()
    return error

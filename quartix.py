import os
import time
from datetime import datetime
import shutil
import fnmatch
import subprocess

import imaplib, email
import datetime
import re
import numpy as np
import json
from cronfuncs import dropupdate

import xlrd
import imaplib, email

from email_functions import get_emails, get_attachments, get_attachment_filename, get_attachments_pdf, search_from_date, get_date, checkdate

from CCC_system_setup import addpath3, addpath4, websites, usernames, passwords, mycompany, addpaths, imap_url
co = mycompany()

if co == 'FELA':
    from CCC_FELA_remote_db_connect import tunnel, db
    from CCC_FELA_models import Trucklog, Drivers, Portlog
    unames = [usernames['mnix']]
    password = passwords['mnix']

elif co == 'OSLM':
    from CCC_OSLM_remote_db_connect import tunnel, db
    from CCC_OSLM_models import Trucklog, Drivers, Portlog
    unames = [usernames['serv']]
    password = passwords['serv']

#First download emails from Quartix
#_____________________________________________________________________________________________________________
# Subroutine for download Quartix attachments from weeklys
#_____________________________________________________________________________________________________________

dayback=8
datefrom = (datetime.date.today() - datetime.timedelta(dayback)).strftime("%d-%b-%Y")
att_dir=addpath4('quartix')
masterdown = []

for username in unames:
    con = imaplib.IMAP4_SSL(imap_url)
    con.login(username,password)
    con.select('INBOX')
    msgs=get_emails(search_from_date('SUBJECT','Weekly vehicle report',con,datefrom),con)
    flist=os.listdir(att_dir)
    qadd=[]
    qupdate=[]
    for j,msg in enumerate(msgs):
        raw=email.message_from_bytes(msg[0][1])
        thesefiles=get_attachment_filename(raw,'xls','xls')
        thisdate=get_date(msg)
        for thisfile in thesefiles:
            masterdown.append(thisfile)
            #print(thisdate,thisfile)
            if thisfile not in flist:
                print('Adding new file:',thisfile)
                qadd.append([thisdate,thisfile])
                get_attachments_pdf(raw,att_dir,'xls','xls')
            else:
                print(f'File {thisfile} already downloaded')

printif = 0
print(masterdown)
if 1==1:
    for thisfile in masterdown:
        afile = addpath4('quartix/'+thisfile)
        partfile = thisfile.replace('TR','')
        parts = partfile.split()
        tag = parts[0]
        date_ending = parts[1]
        date_ending = date_ending.replace('.xls','')
        wb = xlrd.open_workbook(afile)
        sheetlist = wb.sheet_names()
        print('Tag,Datename,Sheetlist:',tag,date_ending,sheetlist) if printif == 1 else 1
        datemode = wb.datemode
        print('Datemode is:', datemode) if printif == 1 else 1
        summary = sheetlist[0]
        sh = wb.sheet_by_name(summary)
        print('Number of Rows in Summary:', sh.nrows) if printif == 1 else 1
        for sheet in sheetlist[1:]:
            sh = wb.sheet_by_name(sheet)
            headerlist = 0
            startlist = 0
            lastlist = 0
            driver = 'NDT'
            dlist = []
            print(f'Number Row Sheetlist {sheet}: ',sh.nrows) if printif == 1 else 1
            distance = 0.0
            total_tol = 0.0
            rowstop = 100
            rowstart = 100
            for rownum in range(sh.nrows):
                alist = sh.row_values(rownum)
                print(f'Values for Row {rownum}',sh.row_values(rownum)) if printif == 1 else 1
                if 'Start location' in alist:
                    headerlist = alist
                    print('found headerlist') if printif == 1 else 1
                    #Now set the parameter locations
                    for j, col in enumerate(headerlist):
                        if col == 'Start location':
                            cstart = j
                if alist[1] == 1.0:
                    startlist = alist
                    rowstart = rownum
                    print('found startlist') if printif == 1 else 1
                if 'Total time on site' in alist:
                    rowstop = rownum-1
                    lastlist = sh.row_values(rownum-1)
                    print('found lastlist') if printif == 1 else 1

            try:
                print(f'Headerlist for {sheet}: ', headerlist)
            except:
                headerlist = 0
            try:
                print(f'Startlist for {sheet}: ', startlist)
            except:
                startlist = 0
            try:
                print(f'Lastlist for {sheet}: ', lastlist)
            except:
                lastlist = 0

            if headerlist == 0 or startlist == 0 or lastlist == 0:
                print(f'Values not found, no work performed on {sheet}')
                print(' ')
            else:

                for rownum in range(rowstart,rowstop+1):
                    alist = sh.row_values(rownum)
                    try:
                        dist = float(alist[cstart+6])
                    except:
                        dist = 0.0
                    print(dist) if printif == 1 else 1
                    distance = distance + dist

                    if cstart == 3:
                        driver = alist[2].strip()
                        dlist.append(driver)

                    if rownum > rowstart:

                        blist = sh.row_values(rownum-1)
                        location = blist[cstart+2]
                        time1 = alist[cstart+1]
                        time2 = blist[cstart+3]
                        print(sheet, rownum, rowstart, rowstop, cstart, time1, time1) if printif == 1 else 1
                        tol = round((time1 - time2) * 24, 2)
                        total_tol = total_tol + tol
                        print('tol=',tol) if printif == 1 else 1
                        if tol > .75:
                            print(f'{location} is potential drop site') if printif == 1 else 1
                            statelist = ['Maryland', 'Pennsylvannia', 'New Jersey', 'Delaware', 'Virginia']
                            abblist = ['MD', 'PA', 'NJ', 'DE', 'VA']
                            zip = re.compile(r'[0123456789]{5}')
                            ellist = location.split()
                            ellen = len(ellist)
                            street = location.split(',')[0]
                            print(street) if printif == 1 else 1
                            cityst = location.replace(street+',','').strip()
                            print(cityst)
                            block = 'GPS Update\n' + street + '\n' + cityst + '\n'
                            print(block) if printif == 1 else 1
                            entity = dropupdate(block)

                if rowstart == rowstop:
                    sloc = startlist[cstart]
                    stim = startlist[cstart + 1]
                    eloc = startlist[cstart + 2]
                    etim = lastlist[cstart + 3]
                    dtim = 0.0
                else:
                    sloc = startlist[cstart]
                    stim = startlist[cstart+1]
                    eloc = lastlist[cstart+2]
                    etim = lastlist[cstart+3]
                    try:
                        dtim = round((etim - stim) * 24,2)
                        distance = round(distance,2)
                    except:
                        print('Issue with time (cstart,etim,stim):', cstart,etim, stim)

                if dtim < .1 or distance < .1:
                    print(f'Truck {tag} was not active on {start_py_date}')
                    print(' ')
                else:

                    year, month, day, hour, minute, second = xlrd.xldate_as_tuple(stim,datemode)
                    start_py_date = datetime.datetime(year, month, day, hour, minute, second)
                    year, month, day, hour, minute, second = xlrd.xldate_as_tuple(etim,datemode)
                    end_py_date = datetime.datetime(year, month, day, hour, minute, second)
                    datehere = start_py_date.date()

                    print(f'Truck {tag} started at {sloc} on {start_py_date}')
                    print(f'Truck {tag} ended at {eloc} on {end_py_date}')
                    print(f'Truck {tag} was in service for {dtim} hours and stopped for {total_tol} hours and traveled {distance} miles')
                    print(' ')

                    total_tol = round(total_tol,2)
                    gotime = round(dtim - total_tol,2)


                    print('dlist = ', dlist)
                    x = np.array(dlist)
                    nu = np.unique(x)
                    print('unique-', nu)
                    if len(nu) == 1:
                        status = '1'
                        driver = dlist[0]
                        phone = 'NDT'
                    else:
                        status = 'M'
                        driver = json.dumps(dlist)
                        phone = None

                    if driver == 'Ty (1)':
                        print('TYTYTYTYTYTYTY')
                        ddat = Drivers.query.filter(Drivers.Name == 'Tiwand McClary').first()
                        if ddat is not None:
                            driver = ddat.Name
                            phone = ddat.Phone
                        else:
                            driver = 'NAY'
                            phone = 'NAY'

                    elif status == 1:
                        driver = 'NAY'
                        phone = 'NAY'

                    tdat = Trucklog.query.filter( (Trucklog.Date == datehere) & (Trucklog.Tag == tag) ).first()
                    if tdat is None:
                        input = Trucklog(Date=datehere,GPSin=start_py_date,GPSout=end_py_date,Tag=tag,Distance=distance,Stoptime=total_tol,Gotime=gotime,Odomstart=None,Odomstop=None,Odverify=None,Driver=driver,Phone=phone,Maintrecord='None',Locationstart=sloc,Locationstop=eloc,Maintid=None,Status=status)
                        db.session.add(input)
                        db.session.commit()
                    else:
                        if tdat.Status == '0':
                            tdat.Status = status
                            tdat.GPSin = start_py_date
                            tdat.GPSout = end_py_date
                            tdat.Distance = distance
                            tdat.Stoptime = total_tol
                            tdat.Gotime = gotime
                            tdat.Locationstart = sloc
                            tdat.Locationstop = eloc
                            db.session.commit()


tunnel.stop()
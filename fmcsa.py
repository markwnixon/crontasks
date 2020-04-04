from datetime import datetime, timedelta
from CCC_system_setup import scac, addpath1
from remote_db_connect import tunnel, db
from models import Drivers, Vehicles, DriverAssign, Trucklog, KeyInfo
from cron_report_maker import reportmaker, subreportmaker, make_each_sumover, get_sections, mergerbook
from utils import d2s, d1s
import shutil
from PyPDF2 import PdfFileMerger
from PyPDF2 import PdfFileReader, PdfFileWriter
import os

printif = 1

runat = datetime.now()
today = runat.date()
lookback = runat - timedelta(30)
cut60 = runat - timedelta(60)
cut90 = runat - timedelta(90)
lbdate = lookback.date()
include_tickets = 0
print(' ')
print('________________________________________________________')
print(f'This sequence run at {runat} with look back to {lbdate}')
print('________________________________________________________')
print(' ')

pdfs,bookmarks = [], []
#report_sections = ['introduction', 'driver_list', 'truck_list', 'insurance', 'driver_sections', 'inspection_sections', 'random_program_cert']
report_sections = ['introduction', 'driver_list', 'truck_list', 'insurance', 'driver_sections', 'inspection_sections', 'drug_test_sections', 'random_program_cert']
for rep in report_sections:
    if 'sections' in rep:
        sumover, subreps = get_sections(rep)
        for each in sumover:
            for subrep in subreps:
                fp, bm = make_each_sumover(rep,each,subrep)
                fpstatic = fp.replace('reports/','reports/static/')
                print(f'Looking for static file: {fpstatic}')
                if os.path.isfile(fpstatic):
                    pdfs.append(fpstatic)
                    bookmarks.append(bm)
                else:
                    docref = subreportmaker(fp,rep,each,subrep)
                    if docref is not None:
                        if os.path.isfile(docref):
                            pdfs.append(fp)
                            bookmarks.append(bm)
                            shutil.move(docref, fp)
    else:
        fp = addpath1(f'reports/{scac}_{rep.title()}.pdf')
        bm = rep.replace('_',' ')
        fpstatic = fp.replace('reports/', 'reports/static/')
        print(f'Looking for static file: {fpstatic}')
        if os.path.isfile(fpstatic):
            pdfs.append(fpstatic)
            bookmarks.append(bm.title())
        else:
            docref = reportmaker(fp, rep)
            if docref is not None:
                pdfs.append(fp)
                bookmarks.append(bm.title())
                shutil.move(docref,fp)

mergerbook(pdfs,bookmarks)











if 1 == 2:
    sp = addpath1('reports/summary.pdf')
    docref = reportmaker('summary',sumdata)
    shutil.move(docref, sp)

    fd = addpath1('reports/driverlist.pdf')
    #Makes a list of the drivers and a 1-page summary for each driver
    docref = reportmaker('driverlist',ddata)
    shutil.move(docref, fd)

    ft = addpath1('reports/trucklist.pdf')
    docref = reportmaker('trucklist',tdata)
    shutil.move(docref, ft)

    pdfs = [sp, fd, ft]
    bookmarks = ['Introduction', 'Driver List','Trucks List']


    fhose = []
    for dname in dnames:
        tlogs = Trucklog.query.filter( (Trucklog.DriverStart == dname) & (Trucklog.Date > cut60 )).all()
        try:
            #get last 30 times in truck
            tlogs = tlogs[-30:]
        except:
            print('Tlogs shorter than 30')

        for tlog in reversed(tlogs):
            duty_hours = tlog.Shift
            try:
                hrs = float(duty_hours)
            except:
                hrs = 0.0
            if hrs > 12.0 and hrs < 12.25: hrs = 12.0

            airmiles = tlog.Rdist
            try:
                airmiles = float(airmiles)
            except:
                airmiles = 0.0

            logmiles = tlog.Distance
            try:
                logmiles = float(logmiles)
            except:
                logmiles = 0.0

            if hrs > 1.0:
                if hrs > 12.0 or airmiles > 100:
                    exempt = 'Paper Log'
                else:
                    exempt = '100 mile exemption'
                print(tlog.Date,tlog.DriverStart,tlog.Unit,tlog.Tag,tlog.GPSin,tlog.GPSout,d2s(hrs),exempt)

        if printif == 1:
            drv_leader = f'reports/{dname}_Summary.pdf'
            drv_leader = drv_leader.replace(' ','_')
            drv_leader = addpath1(drv_leader)
            pdfs.append(drv_leader)
            bookmarks.append(f'{dname}')

            mvr = f'reports/{dname}_MVR.pdf'
            mvr = mvr.replace(' ','_')
            mvr = addpath1(mvr)
            if os.path.isfile(mvr):
                pdfs.append(mvr)
                bookmarks.append(f'{dname} MVR')

            fhos = addpath1(f'reports/hos_{dname}.pdf')
            pdfs.append(fhos)
            docref, int_data, toll_data, valpdfs = reportmaker('hos', tlogs)
            shutil.move(docref, fhos)
            bookmarks.append(f'{dname} Hours of Service')

            fhosval = addpath1(f'reports/hos_val{dname}.pdf')
            pdfs.append(fhosval)
            docref = reportmaker('hosval', [tlogs, int_data, toll_data, valpdfs])
            shutil.move(docref, fhosval)
            bookmarks.append(f'{dname} HOS Validation Data')

            if include_tickets == 1:
                #Assemble the proofs:
                merger = PdfFileMerger()
                pfile = addpath1(f'reports/{dname}_proofs.pdf')
                for val in valpdfs:
                    merger.append(val)
                merger.write(pfile)
                merger.close()
                pdfs.append(pfile)
                bookmarks.append(f'{dname} Interchange Tickets')



    if printif == 1:
        print(pdfs)
        print(bookmarks)

        ranp = f'reports/{scac}_Random_Program_Cert.pdf'
        ranp = ranp.replace(' ', '_')
        ranp = addpath1(ranp)
        if os.path.isfile(ranp):
            pdfs.append(ranp)
            bookmarks.append(f'{scac} Random Drug Test Certification')

        ranp = f'reports/{scac}_List_of_Drivers_Random.pdf'
        ranp = ranp.replace(' ', '_')
        ranp = addpath1(ranp)
        if os.path.isfile(ranp):
            pdfs.append(ranp)
            bookmarks.append(f'{scac} List of Drivers in Random')

        bookmark = 1
        #Assemble the full report
        if bookmark == 0:

            merger = PdfFileMerger()
            for pdf in pdfs:
                merger.append(pdf)

            merger.write(addpath1('reports/fmcsa.pdf'))
            merger.close()

        else:
            mergerbook(pdfs,bookmarks)



tunnel.stop()
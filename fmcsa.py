from datetime import datetime, timedelta
from CCC_system_setup import scac, addpath1
from remote_db_connect import tunnel, db
from models import Drivers, Vehicles, DriverAssign, Trucklog, KeyInfo
from cron_report_maker import reportmaker
from utils import d2s, d1s
import shutil
from PyPDF2 import PdfFileMerger
from PyPDF2 import PdfFileReader, PdfFileWriter

def mergerbook(pdfs,bookmarks):
    # merge page by page
    output_pdf_stream = PdfFileWriter()
    j = 0
    for kx, pdf in enumerate(pdfs):
        f = PdfFileReader(open(pdf, "rb"))
        for i in range(f.numPages):
            output_pdf_stream.addPage(f.getPage(i))
            if i == 0:
                output_pdf_stream.addBookmark(bookmarks[kx], j)
            j = j + 1

    # create output pdf file
    ofile = addpath1('reports/fmcsa.pdf')
    try:
        output_pdf_file = open(ofile, "wb")
        output_pdf_stream.write(output_pdf_file)
    finally:
        output_pdf_file.close()


printif = 1

runat = datetime.now()
today = runat.date()
lookback = runat - timedelta(30)
cut60 = runat - timedelta(60)
cut90 = runat - timedelta(90)
lbdate = lookback.date()
print(' ')
print('________________________________________________________')
print(f'This sequence run at {runat} with look back to {lbdate}')
print('________________________________________________________')
print(' ')


dnames = []
ddata = Drivers.query.filter(Drivers.JobEnd > today).all()
for dd in ddata:
    dnames.append(dd.Name)
    print(f'Creating profile for {dd.Name}')

tdata = Vehicles.query.filter(Vehicles.DOTNum != None).all()
for td in tdata:
    print(f'Creating profile for {td.Unit}')

sumdata = KeyInfo.query.all()
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
        fhos = addpath1(f'reports/hos_{dname}.pdf')
        fhose.append(fhos)
        docref, valpdfs = reportmaker('hos', tlogs)
        shutil.move(docref, fhos)
        drv_leader = f'reports/{dname}_Summary.pdf'
        drv_leader = drv_leader.replace(' ','_')
        drv_leader = addpath1(drv_leader)
        pdfs.append(drv_leader)
        pdfs.append(fhos)

        #Assemble the proofs:
        merger = PdfFileMerger()
        pfile = addpath1(f'reports/{dname}_proofs.pdf')
        for val in valpdfs:
            merger.append(val)
        merger.write(pfile)
        merger.close()
        pdfs.append(pfile)
        bookmarks.append(f'{dname}')
        bookmarks.append(f'{dname} Hours of Service')
        bookmarks.append(f'{dname} HOS Support Docs')

if printif == 1:
    print(pdfs)
    print(bookmarks)

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
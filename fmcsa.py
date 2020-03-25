from datetime import datetime, timedelta
from CCC_system_setup import scac, addpath1
from remote_db_connect import tunnel, db
from models import Drivers, Vehicles, DriverAssign
from cron_report_maker import reportmaker
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

dnames = []
ddata = Drivers.query.filter(Drivers.JobEnd > today).all()
for dd in ddata:
    dnames.append(dd.Name)
    print(f'Creating profile for {dd.Name}')

tdata = Vehicles.query.all()
for td in tdata:
    print(f'Creating profile for {td.Unit}')

fd = addpath1('reports/driverlist.pdf')
#Makes a list of the drivers and a 1-page summary for each driver
docref = reportmaker('driverlist',ddata)
shutil.move(docref, fd)

ft = addpath1('reports/trucklist.pdf')
docref = reportmaker('trucklist',tdata)
shutil.move(docref, ft)

pdfs = [fd,ft]
bookmarks = ['Driver List','Trucks List']

fhose = []
for dname in dnames:
    drvassign = DriverAssign.query.filter( (DriverAssign.Driver == dname) & (DriverAssign.Hours != None )).all()
    drvassign = drvassign[-30:]
    for drv in drvassign:
        print(drv.Driver,drv.Date)
    fhos = addpath1(f'reports/hos_{dname}.pdf')
    fhose.append(fhos)
    docref = reportmaker('hos', drvassign)
    shutil.move(docref, fhos)
    drv_leader = f'reports/{dname}.pdf'
    drv_leader = drv_leader.replace(' ','_')
    drv_leader = addpath1(drv_leader)
    pdfs.append(drv_leader)
    pdfs.append(fhos)
    bookmarks.append(f'{dname}')
    bookmarks.append(f'{dname} Hours of Service')


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
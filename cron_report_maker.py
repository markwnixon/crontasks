#Now lets print the report out
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import landscape
from reportlab.platypus import Image
from reportlab.lib.units import inch
import csv
import math
from datetime import datetime, timedelta
from CCC_system_setup import myoslist, addpath1, addtxt, bankdata, scac, logoi, companydata, websites, addpath3
from page_merger import pagemerger,pagemergermp
import shutil
from utils import avg, parseline
from PyPDF2 import PdfFileReader, PdfFileWriter
import subprocess
from models import Vehicles, Interchange, Tolls, KeyInfo, Drivers, Trucklog
from pdfmergers import pagemerger, pagemergermp
import os

runat = datetime.now()
today = runat.date()

def reportmaker(fp, type):

    file1=addpath1(f'reports/pagestart.pdf')
    file2=addpath1(f'reports/background.pdf')
    file3=addpath1(f'reports/headers.pdf')

    c=canvas.Canvas(file1, pagesize=letter)
    c.setLineWidth(1)
    c.drawImage(logoi, 185, 680, mask='auto')
    c.showPage()
    c.save()
    docref = None

    if type=='introduction':
        report_background(file2,'introduction')
        report_headers(file3,'introduction')
        report_contents(fp,'introduction')
        docref=pagemerger([file1,file2,file3,fp])

    if type=='driver_list':
        file4 = addpath1(f'reports/driverlist.pdf')
        report_background(file2,'drivers')
        report_headers(file3,'drivers')
        report_contents(fp,'drivers')
        docref=pagemerger([file1,file2,file3,fp])

    if type=='truck_list':
        file4 = addpath1(f'reports/trucklist.pdf')
        report_background(file2,'trucks')
        report_headers(file3,'trucks')
        report_contents(fp,'trucks')
        docref=pagemerger([file1,file2,file3,fp])

    return docref

def subreportmaker(fp, type, each, subtype):

    file1=addpath1(f'reports/pagestart.pdf')
    file2=addpath1(f'reports/background.pdf')
    file3=addpath1(f'reports/headers.pdf')

    c=canvas.Canvas(file1, pagesize=letter)
    c.setLineWidth(1)
    c.drawImage(logoi, 185, 680, mask='auto')
    c.showPage()
    c.save()

    if subtype == 'hos' or subtype == 'hosval':
        report_background(file2,subtype)
        report_headers(file3,subtype)
        pages, multioutput = subreport_contents(fp,type,each,subtype)
        if len(pages) > 1:
            docref=pagemergermp([file1,file2,file3,fp], pages, multioutput)
        else:
            docref = pagemerger([file1, file2, file3, fp])
        return docref
    else:
        return None

def topcheck(fp,n2,dh,c,page,pages):
    c.showPage()
    c.save()
    page = page + 1
    base = fp.replace('.pdf', '')
    newfile = base + 'page' + str(page) + '.pdf'
    top = n2 - dh
    c = canvas.Canvas(newfile, pagesize=letter)
    pages.append(newfile)

    return c,page,top,pages


def report_background(file2,item):
    c = canvas.Canvas(file2, pagesize=letter)
    c.setLineWidth(1)
    ltm, rtm, bump, tb, ctrall, left_ctr, right_ctr, dl, dh, tdl, hls, m1, m2, m3, m4, m5, m6, m7, n1, n2, n3 = reportsettings(1)

    n3 = n3 - 20
    fulllinesat = [n3]

    q1 = ltm + 180
    q2 = rtm - 180
    sds3 = [q1, q2]

    # Date and JO boxes
    dateline = m1 + 8.2 * dl
    c.rect(rtm - 100, m1 + 7 * dl, 100, 2 * dl, stroke=1, fill=0)
    c.line(rtm - 100, dateline, rtm, dateline)
    #c.line(rtm - 75, m1 + 7 * dl, rtm - 75, m1 + 9 * dl)

    # Explanation box
    ctm = 218
    mtmp = dateline - 3.5 * dl
    c.rect(ltm, dateline - 4 * dl, 250, 5 * dl, stroke=1, fill=0)
    level1 = mtmp + 3.5 * dl
    c.line(ltm, level1, ltm + 250, level1)

    for i in fulllinesat:
        c.line(ltm, i, rtm, i)

    c.line(ltm, n1, ltm, n3)
    c.line(rtm, n1, rtm, n3)

    c.showPage()
    c.save()


def report_headers(file3, item):
    cdata = companydata()
    today = datetime.today().strftime('%m/%d/%Y')
    invodate = datetime.today().strftime('%m/%d/%Y')
    ltm, rtm, bump, tb, ctrall, left_ctr, right_ctr, dl, dh, tdl, hls, m1, m2, m3, m4, m5, m6, m7, n1, n2, n3 = reportsettings(
        1)

    dateline = m1 + 8.2 * dl
    mtmp = dateline - 3.5 * dl
    level1 = mtmp + 3.5 * dl

    c = canvas.Canvas(file3, pagesize=letter)
    c.setLineWidth(1)

    c.setFont('Helvetica-Bold', 24, leading=None)
    c.drawCentredString(rtm - 75, dateline + 1.5 * dl, 'Report')
    c.setFont('Helvetica-Bold', 12, leading=None)
    c.drawString(ltm + bump * 3, level1 + bump * 2, f'{item.upper()} Report')
    c.setFont('Helvetica', 12, leading=None)
    c.drawCentredString(rtm - 50, dateline + bump, 'Created')
    #c.drawCentredString(rtm - 37.7, dateline + bump, 'Type')

    vdat = Vehicles.query.filter(Vehicles.DOTNum != None).first()
    dh = 13
    top = level1 - dh
    lft = ltm + bump * 3
    header = list(range(5))
    header[0] = f'This Report Page is the {item.upper()}'
    header[1] = 'Information List for'
    header[2] = f'{cdata[0]}'
    header[3] = f'DOT #{vdat.DOTNum}'
    header[4] = ''
    for ix in header:
        c.drawString(lft, top, ix)
        top = top - dh

    x = avg(rtm - 75, rtm)
    y = dateline - dh - bump
    #c.drawCentredString(x, y, f'{item.upper()}')
    x = avg(rtm - 75, rtm - 150)
    c.drawCentredString(rtm-50, y, invodate)

    c.showPage()
    c.save()

#This function defines all the report parameters normally used
def reportsettings(squeeze):
    #squeeze input is squeeze factor to apply to default spacing parameters squeeze=1 is default call
    #Left and right margins:
    ltm=36
    rtm=575
    # Offsets from lines:
    bump=2.5
    tb=bump*2
    #Center Points
    ctrall=310
    left_ctr=170
    right_ctr=480

    dl=17.6
    tdl=dl*2
    dh=dl*.9*squeeze
    hls=530
    m1=hls-dl
    m2=hls-2*dl
    m3=hls-3*dl
    m4=hls-4*dl
    m5=hls-18*dl
    m6=hls-23*dl
    m7=hls-27*dl
    n1=550
    n2=n1-dl
    #bottom margin
    n3=hls-27*dl

    return ltm,rtm,bump,tb,ctrall,left_ctr,right_ctr,dl,dh,tdl,hls,m1,m2,m3,m4,m5,m6,m7,n1,n2,n3


def report_contents(file4,item):

    ltm,rtm,bump,tb,ctrall,left_ctr,right_ctr,dl,dh,tdl,hls,m1,m2,m3,m4,m5,m6,m7,n1,n2,n3=reportsettings(1)

    pages=[file4]
    page=1
    c=canvas.Canvas(file4, pagesize=letter)
    c.setLineWidth(1)

    #Main Items Listing
    c.setFont('Helvetica-Bold',14,leading=None)
    mid = int(ltm+rtm)/2


    if item == 'drivers':
        c.drawCentredString(mid,535,'Active Driver Data')
    if item == 'trucks': c.drawCentredString(mid,535,'Active DOT Truck Data')
    c.line(ltm, 550, rtm, 550)
    c.line(ltm, 530, rtm, 530)
    c.setFont('Helvetica', 10, leading=None)
    top = 510
    leftw1 = ltm+10
    leftw2 = ltm+110
    leftw3 = ltm+320
    leftw4 = ltm+490


    if item == 'introduction':
        c.drawCentredString(mid, 535, 'Introduction')
        ddata = KeyInfo.query.all()
        presents = ['overview', 'focus', 'truckstart', 'logging', 'rod', 'maintenance', 'testing', 'accidents']
        for present in presents:
            for dd in ddata:
                if dd.Type == present:
                    c.drawString(leftw1,top, dd.Type.title())
                    slist = parseline(dd.Description,90)
                    for sl in slist:
                        c.drawString(leftw2, top, sl)
                        top = top - dl*.9
                    top = top - dl*.5
                    if top < n3: c, page, top, pages = topcheck(file4, n2, dh, c, page, pages)


    if item == 'drivers':
        ddata = Drivers.query.filter(Drivers.JobEnd > today).all()
        for dd in ddata:
            c.drawString(leftw1,top, dd.Name)
            c.drawString(leftw2, top, f'{dd.Addr1},  {dd.Addr2}')
            top = top - dl
            c.drawString(leftw2, top, f'{dd.Phone}  {dd.Email}')
            top = top - dl
            c.drawString(leftw2, top, f'Started with Company:  {dd.JobStart}')
            c.drawString(leftw3, top, f'DOB:  {dd.DOB}')
            top = top - dl
            c.drawString(leftw2, top, f'CDL Information:  {dd.CDLstate}  #{dd.CDLnum}  Expires:{dd.CDLexpire}')
            top = top - dl
            c.drawString(leftw2, top, f'Medical Expires: {dd.MedExpire}  TWIC Expires: {dd.TwicExpire}')
            top = top - dl
            c.drawString(leftw2, top, f'Pre-Employment Screening: {dd.PreScreen}    Last Screening Completed: {dd.LastTested}')
            top=top-dl*2

            if top < n3: c, page, top, pages = topcheck(file4, n2, dh, c, page, pages)

    if item == 'trucks':
        ddata = Vehicles.query.filter(Vehicles.DOTNum != None).all()
        for dd in ddata:
            c.drawString(leftw1, top, f'Unit #{dd.Unit}')
            c.drawString(leftw2, top, f'{dd.Year} {dd.Make} {dd.Model}  Place in Service:{dd.ServStr}')
            top = top - dl
            c.drawString(leftw2, top, f'Color: {dd.Color}  VIN: {dd.VIN}  MD Plate:{dd.Plate}')
            top = top - dl
            c.drawString(leftw2, top, f'MD Title: {dd.Title}  EmptyWt: {dd.EmpWeight}  GrossWt: {dd.GrossWt}')
            top = top - dl
            c.drawString(leftw2, top, f'EzPass Transponder:  {dd.Ezpassxponder}  Port Transponer:  {dd.Portxponder}')
            top = top - dl * 2

            if top < n3: c, page, top, pages = topcheck(file4, n2, dh, c, page, pages)

            addtickets = 0
            if addtickets == 1:
                first = 0
                last = 0
                for ix, val in enumerate(valticket):
                    if ix == 0:
                        tlist = val.Time.split(':')
                        firsttime = int(tlist[0])
                        lasttime = firsttime
                    else:
                        tlist = val.Time.split(':')
                        thistime = int(tlist[0])
                        if thistime < firsttime:
                            first = ix
                            firsttime = thistime
                        elif thistime >= lasttime:
                            last = ix
                            lasttime = thistime

                for ix, val in enumerate(valticket):

                    if ix == first or ix == last:
                        placefile = addpath3(f'interchange/{val.Original}')

                        if os.path.isfile(placefile):
                            print(f'Have interchange ticket for {thisdate} {plate}')
                        else:
                            pythonline = websites['ssh_data'] + f'vinterchange/{val.Original}'
                            placefile = addpath3(f'interchange/{val.Original}')
                            copyline1 = f'scp {pythonline} {placefile}'
                            print(copyline1)
                            os.system(copyline1)

                        if ix == first: placefile1 = placefile
                        if ix == last: placefile2 = placefile

                blendfile = addpath3(f'interchange/BLEND_{val.Original}')
                if os.path.isfile(blendfile):
                    print('Have this blend file')
                else:
                    blendticks(placefile1,placefile2, blendfile)
                valpdfs.append(blendfile)


    c.showPage()
    c.save()

    if len(pages)>1:
        pdfcommand=['pdfunite']
        for page in pages:
            pdfcommand.append(page)
        multioutput=addpath1(f'reports/multioutput'+'.pdf')
        pdfcommand.append(multioutput)
        tes=subprocess.check_output(pdfcommand)
    else:
        multioutput=' '

    return pages, multioutput



def blendticks(gfile1,gfile2,outfile):

    reader1 = PdfFileReader(open(gfile1, 'rb'))
    p1 = reader1.getPage(0)

    reader2 = PdfFileReader(open(gfile2, 'rb'))
    p2 = reader2.getPage(0)
    #p2.cropBox.lowerLeft = (50,400)
    #p2.cropBox.upperRight = (600,700)

    #offset_x = p2.mediaBox[2]
    offset_x = 0
    offset_y = -280

    # add second page to first one
    p1.mergeTranslatedPage(p2, offset_x, offset_y, expand=False)
    p1.cropBox.lowerLeft = (50,250)
    p1.cropBox.upperRight = (550,800)

    output = PdfFileWriter()
    output.addPage(p1)

    with open(outfile, "wb") as out_f:
        output.write(out_f)

def get_sections(rep):
    each = []
    if 'driver' in rep:
        ddata = Drivers.query.filter(Drivers.JobEnd > today).all()
        for dd in ddata:
            #Only include drivers requested
            if dd.Pin == '1': each.append(dd.Name)
        subreps = ['summary', 'mvr', 'hos', 'hosval']

    if 'inspection' in rep:
        ddata = Vehicles.query.filter(Vehicles.Unit != None).all()
        for dd in ddata:
            each.append(dd.Unit)
        subreps = ['inspection']

    if 'drug' in rep:
        ddata = Drivers.query.filter(Drivers.JobEnd > today).all()
        for dd in ddata:
            #Only include drivers requested
            if dd.Pin == '1': each.append(dd.Name)
        #subreps = ['ccf']
        subreps = ['ccf', 'results']

    return each, subreps

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

def make_each_sumover(rep,each,subrep):
    if rep == 'driver_sections':
        driver = each.replace(' ','_')
        if subrep == 'summary':
            fp = addpath1(f'reports/{driver}_Summary.pdf')
            bm = f'{each}'
        if subrep == 'mvr':
            fp = addpath1(f'reports/{driver}_MVR.pdf')
            bm = f'{each} MVR'
        if subrep == 'hos':
            fp = addpath1(f'reports/hos_{driver}.pdf')
            bm = f'{each} Hours of Service'
        if subrep == 'hosval':
            fp = addpath1(f'reports/hos_val{driver}.pdf')
            bm = f'{each} HOS Validation Data'

    if rep == 'inspection_sections':
        fp = addpath1(f'reports/Annual_Inspection_Unit_{each}.pdf')
        bm = f'{each} Annual Inspection'

    if rep == 'drug_test_sections':
        driver = each.replace(' ', '_')
        if subrep == 'ccf':
            fp = addpath1(f'reports/{driver}_PreEmp_CCF.pdf')
            bm = f'{each} PreEmployment CCF'
        if subrep == 'results':
            fp = addpath1(f'reports/{driver}_PreEmp_Results.pdf')
            bm = f'{each} PreEmployment Results'


    return fp, bm

def subreport_contents(fp,rep,each,item):
    cut60 = datetime.now() - timedelta(60)

    ltm,rtm,bump,tb,ctrall,left_ctr,right_ctr,dl,dh,tdl,hls,m1,m2,m3,m4,m5,m6,m7,n1,n2,n3=reportsettings(1)

    pages=[fp]
    page=1
    c=canvas.Canvas(fp, pagesize=letter)
    c.setLineWidth(1)

    #Main Items Listing

    mid = int(ltm+rtm)/2
    c.line(ltm, 550, rtm, 550)
    c.line(ltm, 530, rtm, 530)

    if rep == 'driver_sections':
        driver = each
        tlogs = Trucklog.query.filter((Trucklog.DriverStart == driver) & (Trucklog.Date > cut60)).order_by(Trucklog.Date).all()
        try:
            # get last 30 times in truck
            tlogs = tlogs[-30:]
            exemptnumber = 1
        except:
            print('Tlogs shorter than 30')

        if item == 'hos':
            c.setFont('Helvetica-Bold', 14, leading=None)
            c.drawCentredString(mid, 535,f'Hours of Service For Driver {each} Last 30 Drive Days')
            c.setFont('Helvetica', 10, leading=None)
            top = 530
            leftw1 = ltm + 10
            leftw2 = ltm + 170
            leftw3 = ltm + 220
            c.setFont('Helvetica', 10, leading=None)
            top = top - dl * .9

            for dd in reversed(tlogs):
                duty_hours = dd.Shift
                try:
                    hrs = float(duty_hours)
                except:
                    hrs = 0.0
                if hrs > 12.0 and hrs < 12.25: hrs = 12.0

                airmiles = dd.Rdist
                try:
                    airmiles = float(airmiles)
                except:
                    airmiles = 0.0

                logmiles = dd.Distance
                try:
                    logmiles = float(logmiles)
                except:
                    logmiles = 0.0

                if hrs > 1.0:
                    if hrs > 12.0 or airmiles > 100:
                        if hrs > 12.0 and airmiles < 100:  exempt = '**Shift hours exceed 12.0**'
                        if hrs < 12.0 and airmiles > 100:  exempt = '**Airmiles exceed 100.0**'
                        if hrs > 12.0 and airmiles > 100:  exempt = '**Shift hours exceed 12.0 and Airmiles exceed 100.0**'
                    else:
                        exempt = '100 mile exemption'

                    thisdate = dd.GPSin
                    thisdate = thisdate.date()
                    c.drawString(leftw1, top, f'Shift Start: {dd.GPSin}')
                    c.drawString(leftw2, top, f'Unit {dd.Unit}')
                    c.drawString(leftw3, top, f'{dd.Locationstart}')
                    top = top - dl * .7
                    c.drawString(leftw1, top, f'Shift End : {dd.GPSout}')
                    c.drawString(leftw2, top, f'Unit {dd.Unit}')
                    c.drawString(leftw3, top, f'{dd.Locationstop}')
                    top = top - dl * .7
                    c.drawString(leftw1, top, f'Duty Hours: {hrs}')
                    c.drawString(leftw2, top, f'Truck Miles: {dd.Distance}')
                    c.drawString(leftw2 + 120, top, f'Air Miles: {dd.Rdist}')
                    top = top - dl * .7
                    c.drawString(leftw2, top, f'Farthest Location: {dd.Rloc}')
                    #top = top - dl * .7
                    if '**' in exempt:
                        c.setFillColorRGB(1, 0, 0)
                        c.drawString(leftw1, top, f'Paper Log Required')
                        top = top - dl * .7
                        c.drawString(leftw1, top, f'{exempt}')
                        c.drawString(leftw2, top, f'Exemption #{exemptnumber} of 8 allowed last 30 days')
                        exemptnumber = exemptnumber + 1
                        c.setFillColorRGB(0, 0, 0)
                    else:
                        c.drawString(leftw1, top, f'Logging: {exempt}')
                    top = top - dl * 1.2

                    if top < n3:
                        c, page, top, pages = topcheck(fp, n2, dh, c, page, pages)
                        c.drawCentredString(mid, 535, f'HOS Data For Driver {each} (cont.) ')
                        c.line(ltm, 550, rtm, 550)
                        c.line(ltm, 530, rtm, 530)
                        c.setFont('Helvetica', 10, leading=None)

        if item == 'hosval':
            c.drawCentredString(mid, 535, f'HOS Validation Data For Driver {each}')
            top = 510
            leftw1 = ltm + 10
            leftw2 = ltm + 70
            leftw3 = ltm + 110
            leftw4 = ltm + 190
            leftw5 = ltm + 290

            c.drawString(leftw1, top, f'Interchange Tickets from Port')
            top = top - dl * .8
            c.drawString(leftw1, top, f'Date')
            c.drawString(leftw2, top, f'Time')
            c.drawString(leftw3, top, f'Plate')
            c.drawString(leftw4, top, f'Container')
            c.drawString(leftw5, top, f'Gross Weight')
            top = top - dl * .8
            c.setFont('Helvetica', 10, leading=None)

            for dd in reversed(tlogs):
                thisdate = dd.GPSin
                thisdate = thisdate.date()
                tdat = Vehicles.query.filter(Vehicles.Unit == dd.Unit).first()
                plate = tdat.Plate
                valticket = Interchange.query.filter( (Interchange.Date == thisdate) & (Interchange.TruckNumber == plate)).all()

                for val in valticket:
                    c.drawString(leftw1, top, f'{val.Date}')
                    c.drawString(leftw2, top, f'{val.Time}')
                    c.drawString(leftw3, top, f'{val.TruckNumber}')
                    c.drawString(leftw4, top, f'{val.Container}')
                    c.drawString(leftw5, top, f'{val.GrossWt}')
                    top = top - dl * .6

                    if top < n3:
                        c, page, top, pages = topcheck(fp, n2, dh, c, page, pages)
                        c.drawCentredString(mid, 535, f'HOS Validation Data For Driver ')
                        c.line(ltm, 550, rtm, 550)
                        c.line(ltm, 530, rtm, 530)
                        c.setFont('Helvetica', 10, leading=None)

            top = top - dl * .6
            leftw1 = ltm + 10
            leftw2 = ltm + 130
            leftw3 = ltm + 180
            leftw4 = ltm + 240
            c.drawString(leftw1, top, f'Toll Plaza Data')
            top = top - dl * .8
            c.drawString(leftw1, top, f'Date/Time')
            c.drawString(leftw2, top, f'Unit')
            c.drawString(leftw3, top, f'Plaza')
            c.drawString(leftw4, top, f'Amount')
            top = top - dl * .8

            for dd in reversed(tlogs):
                thisdate = dd.GPSin
                thisdate = thisdate.date()
                unit = dd.Unit
                print(thisdate,unit)
                tolldata = Tolls.query.filter((Tolls.Date == thisdate) & (Tolls.Unit == unit)).all()

                for toll in tolldata:
                    c.drawString(leftw1, top, f'{toll.Datetm}')
                    c.drawString(leftw2, top, f'{toll.Unit}')
                    c.drawString(leftw3, top, f'{toll.Plaza}')
                    c.drawString(leftw4, top, f'{toll.Amount}')
                    top = top - dl * .6

                    if top < n3:
                        c, page, top, pages = topcheck(fp, n2, dh, c, page, pages)
                        c.drawCentredString(mid, 535, f'HOS Validation Data For Driver ')
                        c.line(ltm, 550, rtm, 550)
                        c.line(ltm, 530, rtm, 530)
                        c.setFont('Helvetica', 10, leading=None)

        c.showPage()
        c.save()

        if len(pages)>1:
            pdfcommand=['pdfunite']
            for page in pages:
                pdfcommand.append(page)
            multioutput=addpath1(f'reports/multioutput'+'.pdf')
            pdfcommand.append(multioutput)
            tes=subprocess.check_output(pdfcommand)
        else:
            multioutput=' '

        return pages, multioutput

#Now lets print the report out
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import landscape
from reportlab.platypus import Image
from reportlab.lib.units import inch
import csv
import math
import datetime
from CCC_system_setup import myoslist, addpath1, addtxt, bankdata, scac, logoi, companydata, websites, addpath3
from page_merger import pagemerger,pagemergermp
import shutil
from utils import avg, parseline
from PyPDF2 import PdfFileReader, PdfFileWriter
import subprocess
from models import Vehicles, Interchange
import os

def reportmaker(type,ddata):

    file1=addpath1(f'reports/pagestart.pdf')
    file2=addpath1(f'reports/background.pdf')
    file3=addpath1(f'reports/headers.pdf')

    c=canvas.Canvas(file1, pagesize=letter)
    c.setLineWidth(1)
    c.drawImage(logoi, 185, 680, mask='auto')
    c.showPage()
    c.save()

    if type=='summary':
        file4 = addpath1(f'reports/summary.pdf')
        report_background(file2,'summary')
        report_headers(file3,'summary')
        report_contents(file4,ddata,'summary')
        docref=pagemerger([file1,file2,file3,file4])

    if type=='driverlist':
        file4 = addpath1(f'reports/driverlist.pdf')
        report_background(file2,'drivers')
        report_headers(file3,'drivers')
        report_contents(file4,ddata,'drivers')
        docref=pagemerger([file1,file2,file3,file4])

    if type=='trucklist':
        file4 = addpath1(f'reports/trucklist.pdf')
        report_background(file2,'trucks')
        report_headers(file3,'trucks')
        report_contents(file4,ddata,'trucks')
        docref=pagemerger([file1,file2,file3,file4])

    if type=='hos':
        file4 = addpath1(f'reports/hos.pdf')
        report_background(file2,'hos')
        report_headers(file3,'hos')
        pages,multioutput,valpdfs = report_contents(file4,ddata,'hos')

        if len(pages) > 1:
            docref=pagemergermp([file1,file2,file3,file4], pages, multioutput)
        return docref, valpdfs

    return docref




def report_background(file2,item):
    c = canvas.Canvas(file2, pagesize=letter)
    c.setLineWidth(1)
    ltm, rtm, bump, tb, ctrall, left_ctr, right_ctr, dl, dh, tdl, hls, m1, m2, m3, m4, m5, m6, m7, n1, n2, n3 = reportsettings(1)

    fulllinesat = [n3]

    q1 = ltm + 180
    q2 = rtm - 180
    sds3 = [q1, q2]

    # Date and JO boxes
    dateline = m1 + 8.2 * dl
    c.rect(rtm - 150, m1 + 7 * dl, 150, 2 * dl, stroke=1, fill=0)
    c.line(rtm - 150, dateline, rtm, dateline)
    c.line(rtm - 75, m1 + 7 * dl, rtm - 75, m1 + 9 * dl)

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
    today = datetime.datetime.today().strftime('%m/%d/%Y')
    invodate = datetime.date.today().strftime('%m/%d/%Y')
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
    c.drawCentredString(rtm - 112.5, dateline + bump, 'Created')
    c.drawCentredString(rtm - 37.7, dateline + bump, 'Type')

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
    c.drawCentredString(x, y, f'{item.upper()}')
    x = avg(rtm - 75, rtm - 150)
    c.drawCentredString(x, y, invodate)

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
    n3=hls-27*dl

    return ltm,rtm,bump,tb,ctrall,left_ctr,right_ctr,dl,dh,tdl,hls,m1,m2,m3,m4,m5,m6,m7,n1,n2,n3


def report_contents(file4,ddata,item):

    ltm,rtm,bump,tb,ctrall,left_ctr,right_ctr,dl,dh,tdl,hls,m1,m2,m3,m4,m5,m6,m7,n1,n2,n3=reportsettings(1)

    pages=[file4]
    page=1
    c=canvas.Canvas(file4, pagesize=letter)
    c.setLineWidth(1)

    #Main Items Listing
    c.setFont('Helvetica-Bold',14,leading=None)
    mid = int(ltm+rtm)/2
    if item == 'summary': c.drawCentredString(mid, 535, 'Introduction')
    if item == 'drivers': c.drawCentredString(mid,535,'Active Driver Data')
    if item == 'trucks': c.drawCentredString(mid,535,'Active DOT Truck Data')
    if item == 'hos': c.drawCentredString(mid,535, f'Hours of Service For Driver {ddata[0].DriverStart} Last 30 Drive Days')
    c.line(ltm, 550, rtm, 550)
    c.line(ltm, 530, rtm, 530)
    c.setFont('Helvetica', 10, leading=None)
    top = 510
    leftw1 = ltm+10
    leftw2 = ltm+110
    leftw3 = ltm+320
    leftw4 = ltm+490
    if item == 'summary':
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

                    if top<n3:
                        c.showPage()
                        c.save()
                        page=page+1
                        base=file4.replace('.pdf','')
                        newfile=base+'page'+str(page)+'.pdf'
                        top = n2-dh
                        c=canvas.Canvas(newfile, pagesize=letter)
                        pages.append(newfile)

    if item == 'drivers':
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

            if top<n3:
                c.showPage()
                c.save()
                page=page+1
                base=file4.replace('.pdf','')
                newfile=base+'page'+str(page)+'.pdf'
                top = n2-dh
                c=canvas.Canvas(newfile, pagesize=letter)
                pages.append(newfile)

    if item == 'trucks':
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

            if top < n3:
                c.showPage()
                c.save()
                page = page + 1
                base = file4.replace('.pdf', '')
                newfile = base + 'page' + str(page) + '.pdf'
                top = n2 - dh
                c = canvas.Canvas(newfile, pagesize=letter)
                pages.append(newfile)

    if item == 'hos':
        top = 530
        leftw1 = ltm + 10
        leftw2 = ltm + 170
        leftw3 = ltm + 220
        c.setFont('Helvetica', 10, leading=None)
        top = top - dl * .9
        valpdfs = []
        for dd in reversed(ddata):
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
                    if hrs > 12.0 and airmiles < 100:  exempt = 'Paper Log  **Shift hours exceed 12.0**'
                    if hrs < 12.0 and airmiles > 100:  exempt = 'Paper Log **Airmiles exceed 100.0**'
                    if hrs > 12.0 and airmiles > 100:  exempt = 'Paper Log  **Shift hours exceed 12.0 and Airmiles exceed 100.0**'
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
            c.drawString(leftw1, top, f'Duty Hours/Miles: {hrs} / {dd.Distance}')
            c.drawString(leftw2, top, f'Farthest Dist/Loc:{dd.Rdist} / {dd.Rloc}')
            top = top - dl * .7
            c.drawString(leftw1, top, f'Logging: {exempt}')
            top = top - dl* 1.2

            tdat = Vehicles.query.filter(Vehicles.Unit == dd.Unit).first()
            plate = tdat.Plate
            valticket = Interchange.query.filter( (Interchange.Date == thisdate) & (Interchange.TruckNumber == plate)).all()
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
            blendticks(placefile1,placefile2, blendfile)
            valpdfs.append(blendfile)

            if top < n3:
                c.showPage()
                c.save()
                page = page + 1
                base = file4.replace('.pdf', '')
                newfile = base + 'page' + str(page) + '.pdf'
                top = n2 - dh
                c = canvas.Canvas(newfile, pagesize=letter)
                c.drawCentredString(mid, 535, f'Hours of Service For Driver {dd.DriverStart} Last 30 Drive Days (cont.)')
                c.line(ltm, 550, rtm, 550)
                c.line(ltm, 530, rtm, 530)
                c.setFont('Helvetica', 10, leading=None)
                pages.append(newfile)



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
        multioutput=''

    if item == 'hos':
        return pages, multioutput, valpdfs
    else:
        return pages, multioutput

def pagemerger(filelist):

    lfs = len(filelist)-1
    print('lfs has value:', lfs)

    for j in range(lfs):

        if j == 0:
            firstfile = filelist[0]
        else:
            firstfile = addpath1(f'reports/temp'+str(j-1)+'.pdf')

        reader = PdfFileReader(open(firstfile, 'rb'))
        first_page = reader.getPage(0)

        sup_reader = PdfFileReader(open(filelist[j+1], 'rb'))
        sup_page = sup_reader.getPage(0)  # This is the first page, can pick any page of document

    #translated_page = PageObject.createBlankPage(None, sup_page.mediaBox.getWidth(), sup_page.mediaBox.getHeight())
    # translated_page.mergeScaledTranslatedPage(sup_page, 1, 0, 0)  # -400 is approximate mid-page
    # translated_page.mergePage(invoice_page)
        sup_page.mergePage(first_page)
        writer = PdfFileWriter()
    # writer.addPage(translated_page)
        writer.addPage(sup_page)

        if j == lfs-1:
            outfile = addpath1(f'reports/report'+'.pdf')
        else:
            outfile = addpath1(f'reports/temp'+str(j)+'.pdf')

        print('lfs and j are:', j, lfs)
        print('firstfile=', firstfile)
        print('supfile=', filelist[j+1])
        print('outfile=', outfile)

        with open(outfile, 'wb') as f:
            writer.write(f)

        f.close()

    docref = f'reports/report.pdf'

    return docref


def pagemergerx(filelist, page):

    lfs = len(filelist)-1
    print('lfs has value:', lfs)

    for j in range(lfs):

        if j == 0:
            firstfile = filelist[0]
        else:
            firstfile = addpath(f'reports/temp'+str(j-1)+'.pdf')

        reader = PdfFileReader(open(firstfile, 'rb'))
        first_page = reader.getPage(page)

        sup_reader = PdfFileReader(open(filelist[j+1], 'rb'))
        sup_page = sup_reader.getPage(0)  # This is the selected page, can pick any page of document

    #translated_page = PageObject.createBlankPage(None, sup_page.mediaBox.getWidth(), sup_page.mediaBox.getHeight())
    # translated_page.mergeScaledTranslatedPage(sup_page, 1, 0, 0)  # -400 is approximate mid-page
    # translated_page.mergePage(invoice_page)
        sup_page.mergePage(first_page)
        writer = PdfFileWriter()
    # writer.addPage(translated_page)
        writer.addPage(sup_page)

        if j == lfs-1:
            outfile = addpath(f'reports/report'+'.pdf')
        else:
            outfile = addpath(f'reports/temp'+str(j)+'.pdf')

        print('lfs and j are:', j, lfs)
        print('firstfile=', firstfile)
        print('supfile=', filelist[j+1])
        print('outfile=', outfile)

        with open(outfile, 'wb') as f:
            writer.write(f)

        f.close()

    docref = f'reports/report'+'.pdf'
    return docref


def pagemergermp(filelist, pages, multioutput):

    lfs = len(filelist)-1
    print('lfs has value:', lfs)

    for j in range(lfs):

        if j == 0:
            firstfile = filelist[0]
        else:
            firstfile = addpath1(f'reports/temp'+str(j-1)+'.pdf')

        reader = PdfFileReader(open(firstfile, 'rb'))
        first_page = reader.getPage(0)

        sup_reader = PdfFileReader(open(filelist[j+1], 'rb'))
        sup_page = sup_reader.getPage(0)  # This is the first page, can pick any page of document

    #translated_page = PageObject.createBlankPage(None, sup_page.mediaBox.getWidth(), sup_page.mediaBox.getHeight())
    # translated_page.mergeScaledTranslatedPage(sup_page, 1, 0, 0)  # -400 is approximate mid-page
    # translated_page.mergePage(invoice_page)
        sup_page.mergePage(first_page)
        writer = PdfFileWriter()
    # writer.addPage(translated_page)
        writer.addPage(sup_page)

        if j == lfs-1:
            outfile = addpath1(f'reports/reportx.pdf')
        else:
            outfile = addpath1(f'reports/temp'+str(j)+'.pdf')

        print('lfs and j are:', j, lfs)
        print('firstfile=', firstfile)
        print('supfile=', filelist[j+1])
        print('outfile=', outfile)

        with open(outfile, 'wb') as f:
            writer.write(f)

        f.close()

    # This gives us the merges backdrop pdf file on which we will place the contents.
    # Now place the mulitpage content on this file for each page and assemble
    newpages = []
    for j, page in enumerate(pages):
        print('outfilehere=', firstfile)
        reader = PdfFileReader(open(firstfile, 'rb'))
        first_page = reader.getPage(0)

        sup_reader = PdfFileReader(open(multioutput, 'rb'))
        sup_page = sup_reader.getPage(j)

        sup_page.mergePage(first_page)
        writer = PdfFileWriter()
        writer.addPage(sup_page)

        newoutfile = addpath1('reports/multipage'+str(j)+'.pdf')
        with open(newoutfile, 'wb') as f:
            writer.write(f)

        f.close()
        newpages.append(newoutfile)

    pdfcommand = ['pdfunite']
    for page in newpages:
        print('page is:',page)
        pdfcommand.append(page)
    newmultioutput = addpath1(f'reports/newmultioutput'+'.pdf')
    pdfcommand.append(newmultioutput)
    tes = subprocess.check_output(pdfcommand)

    docref = f'reports/report.pdf'
    shutil.copy(newmultioutput, addpath1(docref))

    return docref

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
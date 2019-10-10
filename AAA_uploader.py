import sys
import os
import shutil
import subprocess

from autofinder import autofind
from interchange_parse import interparse
from booking_parse import bookparse
import datetime
from PyPDF2 import PdfFileWriter, PdfFileReader
from scrapers import vinscraper

from CCC_system_setup import websites, addpath3, addpath4, mycompany

co = mycompany()
if co == 'FELA':
    from CCC_FELA_remote_db_connect import tunnel, db
    from CCC_FELA_models import Autos
elif co == 'OSLM':
    from CCC_OSLM_remote_db_connect import tunnel, db
    from CCC_OSLM_models import Autos

print('This run started at: ', datetime.datetime.now())
print(co, websites)

today = datetime.date.today()


def noblanklines(path, txtfile):
    txtlines = []
    with open(path+txtfile) as openfile:
        for line in openfile:
            if len(line) > 3:
                txtlines.append(line)
    fh = open(path+txtfile, 'w')
    fh.writelines(txtlines)
    fh.close()
    return


def checkpdf(s5s, inputf):
    base = os.path.splitext(inputf)[0]
    base = base.replace(' ', '').replace('-', '').replace('.', '')
    pdffile = base+'.pdf'
    txtfile = base+'.txt'
    if inputf != pdffile:
        shutil.move(s5s+inputf, s5s+pdffile)
    # print(inputf)
    # print(fout)
    if 1 == 1:  # try:
        ctest = subprocess.check_output(['pdftotext', s5s+pdffile, s5s+txtfile])
        with open(s5s+txtfile, "rb") as infile:
            size = os.path.getsize(infile.name)
            if size < 10:
                txtfile = 0
            else:
                noblanklines(s5s, txtfile)

    if 1 == 2:  # except:
        os.remove(s5s+txtfile)
        pdffile = 0
        txtfile = 0

    return pdffile, txtfile


def checkpdfscan(s5s, inputf):
    base = os.path.splitext(inputf)[0]
    base = base.replace(' ', '').replace('-', '').replace('.', '')
    txtfile = base+'.txt'
    tiffile = base+'.png'
    pdffile = base+'.pdf'
    pdffile_one = base+'1'+'.pdf'
    
    tcfile = base+'tc'+'.png'
    if inputf != pdffile:
        try:
            shutil.move(s5s+inputf, s5s+pdffile)
        except IOError:
            print('File ', s5s+inputf, ' already moved')

    if 1 == 1:
        # First select only the first page of the pdf file for scan interpretation:
        inputpdf = PdfFileReader(open(s5s+pdffile, "rb"))
        output = PdfFileWriter()
        output.addPage(inputpdf.getPage(0))
        with open(s5s+pdffile_one, "wb") as outputStream:
            output.write(outputStream)
            
        chgpdf = subprocess.check_output(['convert', '-trim', '-density', '300', s5s+pdffile_one,
                                          '-depth', '8', '-strip', '-background', 'white', '-alpha', 'off', s5s+tiffile])
        tc = subprocess.check_output(
            ['textcleaner', '-g', '-e', 'normalize', s5s+tiffile, s5s+tcfile])
        tout = subprocess.check_output(['tesseract', s5s+tcfile, s5s+base, 'quiet'])
        os.remove(s5s+tiffile)
        os.remove(s5s+tcfile)
        os.remove(s5s+pdffile_one)
        noblanklines(s5s, txtfile)
        return pdffile, txtfile
    if 1 == 2:  # except:
        os.remove(s5s+txtfile)
        pdffile = 0
        txtfile = 0
        return pdffile, txtfile


def checkscan(s5s, inputf):
    base = os.path.splitext(inputf)[0]
    extension = os.path.splitext(inputf)[1]
    base = base.replace(' ', '').replace('-', '').replace('.', '')
    newfile = base+extension
    txtfile = base+'.txt'
    tiffile = base+'.png'
    tcfile = base+'tc'+'.png'
    if inputf != newfile:
        shutil.move(s5s+inputf, s5s+newfile)

    if 1 == 1:  # try:
        chgpdf = subprocess.check_output(['convert', '-trim', '-density', '300', s5s+newfile,
                                          '-depth', '8', '-strip', '-background', 'white', '-alpha', 'off', s5s+tiffile])
        tc = subprocess.check_output(
            ['textcleaner', '-g', '-e', 'normalize', s5s+tiffile, s5s+tcfile])
        tout = subprocess.check_output(['tesseract', s5s+tcfile, s5s+base, 'quiet'])
        os.remove(s5s+tiffile)
        os.remove(s5s+tcfile)
        noblanklines(s5s, txtfile)
        return newfile, txtfile
    if 1 == 2:  # except:
        os.remove(s5s+txtfile)
        pdffile = 0
        txtfile = 0
        return inputf, txtfile


def filefix(s1):
    filelist = os.listdir(s1)
    for filename in filelist:
        if '.PDF' in filename:
            newname = filename.replace('.PDF', '.pdf')
            os.rename(s1+filename, s1+newname)
        if '.JPG' in filename:
            newname = filename.replace('.JPG', '.jpg')
            os.rename(s1+filename, s1+newname)
        if '.JPEG' in filename:
            newname = filename.replace('.JPEG', '.jpg')
            os.rename(s1+filename, s1+newname)
        if '.TXT' in filename:
            newname = filename.replace('.TXT', '.txt')
            os.rename(s1+filename, s1+newname)
        if '.jpeg' in filename:
            newname = filename.replace('.jpeg', '.jpg')
            os.rename(s1+filename, s1+newname)


folderlist = ['bills', 'pods', 'general', 'titles', 'dispatch',
              'interchange', 'tjobs', 'ojobs', 'bookings']

if 1 == 1:  # Keep this in case want to convert back to a looping script
    nfiles = 0
    processlist = []

    for folder in folderlist:
        i5s = addpath3(folder+'/')
        s5s = addpath4(folder+'/')
        filefix(i5s)
        filelist = os.listdir(i5s)
        print(folder,i5s,filelist)
        if filelist:
            for filename in filelist:
                nfiles += 1
                processlist.append(filename)
                shutil.move(i5s+filename, s5s+filename)

    print('Number of files processed:', nfiles)
    if nfiles > 0:

        for folder in folderlist:
            s5 = addpath4(folder)
            s5s = s5+'/'
            filelist = os.listdir(s5)
            for file in filelist:
                if file in processlist:  # this prevents thread intermingling
                    print('Working on pfile: ', file)
                    if file.endswith('.pdf'):
                        srcfile, txtfile = checkpdf(s5s, file)
                        print('pdf:', srcfile)
                        print('pdftxt', txtfile)

                        if txtfile == 0:
                            srcfile, txtfile = checkpdfscan(s5s, file)
                            print('Scannedpdf:', srcfile)
                            print('Scannedpdftext:', txtfile)

                    elif (file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png')):
                        srcfile, txtfile = checkscan(s5s, file)
                        print('Scannedjpg:', srcfile)
                        print('Scannedjpgtext:', txtfile)

                    error = 1
                    if folder == 'interchange' or folder == 'dispatch' or folder == 'bookings':
                        if folder == 'interchange':
                            error = interparse(s5s, txtfile, srcfile)
                            newfile = srcfile
                            newtxt = txtfile
                        elif folder == 'dispatch':
                            newfile, error = autofind(s5s, txtfile, srcfile)
                            newtxt = newfile.replace('.pdf', '.txt')
                        elif folder == 'bookings':
                            newfile, error = bookparse(s5s, txtfile)
                            newtxt = newfile.replace('.pdf', '.txt')

                        if error == 0:
                            shutil.move(s5s+srcfile, s5s+newfile)
                            shutil.move(s5s+txtfile, s5s+newtxt)
                            pythonline = websites['ssh_data'] + 'v' + folder
                            copyline1 = f'scp {s5s+newfile} {pythonline}'
                            print(copyline1)
                            os.system(copyline1)
                            copyline2 = 'scp '+s5s+newtxt+pythonline+folder
                            print(copyline2)
                            os.system(copyline2)
                            os.remove(s5s+newfile)
                            os.remove(s5s+newtxt)

                    else:
                        pythonline = websites['ssh_proc'] + folder
                        copyline1 = f'scp {s5s+srcfile} {pythonline}'
                        print(copyline1)
                        os.system(copyline1)
                        copyline2 = f'scp {s5s+txtfile} {pythonline}'
                        print(copyline2)
                        os.system(copyline2)
                        os.remove(s5s+srcfile)
                        os.remove(s5s+txtfile)

try:
    pythonline = websites['ssh_proc'] + 'vins.txt'
    copyline1 = f'scp {pythonline} {addpath4("vins.txt")}'
    print(copyline1)
    os.system(copyline1)

    print(websites['ssh_del_vins'])
    os.system(websites['ssh_del_vins'])
except:
    print('vins.txt not available at site')

try:
    longs = open(addpath4('vins.txt')).read()
    vlist = longs.split()
    print(longs,vlist)
except:
    vlist=[]

try:
    for vin in vlist:
        if len(vin)==18:
            vin=vin[1:18]
        if len(vin)==17:
            adat = Autos.query.filter(Autos.VIN == vin).first()
            if adat is None:

                year,make,model,wt,price,navg=vinscraper(vin)
                lvin=len(vin)
                vin5=vin[lvin-5:lvin]

                if year is not None:

                    print(vin, len(vin), year, make, model, wt, price, navg)
                    adat=Autos.query.filter(Autos.VIN==vin).first()
                    if adat is not None:
                        print('This VIN already in the system')
                        print('Adding Weight and Value updates:')
                        print(adat.id)
                        price=price.replace('$','')
                        adat.TowCompany='xxx'
                        adat.EmpWeight=str(wt)
                        adat.Value=str(price)
                        print(adat.Value)
                        adat.Ncars=1
                        db.session.commit()
                    else:
                        print('This VIN being added to the system')

                        towcost='TBD'
                        orderid='N'+vin5
                        towcompany='TBD'
                        ncars=1

                        price=price.replace('$','')

                        input= Autos(Jo=orderid,Hjo=None,Year=year,Make=make,Model=model,Color='',VIN=vin,Title='',State='',EmpWeight=wt,Dispatched=None,Value=price,TowCompany=towcompany,TowCost=towcost,TowCostEa=' ',Original=None,Status='New',Date1=today,Date2=today,Pufrom='',Delto='',Ncars=ncars,Orderid=orderid)


                        db.session.add(input)
                        db.session.commit()
            else:
                print(f'This vehicle {vin} already in database')
except:
    print('Failed to complete the mission')

try:
    os.remove(addpath4('vins.txt'))
except:
    print('vins.txt does not exist')


tunnel.stop()
sys.exit('Uploading completed...')

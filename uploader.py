from remote_db_connect import db, tunnel
import os
import shutil
import subprocess
from cronpaths import addpath1, addpath2
from autofinder import autofind
from interchange_parse import interparse
from booking_parse import bookparse
import datetime
from scrapers import vinscraper
from models2 import Autos

print('This run started at: ', datetime.datetime.now())

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
    tcfile = base+'tc'+'.png'
    if inputf != pdffile:
        try:
            shutil.move(s5s+inputf, s5s+pdffile)
        except IOError:
            print('File ', s5s+inputf, ' already moved')

    if 1 == 1:
        chgpdf = subprocess.check_output(['convert', '-trim', '-density', '300', s5s+pdffile,
                                          '-depth', '8', '-strip', '-background', 'white', '-alpha', 'off', s5s+tiffile])
        tc = subprocess.check_output(
            ['textcleaner', '-g', '-e', 'normalize', s5s+tiffile, s5s+tcfile])
        tout = subprocess.check_output(['tesseract', s5s+tcfile, s5s+base, 'quiet'])
        os.remove(s5s+tiffile)
        os.remove(s5s+tcfile)
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
        i5s = addpath1(folder+'/')
        s5s = addpath2(folder+'/')
        filefix(i5s)
        filelist = os.listdir(i5s)
        if filelist:
            for filename in filelist:
                nfiles += 1
                processlist.append(filename)
                shutil.move(i5s+filename, s5s+filename)

    print('Number of files processed:', nfiles)
    if nfiles > 0:

        for folder in folderlist:
            s5 = addpath2(folder)
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
                            pythonline = ' mnixon@ssh.pythonanywhere.com:/home/mnixon/felrun/tmp/data/v'
                            copyline1 = 'scp '+s5s+newfile+pythonline+folder
                            print(copyline1)
                            os.system(copyline1)
                            copyline2 = 'scp '+s5s+newtxt+pythonline+folder
                            print(copyline2)
                            os.system(copyline2)
                            os.remove(s5s+newfile)
                            os.remove(s5s+newtxt)

                    else:
                        pythonline = ' mnixon@ssh.pythonanywhere.com:/home/mnixon/felrun/tmp/processing/vins.txt'
                        copyline1 = 'scp '+s5s+srcfile+pythonline+folder
                        print(copyline1)
                        os.system(copyline1)
                        copyline2 = 'scp '+s5s+txtfile+pythonline+folder
                        print(copyline2)
                        os.system(copyline2)
                        os.remove(s5s+srcfile)
                        os.remove(s5s+txtfile)



pythonline = ' mnixon@ssh.pythonanywhere.com:/home/mnixon/felrun/tmp/processing/vins.txt'
#pythonline = '/home/mark/flask/felrun/tmp/processing/vins.txt'
copyline1 = 'scp '+pythonline+' /home/mark/flask/crontasks'
print(copyline1)
os.system(copyline1)

delline1 = 'ssh mnixon@ssh.pythonanywhere.com "rm /home/mnixon/felrun/tmp/processing/vins.txt" '
print(delline1)
os.system(delline1)

try:
    longs = open('vins.txt').read()
    vlist = longs.split()
except:
    vlist=[]

for vin in vlist:
    print('Running VIN:',vin)
    if len(vin)==18:
        vin=vin[1:18]
    if len(vin)==17:
        adat = Autos.query.filter(Autos.VIN == vin).first()
        if adat is None:
            #try:
            year,make,model,wt,price,navg=vinscraper(vin)

            #except:
                #print(vin,' is not a valid vin')

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
                    orderid='NYA'
                    towcompany='TBD'
                    ncars=1

                    price=price.replace('$','')
                    input= Autos(Jo=orderid,Hjo=None,Year=year,Make=make,Model=model,Color='',VIN=vin,Title='',State='',EmpWeight=wt,Dispatched=None,Value=price,TowCompany=towcompany,TowCost=towcost,TowCostEa=' ',Original=None,Status='New',Date1=today,Date2=today,Pufrom='',Delto='',Ncars=ncars,Orderid=orderid)
                    db.session.add(input)
                    db.session.commit()

try:
    os.remove('vins.txt')
except:
    print('vins.txt does not exist')


tunnel.stop()

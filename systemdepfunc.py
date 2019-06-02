
import os


def apathdef():
    # apath is path to the fel directory
    # apath = '/' #fserver
    # apath2 is path to bin locations where documents arrive (alldocs,bills,pods..etc)
    # apath2 = '/home/ftpuser/' #fserver

    apath = '/home/mark/flask/'  # Laptop
    # apath = '/home/mnixon/' #PythonAnywhere
    apath2 = '/home/mark/flask/'  # Laptop
    # apath2 = '/home/mnixon/' #PythonAnywhere
    return apath, apath2

# Define path to the fel based directories


def addpath(inpath):
    apath, apth2 = apathdef()
    wpath = apath+'felrun/'
    absolutepath = wpath+inpath
    return absolutepath

# Define path to the bin directories (alldocs, bills, ...etc)


def addpath2(inpath):
    apath, apath2 = apathdef()
    absolutepath = apath2+inpath
    return absolutepath


def myoslist(indir):
    apath, apath2 = apathdef()
    wpath = apath+'felrun/'
    fdata = [each for each in os.listdir(wpath+indir) if not each.endswith('.txt')]
    return fdata


def manfile(joborder, cache):
    apath, apath2 = apathdef()
    wpath = apath+'felrun/'
    file1 = wpath+'tmp/data/vmanifest/Manifest'+joborder+'.pdf'
    file2 = wpath+'tmp/data/vmanifest/Manifest'+joborder+'c'+str(cache)+'.pdf'
    return file1, file2


def addtxt(inpath):
    apath, apath2 = apathdef()
    wpath = apath+'felrun/'
    absolutepath = wpath+inpath
    basefile = os.path.splitext(absolutepath)[0]
    textfile = basefile+'.txt'
    return textfile


def emailvals():
    email1 = 'info@firsteaglelogistics.com'
    email2 = 'service@firsteaglelogistics.com'
    email3 = 'mnixon@firsteaglelogistics.com'
    email4 = 'info2@firsteaglelogistics.com'
    email5 = 'export@firsteaglelogistics.com'
    password1 = 'User1123!'
    password2 = 'Cash$320'
    ourserver = 'mail.az1-ss7.a2hosting.com:587'
    emails = [email1, email2, email3, email4, email5]
    passwds = [password1, password2]
    return emails, passwds, ourserver

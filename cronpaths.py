
import os


def apathdef():
    # apath is path to the cron working directory
    # apath2 is path to bins location where documents arrive  (alldocs,bills,pods..etc)
    # apath3 is path to bins where documents to on transfer to pythonanywhere

    # file in the apath2 bins on arrival are moved to the apath bins for work and manipulation
    # the final products are transferred to pythonanywhere

    apath1 = '/home/mark/incoming/'  # Ubuntu1700
    # apath2 = '/home/ftpuser/' #fserver
    apath2 = '/home/mark/flask/crontasks/incoming/'  # Ubuntu 1700
    # apath = '/fel/crontasks/' #fserver
    apath3 = '/home/mark/flask/crontasks/processing/'

    apath4 = '/home/mark/flask/crontasks/data/'

    return apath1, apath2, apath3, apath4

# Define path to the cron bins


def addpath1(inpath):
    a, b, c, d = apathdef()
    absolutepath = a+inpath
    return absolutepath

# Define path to the bin directories (alldocs, bills, ...etc)


def addpath2(inpath):
    a, b, c, d = apathdef()
    absolutepath = b+inpath
    return absolutepath

# Define path to the upload directories (processing)


def addpath3(inpath):
    a, b, c, d = apathdef()
    absolutepath = c+inpath
    return absolutepath


def addpath4(inpath):
    a, b, c, d = apathdef()
    absolutepath = d+inpath
    return absolutepath


def addtxt(inpath):
    basefile = os.path.splitext(inpath)[0]
    textfile = basefile+'.txt'
    return textfile

def hiddendata():
    email1 = 'onestoplogisticsco'

    password1 = 'OneUser1123!'

    ourserver = 'mail.az1-ss7.a2hosting.com:587'
    emails = [email1]
    passwds = [password1]
    return emails, passwds, ourserver

import sys


def mymachine():
    machine = 'ubuntu1700'
    # machine='ubuntu1'
    # machine='fserver'
    # machine='pythonanywhere'
    return machine


def emailvals():
    e0 = 'info@firsteaglelogistics.com'
    e1 = 'service@firsteaglelogistics.com'
    e2 = 'mnixon@firsteaglelogistics.com'
    e3 = 'info2@firsteaglelogistics.com'
    e4 = 'export@firsteaglelogistics.com'
    e5 = 'info@horizonmotors1.com'
    e6 = 'WASHMOVE'
    p0 = 'User1123!'
    p1 = 'User1123!'
    p2 = 'User1123!'
    p3 = 'User1123!'
    p4 = 'User1123!'
    p5 = 'User1123!'
    p6 = 'Wmius5445'
    ourserver = "mail.az1-ss7.a2hosting.com:587"
    emails = [e0, e1, e2, e3, e4, e5, e6]
    passwds = [p0, p1, p2, p3, p4, p5, p6]
    return emails, passwds, ourserver


def addpaths():
    machine = mymachine()
    if machine == 'ubuntu1700':
        path1 = '/home/mark/flask/felrun'
        path2 = '/home/mark/flask/crontasks'
        path3 = '/home/mark/.mozilla/firefox/4oe30x7l.selpro'  # firefox profile
    if machine == 'ubuntu1':
        path1 = '/home/mark/flask/felrun'
        path2 = '/home/mark/flask/crontasks'
        path3 = '/home/mark/.mozilla/firefox/4oe30x7l.selpro'  # firefox profile
    if machine == 'fserver':
        path1 = '/fel'    # on fserver
        path2 = '/crontasks'  # on fserver
        path3 = '/home/mark/.mozilla/firefox/5nz086pl.default-release'

    return path1, path2, path3


def addpath1(input):
    path1, path2, path3 = addpaths()
    thispath = path1+'/'+input
    return thispath


def addpath2(input):
    path1, path2, path3 = addpaths()
    thispath = path2+'/'+input
    return thispath


path1, path2, path3 = addpaths()
print(path3)
sys.path.append(path1)

import datetime

today = datetime.date.today()


def nodollar(infloat):
    outstr = "%0.2f" % infloat
    return outstr


def dollar(infloat):
    outstr = '$'+"%0.2f" % infloat
    return outstr


def avg(in1, in2):
    out = (in1+in2)/2
    return out


def stat_update(status, newval, i):
    a = list(status)
    a[i] = newval
    b = ''.join(a)
    return b


def nonone(input):
    if input is not None:
        output = int(input)
    else:
        output = 0
    return output


def d2s(instr):
    try:
        instr = instr.replace('$', '').replace(',', '')
    except:
        instr = str(instr)
    try:
        infloat = float(instr)
        outstr = "%0.2f" % infloat
    except:
        outstr = instr
    return outstr

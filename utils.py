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

def d1s(instr):
    try:
        instr = instr.replace('$', '').replace(',', '')
    except:
        instr = str(instr)
    try:
        infloat = float(instr)
        outstr = "%0.1f" % infloat
    except:
        outstr = instr
    return outstr

def avg(in1,in2):
    out=(in1+in2)/2
    return out

def commaguard(instring):
    sandwich=re.compile(r',[A-Za-z]')
    t1=sandwich.findall(instring)
    for t in t1:
        l=t[1]
        instring=instring.replace(t,', '+l)
    return instring

def parseline(line,j):
    splitline=line.split()
    outlines=[]
    newline=''
    for word in splitline:
        if len(newline)<j-7:
            newline=newline+word+' '
        else:
            outlines.append(newline)
            newline=word+' '
    outlines.append(newline)
    return outlines
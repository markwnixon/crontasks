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
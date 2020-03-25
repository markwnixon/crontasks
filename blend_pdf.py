from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
from PyPDF2.pdf import PageObject
from CCC_system_setup import addpath, addpath2, addtxt, scac

g1 =

def blendticks(g1,g2):
    cnum = g1.split('_')[0]
    if len(cnum) == 11:
        base = cnum
    else:
        base = 'blendtemp'

    gfile1 = addpath(f'tmp/{scac}/data/vinterchange/{g1}')
    print(gfile1)
    reader1 = PdfFileReader(open(gfile1, 'rb'))
    p1 = reader1.getPage(0)

    gfile2 = addpath(f'tmp/{scac}/data/vinterchange/{g2}')
    reader2 = PdfFileReader(open(gfile2, 'rb'))
    p2 = reader2.getPage(0)

    #offset_x = p2.mediaBox[2]
    offset_x = 500
    offset_y = 0

    # add second page to first one
    p2.mergeTranslatedPage(p1, offset_x, offset_y, expand=True)

    p2.cropBox.lowerLeft = (50,525)
    p2.cropBox.upperRight = (1050,800)

    outfile = addpath(f'tmp/{scac}/data/vinterchange/{base}_BLEND.pdf')
    with open(outfile, "wb") as out_f:
        writer3 = PdfFileWriter()
        writer3.addPage(p2)
        writer3.write(out_f)

    return outfile

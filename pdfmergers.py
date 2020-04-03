from PyPDF2 import PdfFileReader, PdfFileWriter
import subprocess
import shutil
from CCC_system_setup import addpath1

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
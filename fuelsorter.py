from CCC_system_setup import addpath4, websites, usernames, passwords, mycompany, addpaths
co = mycompany()
if co == 'FELA':
    from CCC_FELA_remote_db_connect import tunnel, db
    from CCC_FELA_models import Bills,People
elif co == 'OSLM':
    from CCC_OSLM_remote_db_connect import tunnel, db
    from CCC_OSLM_models import Bills, People


import datetime
import subprocess
import re
from PyPDF2 import PdfFileReader, PdfFileWriter
from viewfuncs import nodollar

date_y4=re.compile(r'\d{2}[/-]\d{1,2}[/-]\d{4}')
fuel_d4=re.compile(r'[a]\d{1,3}[.]\d{4}[a]')
fuel_d3=re.compile(r'[a]\d{1}[.]\d{3}[a]')
fuel_d2=re.compile(r'[a]\d{2,3}[.]\d{2}[a]')
money_d2=re.compile(r'\d{2,3}[.]\d{2}')
card_d1=re.compile(r'[a]\d{1}[a]')

def pdfburst(pdffile):
    pdf_file = open(testpdf,'rb')
    pdf_reader = PdfFileReader(pdf_file)
    pageNumbers = pdf_reader.getNumPages()
    for i in range (pageNumbers):
        pdf_writer = PdfFileWriter()
        pdf_writer.addPage(pdf_reader.getPage(i))
        split_motive = open(testbase + str(i+1) + '.pdf','wb')
        pdf_writer.write(split_motive)
        split_motive.close()
    pdf_file.close()

def getpattern(nline,input,plines):
    with open(input) as thisfile:
        for j,line in enumerate(thisfile):
            if j==nline:
                cvec=[]
                for s in range(plines):
                    newline=next(thisfile).strip()
                    if len(newline)==0:
                        cvec.append(0)
                    else:
                        cvec.append(1)
    return cvec

def getdata(nline,input,plines):
    with open(input) as thisfile:
        for j,line in enumerate(thisfile):
            if j==nline:
                data=[]
                for s in range(plines):
                    newline=next(thisfile).strip()
                    data.append(newline)
    return data



def fuelsort(thisdate,testpdf,nbill):
    s=addpath4('emaildocs/msfleet/')
    #for file in os.listdir(s):
    if 1==1:
        #fname=thisfile.replace('.pdf','')
        testbase=testpdf.replace('.pdf','')
        filebase=testbase.split('msfleet/',1)[1]
        filebase=filebase+'.pdf'
        #testpdf=testbase+'.pdf'
        testtxt=testbase+'.txt'

        avgprice='off'
        totqty='off'

        #tj=subprocess.check_output(['pdf2txt.py', '-o', testtxt, testpdf])
        ctest = subprocess.check_output(['pdftotext', testpdf, testtxt])


        np=0
        np2=0
        gettotal=0
        getinfo=0
        fuelqty=[]
        ppg=[]
        isocards=[]
        cardtrigger='off'
        totaltrigger='off'
        fueltrigger='on'

        with open(testtxt) as openfile:
            for line in openfile:
                nl=line.strip()
                nla='a'+nl+'a'

                if 'MS Local Card' in line and 'Current Purchases' in line:
                    npurchases=line.split('Current',1)[0]
                    npurchases=npurchases.split('Card',1)[1]
                    npurchases=npurchases.strip()
                    np=int(npurchases)

                #Define Triggers for Sequential Assumptioning:

                if 'Dyed Bio' in line:
                    print('Potential Problem with extra Dyed Bio Purchase')

                if 'Card' in line:
                    cardtrigger='on'

                if 'Total Amount' in line:
                    totaltrigger='on'

                if totaltrigger=='on':
                    tottry=money_d2.findall(nla)
                    if tottry:
                        tottry=nl
                        tottry=tottry.replace(',','')
                        total=float(tottry)
                        if total>1.0:
                            amount=total
                            #print('fuelamt=',amount)


                #Perform if Triggers applied:

                if cardtrigger=='on':
                    cardtry=card_d1.findall(nla)
                    if len(isocards)<np and cardtry:
                        cardtry=nl
                        ctest=int(cardtry)
                        if ctest>0 and ctest<9:
                            isocards.append(cardtry)

                if fueltrigger=='on':
                    if nl=='Fuel':
                        nextline=next(openfile).strip()
                        if nextline=='Quantity':
                            totqty='on'

                    if nl=='Avg.':
                        nextline=next(openfile).strip()
                        if nextline=='Fuel':
                            avgprice='on'
                        #print(nl)
                    if len(nl)>0:
                        fueltry=fuel_d4.findall(nla)
                        if len(fuelqty)<np and fueltry:
                            fueltry=nl
                            ftest=float(fueltry)
                            if ftest>1.0:
                                if totqty=='off':
                                    fuelqty.append(fueltry)
                                else:
                                    totqty='off'

                        ppgtry=fuel_d3.findall(nla)
                        if len(ppg)<np and ppgtry:
                            ppgtry=nl
                            ppgf=float(ppgtry)
                            if ppgf>1.0:
                                if avgprice=='off':
                                    ppg.append(ppgtry)
                                else:
                                    avgprice='off'
                                    #print('ppg=',ppgtry)


            w=14
            header=[]
            cards=[]
            dates=[]
            with open(testtxt) as openfile:
                for line in openfile:

                    if 'Transaction Count:' in line:
                        npurchases=line.split('Count:',1)[1]
                        npurchases=npurchases.strip()
                        np2=int(npurchases)
                        #print('Number Purchases:',np2)

                    if 'Page' in line and np2>0:
                        nl=next(openfile)
                        for j in range(w):
                            nl=next(openfile).strip()
                            nln=next(openfile).strip()
                            if len(nln)<1:
                                header.append(nl)
                            else:
                                header.append(nl+' '+nln)
                                waste=next(openfile).strip()
                                #print('w',waste)
                        k=0
                        #print(header)
                        while len(cards)<np2 and k<50:
                            nl=next(openfile).strip()
                            #print(nl)
                            if len(nl)>0:
                                cards.append(nl)
                            k=k+1
                        #print(cards)

                        k=0
                        while len(dates)<np2 and k<70:
                            try:
                                nl=next(openfile).strip()
                                #print(nl)
                                if len(nl)>0:
                                    datetry=date_y4.findall(nl)
                                    if datetry:
                                        datetry=datetry[0]
                                        dates.append(datetry)
                            except:
                                print('Could not find all dates')
                            k=k+1






            print('BillNo=',nbill)
            print('Number of Purchases is:',np,np2)
            print('Total Amount is:',amount)
            print('Cards=',cards)
            print('Isocards=',isocards)
            print('Dates=',dates)
            print('FuelQty=',fuelqty)
            print('PPG=',ppg)
            amtnew=[]
            for j in range(np2):
                q=float(fuelqty[j])
                p=float(ppg[j])
                p=p+.009
                a=p*q
                amtnew.append(nodollar(a))

            print(amtnew)

            try:
                patternlines=np2*4
                patternvec=[1,1,1,0]*np
                with open(testtxt) as openfile:
                    for k,line in enumerate(openfile):
                        cvec=getpattern(k,testtxt,patternlines)
                        #print(cvec)
                        if cvec==patternvec:
                            print('They match at k=',k)
                            addresses=getdata(k,testtxt,patternlines)
                            print(addresses)
                            break
            except:
                print('Out of file lines')
                addresses = ''

            #os.remove(testpdf)
            #os.remove(testtxt)

            print('Example Database Entries')
            print('FELBill Entered for Total Fuel This Week')
            print('     Date:',thisdate)
            print('     Amount:',amount)
            print(' ')
            billno='fleet'+str(nbill)
            company='MSFleet'
            pdat=People.query.filter(People.Company==company).first()
            aid=pdat.id
            sdate=datetime.datetime.strptime(thisdate, '%Y-%m-%d').date()
            input = Bills(Jo='FT11', Pid=aid, Company=company, Memo='Weekly Fuel Bill', Description='Weekly Fuel Bill '+thisdate, bAmount=amount, Status='Paid', Cache=0, Original=filebase,
                             Ref='', bDate=sdate, pDate=sdate, pAmount=amount, pMulti=None, pAccount='FEL CitiBank', bAccount = 'Fuel', bType='Expense',
                             bCat='Direct', bSubcat='Trucking', Link=billno, User='mark', Co='F', Temp1='', Temp2='', Recurring=0, dDate=sdate,pAmount2='0.00', pDate2=None)


            db.session.add(input)
            db.session.commit()
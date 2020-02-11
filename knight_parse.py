from CCC_system_setup import scac
from remote_db_connect import db
from models import Orders, JO, People
import datetime
import re
from cronfuncs import dropupdate

def knight_parse(txtfile):
    longs = open(txtfile).read()


    #Using new format here the left item is what we are looking for (keyword) and right side is the Label
    hitems=['Order:Order', 'BOL:BOL', 'Booking:Booking', 'Pick Up:Pickup', 'Delivery:Delivery']

    # These items we look to see if there are load and delivery points to add to database
    vadditems=['Load At:Load at', 'Deliver To:Deliver to']

    today = datetime.datetime.today()
    year= str(today.year)
    day=str(today.day)
    month=str(today.month)
    #print(month,day,year)
    datestr='label:'+month+'/'+day+'/'+year

    pyr=year[2]+year[3]
    date_p1=re.compile(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December)\s?\d{1,2},?\s?\d{4}')
    date_y2=re.compile(r'\d{1,2}[/-]\d{1,2}[/-]\d{2}')
    date_y4=re.compile(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}')
    date_p3=re.compile(r'\d{1,2}\s?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s?\d{4}')
    date_p4=re.compile(r'\s'+pyr+'(?:0[1-9]|1[012])(?:0[1-9]|[12][0-9]|3[01])')
    time_p24=re.compile(r'(?:[1-9]|0[0-9]|1[0-9]|2[01234])[:](?:0[0-9]|[12345][0-9])')
    container_p = re.compile(r'[A-Z,a-z]{4}\s?[Ool0123456789]{7}')
    amount_p = re.compile(r'\$(?:[0-9]|[0-9]{2}|[0-9]{3}|[1-9],[0-9]{3})\.[0-9]{2}')

    orderdata = []
    fcount=0
    if 1 == 1:
        if 2 == 2:
            mysetlist={'Load':''}
            #print(file2,base,load)

            #add some default values here for database:
            mysetlist.update({'Status':'A0'})
            mysetlist.update({'Description':'Load Broker Line Haul'})
            mysetlist.update({'Chassis': 'NFO'})
            mysetlist.update({'Detention': 0})
            mysetlist.update({'Storage': 0})
            mysetlist.update({'Release': 0})
            mysetlist.update({'Container': 'NFO'})
            mysetlist.update({'BOL': 'NFO'})
            mysetlist.update({'Driver': 'NFO'})
            mysetlist.update({'Company2': 'NFO'})
            mysetlist.update({'Seal': 'NFO'})
            mysetlist.update({'Shipper': 'Knight Logistics LLC'})
            mysetlist.update({'Type': 'NFO'})
            mysetlist.update({'Order': '000000'})

            companyfound=''
            locationfound=''
            # Find and add load and delivery points to database
            for item in vadditems:
                subitem = item.split(':',1)[1]
                item = item.split(':',1)[0]
                label=item
                with open(txtfile) as openfile:
                    for line in openfile:
                        if re.search(item, line, re.IGNORECASE) or re.search(subitem, line, re.IGNORECASE):
                            if re.search(item, line, re.IGNORECASE):
                                test=item
                            else:
                                test=subitem

                            rest=line.lower().split(test.lower(),1)[0]
                            line1=line
                            line2=next(openfile)
                            line3=next(openfile)
                            line4=next(openfile)

                            l1=len(rest)

                            st=max(0,l1-15)
                            en=st+40
                            capture1=line2[st:en]
                            capture2=line3[st:en]
                            capture3=line4[st:en]

                            capture1=capture1.strip()
                            capture2=capture2.strip()
                            capture3=capture3.strip()
                            capture4=capture3.split(' ',1)[0]
                            capture4=capture4.replace(',','')
                            capture4=capture4.strip()

                            #print(capture1)
                            #print(capture2)
                            #print(capture3)
                            #print(capture4)
                            if 'load' in line1.lower():
                                type='Load'
                            if 'deliver' in line1.lower():
                                type='Deliver'

                            #print(type)
                            # Update Database
                            company1=dropupdate(capture1+'\n'+capture2+'\n'+capture3+'\n'+capture4)
                            if 'load' in line1.lower():
                                mysetlist.update({'Company' : company1})

                            if 'deliver' in line1.lower():
                                mysetlist.update({'Company2' : company1})

            date=None
            date2=None
            time=None
            time2=None
            time3=None
            with open(txtfile) as openfile:
                for line in openfile:
                    if 'earliest' in line.lower() and not date:

                        datep=date_y2.findall(line)
                        if datep:
                            date=datetime.datetime.strptime(datep[0], '%m/%d/%y').strftime('%Y/%m/%d')

                        datep=date_y4.findall(line)
                        if datep:
                            date=datetime.datetime.strptime(datep[0], '%m/%d/%Y').strftime('%Y/%m/%d')

                        time=time_p24.findall(line)
                        if time:
                            time=time[0]
                        else:
                            time=None
                        #print(line)
                        #print(date)
                        #print(time)

                        mysetlist.update({'Date' : date})
                        mysetlist.update({'Time' : time})
                        date_p2=re.compile(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}')
                    if 'earliest' in line.lower() and not date2:
                        datep=date_y2.findall(line)
                        if datep:
                            date2=datetime.datetime.strptime(datep[0], '%m/%d/%y').strftime('%Y/%m/%d')
                        datep=date_y4.findall(line)
                        if datep:
                            date2=datetime.datetime.strptime(datep[0], '%m/%d/%Y').strftime('%Y/%m/%d')
                        time2=time_p24.findall(line)
                        if time2:
                            time2=time2[0]
                        else:
                            time2=None
                        mysetlist.update({'Date2' : date2})
                        mysetlist.update({'Time2' : time2})
                        mysetlist.update({'Time3' : time3})

                    container=container_p.findall(line)

                    if container:
                        mysetlist.update({'Container' : container[0]})

            for item in hitems:
                list=[]
                label = item.split(':',1)[1]
                item  = item.split(':',1)[0]
                with open(txtfile) as openfile:
                    for line in openfile:
                        if item.lower() in line.lower():
                            rest=line.lower().split(item.lower(),1)[1]
                            rest=line[-len(rest):]

                            if ':' in rest:
                                rest=rest.split(':',1)[1]
                            elif '#' in rest:
                                rest=rest.split('#',1)[1]
                            elif 'NUMBER' in rest:
                                rest=rest.split('NUMBER',1)[1]


                            rest=rest.replace('#', '')
                            rest=rest.replace(':', '')
                            rest=rest.replace('-', '')
                            rest=rest.strip()

                            #Could have multiple space inside words which we do not want to store in database:
                            pieces=rest.split()
                            phrase=''
                            for piece in pieces:
                                piece=piece.strip()
                                phrase=phrase + ' ' + piece
                            rest=phrase.strip()

                            #print('item=',item,'rest=',rest,'line=',line)

                            lofrest=len(rest)
                            if lofrest > 0:
                                numbers = sum(c.isdigit() for c in rest)
                                keyratio = float(numbers)/float(lofrest)
                            else:
                                keyratio = 0.0

                            if keyratio > .4:
                                list.append(rest)
                if len(list)>0:
                        best=max(list,key=list.count)
                else:
                    best=None

                mysetlist.update({label : best})
                print('This is what I got on each iteration', list)

            #Looking for amount in whole file:
            amount=amount_p.findall(longs)
            if amount:
                amount = [w.replace('$','') for w in amount]
                amount = [w.replace(',','') for w in amount]
                amt=[float(i) for i in amount]
                newamount="{:.2f}".format(max(amt))
                mysetlist.update({'Amount': newamount})

            #Little cheat, the future name of the document after signing
            #Need it here to save in database
            order=mysetlist["Order"]
            print(mysetlist)
            print(order)
            forig='Order' + order + '.pdf'

           # fsig='load'+load+'_order' + mysetlist["Order"] + '_sig.pdf'
           # mysetlist.update({'Orders_Signed': fsig})

            orderdata.append(mysetlist)

            print('File ',fcount,flush=True)
            print(mysetlist)


    if 1==1:
        # Get the next Job Order number
        print('Now entering the parsed data into database...',flush=True)
        lv=JO.query.get(1)
        nextid=lv.nextid
        eval=str(nextid%100).zfill(2)
        day2="{0:0=2d}".format(int(day))
        if month=='10':
            month='X'
        if month=='11':
            month='Y'
        if month=='12':
            month='Z'
        # The type and company can be changed depending on who is calling
        jtype='T'
        jcompany=scac[0]
        nextjo=jcompany+jtype+month+day2+year[3]+eval
        #print(nextjo, today)


        for index in range(len(orderdata)):
            obj=orderdata[index]
            Order=obj.get("Order")
            Order=Order.strip()
            tDate=obj.get("Date")
            #print('tDate=',tDate)
            if tDate is not None and tDate != '':
                Date=datetime.datetime.strptime(tDate, '%Y/%m/%d')
            else:
                Date=today
            tDate=obj.get("Date2")
            if tDate is not None and tDate != '':
                Date2=datetime.datetime.strptime(tDate, '%Y/%m/%d')
            else:
                Date2=today

            loadcompany=obj.get("Company")
            pdata=People.query.filter(People.Company==loadcompany).first()
            if pdata is None:
                lid=None
            else:
                lid=pdata.id

            delivercompany=obj.get("Company2")
            pdata=People.query.filter(People.Company==delivercompany).first()
            if pdata is None:
                did=None
            else:
                did=pdata.id

            # Check to see if this order file is in database already:
            odata = Orders.query.filter(Orders.Order == Order).first()
            if odata is None:
                input = Orders(Status=obj.get("Status"), Jo=nextjo, Load=obj.get("Load"),Order=obj.get("Order"),  Company=obj.get("Company"),
                                Location=obj.get("Location"),Booking=obj.get("Booking"), BOL=obj.get("BOL"),Container=obj.get("Container"),
                                Date=Date,Driver=obj.get("Driver"),Company2=obj.get("Company2"), Time=obj.get("Time"), Date2=Date2,
                                Time2=obj.get("Time2"), Seal=obj.get("Seal"), Pickup=obj.get("Pickup"), Delivery=obj.get("Delivery"),
                                Amount=obj.get('Amount'), Path=None, Original=obj.get('Original'), Description=obj.get("Description"),
                                Chassis=obj.get('Chassis'), Detention=obj.get('Detention'), Storage=obj.get('Storage'), Release=obj.get('Release'),
                                Shipper=obj.get('Shipper'), Type=obj.get('Type'), Time3=None, Bid=None, Lid=lid, Did=did, Label='', Dropblock1='',Dropblock2='',
                                Commodity=None, Packing=None,Links = None, Hstat=-1,Istat=0,Proof=None,Invoice=None,Gate=None,Package=None,Manifest=None,
                                Pcache=None,Icache=None,Mcache=None,Pkcache=None,QBi=None)



                print ('Data part ', index+1, ' of ', len(orderdata), 'is being added to database: Orders')
                db.session.add(input)

                input2 = JO(jo=nextjo, nextid=0, date=today, status=1)
                db.session.add(input2)
                nextid=nextid+1
                lv.nextid=nextid
                eval=str(nextid%100).zfill(2)
                nextjo=jcompany+jtype+month+day2+year[3]+eval
            else:

                # The order already exists so we merge the new with the old if have no values
                print ('The data for dataset ', index+1, ' of ', len(orderdata), 'is already in the database: table Orders has been updated')
                odata.Date=Date
                odata.Time=obj.get("Time")
                odata.Date2=Date2
                odata.Time2=obj.get("Time2")
                odata.Original=obj.get('Original')
                if odata.Pickup=='NFO' or odata.Pickup=='None' or odata.Pickup is None:
                    odata.Pickup=obj.get("Pickup")
                if odata.Location=='NFO':
                    odata.Location=Location
                if odata.Company=='NFO':
                    odata.Company=obj.get("Company")
                if odata.Driver=='NFO':
                    odata.Driver=obj.get("Driver")
                if odata.Booking=='NFO' or odata.Booking=='None' or odata.Booking is None:
                    odata.Booking=obj.get("Booking")
                if odata.BOL=='NFO':
                    odata.BOL=obj.get("BOL")
                if odata.Container=='NFO' or odata.Container=='None' or odata.Container is None:
                    odata.Container=obj.get("Container")
                if odata.Delivery=='NFO':
                    odata.Delivery=obj.get("Delivery")
                odata.Amount=obj.get('Amount')
                if odata.Company2=='NFO':
                    odata.Company2=obj.get('Company2')
                if odata.Seal=='NFO':
                    odata.Seal=obj.get('Seal')
                if odata.Shipper=='NFO':
                    odata.Shipper=obj.get('Shipper')
                if odata.Type=='NFO':
                    odata.Type=obj.get('Type')

            db.session.commit()

    print('Total # pdf files found: ', fcount)

    return forig
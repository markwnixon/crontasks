from remote_db_connect import db

class users(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    username = db.Column(db.String(30))
    password = db.Column(db.String(100))
    register_date = db.Column(db.DateTime)

class feltask(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    task = db.Column(db.String(100))
    register_date = db.Column(db.DateTime)
    creator=db.Column(db.String(30))
    due_date = db.Column(db.DateTime)
    comments = db.Column(db.String(100))
    status = db.Column(db.Boolean)

class hortask(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    task = db.Column(db.String(100))
    register_date = db.Column(db.DateTime)
    creator=db.Column(db.String(30))
    due_date = db.Column(db.DateTime)
    comments = db.Column(db.String(100))
    status = db.Column(db.Boolean)

class ChalkBoard(db.Model):
    __tablename__ = 'chalkboard'
    id = db.Column('id',db.Integer,primary_key=True)
    Jo = db.Column('Jo',db.String(25))
    register_date = db.Column(db.DateTime)
    creator=db.Column('creator',db.String(30))
    comments = db.Column('comments',db.String(400))
    def __init__(self, Jo, register_date,creator,comments):
        self.Jo=Jo
        self.register_date=register_date
        self.creator=creator
        self.comments=comments
                
class General(db.Model):
    __tablename__ = 'general'
    id = db.Column('id',db.Integer,primary_key=True)
    Subject = db.Column('Subject', db.String(50))
    Category=db.Column('Category', db.String(50))
    Textinfo=db.Column('Textinfo', db.String(25))
    Path = db.Column('Path', db.String(25))
    
    def __init__(self,Subject,Category,Textinfo,Path):
        self.Subject=Subject
        self.Category=Category
        self.Textinfo=Textinfo
        self.Path=Path

class TruckJobs(db.Model):
    __tablename__ = 'truckjobs'
    id = db.Column('id',db.Integer,primary_key=True)
    Jo = db.Column('Jo', db.String(25))
    Driver=db.Column('Driver', db.String(25))
    Truck=db.Column('Truck', db.String(25))
    Booking = db.Column('Booking', db.String(25))
    Miles = db.Column('Miles', db.String(25))
    Cost = db.Column('Cost', db.String(25))
    Container = db.Column('Container', db.String(25))
    Seal = db.Column('Seal', db.String(25))
    Description = db.Column('Description', db.String(400))
    StartTime = db.Column('StartTime', db.DateTime)
    EndTime = db.Column('EndTime', db.DateTime)
    Origin = db.Column('Origin', db.String(25))
    Destination = db.Column('Destination', db.String(25))
    Comm = db.Column('Comm', db.Boolean)

    def __init__(self, Jo, Driver, Truck, Booking, Miles, Cost, Container, Seal, Description, StartTime, EndTime, Origin, Destination, Comm):
        self.Jo=Jo
        self.Driver=Driver
        self.Truck=Truck
        self.Booking=Booking
        self.Miles=Miles
        self.Cost=Cost
        self.Container=Container
        self.Seal=Seal
        self.Description=Description
        self.StartTime=StartTime
        self.EndTime=EndTime
        self.Origin=Origin
        self.Destination=Destination
        self.Comm=Comm
        
class Interchange(db.Model):
    __tablename__ = 'interchange'
    id = db.Column('id',db.Integer,primary_key=True)
    CONTAINER = db.Column('CONTAINER', db.String(25))
    TRUCK_NUMBER = db.Column('TRUCK NUMBER', db.String(25))
    DRIVER = db.Column('DRIVER', db.String(25))
    CHASSIS = db.Column('CHASSIS', db.String(25))
    Date = db.Column('Date', db.DateTime)
    RELEASE = db.Column('RELEASE', db.String(25))
    GROSS_WT= db.Column('GROSS WT', db.String(25))
    SEALS = db.Column('SEALS', db.String(25))
    CONTYPE = db.Column('SCALE WT', db.String(25))
    CARGO_WT = db.Column('CARGO WT', db.String(25))
    Time = db.Column('Time', db.String(25))
    Status = db.Column('Status', db.String(25))
    Original = db.Column('Original', db.String(50))
    Path = db.Column('Path', db.String(50))
    TYPE = db.Column('TYPE', db.String(25))
    Jo = db.Column('Jo', db.String(25))
    Company = db.Column('Company', db.String(25))

    def __init__(self, CONTAINER,TRUCK_NUMBER,DRIVER,CHASSIS,Date,RELEASE,GROSS_WT,SEALS,CONTYPE,CARGO_WT,Time,Status,Original,Path,TYPE,Jo,Company):
        self.CONTAINER=CONTAINER
        self.TRUCK_NUMBER=TRUCK_NUMBER
        self.DRIVER=DRIVER
        self.CHASSIS=CHASSIS
        self.Date=Date
        self.RELEASE=RELEASE
        self.GROSS_WT=GROSS_WT
        self.SEALS=SEALS
        self.CONTYPE=CONTYPE
        self.CARGO_WT=CARGO_WT
        self.Time=Time
        self.Status=Status
        self.Original=Original
        self.Path=Path
        self.TYPE=TYPE
        self.Jo=Jo
        self.Company=Company

class Proofs(db.Model):
    __tablename__ = 'proofs'
    id = db.Column('id',db.Integer,primary_key=True)
    Status = db.Column('Status', db.String(50))
    Original = db.Column('Original', db.String(50))
    Path = db.Column('Path', db.String(50))
    Company = db.Column('Company', db.String(50))
    Location = db.Column('Location', db.String(50))
    Booking= db.Column('Booking', db.String(50))
    Order= db.Column('Order', db.String(50))
    BOL = db.Column('BOL', db.String(50))
    Container = db.Column('Container', db.String(50))
    Driver = db.Column('Driver', db.String(25))
    Date = db.Column('Date', db.DateTime)
    Time = db.Column('Time', db.DateTime)

    def __init__(self, Status, Original, Path, Company, Location, Booking, Order, BOL, Container, Driver, Date, Time):
        self.Status=Status
        self.Original=Original
        self.Path=Path
        self.Company=Company
        self.Location=Location
        self.Booking=Booking
        self.Order=Order
        self.BOL=BOL
        self.Container=Container
        self.Driver=Driver
        self.Date=Date
        self.Time = Time

            
class Orders(db.Model):
    __tablename__ = 'orders'
    id = db.Column('id',db.Integer,primary_key=True)
    Status = db.Column('Status', db.String(50))
    Jo = db.Column('JO', db.String(25))
    Load = db.Column('Load', db.String(50))
    Order = db.Column('Order', db.String(50))
    Bid=db.Column('Bid', db.Integer)
    Lid=db.Column('Lid', db.Integer)
    Did=db.Column('Did', db.Integer)    
    Company = db.Column('Company', db.String(50))
    Location = db.Column('Location', db.String(99))
    BOL = db.Column('BOL', db.String(50))
    Booking= db.Column('Booking', db.String(50))
    Container = db.Column('Container', db.String(50))
    Driver = db.Column('Driver', db.String(50))        
    Pickup = db.Column('Pickup', db.String(50))
    Delivery = db.Column('Delivery', db.String(50))
    Amount = db.Column('Amount', db.String(50))
    Date = db.Column('Date', db.DateTime)
    Time = db.Column('Time', db.String(20))
    Date2 = db.Column('Date2', db.DateTime)
    Time2 = db.Column('Time2', db.String(20))
    Time3 = db.Column('Time3', db.String(20))
    Path = db.Column('Path', db.String(50))
    Original = db.Column('Original', db.String(99))
    Description = db.Column('Description', db.String(400))
    Chassis = db.Column('Chassis', db.String(50))
    Detention = db.Column('Detention', db.Integer)
    Storage = db.Column('Storage', db.Integer)
    Release = db.Column('Release',db.Boolean)
    Company2 = db.Column('Company2', db.String(50))   
    Seal = db.Column('Seal', db.String(50))
    Shipper = db.Column('Shipper', db.String(50))
    Type = db.Column('Type', db.String(50))
    Label = db.Column('Label', db.String(99))
    Dropblock1 = db.Column('Dropblock1', db.String(500))
    Dropblock2 = db.Column('Dropblock2', db.String(500))

    def __init__(self, Status, Jo, Load, Order, Company, Location, BOL, Booking, Container, Driver, Pickup,
                    Delivery, Amount, Date, Time, Date2, Time2, Time3, Path, Original, Description, Chassis,
                    Detention, Storage, Release, Company2, Seal, Shipper, Type, Bid, Lid, Did, Label, Dropblock1, Dropblock2):
        self.Status=Status
        self.Jo=Jo
        self.Load=Load
        self.Order=Order
        self.Company=Company
        self.Location=Location
        self.BOL=BOL
        self.Booking=Booking
        self.Container=Container
        self.Driver=Driver
        self.Pickup= Pickup
        self.Delivery= Delivery
        self.Amount= Amount
        self.Date= Date
        self.Time = Time
        self.Date2= Date2
        self.Time2 = Time2
        self.Path = Path
        self.Original = Original
        self.Description = Description
        self.Chassis=Chassis
        self.Detention=Detention
        self.Storage=Storage
        self.Release=Release
        self.Company2=Company2
        self.Seal=Seal
        self.Shipper=Shipper
        self.Type=Type
        self.Bid=Bid
        self.Lid=Lid
        self.Did=Did
        self.Label=Label
        self.Dropblock1=Dropblock1
        self.Dropblock2=Dropblock2
        
class Drops(db.Model):
    __tablename__ = 'drops'
    id = db.Column('id',db.Integer,primary_key=True)
    Entity = db.Column('Entity',db.String(50))
    Addr1 = db.Column('Addr1',db.String(50))
    Addr2 = db.Column('Addr2',db.String(50))
    Phone = db.Column('Phone',db.String(50))
    Email = db.Column('Email',db.String(50))
    
    def __init__(self, Entity,Addr1,Addr2,Phone,Email):
        self.Entity=Entity
        self.Addr1=Addr1
        self.Addr2=Addr2
        self.Phone=Phone
        self.Email=Email
        
        
class Moving(db.Model):
    __tablename__ = 'moving'
    id = db.Column('id',db.Integer,primary_key=True)
    Status = db.Column('Status', db.String(50))
    Jo = db.Column('JO', db.String(25))
    Order = db.Column('Order', db.String(50))   
    Dropblock1 = db.Column('Dropblock1', db.String(500))
    Drop1 = db.Column('Drop1', db.String(50))
    Dropblock2 = db.Column('Dropblock2', db.String(500))
    Drop2 = db.Column('Drop2', db.String(50))   
    BOL = db.Column('BOL', db.String(50))
    Booking= db.Column('Booking', db.String(50))
    Container = db.Column('Container', db.String(50))
    Driver = db.Column('Driver', db.String(50))        
    Pickup = db.Column('Pickup', db.String(50))
    Delivery = db.Column('Delivery', db.String(50))
    Amount = db.Column('Amount', db.String(50))
    Date = db.Column('Date', db.DateTime)
    Time = db.Column('Time', db.String(20))
    Date2 = db.Column('Date2', db.DateTime)
    Time2 = db.Column('Time2', db.String(20))
    Time3 = db.Column('Time3', db.String(20))
    Path = db.Column('Path', db.String(50))
    Original = db.Column('Original', db.String(99))
    Description = db.Column('Description', db.String(400))
    Chassis = db.Column('Chassis', db.String(50))
    Cache = db.Column('Storage', db.Integer)
    Release = db.Column('Release',db.Boolean)   
    Seal = db.Column('Seal', db.String(50))
    Shipper = db.Column('Shipper', db.String(50))
    Pid = db.Column('Pid', db.Integer)
    Type = db.Column('Type', db.String(50))
    Label = db.Column('Label', db.String(99))

    def __init__(self, Status, Jo, Order, Dropblock1, Drop1, Dropblock2, Drop2, BOL, Booking, Container, Driver, Pickup,
                    Delivery, Amount, Date, Time, Date2, Time2, Time3, Path, Original, Description, Chassis,
                    Cache, Release, Seal, Shipper, Pid, Type, Label):
        self.Status=Status
        self.Jo=Jo
        self.Order=Order
        self.Dropblock1=Dropblock1
        self.Drop1=Drop1
        self.Dropblock2=Dropblock2
        self.Drop2=Drop2
        self.BOL=BOL
        self.Booking=Booking
        self.Container=Container
        self.Driver=Driver
        self.Pickup= Pickup
        self.Delivery= Delivery
        self.Amount= Amount
        self.Date= Date
        self.Time = Time
        self.Date2= Date2
        self.Time2 = Time2
        self.Path = Path
        self.Original = Original
        self.Description = Description
        self.Chassis=Chassis
        self.Pid=Pid
        self.Cache=Cache
        self.Release=Release
        self.Seal=Seal
        self.Shipper=Shipper
        self.Type=Type
        self.Label=Label
                        
            
class JO(db.Model):
    __tablename__ = 'job'
    id = db.Column('id',db.Integer,primary_key=True)
    nextid = db.Column('nextid',db.Integer)
    jo = db.Column('jo',db.String(20))
    dinc = db.Column('dinc', db.Numeric(20,2))
    dexp = db.Column('dexp', db.Numeric(20,2))
    date = db.Column('date', db.DateTime)
    status = db.Column('status', db.Boolean)

    def __init__(self, nextid, jo, date, status):    #, dinc, dexp,):
        self.jo=jo
        self.nextid=nextid
        self.date=date
        self.status=status
        # self.dinc=dinc
        # self.dexp=dexp
        
class Services(db.Model): 
    __tablename__ = 'services'
    id = db.Column('id',db.Integer,primary_key=True)
    Service = db.Column('Service', db.String(40))
    Price = db.Column('Price', db.Numeric(10,2))
        
    def __init__(self, Service, Price):
        self.Service=Service
        self.Price=Price

class Partners(db.Model):
    __tablename__ = 'partners'
    id = db.Column('id',db.Integer,primary_key=True)
    Name = db.Column('Name',db.String(50))
    Addr1= db.Column('Addr1',db.String(50))
    Addr2= db.Column('Addr2',db.String(50))
    Location= db.Column('Location',db.String(50))
    Type= db.Column('Type',db.String(20))

    def __init__(self, Name, Addr1, Addr2, Location, Type):    #, dinc, dexp,):
        self.Name=Name
        self.Addr1=Addr1
        self.Addr2=Addr2
        self.Location=Location
        self.Type=Type
        
class Drivers(db.Model):
    __tablename__='drivers'
    id = db.Column('id',db.Integer,primary_key=True)
    Name = db.Column('Name',db.String(50))
    Truck= db.Column('Truck',db.String(9))
    Tag= db.Column('Tag',db.String(9))
    Email= db.Column('Email',db.String(50))
    Path= db.Column('Path',db.String(50))
    Phone=db.Column('Phone',db.String(25))
    
    def __init__(self, Name, Truck, Tag, Email,Path, Phone):  
        self.Name=Name
        self.Truck=Truck
        self.Tag=Tag
        self.Email=Email
        self.Path=Path
        self.Phone=Phone


class People(db.Model):
    __tablename__='people'
    id = db.Column('id',db.Integer,primary_key=True)
    Ptype = db.Column('Ptype',db.String(25))
    Company = db.Column('Company',db.String(50))
    First = db.Column('First',db.String(25))
    Middle = db.Column('Middle',db.String(25))
    Last = db.Column('Last',db.String(25))
    Addr1 = db.Column('Addr1',db.String(75))
    Addr2 = db.Column('Addr2',db.String(50))
    Addr3 = db.Column('Addr3',db.String(50))
    Idtype = db.Column('Idtype',db.String(25))
    Idnumber = db.Column('Idnumber',db.String(25))
    Telephone = db.Column('Telephone',db.String(75))
    Email = db.Column('Email',db.String(50))
    Associate1 = db.Column('Associate1',db.String(50))
    Associate2 = db.Column('Associate2',db.String(50))
    Temp1 = db.Column('Temp1',db.String(50))
    Temp2 = db.Column('Temp2',db.String(50))
    Date1 = db.Column('Date1',db.DateTime)
    Date2 = db.Column('Date2',db.DateTime)
    Original = db.Column('Original', db.String(50))
    
    def __init__(self, Ptype,Company,First,Middle,Last,Addr1,Addr2,Addr3,Idtype,Idnumber,Telephone,Email,Associate1,Associate2,Temp1,Temp2,Date1,Date2,Original):  
        self.Ptype=Ptype
        self.Company=Company
        self.First=First
        self.Middle=Middle
        self.Last=Last
        self.Addr1=Addr1
        self.Addr2=Addr2
        self.Addr3=Addr3
        self.Idtype=Idtype
        self.Idnumber=Idnumber
        self.Telephone=Telephone
        self.Email=Email
        self.Associate1=Associate1
        self.Associate2=Associate2
        self.Temp1=Temp1
        self.Temp2=Temp2
        self.Date1=Date1
        self.Date2=Date2
        self.Original=Original
        
class Storage(db.Model):
    __tablename__='storage'
    id = db.Column('id',db.Integer,primary_key=True)
    Jo = db.Column('JO',db.String(25))
    Pid = db.Column('Pid',db.Integer)
    Company = db.Column('Company',db.String(50))
    Description = db.Column('Description',db.String(200))
    Amount= db.Column('Amount',db.String(20))
    Status= db.Column('Status',db.String(25))
    Cache=db.Column('Cache',db.Integer)
    Original = db.Column('Original', db.String(75))
    Path = db.Column('Path', db.String(50))
    Date = db.Column('Date', db.DateTime)
    Label = db.Column('Label', db.String(99))
    BalFwd=db.Column('BalFwd',db.String(25))
    
    def __init__(self, Jo, Pid, Description, Amount, Status, Cache, Original, Path, Company, Date, Label, BalFwd):  
        self.Pid=Pid
        self.Jo=Jo
        self.Description=Description
        self.Amount=Amount
        self.Status=Status
        self.Cache=Cache
        self.Original=Original
        self.Path=Path
        self.Company=Company
        self.Date=Date
        self.Label=Label
        self.BalFwd=BalFwd
        

class AutoInvoice(db.Model):
    __tablename__='autoinvoice'
    id = db.Column('id',db.Integer,primary_key=True)
    Jo = db.Column('JO',db.String(25))
    Sid= db.Column('sid',db.Integer)
    Freq= db.Column('freq',db.String(20))
    Day= db.Column('day',db.Integer)
    
    def __init__(self, Jo, Sid, Freq, Day):
        self.Jo=Jo
        self.Sid=Sid
        self.Freq=Freq
        self.Day=Day
        
class Horizon(db.Model):
    __tablename__='horizon'
    id = db.Column('id',db.Integer,primary_key=True)
    Jo = db.Column('Jo',db.String(25))
    Pid=db.Column('Pid',db.Integer)
    Company=db.Column('Company',db.String(50))
    Aid=db.Column('Aid',db.Integer)
    Make=db.Column('Make',db.String(25))
    Model=db.Column('Model',db.String(25))
    Year=db.Column('Year',db.String(25))
    Vin=db.Column('Vin',db.String(25))
    Cost=db.Column('Cost',db.String(25))
    Sale=db.Column('Sale',db.String(25))
    Bfee=db.Column('Bfee',db.String(25))    
    Tow=db.Column('Tow',db.String(25))
    Repair=db.Column('Repair',db.String(25))
    Oitem=db.Column('Oitem',db.String(25))
    Ocost=db.Column('Ocost',db.String(25))
    Ipath=db.Column('Ipath',db.String(50))
    Apath=db.Column('Apath',db.String(50))
    Cache=db.Column('Cache',db.Integer)
    Status=db.Column('Status',db.String(25))
    Label=db.Column('Label',db.String(99))
    Date=db.Column('Date',db.DateTime)
    DocumentFee=db.Column('DocumentFee',db.String(25))
    
    def __init__(self, Jo, Pid,Company,Aid,Make,Model,Year, Vin, Cost, Sale, Bfee, DocumentFee, Tow, Repair,
                 Oitem, Ocost, Ipath, Apath, Cache, Status, Label, Date):
        self.Jo=Jo
        self.Pid=Pid
        self.Company=Company
        self.Aid=Aid
        self.Make=Make
        self.Model=Model    
        self.Year=Year
        self.Vin=Vin        
        self.Cost=Cost        
        self.Sale=Sale        
        self.Bfee=Bfee
        self.DocumentFee=DocumentFee
        self.Tow=Tow       
        self.Repair=Repair        
        self.Oitem=Oitem        
        self.Ocost=Ocost        
        self.Ipath=Ipath        
        self.Apath=Apath        
        self.Cache=Cache
        self.Status=Status
        self.Label=Label
        self.Date=Date
        
                 
class OverSeas(db.Model):
    __tablename__='overseas'
    id = db.Column('id',db.Integer,primary_key=True)
    Jo = db.Column('JO',db.String(25))
    Pid= db.Column('Pid',db.Integer)
    MoveType = db.Column('MoveType',db.String(25))
    Direction = db.Column('Direction',db.String(25))
    Commodity = db.Column('Commodity',db.String(25))
    Pod = db.Column('Pod',db.String(50))
    Pol = db.Column('Pol',db.String(25))
    Origin = db.Column('Origin',db.String(25))
    PuDate = db.Column('PuDate',db.DateTime)
    RetDate = db.Column('RetDate',db.DateTime)
    Tpath = db.Column('Tpath', db.String(25))
    ContainerType = db.Column('ContainerType',db.String(25))
    Container = db.Column('Container',db.String(25))
    Booking = db.Column('Booking',db.String(25))
    CommoList = db.Column('CommoList',db.Integer)    
    ExportID = db.Column('ExportID',db.Integer)
    ConsigID = db.Column('ConsigID',db.Integer)
    NotifyID = db.Column('NotifyID',db.Integer)
    FrForID = db.Column('FrForID',db.Integer)
    PreCarryID = db.Column('PreCarryID',db.Integer)    
    BillTo = db.Column('BillTo', db.String(50))
    Exporter = db.Column('Exporter', db.String(50))
    Consignee = db.Column('Consignee', db.String(50))
    Notify = db.Column('Notify', db.String(50))
    FrFor = db.Column('FrFor', db.String(50))
    PreCarry = db.Column('PreCarry', db.String(50))    
    Estimate = db.Column('Estimate',db.String(25))
    Charge = db.Column('Charge',db.String(25))
    Itotal= db.Column('Itotal',db.String(25))
    Dpath = db.Column('Dpath', db.String(50))
    Ipath = db.Column('Ipath', db.String(50))
    Apath = db.Column('Apath', db.String(50))
    Cache = db.Column('Cache', db.Integer)
    Status= db.Column('Status',db.String(25))
    Label = db.Column('Label', db.String(99))
    Driver = db.Column('Driver', db.String(50))
    Seal = db.Column('Seal',db.String(25))
    Description = db.Column('Description',db.String(400))
    RelType=db.Column('RelType',db.String(25))
    AES = db.Column('AES',db.String(50))
    ExpRef = db.Column('ExpRef',db.String(45))
    AddNote = db.Column('AddNote',db.String(45))

       
    def __init__(self, Jo, Pid, MoveType, Direction, Commodity, Pod, Pol, Origin,ContainerType, Container, Booking, CommoList, ExportID, ConsigID, NotifyID, FrForID, PreCarryID, BillTo, Exporter, Consignee, Notify, FrFor, PreCarry, Estimate, Charge, Dpath,Ipath,Apath,Cache, Status, Label, Driver, Seal, Description,Tpath,PuDate,RetDate,Itotal,RelType,AES,ExpRef,AddNote):  
        self.Jo=Jo
        self.Pid=Pid
        self.MoveType=MoveType
        self.Direction=Direction
        self.Commodity=Commodity
        self.Pod=Pod
        self.Pol=Pol
        self.Origin=Origin
        self.PuDate=PuDate
        self.RetDate=RetDate
        self.Tpath=Tpath
        self.Itotal=Itotal
        self.ContainerType=ContainerType
        self.Container=Container
        self.Booking=Booking
        self.CommoList=CommoList
        self.ExportID=ExportID
        self.ConsigID=ConsigID
        self.NotifyID=NotifyID
        self.FrForID=FrForID
        self.PreCarryID=PreCarryID
        self.BillTo=BillTo
        self.Exporter=Exporter
        self.Consignee=Consignee
        self.Notify=Notify
        self.FrFor=FrFor
        self.PreCarry=PreCarry
        self.Estimate=Estimate
        self.Charge=Charge
        self.Dpath=Dpath
        self.Ipath=Ipath
        self.Apath=Apath
        self.Cache=Cache
        self.Status=Status
        self.Label=Label
        self.Driver=Driver
        self.Seal=Seal
        self.Description=Description
        self.RelType=RelType
        self.AES=AES
        self.ExpRef=ExpRef
        self.AddNote=AddNote
        
class Vocc(db.Model):
    __tablename__='vocc'
    id = db.Column('id',db.Integer,primary_key=True)
    Name = db.Column('Name',db.String(25))
    B_First = db.Column('B_First',db.String(25))
    B_Last = db.Column('B_Last',db.String(25))
    B_Email = db.Column('B_Email',db.String(50))
    P_First = db.Column('P_First',db.String(25))
    P_Last = db.Column('P_Last',db.String(25))
    P_Email = db.Column('P_Email',db.String(50))
    
    def __init__(self, Name, B_First, B_Last, B_Email, P_First, P_Last, P_Email):
        self.Name=Name
        self.B_First=B_First
        self.B_Last=B_Last
        self.B_Email=B_Email
        self.P_First=P_First
        self.P_Last=P_Last
        self.P_Email=P_Email
        
class Autos(db.Model):
    __tablename__='autos'
    id = db.Column('id',db.Integer,primary_key=True)
    Jo = db.Column('JO',db.String(25))    
    Year = db.Column('Year',db.String(25))
    Make = db.Column('Make',db.String(25))
    Model = db.Column('Model',db.String(25))
    Color = db.Column('Color',db.String(25))
    VIN = db.Column('VIN',db.String(25))
    Title = db.Column('Title',db.String(25))
    State = db.Column('State',db.String(25))
    EmpWeight = db.Column('EmpWeight',db.String(25))
    Dispatched = db.Column('Dispatched',db.String(25))
    Value = db.Column('Value',db.String(50))
    Original = db.Column('Original',db.String(50))
    TowCompany = db.Column('TowCompany',db.String(50))
    TowCost = db.Column('TowCost',db.String(25))
    TowCostEa = db.Column('TowCostEa',db.String(25))
    Status = db.Column('Status',db.String(25))
    Date1 = db.Column('Date1',db.DateTime)
    Date2 = db.Column('Date2',db.DateTime)
    Pufrom = db.Column('Pufrom',db.String(50))
    Delto = db.Column('Delto',db.String(50))
    Ncars = db.Column('Ncars',db.Integer)
    Orderid= db.Column('Orderid',db.String(25))
    Hjo = db.Column('Hjo',db.String(25))
    
    def __init__(self, Jo, Year, Make, Model, Color, VIN, Title, State, EmpWeight, Dispatched, Value, Original, TowCompany,
                 TowCost, TowCostEa, Status, Date1, Date2, Pufrom, Delto, Ncars, Orderid, Hjo):
        self.Jo=Jo
        self.Year=Year
        self.Make=Make
        self.Model=Model
        self.Color=Color
        self.VIN=VIN
        self.Title=Title
        self.State=State
        self.EmpWeight=EmpWeight
        self.Dispatched=Dispatched
        self.Value=Value
        self.TowCompany=TowCompany
        self.TowCost=TowCost
        self.TowCostEa=TowCostEa
        self.Original=Original
        self.Status=Status
        self.Date1=Date1
        self.Date2=Date2
        self.Pufrom=Pufrom
        self.Delto=Delto
        self.Ncars=Ncars
        self.Orderid=Orderid
        self.Hjo=Hjo
        
class Autoshold(db.Model):
    __tablename__='autoshold'
    id = db.Column('id',db.Integer,primary_key=True)
    Jo = db.Column('JO',db.String(25))    
    Year = db.Column('Year',db.String(25))
    Make = db.Column('Make',db.String(25))
    Model = db.Column('Model',db.String(25))
    Color = db.Column('Color',db.String(25))
    VIN = db.Column('VIN',db.String(25))
    Title = db.Column('Title',db.String(25))
    State = db.Column('State',db.String(25))
    EmpWeight = db.Column('EmpWeight',db.String(25))
    Dispatched = db.Column('Dispatched',db.String(25))
    Value = db.Column('Value',db.String(50))
    Original = db.Column('Original',db.String(50))
    TowCompany = db.Column('TowCompany',db.String(50))
    TowCost = db.Column('TowCost',db.String(25))
    TowCostEa = db.Column('TowCostEa',db.String(25))
    Status = db.Column('Status',db.String(25))
    Date1 = db.Column('Date1',db.DateTime)
    Date2 = db.Column('Date2',db.DateTime)
    Pufrom = db.Column('Pufrom',db.String(50))
    Delto = db.Column('Delto',db.String(50))
    Ncars = db.Column('Ncars',db.Integer)
    Orderid= db.Column('Orderid',db.String(25))
    Hjo = db.Column('Hjo',db.String(25))
    
    def __init__(self, Jo, Year, Make, Model, Color, VIN, Title, State, EmpWeight, Dispatched, Value, Original, TowCompany,
                 TowCost, TowCostEa, Status, Date1, Date2, Pufrom, Delto, Ncars, Orderid, Hjo):
        self.Jo=Jo
        self.Year=Year
        self.Make=Make
        self.Model=Model
        self.Color=Color
        self.VIN=VIN
        self.Title=Title
        self.State=State
        self.EmpWeight=EmpWeight
        self.Dispatched=Dispatched
        self.Value=Value
        self.TowCompany=TowCompany
        self.TowCost=TowCost
        self.TowCostEa=TowCostEa
        self.Original=Original
        self.Status=Status
        self.Date1=Date1
        self.Date2=Date2
        self.Pufrom=Pufrom
        self.Delto=Delto
        self.Ncars=Ncars
        self.Orderid=Orderid
        self.Hjo=Hjo
        
        
class Bookings(db.Model):
    __tablename__='bookings'
    id = db.Column('id',db.Integer,primary_key=True)
    Jo = db.Column('JO',db.String(25))
    Booking = db.Column('Booking',db.String(25))
    ExportRef = db.Column('ExportRef',db.String(25))    
    Vessel = db.Column('Vessel',db.String(50))
    Line = db.Column('Line',db.String(50))
    PortCut = db.Column('PortCut',db.DateTime)
    DocCut = db.Column('DocCut',db.DateTime)
    SailDate = db.Column('SailDate',db.DateTime)
    EstArr = db.Column('EstArr',db.DateTime)
    RelType=db.Column('RelType',db.String(25))
    AES = db.Column('AES',db.String(50))
    Original = db.Column('Original', db.String(50))
    Amount = db.Column('Amount', db.String(25))
    LoadPort = db.Column('LoadPort', db.String(50))
    Dest = db.Column('Dest', db.String(50))
    Status= db.Column('Status',db.String(25))

    def __init__(self, Jo, Booking, ExportRef, Vessel, Line, PortCut, DocCut, SailDate, EstArr, RelType,
                  AES, Original, Amount, LoadPort, Dest, Status):
        self.Jo=Jo
        self.Booking=Booking
        self.ExportRef=ExportRef
        self.Vessel=Vessel
        self.Line=Line
        self.PortCut=PortCut
        self.DocCut=DocCut
        self.SailDate=SailDate
        self.EstArr=EstArr
        self.RelType=RelType
        self.AES=AES
        self.Original=Original
        self.Amount=Amount
        self.LoadPort=LoadPort
        self.Dest=Dest
        self.Status=Status
        
class FELVehicles(db.Model):
    __tablename__='felvehicles'
    id = db.Column('id',db.Integer,primary_key=True)
    Unit= db.Column('Unit',db.String(9))
    Year= db.Column('Year',db.String(25))
    Make= db.Column('Make',db.String(25))
    Model= db.Column('Model',db.String(25))
    Color= db.Column('Color',db.String(25))
    VIN= db.Column('VIN',db.String(25))
    Title= db.Column('Title',db.String(25))
    Plate= db.Column('Plate',db.String(25))
    EmpWeight= db.Column('EmpWeight',db.String(25))
    GrossWt= db.Column('GrossWt',db.String(25))
    DOTNum= db.Column('DOTNum',db.String(25))
    ExpDate= db.Column('ExpDate',db.Date)
    Odometer= db.Column('Odometer',db.String(25))
    Owner= db.Column('Owner',db.String(50))
    Status= db.Column('Status',db.String(25))
    
    def __init__(self, Unit, Year, Make, Model, Color, VIN, Title, Plate, EmpWeight, GrossWt, DOTNum, ExpDate, Odometer, Owner, Status):   
        self.Unit=Unit
        self.Year=Year
        self.Make=Make
        self.Model=Model
        self.Color=Color
        self.VIN=VIN
        self.Title=Title
        self.Plate=Plate
        self.EmpWeight=EmpWeight
        self.GrossWt=GrossWt
        self.DOTNum=DOTNum
        self.ExpDate=ExpDate
        self.Owner=Owner
        self.Odometer=Odometer
        self.Status=Status


class Invoices(db.Model):
    __tablename__='invoices'
    id = db.Column('id',db.Integer,primary_key=True)
    Jo = db.Column('Jo',db.String(25))
    SubJo=db.Column('SubJo',db.String(25))
    Pid=db.Column('Pid',db.Integer)
    Service=db.Column('Service',db.String(50))
    Description=db.Column('Description',db.String(400))
    Ea=db.Column('Ea',db.Numeric(10,2))
    Qty=db.Column('Qty',db.Numeric(10,2))
    Amount=db.Column('Amount',db.Numeric(10,2))
    Total=db.Column('Total',db.Numeric(10,2))
    Date = db.Column('Date', db.DateTime)
    Original = db.Column('Original', db.String(50))
    Status = db.Column('Status', db.String(25))
    
    def __init__(self, Jo, SubJo, Pid, Service, Description, Ea, Qty, Amount, Total, Date, Original, Status):
        self.Jo=Jo
        self.SubJo=SubJo
        self.Pid=Pid
        self.Service=Service
        self.Description=Description
        self.Ea=Ea
        self.Qty=Qty
        self.Amount=Amount
        self.Total=Total
        self.Date=Date
        self.Original=Original
        self.Status=Status

class Income(db.Model):
    __tablename__='income'
    id = db.Column('id',db.Integer,primary_key=True)
    Jo = db.Column('Jo',db.String(25))
    SubJo = db.Column('SubJo',db.String(25))
    Pid=db.Column('Pid',db.Integer)
    Description=db.Column('Description',db.String(200))
    Amount=db.Column('Amount',db.Numeric(10,2))
    Ref=db.Column('Ref',db.String(25))
    Date = db.Column('Date', db.DateTime)
    Original = db.Column('Original', db.String(50))
    
    def __init__(self, Jo, SubJo, Pid, Description, Amount, Ref, Date, Original):
        self.Jo=Jo
        self.SubJo=SubJo
        self.Pid=Pid
        self.Description=Description
        self.Amount=Amount
        self.Ref=Ref
        self.Date=Date
        self.Original=Original
        
class FELBills(db.Model):
    __tablename__='felbills'
    id = db.Column('id',db.Integer,primary_key=True)
    Jo = db.Column('JO',db.String(25))
    Pid = db.Column('Pid',db.Integer)
    Company = db.Column('Company',db.String(50))
    Memo = db.Column('Memo',db.String(50))
    Description = db.Column('Description',db.String(600))
    bAmount= db.Column('bAmount',db.String(20))
    Status= db.Column('Status',db.String(25))
    Cache=db.Column('Cache',db.Integer)
    Original = db.Column('Original', db.String(75))
    Ref = db.Column('Ref', db.String(50))
    bDate = db.Column('bDate', db.DateTime)
    pDate = db.Column('pDate', db.DateTime)
    pAmount= db.Column('pAmount',db.String(20))
    pMulti=db.Column('pMulti',db.String(20))
    Account=db.Column('Account',db.String(50))
    bType=db.Column('bType',db.String(25))
    bClass=db.Column('bClass',db.String(25))
    Link=db.Column('Link',db.String(100))
    User=db.Column('User',db.String(25))
    Co=db.Column('Co',db.String(9))
    Temp1=db.Column('Temp1',db.String(50))
    Temp2=db.Column('Temp2',db.String(50))
    
    def __init__(self, Jo, Pid, Company, Memo, Description, bAmount, Status, Cache, Original, Ref, bDate, pDate, pAmount, pMulti, Account, bType, bClass, Link, User, Co, Temp1, Temp2):          
        self.Jo=Jo
        self.Pid=Pid
        self.Company=Company
        self.Memo=Memo
        self.Description=Description
        self.bAmount=bAmount
        self.Status=Status
        self.Cache=Cache
        self.Original=Original
        self.Ref=Ref
        self.bDate=bDate
        self.pDate=pDate
        self.pAmount=pAmount
        self.pMulti=pMulti
        self.Account=Account
        self.bType=bType
        self.bClass=bClass
        self.Link=Link
        self.User=User
        self.Co=Co
        self.Temp1=Temp1
        self.Temp2=Temp2

class BillAccts(db.Model):
    __tablename__='billaccts'
    id = db.Column('id',db.Integer,primary_key=True)
    Btype = db.Column('Btype',db.String(25))
    Bclass = db.Column('Bclass',db.String(25))
    Bnum = db.Column('Bnum',db.String(10))
    
    def __init__(self,Btype,Bclass, Bnum):
        self.Btype=Btype
        self.Bclass=Bclass
        self.Bnum=Bnum
        
class Accounts(db.Model):
    __tablename__='accounts'
    id = db.Column('id',db.Integer,primary_key=True)
    Name = db.Column('Name',db.String(50))
    Balance = db.Column('Balance',db.String(25))
    AcctNumber = db.Column('AcctNumber',db.String(25))
    Routing = db.Column('Routing',db.String(25))
    Payee = db.Column('Payee',db.String(50))
    
    def __init__(self, Name, Amount, AcctNumber, Routing, Payee):
        self.Name=Name
        self.Amount=Amount
        self.AcctNumber=AcctNumber
        self.Routing=Routing
        self.Payee=Payee
    
    
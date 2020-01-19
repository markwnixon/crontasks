test = 1

if test == 1:
    from CCC_FELA_remote_db_connect import db

    class QB_Invoices(db.Model):
        __bind_key__ = 'QBDATA'
        __tablename__ = 'Invoices'
        ID = db.Column('ID', db.Integer, primary_key=True)
        CustomerName = db.Column('CustomerName', db.String(255))
        ItemAggregate = db.Column('ItemAggregate', db.String(255))

        def __init__(self, CustomerName, ItemAggregate):
            self.CustomerName = CustomerName
            self.ItemAggregate = ItemAggregate


    class QB_Accounts(db.Model):
        __bind_key__ = 'QBDATA'
        __tablename__ = 'Accounts'
        ID = db.Column('ID', db.Integer, primary_key=True)
        Name = db.Column('Name', db.String(255))
        Type = db.Column('Type', db.String(255))

        def __init__(self, Name, Type):
            self.Name = Name
            self.Type = Type

    class QB_Bills(db.Model):
        __bind_key__ = 'QBDATA'
        __tablename__ = 'Bills'
        ID = db.Column('ID', db.Integer, primary_key=True)
        VendorName = db.Column('VendorName', db.String(255))
        Date = db.Column('Date', db.DateTime)
        Amount = db.Column('Amount', db.String(255))

        def __init__(self, VendorName, Date, Amount):
            self.VendorName = VendorName
            self.Date = Date
            self.Amount = Amount

    class QB_BillExpenseItems(db.Model):
        __bind_key__ = 'QBDATA'
        __tablename__ = 'BillExpenseItems'
        ID = db.Column('ID', db.Integer, primary_key=True)
        BillId = db.Column('BillId', db.String(255))
        VendorName = db.Column('VendorName', db.String(255))
        Date = db.Column('Date', db.DateTime)
        Amount = db.Column('Amount', db.String(255))
        ExpenseAccount = db.Column('ExpenseAccount', db.String(255))
        ExpenseAmount = db.Column('ExpenseAmount', db.String(255))
        ReferenceNumber = db.Column('ReferenceNumber', db.String(255))
        Memo = db.Column('Memo', db.String(255))

        def __init__(self, BillId, VendorName, Date, Amount, ExpenseAccount, ExpenseAmount, ReferenceNumber, Memo):
            self.BillId = BillId
            self.VendorName = VendorName
            self.Date = Date
            self.Amount = Amount
            self.ExpenseAccount = ExpenseAccount
            self.ExpenseAmount = ExpenseAmount
            self.ReferenceNumber = ReferenceNumber
            self.Memo = Memo

    class QB_Customers(db.Model):
        __bind_key__ = 'QBDATA'
        __tablename__ = 'Customers'
        ID = db.Column('ID', db.Integer, primary_key=True)
        Name = db.Column('Name', db.String(255))
        Company = db.Column('Company', db.String(255))
        BillingAddress = db.Column('BillingAddress', db.String(255))
        BillingLine1 = db.Column('BillingLine1', db.String(255))
        BillingLine2 = db.Column('BillingLine2', db.String(255))
        BillingLine3 = db.Column('BillingLine3', db.String(255))
        BillingLine4 = db.Column('BillingLine4', db.String(255))
        BillingLine5 = db.Column('BillingLine5', db.String(255))
        BillingCity  = db.Column('BillingCity', db.String(255))
        BillingState = db.Column('BillingState', db.String(255))
        BillingPostalCode = db.Column('BillingPostalCode', db.String(255))
        ShippingAddress = db.Column('ShippingAddress', db.String(255))
        Phone = db.Column('Phone', db.String(255))
        Email = db.Column('Email', db.String(255))

        def __init__(self, Name, Company, BillingAddress, BillingLine1, BillingLine2, BillingLine3, BillingLine4, BillingLine5, BillingCity, BillingState, BillingPostalCode, ShippingAddress, Phone, Email):
            self.Name = Name
            self.Company = Company
            self.BillingAddress = BillingAddress
            self.ShippingAddress = ShippingAddress
            self. Phone = Phone
            self.Email = Email
            self.BillingLine1 = BillingLine1
            self.BillingLine2 = BillingLine2
            self.BillingLine3 = BillingLine3
            self.BillingLine4 = BillingLine4
            self.BillingLine5 = BillingLine5
            self.BillingCity = BillingCity
            self.BillingState = BillingState
            self.BillingPostalCode = BillingPostalCode


    class QB_Vendors(db.Model):
        __bind_key__ = 'QBDATA'
        __tablename__ = 'Vendors'
        ID = db.Column('ID', db.Integer, primary_key=True)
        Name = db.Column('Name', db.String(255))
        Company = db.Column('Company', db.String(255))
        Address = db.Column('Address', db.String(255))
        Phone = db.Column('Phone', db.String(255))
        Email = db.Column('Email', db.String(255))

        def __init__(self, Name, Company, BillingAddress, ShippingAddress, Phone, Email):
            self.Name = Name
            self.Company = Company
            self.BillingAddress = BillingAddress
            self.ShippingAddress = ShippingAddress
            self. Phone = Phone
            self.Email = Email










if test == 2:
    from CCC_remote_db_QBconnect import db

    class QB_Invoices(db.Model):
        __tablename__ = 'Invoices'
        ID = db.Column('ID', db.Integer, primary_key=True)
        CustomerName = db.Column('CustomerName', db.String(255))
        ItemAggregate = db.Column('ItemAggregate', db.String(255))

        def __init__(self, CustomerName, ItemAggregate):
            self.CustomerName = CustomerName
            self.ItemAggregate = ItemAggregate




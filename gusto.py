import time
import datetime
import os
from cronfuncs import dropupdate, d1s, d2s

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from random import randint

from statistics import mean
from CCC_system_setup import mycompany, usernames, passwords, websites, addpath4

co = mycompany()
if co == 'FELA':
    from CCC_FELA_remote_db_connect import tunnel, db
    from CCC_FELA_models import Chassis, Interchange, FELBills, People, Payroll
elif co == 'OSLM':
    from CCC_OSLM_remote_db_connect import tunnel, db
    from CCC_OSLM_models import Chassis, Interchange

import csv
admin = ['Mark Nixon', 'Nadav Khalai', 'Norma Ghanem']
truckdriver = ['Jeff Stivason', 'Tiwand McClary', 'Darrell Tibbs', 'Carter Bradley', 'Bryan McComus']
other = ['Muhammed Zeidan']
period = 'none'

def put_payroll(type, fn, earn, empcost, emptaxes, paydt, pdsdt, pdedt, hours, ot, thours):
    pdat = Payroll.query.filter( (Payroll.Name == fn) & (Payroll.Date == paydt) ).first()
    if pdat is None:
        input = Payroll(Name = fn, Function = type, GrossEarning = earn, EmployerTaxes = emptaxes, CompanyPay = empcost,
                        Date = paydt, PayrollStart = pdsdt, PayrollEnd = pdedt, RegHours = hours, OT = ot, TotHours = thours)
        db.session.add(input)
        db.session.commit()




csvfile = addpath4('payroll/gusto_history.csv')
print(csvfile)

name =''
with open(csvfile) as cv:
    csv_reader = csv.reader(cv)
    lc = 0
    for row in csv_reader:
        if lc == 0:
            print(f'Column name are {", ".join(row)}')
            lc += 1
        else:
            if row[0] == 'Payroll period':
                period = row[1]
            if row[0] == 'Pay day':
                paydate = row[1].strip()
                subrow = 0
                pgo = 1
                while pgo == 1:
                    for nr in csv_reader:
                        subrow += 1
                        name = nr[0]
                        if subrow > 1 and pgo == 1:
                            #print('sr1',nr)
                            fname = nr[1]
                            fn = f'{fname} {name}'
                            try:
                                hours = float(nr[4])
                            except:
                                hours = 0.00
                            try:
                                ot = float(nr[7])
                            except:
                                ot = 0.00
                            try:
                                earn = float(nr[14])
                            except:
                                earn = 0.00
                            try:
                                empcost = float(nr[len(nr)-1])
                            except:
                                empcost = 0.00
                            if period != 'none':
                                paydt = datetime.datetime.strptime(paydate,'%m/%d/%Y')
                                pds, pde = period.split('-')
                                pdsdt, pdedt =  datetime.datetime.strptime(pds.strip(),'%m/%d/%Y'), datetime.datetime.strptime(pde.strip(),'%m/%d/%Y')
                                try:
                                    emptaxes = d2s(empcost - earn)
                                    thours = d2s(hours + ot)
                                    hours = d2s(hours)
                                    ot = d2s(ot)
                                    empcost = d2s(empcost)
                                    earn = d2s(earn)
                                except:
                                    print(empcost, earn,hours, ot)
                                if fn in truckdriver:
                                    print(paydate, period)
                                    print(f'Driver Name:{fn} Hours:{hours} OT:{ot} Earnings:{earn} EmpCost:{empcost} EmpTaxes{emptaxes}')
                                    put_payroll('Driver',fn,earn,empcost,emptaxes,paydt,pdsdt,pdedt,hours,ot,thours)
                                elif fn in admin:
                                    print(paydate, period)
                                    print(f'Admin Name:{fn} Hours:{hours} OT:{ot} Earnings:{earn} EmpCost:{empcost} EmpTaxes{emptaxes}')
                                    put_payroll('Admin', fn, earn, empcost, emptaxes, paydt, pdsdt, pdedt, hours, ot, thours)
                                elif fn in other:
                                    print(paydate, period)
                                    print(f'Warehouse:{fn} Hours:{hours} OT:{ot} Earnings:{earn} EmpCost:{empcost} EmpTaxes{emptaxes}')
                                    put_payroll('Warehouse', fn, earn, empcost, emptaxes, paydt, pdsdt, pdedt, hours, ot, thours)

                        if name == 'Payroll Totals' or nr[0] == 'Payroll Totals':
                            pgo = 0
                            break

if 1 == 1:
    #Fixes to payroll
    pdata = Payroll.query.all()
    for pdat in pdata:
        etax = pdat.EmployerTaxes
        try:
            etax = float(etax)
        except:
            ge = float(pdat.GrossEarning)
            etax = ge*.0845
            tot = ge + etax
            pdat.EmployerTaxes = d2s(etax)
            pdat.CompanyPay = d2s(tot)
            db.session.commit()
        ot = pdat.OT
        try:
            otf = float(ot)
        except:
            otf = 0.00
            pdat.OT = '0.00'
            db.session.commit()
        reghrs = float(pdat.RegHours)
        tothrs = reghrs + otf
        pdat.TotHours = d2s(tothrs)

        type = pdat.Function
        if type == 'Driver':
            wcrate = .10
        elif type == 'Admin:':
            wcrate = .1
        elif type == 'Warehouse':
            wcrate == .04
        pay = float(pdat.GrossEarning)
        wcomp = wcrate * pay
        fullcost = wcomp + float(pdat.CompanyPay)
        pdat.WorkerComp = d2s(wcomp)
        pdat.FullCost = d2s(fullcost)
        db.session.commit()


tunnel.stop()
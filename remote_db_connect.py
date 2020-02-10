from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
import numpy as np
import subprocess
import os
import shutil
import datetime
import re
import mysql.connector
import sshtunnel
from CCC_system_setup import tup, dbp, qbp

app = Flask(__name__, static_folder="tmp")

sshtunnel.SSH_TIMEOUT = 5.0
sshtunnel.TUNNEL_TIMEOUT = 5.0

tunnel = sshtunnel.SSHTunnelForwarder(
    (tup[0]), ssh_username=tup[1], ssh_password=tup[2],
    remote_bind_address=(tup[3], tup[4])
)
tunnel.start()

SQLALCHEMY_DATABASE_URI = "mysql://{username}:{password}@{hostname}:{port}/{databasename}".format(
    username=dbp[0],
    password=dbp[1],
    hostname=dbp[2],
    port=tunnel.local_bind_port,
    databasename=dbp[3],
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG"] = True
app.secret_key = dbp[4]

if qbp[0] == 1:
    qburi = "mysql://{username}:{password}@{hostname}:{port}/{databasename}".format(
        username=qbp[1],
        password=qbp[2],
        hostname=qbp[3],
        port=qbp[4],
        databasename=qbp[5],
    )

    print(qburi)
    app.config['SQLALCHEMY_BINDS'] = {'QBDATA' : qburi}

db = SQLAlchemy(app)



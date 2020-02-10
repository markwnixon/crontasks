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

app = Flask(__name__, static_folder="tmp")

SQLALCHEMY_DATABASE_URI = "mysql://{username}:{password}@{hostname}:{port}/{databasename}".format(
    username="felqb",
    password="User1123!",
    hostname="70.88.236.49",
    port="3307",
    databasename="CDataFELQB",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG"] = True
app.secret_key = "skdevil45"

db = SQLAlchemy(app)



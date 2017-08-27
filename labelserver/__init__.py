from flask import Flask
import datetime
import threading
import webargs.flaskparser
import yaml

app = Flask(__name__)
parser = webargs.flaskparser.FlaskParser()

import labelserver.config
with open("config.yaml", "r") as config_file:
    printers = labelserver.config.load(config_file)


for printer in printers.values():
    printer.start();


import labelserver.status
import labelserver.api

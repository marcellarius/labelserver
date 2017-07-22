from flask import Flask
import datetime
import threading
import yaml

app = Flask(__name__)


import labelserver.config
with open("config.yaml", "r") as config_file:
    printers = labelserver.config.load(config_file)


import labelserver.status
import labelserver.api

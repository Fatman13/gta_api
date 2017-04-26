#!/usr/bin/env python
# coding=utf-8

import pprint
import click 
import requests
import datetime as datetime
from datetime import date
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import fromstring
import os
import random
from sqlalchemy import create_engine
from sqlalchemy import text
import copy
import json

url = 'https://rbs.gta-travel.com/rbscnapi/RequestListenerServlet'

si_tree = ET.parse(os.path.join(os.getcwd(), 'SearchItemInformationRequest.xml'))

try:
	ri = requests.post(url, data=ET.tostring(si_tree.getroot(), encoding='UTF-8', method='xml'), timeout=350)
except OSError:
	pprint.pprint('Error: ignoring OSError...')

ri_tree = ET.fromstring(ri.text)

pprint.pprint(ri.text)
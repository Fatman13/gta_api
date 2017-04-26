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

t_tree = ET.parse(os.path.join(os.getcwd(), 'Response.xml'))

if not len(list(t_tree.find('.//SightseeingDetails'))):
	pprint.pprint('No child sightseeing price returned...')
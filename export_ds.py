#!/usr/bin/env python
# coding=utf-8

import sys
if sys.version_info.major == 2:
	reload(sys)
	sys.setdefaultencoding('utf-8')

import pprint
import click 
import requests
import datetime as datetime
from datetime import date
import os
import random
from sqlalchemy import create_engine
from sqlalchemy import text
import copy
import json
import csv
# import random
from requests.exceptions import ConnectionError

def validate_d(date_text):
	try:
		datetime.datetime.strptime(date_text, '%Y-%m-%d')
	except ValueError:
		raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)

tour_mapping = None
cur_clients = {}
cur_supported_clients = None
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secrets.json')) as data_file:
	d_config = (json.load(data_file))
	tour_mapping = d_config['TOUR_MAPPING']

	cur_supported_clients = d_config['supported_clients']
	for client in cur_supported_clients:
		cur_clients[client] = d_config[client]

# ['D', 'IS', 'A', 'SF', 'I', 'EI', 'NL', 'CH', 'GB' ]

def try_get(dict, key):
	try:
		return dict[key]
	except KeyError:
		return ''

@click.command()
# @click.option('--country', default='Germany')
@click.option('--client', default='ctrip')
def export_ds(client):

	url = 'https://rbs.gta-travel.com/rbscnapi/RequestListenerServlet'
	res = []

	engine = create_engine('sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'destServ.db'))
	services = engine.execute("SELECT * FROM destination_service;")

	for row in services:
		tour_ops = json.loads(row[tour_mapping[client]])

		for op in tour_ops:

			for dep in op['departures']:
				ent = {}
				ent['country'] = row['country']
				ent['city_code'] = row['city_code']
				ent['item_code'] = row['item_code']
				ent['name'] = row['name']
				ent['duration'] = row['duration']
				ent['summary'] = row['summary']
				ent['please_note'] = row['please_note']
				ent['includes'] = row['includes']
				ent['the_tour'] = row['the_tour']
				ent['additional_information'] = row['additional_information']
				ent['currency'] = row['currency']
				ent['policy'] = row['policy']
				ent['closed_dates'] = row['closed_dates']
				ent['thumb_nail'] = row['thumb_nail']
				ent['image'] = row['image']
				# ent['min_pax'] = op['min_pax']
				ent['min_pax'] = try_get(op, 'min_pax')
				# ent['pax_type'] = op['pax_type']
				ent['pax_type'] = try_get(op, 'pax_type')
				# ent['from_date'] = op['from_date']
				ent['from_date'] = try_get(op, 'from_date')
				# ent['to_date'] = op['to_date']
				ent['to_date'] = try_get(op, 'to_date')
				# ent['prices'] = op['prices']
				ent['prices'] = try_get(op, 'prices')
				ent['price'] = try_get(op, 'price')
				ent['commentary'] = try_get(op, 'commentary')
				ent['languages'] = try_get(op, 'languages')
				# ent['departure_point'] = dep['departure_point']['value']
				if try_get(dep, 'departure_point') != '':
					ent['departure_point'] = dep['departure_point']['value']				
					ent['departure_point_code'] = dep['departure_point']['code']				
				ent['address'] = try_get(dep, 'address')
				ent['time'] = try_get(dep, 'time')
				ent['telephone'] = try_get(dep, 'telephone')
				res.append(ent)

	keys = res[0].keys()
	# with open('output_SearchPrice_' + date.today().strftime('%Y_%m_%d') + '.csv', 'w', encoding='utf-8') as output_file:
	target_file_name = '_'.join([ 'Output_ds_products',
									datetime.datetime.today().date().strftime('%y%m%d'),
									datetime.datetime.now().strftime('%H%M')
								]) + '.csv'
	with open(target_file_name, 'w', newline='', encoding='utf-8') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(res)

if __name__ == '__main__':
	export_ds()
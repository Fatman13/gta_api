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
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import fromstring
from xml.etree.ElementTree import ParseError
import os
import random
from sqlalchemy import create_engine
from sqlalchemy import text
import copy
import json
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

TIME_OUT = 10

columns = 'country, city_code, item_code, name, duration, summary, please_note, includes, the_tour, additional_information, currency, policy, tour_operations, tour_operations1, tour_operations2, tour_operations3, tour_operations4, tour_operations5, tour_operations6, tour_operations7, closed_dates, thumb_nail, image'

def init_cols(entry):
	for col in columns:
		entry[col] = ''

@click.command()
# @click.option('--country', default='IA')
@click.option('--req/--no-req', default=True)
# @click.option('--client', default='ctrip')
def updateds_static(req):

	url = 'https://rbs.gta-travel.com/rbscnapi/RequestListenerServlet'
	res = []

	services = []
	services_i = []
	services_p = []
	# sp_tree = ET.parse(os.path.join(os.getcwd(), 'SearchSightseeingPriceRequest.xml'))
	sp_tree = ET.parse(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SearchSightseeingPriceRequest.xml'))
	# si_tree = ET.parse(os.path.join(os.getcwd(), 'SearchItemInformationRequest.xml'))
	si_tree = ET.parse(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SearchItemInformationRequest.xml'))

	# engine = create_engine('sqlite:///destServ.db')
	engine = create_engine('sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'destServ.db'))
	# 
	# services_raw = engine.execute("SELECT * FROM destination_service_raw WHERE country_code='{0}';".format(country))
	services_raw = engine.execute("SELECT * FROM destination_service_raw;")

	n_d = datetime.datetime.now().date()

	last_city_code = None
	last_item_code = None
	entry = None

	# reqs_rows = engine.execute("SELECT * FROM {0};".format(client))
	reqs_rows = engine.execute("SELECT * FROM {0};".format('top_selling'))
	reqs = set()
	for row in reqs_rows:
		reqs.add('_'.join([row['city_code'], row['item_code']]))

	# Merge raw entries
	for row in services_raw:
		# pprint.pprint(row)

		# if client == 'ctrip':
		# 	if not ('#'.join([row['city_code'], row['item_code']]) in reqs):
		# 		continue
		if req:
			gta_key = '_'.join([row['city_code'], row['item_code']])
			if not gta_key in reqs:
				# print('Not in top selling .. skipping .. ' + str(gta_key))
				continue

		if not (last_city_code == row['city_code'] and last_item_code == row['item_code']):
			entry = {}
			#
			init_cols(entry)
			entry['country'] = row['country']
			entry['city_code'] = row['city_code']
			entry['item_code'] = row['item_code']
			entry['adult_min_pax'] = set()
			entry['child_min_pax'] = []
			entry['rate_plan'] = []
			services.append(entry)

		min_pax = int(row['min_pax'])
		if row['pax_type'] == 'Adult' and min_pax <= 9:
			entry['adult_min_pax'].add(min_pax)
		elif row['pax_type'] == 'Child' and min_pax <= 9:
			child = {}
			child['age_from'] = row['age_from']
			child['age_to'] = row['age_to']
			child['min_pax'] = min_pax

			if child in entry['child_min_pax'] or int(row['age_to']) < 2:
				last_city_code = row['city_code']
				last_item_code = row['item_code']
				continue

			entry['child_min_pax'].append(child)

		last_city_code = row['city_code']
		last_item_code = row['item_code']

		# pprint.pprint(entry)

	# pprint.pprint(services)
	print('Total services: ' + str(len(services)))

	# Get item info
	for counter, service in enumerate(services):
		# a = 1
		si_tree.find('.//ItemDestination').set('DestinationCode', service['city_code'])
		si_tree.find('.//ItemCode').text = service['item_code']

		# pprint.pprint(ET.tostring(si_tree.getroot(), encoding='UTF-8', method='xml'))
		# if not counter % random.randint(23,25):
			# print('Fetching static info.. ' + str(counter))
		print('Fetching static info.. ' + str(counter) + ': ' + '_'.join([service['city_code'], service['item_code']]))

		try:
			ri = requests.post(url, data=ET.tostring(si_tree.getroot(), encoding='UTF-8', method='xml'), timeout=TIME_OUT)
		except OSError:
			pprint.pprint('Error: ignoring OSError...')
			continue

		try:
			ri_tree = ET.fromstring(ri.text)
		except ParseError:
			print('Error: Parser error.. i')
			continue

		if ri_tree.find('.//Errors') != None:
			if not len(list(ri_tree.find('.//Errors'))):
				errors = {}
				for i, er in enumerate(ri_tree.find('.//Errors')):
					if er.find('.//ErrorText') != None:
						errors[str(i)] = er.find('.//ErrorText').text
				pprint.pprint(errors)
				break

		if ri_tree.find('.//ItemDetails') == None:
			pprint.pprint('Error: ItemDetails not found?...{0}'.format(service['city_code'] + '_' + service['item_code']))
			continue

		if not len(list(ri_tree.find('.//ItemDetails'))):
			pprint.pprint('No item information returned...')
			# update obsolete destination services
			service['adult_min_pax'] = set()
			service['child_min_pax'] = []

		if ri_tree.find('.//Item') != None:
			service['name'] = ri_tree.find('.//Item').text.replace('\n', ' ').replace('\r', '')
		else:
			service['name'] = ''
		if ri_tree.find('.//TourSummary') != None:
			service['summary'] = ri_tree.find('.//TourSummary').text.replace('\n', ' ').replace('\r', '')
		else:
			service['summary'] = ''
		if ri_tree.find('.//Duration') != None:
			service['duration'] = ri_tree.find('.//Duration').text.replace('\n', ' ').replace('\r', '')
		else:
			service['duration'] = ''
		if ri_tree.find('.//TheTour') != None:
			service['the_tour'] = ri_tree.find('.//TheTour').text.replace('\n', ' ').replace('\r', '')
		else:
			service['the_tour'] = ''
		if ri_tree.find('.//Includes') != None:
			service['includes'] = ri_tree.find('.//Includes').text.replace('\n', ' ').replace('\r', '')
		else:
			service['includes'] = ''
		if ri_tree.find('.//PleaseNote') != None:
			service['please_note'] = ri_tree.find('.//PleaseNote').text.replace('\n', ' ').replace('\r', '')
		else:
			service['please_note'] = ''
		if ri_tree.find('.//AdditionalInformation') != None:
			service['additional_information'] = ''
			if ri_tree.find('.//AdditionalInformation') != None:
				for info in ri_tree.find('.//AdditionalInformation'):
					service['additional_information'] += info.text + ' '
			service['additional_information'] = service['additional_information'].strip().replace('\n', ' ').replace('\r', '')

		else:
			service['additional_information'] = ''

		if ri_tree.find('.//TourOperations') != None:
			for op in ri_tree.find('.//TourOperations'):
				op_ent = {}
				op_ent['languages'] = []
				if op.find('.//TourLanguages') != None:
					for language in op.find('.//TourLanguages'):
						if language != None:
							lang_ent = {}
							lang_ent['language'] = language.text
							lang_ent['code'] = language.get('Code')
							lang_ent['list_code'] = ''
							if language.get('LanguageListCode') != None:
								lang_ent['list_code'] = language.get('LanguageListCode')
							# op_ent['languages'].append(language.text)
							op_ent['languages'].append(lang_ent)
				op_ent['days'] = op.find('.//Frequency').text
				op_ent['commentary'] = op.find('.//Commentary').text
				op_ent['from_date'] = op.find('.//FromDate').text
				op_ent['to_date'] = op.find('.//ToDate').text

				to_date = datetime.datetime.strptime(op_ent['to_date'], '%Y-%m-%d').date()
				if to_date < n_d: 
					pprint.pprint('To date is less than now date... skipping...')
					continue

				op_ent['departures'] = []
				for dep in op.find('.//Departures'):
					dep_ent = {}
					if dep.find('.//Time') != None:
						dep_ent['time'] = dep.find('.//Time').text
					if dep.find('.//DeparturePoint') != None:
						# dep_ent['meeting_point'] = dep.find('.//DeparturePoint').text
						# fix name
						departure_point = dep.find('.//DeparturePoint').text
						departure_code = dep.find('.//DeparturePoint').get('Code')
						dep_ent['departure_point'] = {"code": departure_code, "value": departure_point}

					if dep.find('.//Telephone') != None:
						dep_ent['telephone'] = dep.find('.//Telephone').text
					if dep.find('.//AddressLine1') != None:
						dep_ent['address'] = str(dep.find('.//AddressLine1').text) + ' ' + str(dep.find('.//AddressLine2').text) 
					op_ent['departures'].append(dep_ent)

				service['rate_plan'].append(op_ent)

		service['closed_dates'] = []
		if ri_tree.find('.//ClosedDates') != None:
			for date in ri_tree.find('.//ClosedDates'):
				if date != None:
					service['closed_dates'].append(date.text)
		if ri_tree.find('.//ThumbNail') != None:
			service['thumb_nail'] = ri_tree.find('.//ThumbNail').text
		else:
			service['thumb_nail'] = ''

		if ri_tree.find('.//Image') != None:
			service['image'] = ri_tree.find('.//Image').text
		else:
			service['image'] = ''

		# some hardcoded shit..
		service['tour_operations'] = []
		service['tour_operations1'] = []
		service['tour_operations2'] = []
		service['tour_operations3'] = []
		service['tour_operations4'] = []
		service['tour_operations5'] = []
		service['tour_operations6'] = []
		service['tour_operations7'] = []

		# pprint.pprint(service)
		services_i.append(service)

	# pprint.pprint(services_i)
	# pprint.pprint('///////////////////////////////////////////')
	print('And total services i: ' + str(len(services_i)))

	for service in services_i:
		engine.execute("DELETE FROM destination_service WHERE city_code='{0}' AND item_code='{1}';".format(service['city_code'], service['item_code']))
	for service in services_i:
		if len(service['tour_operations']) != 0:
			r = [service['country'], service['city_code'], service['item_code'], \
					service['name'], service['duration'], service['summary'], \
					service['please_note'], service['includes'], service['the_tour'], service['additional_information'], \
					service['currency'], json.dumps(service['policy']), json.dumps(service['tour_operations']), json.dumps(service['tour_operations1']), json.dumps(service['tour_operations2']), json.dumps(service['tour_operations3']), json.dumps(service['tour_operations4']), json.dumps(service['tour_operations5']), json.dumps(service['tour_operations6']), json.dumps(service['tour_operations7']), \
					json.dumps(service['closed_dates']), service['thumb_nail'], service['image']]
			if r == None:
				print('Error: r is none when inserting into database..')
				continue
			engine.execute("INSERT INTO destination_service ({0}) VALUES({1});".format(columns, ','.join( '\'' + ent.replace('\'', '\'\'') + '\'' for ent in r) ))

if __name__ == '__main__':
	updateds_static()
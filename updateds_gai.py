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

@click.command()
# @click.option('--country', default='IA')
@click.option('--req/--no-req', default=True)
# @click.option('--client', default='ctrip')
def updateds(req):

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

	# Get price
	for counter_client, client in enumerate(cur_supported_clients):
		sp_tree.find('.//RequestorID').set('Client', cur_clients[client]['id'])
		sp_tree.find('.//RequestorID').set('EMailAddress', cur_clients[client]['email'])
		sp_tree.find('.//RequestorID').set('Password', cur_clients[client]['password'])

		mapped_tour_key = tour_mapping[client]
		print('Now searching price for ' + client)		

		for counter, service in enumerate(services_i):
			sp_tree.find('.//ItemDestination').set('DestinationCode', service['city_code'])
			sp_tree.find('.//ItemCode').text = service['item_code']

			# pprint.pprint('111111111111111111111111111111111')
			# pprint.pprint(ET.tostring(sp_tree.getroot(), encoding='UTF-8', method='xml'))

			# multi price change
			# service['tour_operations'] = []
			service[mapped_tour_key] = []
			print('Updating Adult price id: ' + str(counter) + ': ' + service['city_code'] + '_' + service['item_code'])

			for min_pax in service['adult_min_pax']:
				for rate_plan in service['rate_plan']:
					tour_operation = copy.deepcopy(rate_plan)

					from_d = datetime.datetime.strptime(rate_plan['from_date'], '%Y-%m-%d').date()
					to_d = datetime.datetime.strptime(rate_plan['to_date'], '%Y-%m-%d').date()

					if to_d < n_d:
						pprint.pprint('To date is less than now date... skipping...')
						continue

					# pprint.pprint('222222222222222222222222222222222222222')
					# pprint.pprint(ET.tostring(sp_tree.getroot(), encoding='UTF-8', method='xml'))			

					parent = sp_tree.find('.//Children')
					for child_node in list(parent):
						parent.remove(child_node)	

					search_d = to_d - datetime.timedelta(days=1)
					sp_tree.find('.//TourDate').text = search_d.strftime('%Y-%m-%d')
					sp_tree.find('.//NumberOfAdults').text = str(min_pax)

					# pprint.pprint('33333333333333333333333333333333333')
					# pprint.pprint(service)
					# pprint.pprint(ET.tostring(sp_tree.getroot(), encoding='UTF-8', method='xml'))

					try:
						# rp = requests.post(url, data=ET.tostring(sp_tree.getroot(), encoding='UTF-8', method='xml'), timeout=10)
						rp = requests.post(cur_clients[client]['url'], data=ET.tostring(sp_tree.getroot(), encoding='UTF-8', method='xml'), timeout=TIME_OUT)
					except OSError:
						pprint.pprint('Error: ignoring OSError...')
						continue
					except ConnectionError:
						pprint.pprint('Fatal Error: Connection error... A')
						continue
							
					rp_tree = ET.fromstring(rp.text)

					if rp_tree == None:
						print('Error: Price search rp tree is none..')
						continue

					if rp_tree.find('.//Errors') != None:
						pprint.pprint('Errors in returns of Adults price... on ' + search_d.strftime('%Y-%m-%d'))
						continue

					# pprint.pprint(rp.text)

					if rp_tree.find('.//SightseeingDetails') == None:
						print('Warning: no sightseeing ele.. i')
						continue

					if not len(list(rp_tree.find('.//SightseeingDetails'))):
						pprint.pprint('No sightseeing price returned...')
						continue

					service['currency'] = rp_tree.find('.//ItemPrice').get('Currency')

					service['policy'] = []
					for charge_condition in rp_tree.find('.//ChargeConditions'):
						if charge_condition.get('Type') == 'cancellation':
							for conditoin in charge_condition:
								con_ent = {}
								if conditoin.get('Charge') == 'true':
									# service['policy'] += 'Charge(FromDay: ' + str(conditoin.get('FromDay')) + ' ToDay: ' + str(conditoin.get('ToDay')) + ') '
									con_ent['type'] = 'Charge'
									con_ent['charge_amount'] = float(conditoin.get('ChargeAmount'))
									con_ent['from_day'] = int(conditoin.get('FromDay'))
									if conditoin.get('ToDay') != None:
										con_ent['to_day'] = int(conditoin.get('ToDay'))
								else:
									# service['policy'] += 'Free(FromDay: ' + str(conditoin.get('FromDay')) + ') '
									con_ent['type'] = 'Free'
									con_ent['from_day'] = int(conditoin.get('FromDay'))
								service['policy'].append(con_ent)


					tour_ops = rp_tree.find('.//TourOperations')

					if len(list(tour_ops)) == 1:
						tour_operation['price'] = float(rp_tree.find('.//ItemPrice').text)
					else:
						tour_operation['prices'] = []			
						for tour_op in tour_ops:
							op_entry = {}
							if tour_op.find('.//SpecialItem') != None:
								op_entry['name'] = tour_op.find('.//SpecialItem').text
							else:
								op_entry['name'] = tour_op.find('.//TourLanguage').text
							op_entry['price'] = float(tour_op.find('.//ItemPrice').text)
							tour_operation['prices'].append(op_entry)
					tour_operation['min_pax'] = min_pax
					tour_operation['pax_type'] = 'Adult'

					# service['tour_operations'].append(tour_operation)
					service[mapped_tour_key].append(tour_operation)
						
			for child in service['child_min_pax']:

				print('Updating Child price .. ' + service['city_code'] + '_' + service['item_code'])

				for rate_plan in service['rate_plan']:

					tour_operation = copy.deepcopy(rate_plan)

					from_d = datetime.datetime.strptime(rate_plan['from_date'], '%Y-%m-%d').date()
					to_d = datetime.datetime.strptime(rate_plan['to_date'], '%Y-%m-%d').date()

					if to_d < n_d:
						pprint.pprint('To date is less than now date... skipping...2')
						continue

					search_d = to_d - datetime.timedelta(days=1)
					sp_tree.find('.//TourDate').text = search_d.strftime('%Y-%m-%d')
					sp_tree.find('.//NumberOfAdults').text = str(child['min_pax'])

					child_from_age = int(child['age_from'])
					if child_from_age < 2:
						continue
					parent = sp_tree.find('.//Children')
					for child_node in list(parent):
						parent.remove(child_node)
					for i in range(int(child['min_pax'])):
						# GTA API doesn't accept child under age 2...
						sp_tree.find('.//Children').append(fromstring('<Age>{0}</Age>'.format(str(child_from_age+1))))

					# pprint.pprint(service)
					# pprint.pprint(ET.tostring(sp_tree.getroot(), encoding='UTF-8', method='xml'))

					try:
						# rp = requests.post(url, data=ET.tostring(sp_tree.getroot(), encoding='UTF-8', method='xml'), timeout=TIME_OUT)
						rp = requests.post(cur_clients[client]['url'], data=ET.tostring(sp_tree.getroot(), encoding='UTF-8', method='xml'), timeout=TIME_OUT)
						# cur_clients[client]['url']
					except OSError:
						pprint.pprint('Error: ignoring OSError...')
						continue
					except ConnectionError:
						pprint.pprint('Fatal Error: Connection error...')
						continue

					# pprint.pprint(rp.text)

					rp_tree = ET.fromstring(rp.text)

					if rp_tree.find('.//Errors') != None:
						pprint.pprint('Errors in returns of Child price...')
						continue

					# pprint.pprint(ET.tostring(rp_tree.getroot(), encoding='UTF-8', method='xml'))

					if rp_tree.find('.//SightseeingDetails') == None:
						continue

					if not len(list(rp_tree.find('.//SightseeingDetails'))):
						pprint.pprint('No child sightseeing price returned...')
						continue

					tour_ops = rp_tree.find('.//TourOperations')

					if tour_ops == None:
						pprint.pprint('No Child tour ops returned...')
						continue

					if len(list(tour_ops)) == 1:
						# for t_op in service['tour_operations']:
						for t_op in service[mapped_tour_key]:
							if t_op['min_pax'] == child['min_pax'] and t_op['pax_type'] == 'Adult'and rate_plan['from_date'] == t_op['from_date'] and rate_plan['to_date'] == t_op['to_date']:
								tour_operation['price'] = float(rp_tree.find('.//ItemPrice').text) - float(t_op['price'])
					else:
						# for t_op in service['tour_operations']:
						for t_op in service[mapped_tour_key]:
							if t_op['min_pax'] == child['min_pax'] and t_op['pax_type'] == 'Adult' and rate_plan['from_date'] == t_op['from_date'] and rate_plan['to_date'] == t_op['to_date']:
								tour_operation['prices'] = []			
							
								for tour_op in tour_ops:
									child_tour_name = ''
									if tour_op.find('.//SpecialItem') != None:
										child_tour_name = tour_op.find('.//SpecialItem').text
									else:
										child_tour_name = tour_op.find('.//TourLanguage').text

									child_tour_price = tour_op.find('.//ItemPrice').text
									for adult_tour_op in t_op['prices']:
										if child_tour_name == adult_tour_op['name']:
											op_entry = {}
											op_entry['name'] = child_tour_name
											op_entry['price'] = float(child_tour_price) - float(adult_tour_op['price'])
											tour_operation['prices'].append(op_entry)

					tour_operation['min_pax'] = min_pax
					tour_operation['pax_type'] = 'Child'
					tour_operation['age_from'] = child['age_from']
					tour_operation['age_to'] = child['age_to']

					# service['tour_operations'].append(tour_operation)
					service[mapped_tour_key].append(tour_operation)

			if counter_client == 0:
				services_p.append(service)

	columns = 'country, city_code, item_code, name, duration, summary, please_note, includes, the_tour, additional_information, currency, policy, tour_operations, tour_operations1, tour_operations2, tour_operations3, tour_operations4, tour_operations5, tour_operations6, tour_operations7, closed_dates, thumb_nail, image'

	for service in services_p:
		engine.execute("DELETE FROM destination_service WHERE city_code='{0}' AND item_code='{1}';".format(service['city_code'], service['item_code']))
	for service in services_p:
		if len(service['tour_operations']) != 0:
			r = [service['country'], service['city_code'], service['item_code'], \
				service['name'], service['duration'], service['summary'], \
				service['please_note'], service['includes'], service['the_tour'], service['additional_information'], \
				service['currency'], json.dumps(service['policy']), json.dumps(service['tour_operations']), json.dumps(service['tour_operations1']), json.dumps(service['tour_operations2']), json.dumps(service['tour_operations3']), json.dumps(service['tour_operations4']), json.dumps(service['tour_operations5']), json.dumps(service['tour_operations6']), json.dumps(service['tour_operations7']), \
				json.dumps(service['closed_dates']), service['thumb_nail'], service['image']]
				# with engine.connect() as connection:
					# connection.execute(text("INSERT INTO destination_service ({0}) VALUES({1});".format(columns, ','.join( '\'' + ent.replace('\'', '\'\'') + '\'' for ent in r))).execution_options(autocommit=True) )
					# connection.commit()
			if r == None:
				print('Error: r is none when inserting into database..')
				continue
			engine.execute("INSERT INTO destination_service ({0}) VALUES({1});".format(columns, ','.join( '\'' + ent.replace('\'', '\'\'') + '\'' for ent in r) ))

if __name__ == '__main__':
	updateds()
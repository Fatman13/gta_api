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
import copy
import json

def validate_d(date_text):
	try:
		datetime.datetime.strptime(date_text, '%Y-%m-%d')
	except ValueError:
		raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)

@click.command()
@click.option('--country', default='Canada')
def updateds(country):

	url = 'https://rbs.gta-travel.com/rbscnapi/RequestListenerServlet'
	res = []

	services = []
	services_i = []
	services_p = []

	sp_tree = ET.parse(os.path.join(os.getcwd(), 'SearchSightseeingPriceRequest.xml'))
	si_tree = ET.parse(os.path.join(os.getcwd(), 'SearchItemInformationRequest.xml'))

	engine = create_engine('sqlite:///destServ.db')
	services_raw = engine.execute("SELECT * FROM destination_service_raw WHERE country='{0}';".format(country))

	n_d = datetime.datetime.now().date()

	last_city_code = None
	last_item_code = None
	entry = None

	# Merge raw entries
	for row in services_raw:
		# pprint.pprint(row)

		if not (last_city_code == row['city_code'] and last_item_code == row['item_code']):
			entry = {}
			entry['country'] = row['country']
			entry['city_code'] = row['city_code']
			entry['item_code'] = row['item_code']
			entry['adult_min_pax'] = set()
			entry['child_min_pax'] = []
			entry['rate_plan'] = []
			services.append(entry)

		if row['pax_type'] == 'Adult':
			entry['adult_min_pax'].add(int(row['min_pax']))
		elif row['pax_type'] == 'Child':
			child = {}
			child['age_from'] = row['age_from']
			child['age_to'] = row['age_to']
			child['min_pax'] = int(row['min_pax'])

			if child in entry['child_min_pax'] or int(row['age_to']) < 2:
				last_city_code = row['city_code']
				last_item_code = row['item_code']
				continue

			entry['child_min_pax'].append(child)

		last_city_code = row['city_code']
		last_item_code = row['item_code']

		# pprint.pprint(entry)

	# pprint.pprint(services)

	# Get item info
	for service in services:
		# a = 1
		si_tree.find('.//ItemDestination').set('DestinationCode', service['city_code'])
		si_tree.find('.//ItemCode').text = service['item_code']

		# pprint.pprint(ET.tostring(si_tree.getroot(), encoding='UTF-8', method='xml'))

		try:
			ri = requests.post(url, data=ET.tostring(si_tree.getroot(), encoding='UTF-8', method='xml'), timeout=350)
		except OSError:
			pprint.pprint('Error: ignoring OSError...')
			continue

		ri_tree = ET.fromstring(ri.text)

		if ri_tree.find('.//Errors') != None:
			if not len(list(ri_tree.find('.//Errors'))):
				errors = {}
				for i, er in enumerate(ri_tree.find('.//Errors')):
					if er.find('.//ErrorText') != None:
						errors[str(i)] = er.find('.//ErrorText').text
				pprint.pprint(errors)
				break

		if not len(list(ri_tree.find('.//ItemDetails'))):
			pprint.pprint('No item information returned...')
			continue

		if ri_tree.find('.//Item') != None:
			service['name'] = ri_tree.find('.//Item').text
		else:
			service['name'] = ''
		if ri_tree.find('.//TourSummary') != None:
			service['summary'] = ri_tree.find('.//TourSummary').text
		else:
			service['summary'] = ''
		if ri_tree.find('.//Duration') != None:
			service['duration'] = ri_tree.find('.//Duration').text
		else:
			service['duration'] = ''
		if ri_tree.find('.//TheTour') != None:
			service['more_info'] = ri_tree.find('.//TheTour').text
		else:
			service['more_info'] = ''
		if ri_tree.find('.//Includes') != None:
			service['includes'] = ri_tree.find('.//Includes').text
		else:
			service['includes'] = ''
		if ri_tree.find('.//PleaseNote') != None:
			service['please_note'] = ri_tree.find('.//PleaseNote').text
		else:
			service['please_note'] = ''
		if ri_tree.find('.//AdditionalInformation') != None:
			service['additonal_information'] = ''
		else:
			service['additonal_information'] = ''

		for op in ri_tree.find('.//TourOperations'):
			op_ent = {}
			op_ent['languages'] = []
			if op.find('.//TourLanguages') != None:
				for language in op.find('.//TourLanguages'):
					if language.find('.//TourLanguage') != None:
						op_ent['languages'].append(language.find('.//TourLanguage').text)
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
					dep_ent['meeting_point'] = dep.find('.//DeparturePoint').text
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
		if ri_tree.find('.//Image') != None:
			service['image'] = ri_tree.find('.//Image').text

		# pprint.pprint(service)
		services_i.append(service)

	# pprint.pprint(services_i)
	# pprint.pprint('///////////////////////////////////////////')
			
	# Get price
	for service in services_i:
		sp_tree.find('.//ItemDestination').set('DestinationCode', service['city_code'])
		sp_tree.find('.//ItemCode').text = service['item_code']

		# pprint.pprint('111111111111111111111111111111111')
		# pprint.pprint(ET.tostring(sp_tree.getroot(), encoding='UTF-8', method='xml'))

		service['tour_operations'] = []

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
				# pprint.pprint(ET.tostring(sp_tree.getroot(), encoding='UTF-8', method='xml'))

				try:
					rp = requests.post(url, data=ET.tostring(sp_tree.getroot(), encoding='UTF-8', method='xml'), timeout=600)
				except OSError:
					pprint.pprint('Error: ignoring OSError...')
					continue

				rp_tree = ET.fromstring(rp.text)

				if not len(list(rp_tree.find('.//SightseeingDetails'))):
					pprint.pprint('No sightseeing price returned...')
					continue

				service['currency'] = rp_tree.find('.//ItemPrice').get('Currency')

				service['policy'] = ''
				for charge_condition in rp_tree.find('.//ChargeConditions'):
					if charge_condition.get('Type') == 'cancellation':
						for conditoin in charge_condition:
							if conditoin.get('Charge') == 'true':
								service['policy'] += 'Charge(FromDay: ' + str(conditoin.get('FromDay')) + ' ToDay: ' + str(conditoin.get('ToDay')) + ') '
							else:
								service['policy'] += 'Free(FromDay: ' + str(conditoin.get('FromDay')) + ') '

				tour_ops = rp_tree.find('.//TourOperations')

				if len(list(tour_ops)) == 1:
					tour_operation['price'] = rp_tree.find('.//ItemPrice').text
				else:
					tour_operation['prices'] = []			
					for tour_op in tour_ops:
						op_entry = {}
						if tour_op.find('.//SpecialItem') != None:
							op_entry['name'] = tour_op.find('.//SpecialItem').text
						else:
							op_entry['name'] = tour_op.find('.//TourLanguage').text
						op_entry['price'] = tour_op.find('.//ItemPrice').text
						tour_operation['prices'].append(op_entry)
				tour_operation['min_pax'] = min_pax
				tour_operation['pax_type'] = 'Adult'

				service['tour_operations'].append(tour_operation)
					
		for child in service['child_min_pax']:
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

				try:
					rp = requests.post(url, data=ET.tostring(sp_tree.getroot(), encoding='UTF-8', method='xml'), timeout=600)
				except OSError:
					pprint.pprint('Error: ignoring OSError...')
					continue

				rp_tree = ET.fromstring(rp.text)

				if not len(list(rp_tree.find('.//SightseeingDetails'))):
					pprint.pprint('No sightseeing price returned...')
					continue

				tour_ops = rp_tree.find('.//TourOperations')

				if len(list(tour_ops)) == 1:
					for t_op in service['tour_operations']:
						if t_op['min_pax'] == child['min_pax'] and t_op['pax_type'] == 'Adult'and rate_plan['from_date'] == t_op['from_date']:
							tour_operation['price'] = float(rp_tree.find('.//ItemPrice').text) - float(t_op['price'])
				else:
					for t_op in service['tour_operations']:
						if t_op['min_pax'] == child['min_pax'] and t_op['pax_type'] == 'Adult' and rate_plan['from_date'] == t_op['from_date']:
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

				service['tour_operations'].append(tour_operation)


		pprint.pprint(service)
		services_p.append(service)

	columns = 'country, city_code, item_code, name, duration, summary, please_note, includes, more_info, currency, policy, tour_operations'

	for service in services_p:
		if len(service['tour_operations']) != 0:

			entry = engine.execute("SELECT * FROM destination_service WHERE city_code={0} AND item_code={1};".format('\'' + service['city_code'] + '\'', '\'' + service['item_code'] + '\'') )

			if entry != None:
				updates = []
				for col_name in columns.split(', '):
					updates.append(col_name + '=' + '\'' + service[col_name] + '\'')
				update_str = ', '.join(updates)
				engine.execute("UPDATE destination_service SET {0} WHERE city_code={1} AND item_code={2};".format(update_str, \
					'\'' + service['city_code'] + '\'', '\'' + service['item_code'] + '\'') )
			else:
				r = [service['country'], service['city_code'], service['item_code'], \
					service['name'], service['duration'], service['summary'], \
					service['please_note'], service['includes'], service['more_info'], \
					service['currency'], service['policy'], json.dumps(service['tour_operations'])]
				engine.execute("INSERT INTO destination_service ({0}) VALUES({1});".format(columns, ','.join( '\'' + ent.replace('\'', '\'\'') + '\'' for ent in r) ))

if __name__ == '__main__':
	updateds()
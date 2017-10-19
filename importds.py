#!/usr/bin/env python
# coding=utf-8

import glob
import pprint
import csv
import click 
import datetime as datetime
from xml.etree import ElementTree as ET
import os
from sqlalchemy import create_engine

@click.command()
@click.option('--country', default='Germany')
def importds(country):

	pprint.pprint('Importing... Country: ' + country)

	columns22 = 'country, country_code, city, city_code, currency, item_name, item_code, description, duration, language, dates_from, dates_to, days, min_pax, please_note, conditions, additional_info, pax_type, price, age_from, age_to, commision'
	columns21 = 'country, country_code, city, city_code, currency, item_name, item_code, description, duration, language, dates_from, dates_to, days, min_pax, please_note, conditions, pax_type, price, age_from, age_to, commision'

	engine = create_engine('sqlite:///destServ.db')

	# country = os.path.splitext(os.path.basename(file_name))[0]
	engine.execute("DELETE FROM destination_service_raw WHERE country_code='{0}';".format(country))

	with open(glob.glob(country + '????.csv').pop(), 'r') as csvfile:
		tbl_reader = csv.reader(csvfile, delimiter=',')

		for i, row in enumerate(tbl_reader):
			if i < 11:
				continue

			# if not '%' in row[21]:
				# continue

			if len(row) == 22:
				# pprint.pprint(','.join( '\'' + ent.replace('\'', '\'\'') + '\'' for ent in row[0:22]))
				engine.execute("INSERT INTO destination_service_raw ({0}) VALUES({1});".format(columns22, ','.join( '\'' + ent.replace('\'', '\'\'') + '\'' for ent in row[0:22]) ))
			elif len(row) == 21:
				engine.execute("INSERT INTO destination_service_raw ({0}) VALUES({1});".format(columns21, ','.join( '\'' + ent.replace('\'', '\'\'') + '\'' for ent in row[0:21]) ))
			else:
				pprint.pprint('Error: Wrong Column number ' + str(len(row)) + ' at row ' + str(i))



if __name__ == '__main__':
	importds()
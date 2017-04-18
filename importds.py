#!/usr/bin/env python
# coding=utf-8

import pprint
import csv
import click 
import datetime as datetime
from xml.etree import ElementTree as ET
import os
from sqlalchemy import create_engine

@click.command()
@click.option('--file_name', default='Canada.csv')
def importds(file_name):

	columns = 'country, country_code, city, city_code, currency, item_name, item_code, description, duration, language, dates_from, dates_to, days, min_pax, please_note, conditions, additional_info, pax_type, price, age_from, age_to, commision'

	engine = create_engine('sqlite:///destServ.db')

	country = os.path.splitext(os.path.basename(file_name))[0]
	engine.execute("DELETE FROM destination_service_raw WHERE country='{0}';".format(country))

	with open(file_name, 'r') as csvfile:
		tbl_reader = csv.reader(csvfile, delimiter=',')

		for row in tbl_reader:
			engine.execute("INSERT INTO destination_service_raw ({0}) VALUES({1});".format(columns, ','.join( '\'' + ent.replace('\'', '\'\'') + '\'' for ent in row[0:22]) ))


if __name__ == '__main__':
	importds()
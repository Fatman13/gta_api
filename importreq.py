#!/usr/bin/env python
# coding=utf-8

import pprint
import csv
import click 
import datetime as datetime
from xml.etree import ElementTree as ET
import os
from sqlalchemy import create_engine

index_req = {'ctrip': [2, 6, 7]}

@click.command()
@click.option('--file_name', default='ds_req.csv')
def importds(file_name):

	columns = 'city_code, item_code'

	engine = create_engine('sqlite:///destServ.db')

	engine.execute("DELETE FROM {0};".format('top_selling'))

	with open(file_name, 'r', encoding='utf-8', errors='ignore') as csvfile:
		# tbl_reader = csv.reader(csvfile, delimiter='\t')
		tbl_reader = csv.reader(csvfile)

		for i, row in enumerate(tbl_reader):
			if i == 0:
				continue

			# if row[2] == '':
			# 	# pprint.pprint(row[2])
			# 	continue
			# engine.execute("INSERT INTO {0} ({1}) VALUES({2});".format('top_selling', columns, ','.join( '\'' + ent.replace('\'', '\'\'') + '\'' for ent in [row[index] for index in index_req[client]])))
			engine.execute("INSERT INTO {0} ({1}) VALUES({2});".format('top_selling', columns, ','.join( '\'' + ent.replace('\'', '\'\'') + '\'' for ent in row)))


if __name__ == '__main__':
	importds()
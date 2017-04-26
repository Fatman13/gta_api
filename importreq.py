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
@click.option('--file_name', default='ctrip_ds_prod_list.csv')
@click.option('--client', default='ctrip')
def importds(file_name, client):

	columns = 'gta_code, city, country'

	engine = create_engine('sqlite:///destServ.db')

	engine.execute("DELETE FROM {0};".format(client))

	with open(file_name, 'r', encoding='utf-8', errors='ignore') as csvfile:
		tbl_reader = csv.reader(csvfile, delimiter='\t')

		for i, row in enumerate(tbl_reader):
			if i == 0:
				continue

			if row[2] == '':
				# pprint.pprint(row[2])
				continue

			if not '%' in row[21]:
				continue
			engine.execute("INSERT INTO {0} ({1}) VALUES({2});".format(client, columns, ','.join( '\'' + ent.replace('\'', '\'\'') + '\'' for ent in [row[index] for index in index_req[client]])))


if __name__ == '__main__':
	importds()
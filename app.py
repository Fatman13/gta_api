#!/usr/bin/env python
# coding=utf-8

import sys
if sys.version_info.major == 2:
	reload(sys)
	sys.setdefaultencoding('utf-8')

from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

import pprint
import json
import datetime

import os
 
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secrets.json')) as data_file:
	d_config = (json.load(data_file))
	# app.config['AUTHORIZED_TOKENS'] = (json.load(data_file))['AUTHORIZED_TOKENS']
	app.config['AUTHORIZED_TOKENS'] = d_config['AUTHORIZED_TOKENS']
	# app.config['TOUR_MAPPING'] = (json.load(data_file))['TOUR_MAPPING']
	app.config['TOUR_MAPPING'] = d_config['TOUR_MAPPING']

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///destServ.db'
db = SQLAlchemy(app)

def row2dict(tbl, row):
	d = {}
	for column in tbl.columns:
		d[column.name] = str(getattr(row, column.name))
	return d

def row2dict_p(tbl, row, mapped_tour_column):
	d = {}
	for column in tbl.columns:
		# print('column name: ' + column.name)
		if 'tour_operations' in column.name:
			if column.name == mapped_tour_column:
				d['tour_operations'] = json.loads(str(getattr(row, column.name)))
				# d[column.name] = json.loads(str(getattr(row, column.name)))
				# print(mapped_tour_column)
			continue
		if 'policy' in column.name:
			d[column.name] = json.loads(str(getattr(row, column.name)))
			continue
		if 'closed_dates' in column.name:
			d[column.name] = json.loads(str(getattr(row, column.name)))
			continue
		d[column.name] = str(getattr(row, column.name))
	return d

class topSelling(db.Model):
	__table_args__ = {'sqlite_autoincrement': True}

	id = db.Column(db.Integer, primary_key=True)

	city_code = db.Column(db.String())
	item_code = db.Column(db.String())

	def __init__(self, city_code, item_code):
		self.city_code = city_code
		self.item_code = item_code

	def __repr__(self):
		return "<ctrip id: {0} city_code: {1} item_code: {2}>".format(self.id, self.city_code, self.item_code)


class DestinationService(db.Model):
	__table_args__ = {'sqlite_autoincrement': True}

	id = db.Column(db.Integer, primary_key=True)

	country = db.Column(db.String())
	city_code = db.Column(db.String())
	item_code = db.Column(db.String())

	name = db.Column(db.String())
	duration = db.Column(db.String())
	summary = db.Column(db.String())
	please_note = db.Column(db.String())	
	includes = db.Column(db.String())
	the_tour = db.Column(db.String())
	additional_information = db.Column(db.String())

	currency = db.Column(db.String())
	policy = db.Column(db.String())
	tour_operations = db.Column(db.String())
	tour_operations1 = db.Column(db.String())
	tour_operations2 = db.Column(db.String())
	tour_operations3 = db.Column(db.String())
	tour_operations4 = db.Column(db.String())
	tour_operations5 = db.Column(db.String())
	tour_operations6 = db.Column(db.String())
	tour_operations7 = db.Column(db.String())

	closed_dates = db.Column(db.String())
	thumb_nail = db.Column(db.String())
	image = db.Column(db.String())


	def __init__(self, country, city_code, currency, name, item_code, duration, \
					 please_note, \
					 policy, \
					 summary, includes, the_tour, additional_information, \
					 tour_operations, \
					 tour_operations1, \
					 tour_operations2, \
					 tour_operations3, \
					 tour_operations4, \
					 tour_operations5, \
					 tour_operations6, \
					 tour_operations7, \
					 closed_dates, thumb_nail, image):
		self.country = country
		self.city_code = city_code
		self.currency = currency
		self.name = name
		self.item_code = item_code
		self.summary = summary
		self.duration = duration
		self.please_note = please_note
		self.policy = policy
		self.includes = includes
		self.the_tour = the_tour
		self.additional_information = additional_information
		self.tour_operations = tour_operations
		self.tour_operations1 = tour_operations1
		self.tour_operations2 = tour_operations2
		self.tour_operations3 = tour_operations3
		self.tour_operations4 = tour_operations4
		self.tour_operations5 = tour_operations5
		self.tour_operations6 = tour_operations6
		self.tour_operations7 = tour_operations7
		self.closed_dates = closed_dates
		self.thumb_nail = thumb_nail
		self.image = image

	def __repr__(self):
		return "<DS id: {0} code: {1} name: {2}>".format(self.id, self.city_code + '_' + self.item_code, self.name)

class DestinationServiceRaw(db.Model):
	__table_args__ = {'sqlite_autoincrement': True}

	id = db.Column(db.Integer, primary_key=True)

	country = db.Column(db.String())
	country_code = db.Column(db.String())
	city = db.Column(db.String())
	city_code = db.Column(db.String())
	currency = db.Column(db.String())
	item_name = db.Column(db.String())
	item_code = db.Column(db.String())
	description = db.Column(db.String())	
	duration = db.Column(db.String())
	language = db.Column(db.String())
	dates_from = db.Column(db.String())
	# dates_from = db.Column(db.DateTime)
	# dates_from = db.Column(d)
	dates_to = db.Column(db.String())
	# dates_to = db.Column(db.DateTime)
	# dates_to = db.Column(d)
	days = db.Column(db.String())
	min_pax = db.Column(db.String())
	please_note = db.Column(db.String())
	conditions = db.Column(db.String())
	additional_info = db.Column(db.String())
	pax_type = db.Column(db.String())
	price = db.Column(db.Float)
	age_from = db.Column(db.Integer())
	age_to = db.Column(db.Integer())
	commision = db.Column(db.String())

	def __init__(self, country, country_code, city, city_code, currency, item_name, item_code, description, duration, language, \
					 dates_from, dates_to, days, min_pax, please_note, \
					 conditions, pax_type, price, age_from, age_to, \
					 commision):
		self.country = country
		self.country_code = country_code
		self.city = city
		self.city_code = city_code
		self.currency = currency
		self.item_name = item_name
		self.item_code = item_code
		self.description = description
		self.duration = duration
		self.language = language
		self.dates_from = dates_from
		self.dates_to = dates_to
		self.days = days
		self.min_pax = min_pax
		self.please_note = please_note
		self.conditions = conditions
		self.pax_type = pax_type
		self.price = price
		self.age_from = age_from
		self.age_to = age_to
		self.commision = commision

	def __repr__(self):
		return "<DS_raw id: {0} code: {1} name: {2}>".format(self.id, self.city_code + '_' + self.item_code, self.item_name)

def authorized(fn):
	def _wrap(*args, **kwargs):
		if 'Api-Token' not in request.headers:
			print("No token in header")
			abort(401)
			return None

		if request.headers.get('Api-Token') not in app.config['AUTHORIZED_TOKENS'].keys():
			print("Authorization FAIL!")
			abort(401)
			return None

		return fn(*args, **kwargs)
	return _wrap

@app.route('/destinationServices', methods=['GET'])
@authorized
def ds():
	city_code, item_code = request.args.get('cityCode'), request.args.get('itemCode')
	# pprint.pprint(res)

	q = db.session.query(DestinationService)
	if city_code != None:
		q = q.filter(DestinationService.__table__.c.city_code == city_code)
	if item_code != None:
		q = q.filter(DestinationService.__table__.c.item_code == item_code)

	mapped_tour_column = app.config['TOUR_MAPPING'][app.config['AUTHORIZED_TOKENS'][request.headers.get('Api-Token')]]
	# print(mapped_tour_column)

	data = []
	for row in q.all():
		entry = row2dict_p(DestinationService.__table__, row, mapped_tour_column)
		data.append(entry)
	res = {}
	res['Data'] = data
	return json.dumps(res, ensure_ascii=False)

if __name__ == "__main__":
	app.run()
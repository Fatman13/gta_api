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
	app.config['AUTHORIZED_TOKENS'] = (json.load(data_file))['AUTHORIZED_TOKENS']

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///destServ.db'
db = SQLAlchemy(app)

def row2dict(tbl, row):
	d = {}
	for column in tbl.columns:
		d[column.name] = str(getattr(row, column.name))
	return d

# class DestinationService(db.Model):
# 	id = db.Column(db.Integer, primary_key=True)
# 	country = db.Column(db.String())
# 	country_code = db.Column(db.String())
# 	city = db.Column(db.String())
# 	city_code = db.Column(db.String())
# 	currency = db.Column(db.String())
# 	item_name = db.Column(db.String())
# 	item_code = db.Column(db.String())
# 	duration = db.Column(db.String())
# 	language = db.Column(db.String())
# 	dates_from = db.Column(db.String())
# 	# dates_from = db.Column(db.DateTime)
# 	# dates_from = db.Column(d)
# 	dates_to = db.Column(db.String())
# 	# dates_to = db.Column(db.DateTime)
# 	# dates_to = db.Column(d)
# 	days = db.Column(db.String())
# 	min = db.Column(db.String())
# 	conditions = db.Column(db.String())
# 	pax_type = db.Column(db.String())
# 	price = db.Column(db.Float)
# 	age_from = db.Column(db.Integer())
# 	age_to = db.Column(db.Integer())
# 	commision = db.Column(db.String())
# 	languageCode_list = db.Column(db.String())
# 	specialItem_code = db.Column(db.String())
# 	net_price = db.Column(db.Float)
# 	closed_date = db.Column(db.String())
# 	commentary = db.Column(db.String())
# 	meeting_point = db.Column(db.String())

# 	def __init__(self, id, country, country_code, city, city_code, currency, item_name, item_code, duration, language, \
# 					 dates_from, dates_to, days, min, conditions, pax_type, price, age_from, age_to, \
# 					 commision, languageCode_list, specialItem_code, net_price, closed_date, commentary, meeting_point):
# 		self.id = id
# 		self.country = country
# 		self.country_code = country_code
# 		self.city = city
# 		self.city_code = city_code
# 		self.currency = currency
# 		self.item_name = item_name
# 		self.item_code = item_code
# 		self.duration = duration
# 		self.language = language
# 		self.dates_from = dates_from
# 		self.dates_to = dates_to
# 		self.days = days
# 		self.min = min
# 		self.conditions = conditions
# 		self.pax_type = pax_type
# 		self.price = price
# 		self.age_from = age_from
# 		self.age_to = age_to
# 		self.commision = commision
# 		self.languageCode_list = languageCode_list
# 		self.specialItem_code = specialItem_code
# 		self.net_price = net_price
# 		self.closed_date = closed_date
# 		self.commentary = commentary
# 		self.meeting_point = meeting_point

# 	def __repr__(self):
# 		return "<DS id: {0} code: {1} name: {2}>".format(self.id, self.city_code + '_' + self.item_code, self.item_name)

class ctrip(db.Model):
	__table_args__ = {'sqlite_autoincrement': True}

	id = db.Column(db.Integer, primary_key=True)

	gta_code = db.Column(db.String())
	city = db.Column(db.String())
	country = db.Column(db.String())

	def __init__(self, gta_code, city, country):
		self.gta_code = gta_code
		self.city = city
		self.country = country

	def __repr__(self):
		return "<ctrip id: {0} gta_code: {1} country: {2}>".format(self.id, self.gta_code, self.country)


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

	closed_dates = db.Column(db.String())
	thumb_nail = db.Column(db.String())
	image = db.Column(db.String())


	def __init__(self, country, city_code, currency, name, item_code, duration, \
					 please_note, \
					 policy, \
					 summary, includes, the_tour, additional_information, tour_operations,
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

		if request.headers.get('Api-Token') not in app.config['AUTHORIZED_TOKENS']:
			print("Authorization FAIL!")
			abort(401)
			return None

		return fn(*args, **kwargs)
	return _wrap

@app.route('/destinationServices', methods=['GET'])
@authorized
def ds():
	city_code, item_code, from_d, to_d = request.args.get('cityCode'), request.args.get('itemCode'), request.args.get('fromDate'), request.args.get('toDate') 
	# pprint.pprint('params: ' + str(city_code) + ' a ' + str(item_code) + ' a ' + str(from_d) + ' a ' + str(to_d) )
	# res = services.select(services.c.id == 1).execute().first()
	# pprint.pprint(res)

	q = db.session.query(DestinationService)
	if city_code != None:
		q = q.filter(DestinationService.__table__.c.city_code == city_code)
	if item_code != None:
		q = q.filter(DestinationService.__table__.c.item_code == item_code)

	data = []
	# from_date = datetime.datetime.strptime(from_d, "%Y-%m-%d").date() if from_d != None else None
	# to_date = datetime.datetime.strptime(to_d, "%Y-%m-%d").date() if to_d != None else None
	# pprint.pprint('Dates: ' + str(from_date) + ' ' + str(to_date))
	for row in q.all():
		# if from_date != None and to_date != None:
		# 	# pprint.pprint('Row Dates: ' + str(row.dates_from) + ' ' + str(row.dates_to))
		# 	row_from_date = datetime.datetime.strptime(from_d, "%Y-%m-%d").date()
		# 	row_to_date = datetime.datetime.strptime(from_d, "%Y-%m-%d").date()
		# 	# if row.dates_from >= from_date and row.dates_to <= to_date:
		# 	if row_from_date >= from_date and row_to_date <= to_date:
		# 		# pprint.pprint("True?")
		# 		data.append(row2dict(DestinationService.__table__, row))
		# 	continue
		# row['tour_operations'] = json.loads(row['tour_operations'])
		entry = row2dict(DestinationService.__table__, row)
		entry['tour_operations'] = json.loads(entry['tour_operations'])
		entry['policy'] = json.loads(entry['policy'])
		entry['closed_dates'] = json.loads(entry['closed_dates'])
		# data.append(row2dict(DestinationService.__table__, row))
		data.append(entry)
	res = {}
	res['Data'] = data

	return json.dumps(res, ensure_ascii=False)

if __name__ == "__main__":
	app.run()
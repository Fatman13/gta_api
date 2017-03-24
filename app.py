from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

from sqlalchemy import create_engine, MetaData, Table
import pprint
import json
import datetime

import re
from sqlalchemy.dialects.sqlite import DATE
from sqlalchemy import cast

d = DATE(
		storage_format="%(year)04d/%(month)02d/%(day)02d",
		regexp=re.compile("(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)")
	)

def row2dict(tbl, row):
	d = {}
	for column in tbl.columns:
		d[column.name] = str(getattr(row, column.name))
	return d

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///destServ.db'
db = SQLAlchemy(app)

class DestinationService(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	country = db.Column(db.String())
	country_code = db.Column(db.String())
	city = db.Column(db.String())
	city_code = db.Column(db.String())
	currency = db.Column(db.String())
	item_name = db.Column(db.String())
	item_code = db.Column(db.String())
	duration = db.Column(db.String())
	language = db.Column(db.String())
	# dates_from = db.Column(db.String())
	# dates_from = db.Column(db.DateTime)
	dates_from = db.Column(d)
	# dates_to = db.Column(db.String())
	# dates_to = db.Column(db.DateTime)
	dates_to = db.Column(d)
	days = db.Column(db.String())
	min = db.Column(db.String())
	conditions = db.Column(db.String())
	pax_type = db.Column(db.String())
	price = db.Column(db.Float)
	age_from = db.Column(db.Integer())
	age_to = db.Column(db.Integer())
	commision = db.Column(db.String())
	languageCode_list = db.Column(db.String())
	specialItem_code = db.Column(db.String())
	net_price = db.Column(db.Float)
	closed_date = db.Column(db.String())
	commentary = db.Column(db.String())
	meeting_point = db.Column(db.String())

	def __init__(self, id, country, country_code, city, city_code, currency, item_name, item_code, duration, language, \
					 dates_from, dates_to, days, min, conditions, pax_type, price, age_from, age_to, \
					 commision, languageCode_list, specialItem_code, net_price, closed_date, commentary, meeting_point):
		self.id = id
		self.country = country
		self.country_code = country_code
		self.city = city
		self.city_code = city_code
		self.currency = currency
		self.item_name = item_name
		self.item_code = item_code
		self.duration = duration
		self.language = language
		self.dates_from = dates_from
		self.dates_to = dates_to
		self.days = days
		self.min = min
		self.conditions = conditions
		self.pax_type = pax_type
		self.price = price
		self.age_from = age_from
		self.age_to = age_to
		self.commision = commision
		self.languageCode_list = languageCode_list
		self.specialItem_code = specialItem_code
		self.net_price = net_price
		self.closed_date = closed_date
		self.commentary = commentary
		self.meeting_point = meeting_point

	def __repr__(self):
		# return "<DS %r %r %r>" % self.id, 'c: ' + self.city_code + '_' + self.item_code, 'n: ' + self.item_name
		return "<DS id: {0} code: {1} name: {2}>".format(self.id, self.city_code + '_' + self.item_code, self.item_name)

@app.route('/destinationServices', methods=['GET'])
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
	from_date = datetime.datetime.strptime(from_d, "%Y-%m-%d").date() if from_d != None else None
	to_date = datetime.datetime.strptime(to_d, "%Y-%m-%d").date() if to_d != None else None
	# pprint.pprint('Dates: ' + str(from_date) + ' ' + str(to_date))
	for row in q.all():
		if from_date != None and to_date != None:
			# pprint.pprint('Row Dates: ' + str(row.dates_from) + ' ' + str(row.dates_to))
			if row.dates_from >= from_date and row.dates_to <= to_date:
				# pprint.pprint("True?")
				data.append(row2dict(DestinationService.__table__, row))
			continue


		data.append(row2dict(DestinationService.__table__, row))
	res = {}
	res['Data'] = data

	return json.dumps(res, ensure_ascii=False)


# engine = create_engine('sqlite:///destServ.db', convert_unicode=True)
# metadata = MetaData(bind=engine)
# services = Table('destinationServices', metadata, autoload=True)

# @app.route('/destinationServices', methods=['GET'])
# def ds():
# 	city_code, item_code, from_d, to_d = request.args.get('cityCode'), request.args.get('itemcode'), request.args.get('fromdate'), request.args.get('todate') 
# 	pprint.pprint('params: ' + str(city_code) + ' a ' + str(item_code) + ' a ' + str(from_d) + ' a ' + str(to_d) )
# 	res = services.select(services.c.id == 1).execute().first()
# 	# pprint.pprint(res)
# 	return json.dumps(row2dict(services, res), ensure_ascii=False)

if __name__ == "__main__":
	app.run()

# app.config.from_object('config')
# db = SQLAlchemy(app)

# import sqlite3

# DATABASE = 'destServ.db'

# def connect_db():
# 	return sqlite3.connect(DATABASE)

# @app.before_request
# def before_request():
# 	g.db = connect_db()

# @app.teardown_request
# def teardown_request(exception):
# 	if hasattr(g, 'db'):
# 		g.db.close()

# def query_db(query, args=(), one=False):
# 	cur = g.db.execute(query, args)
# 	rv = [dict((cur.description[idx][0], value)
# 				for idx, value in enumerate(row)) for row in cur.fetchall()]
# 	return (rv[0] if rv else None) if one else rv

# from sqlalchemy.ext.automap import automap_base
# from sqlalchemy.orm import Session
# from sqlalchemy import create_engine
# from sqlalchemy import Table
# from sqlalchemy import Column
# from sqlalchemy.Column import Integer

# # M1
# Base = automap_base()
# engine = create_engine("sqlite:///destServ.db")
# Base.prepare(engine, reflect=True)
# Service = Base.classes.destinationServices
# session = Session(engine)

# from flask_restful import Resource, Api
# api = Api(app)

# class DestinationService(Resource):
# 	def get(self):
# 		query = session.query(Service).first()
# 		# return { 'Data': [i[0] for i in query.cursor.fetchall()] }
# 		return query

# api.add_resource(DestinationService, '/')


# M2
# from sqlalchemy import create_engine, MetaData, Table, Column, ForeignKey
# engine = create_engine("sqlite:///destServ.db")
# metadata = MetaData()
# metadata.reflect(engine, only=['destinationServices'])
# Base = automap_base(metadata=metadata)
# Base.prepare()

# M3
# from sqlalchemy import PrimaryKeyConstraint
# Base = automap_base()
# class Service(Base):
# 	__tablename__ = 'destionationServices'
# 	__table_args__ = (
#         PrimaryKeyConstraint('city_code', 'item_code'),
#     )
# # reflect
# engine = create_engine("sqlite:///destServ.db")
# Base.prepare(engine, reflect=True)

# M4
# Base = automap_base()
# class Service(Base):
# 	__table__ = Table('destinationServices', Base.metadata,
# 		Column('id', Integer, primary_key=True),
# 	)

# # reflect
# engine = create_engine("sqlite:///destServ.db")
# Base.prepare(engine, reflect=True)

# M5
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine, MetaData, Table

# engine = create_engine('sqlite:///destServ.db', echo=False)
# dsmeta = MetaData(engine)
# ds_tbl = Table('destinationServices', dsmeta, autoload=True)

# Session = sessionmaker(bind=engine)
# session = Session()


# class DestinationService(Base):
# 	__table__ = 'destinationservices'
# 	__mapper_args__ = {
# 		# 'primary_key':[destinationservices.c.city_code, destinationservices.c.item_code]
# 		'primary_key':['city_code', 'item_code']
# 	}

# engine, suppose it has two tables 'user' and 'address' set up

# reflect the tables

# mapped classes are now created with names by default
# matching that of the table name.

# session = Session(engine)



# class Service(db.Model):
# 	__tablename__ = 'ds'
# 	# city_code = db.Column()
# 	# city = db.Column()
# 	# country_code = db.Column()
# 	# country = db.Column()
# 	# item_code = db.Column()
# 	# item_name = db.Column()

# 	# def __init__(self, city_code, item_code):
# 	# 	self.city_code = city_code
# 	# 	self.item_code = item_code

# 	def __repr__(self):
# 		return '<Service %r>' % self.city_code + '_' + self.item_code
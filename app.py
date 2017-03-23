from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

from sqlalchemy import create_engine, MetaData, Table
import pprint
import json
import datetime

def row2dict(tbl, row):
	d = {}
	for column in tbl.columns:
		d[column.name] = str(getattr(row, column.name))
	return d

engine = create_engine('sqlite:///destServ.db', convert_unicode=True)
metadata = MetaData(bind=engine)
services = Table('destinationServices', metadata, autoload=True)

@app.route('/', methods=['GET'])
def ds():
	# service = query_db('select * from destinationServices where country_code="CA"')
	res = services.select(services.c.id == 1).execute().first()
	pprint.pprint(res)
	# return res
	return json.dumps(row2dict(services, res), ensure_ascii=False)
	# return row2dict(services, res)
	# return json.dumps(res, cls=AlchemyEncoder)
	# return json.dumps([dict(r) for r in res])
	# return {'data': [dict(zip(tuple (res.keys()) ,i)) for i in res.cursor]}

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
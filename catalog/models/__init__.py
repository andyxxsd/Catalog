import catalog
import traceback
import subprocess
from datetime import datetime
from functools import wraps

from catalog.models.database_setup import Catalog, Base, Item
from sqlalchemy import create_engine, desc, func
from sqlalchemy.orm import sessionmaker, outerjoin

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBsession = sessionmaker(bind=engine)
session = DBsession()


def session_copy_close(f):
	"""Get connection and cursor at the same time"""
	@wraps(f)
	def decorated_function(*args, **kwargs):
		session = DBsession()
		res = f(*args, **kwargs)
		session.close()
		return res 
	return decorated_function

def rebuild():
	"""Rebuild the whole database to initial or debug"""
	conn, cur = connect()
	cur.execute(open(catalog.app.config["REBUILD_SQL"], 'r').read())
	conn.commit()

def test():
	"""Neccessary debug data"""
	Base.metadata.drop_all(engine)
	Base.metadata.create_all(engine)
	c = insert_catalog("Sichuan Dish")
	insert_catalog("Fujian Dish")
	insert_catalog("Guangdong Dish")
	insert_catalog("Zhejiang Dish")
	insert_catalog("Beijing Dish")
	insert_item("Iphone 6 plus", c, 'Is a phone')
	insert_item("Hot pot", c, "Hot hot hot")
	insert_item("Kong Bao Chicken", c, "Classic")

@session_copy_close
def insert_item(name, c, description):
	i = Item(name=name, description=description, updated_time=datetime.now(), catalog=c)
	session.add(i)
	session.commit()
	session.refresh(i)
	return i

@session_copy_close
def insert_catalog(name):
	c = Catalog(name=name)
	session.add(c)
	session.commit()
	session.refresh(c)
	return c

@session_copy_close
def select_catalog(catalog_name):
	return session.query(Catalog).filter_by(name=catalog_name).one()

# Working on
@session_copy_close
def select_catalogs():
	return session.query(
		Catalog.id.label('id'), 
		Catalog.name.label('name'), 
		func.count(Item.id).label('quantity'),
	). outerjoin(Item, Catalog.id == Item.cid). \
	group_by(Catalog.id).all()

@session_copy_close
def select_item_by_id(id):
	return session.query(Item).filter_by(id=id).one()

@session_copy_close
def select_items_by_catalog(c):
	return session.query(
		Item.id.label('id'), 
		Item.name.label('name'), 
		Catalog.name.label('catalog'), 
		Item.updated_time.label('updated_time')
	).join(Catalog, Catalog.id == Item.cid). \
	filter(Item.catalog == c). \
	order_by(Item.updated_time).all()

@session_copy_close
def select_latest_items():
	return session.query(
		Item.id.label('id'), 
		Item.name.label('name'), 
		Catalog.name.label('catalog'), 
		Item.updated_time.label('updated_time')
	).join(Catalog, Catalog.id == Item.cid). \
	order_by(desc(Item.updated_time)).all()

@session_copy_close
def delete_catalog(c):
	session.delete(c)
	session.commit()

@session_copy_close
def delete_item(i):
	session.delete(i)
	session.commit()	












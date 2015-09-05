import catalog
import traceback
import subprocess
from datetime import datetime
from functools import wraps

from catalog.models.database_setup import Catalog, Base, Item, User
from sqlalchemy import create_engine, desc, func
from sqlalchemy.orm import sessionmaker, outerjoin
from flask import current_app as app

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBsession = sessionmaker(bind=engine)
session = DBsession()


def session_copy_close(f):
	"""
		Copy session for each execution.
		Close session after execution.
	"""
	@wraps(f)
	def decorated_function(*args, **kwargs):
		session = DBsession()
		res = f(*args, **kwargs)
		session.close()
		return res 
	return decorated_function

def insert_data():
	"""Necessary good looking data"""
	Base.metadata.drop_all(engine)
	Base.metadata.create_all(engine)
	u1 = insert_user("233@B.com", "/static/image/avatar.JPG")
	u2 = insert_user("fy@B.com", "/static/image/avatar.JPG")
	c = insert_catalog(u1.id, "Sichuan Dish")
	insert_catalog(u1.id, "Fujian Dish")
	insert_catalog(u1.id, "Guangdong Dish")
	insert_catalog(u2.id, "Zhejiang Dish")
	insert_catalog(u2.id, "Beijing Dish")
	insert_item(u1.id, "Iphone 6 plus", c, 'Is a phone', None)
	insert_item(u1.id, "Hot pot", c, "Hot hot hot", None)
	insert_item(u2.id, "Kong Bao Chicken", c, "Classic", None)

@session_copy_close
def insert_user(email, picture):
	user = User(email=email, picture=picture)
	session.add(user)
	session.commit()
	session.refresh(user)
	return user

@session_copy_close
def insert_item(uid, name, c, description, image):
	i = Item(name=name, description=description, updated_time=datetime.now(), catalog=c, created_user=uid, image=image)
	session.add(i)
	session.commit()
	session.refresh(i)
	return i

@session_copy_close
def insert_catalog(uid, name):
	c = Catalog(name=name, created_user=uid)
	session.add(c)
	session.commit()
	session.refresh(c)
	return c

@session_copy_close
def select_user_by_email(email):
	return session.query(User).filter_by(email=email).scalar()

@session_copy_close
def select_catalog(catalog_name):
	return session.query(Catalog).filter_by(name=catalog_name).scalar()

@session_copy_close
def select_catalogs():
	'''
		Output id, name and how many items under this catalog.
	'''
	return session.query(
		Catalog.id.label('id'), 
		Catalog.name.label('name'), 
		func.count(Item.id).label('quantity'),
	). outerjoin(Item, Catalog.id == Item.cid). \
	group_by(Catalog.id).all()

@session_copy_close
def select_catalogs_all():
	return session.query(Catalog).all()

@session_copy_close
def select_items_all():
	return session.query(Item).all()

@session_copy_close
def select_item_by_id(id):
	return session.query(Item).filter_by(id=id).scalar()

@session_copy_close
def select_items_by_catalog(c):
	'''
		Output id, name, name of catalog and updated_time for every items under this catalog.
	'''
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
	'''
		Output id, name, name of catalog and updated_time for latest items.
		Of course, it's descending ordered by updated time.
	'''
	return session.query(
		Item.id.label('id'), 
		Item.name.label('name'), 
		Catalog.name.label('catalog'), 
		Item.updated_time.label('updated_time')
	).join(Catalog, Catalog.id == Item.cid). \
	order_by(desc(Item.updated_time)).all()

@session_copy_close
def update_catalog(c, name):
	c.name = name
	session.add(c)
	session.commit()

@session_copy_close
def update_item(i, name, description, image):
	i.name = name
	i.description = description
	i.image = image
	i.updated_time = datetime.now()
	session.add(i)
	session.commit()	

@session_copy_close
def delete_catalog(c):
	session.delete(c)
	session.commit()

@session_copy_close
def delete_item(i):
	session.delete(i)
	session.commit()	

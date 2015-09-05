import json

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True)
	email = Column(String(80), nullable=False, unique=True)
	picture = Column(String(200))

	@property
	def serialize(self):
		return {
			'id': self.id,
			'email': self.email,
			'picture': self.picture,
		}

class Item(Base):
	__tablename__ = 'items'

	id = Column(Integer, primary_key=True)
	name = Column(String(80), nullable=False, unique=True)
	cid = Column(Integer, ForeignKey('catalogs.id'))
	description = Column(String(300))
	updated_time = Column(DateTime, nullable=True)
	created_user = Column(Integer, ForeignKey('users.id'))

	user = relationship(User, backref='items')
	catalog = relationship('Catalog')

	@property
	def serialize(self):
		return {
			'id': self.id,
			'name': self.name,
			'cid': self.cid,
			'updated_time': self.updated_time.__str__(),
			'created_user': self.created_user,
		}

class Catalog(Base):
	__tablename__ = 'catalogs'

	id = Column(Integer, primary_key=True)
	name = Column(String(80), nullable=False, unique=True)
	created_user = Column(Integer, ForeignKey('users.id'))

	user = relationship(User, backref='catalogs')
	items = relationship(Item, backref='catalogs')

	@property
	def serialize(self):
		return {
			'id': self.id,
			'name': self.name,
			'created_user': self.created_user,	
		}

engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
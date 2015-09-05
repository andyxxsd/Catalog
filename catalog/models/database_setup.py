import sys

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Catalog(Base):
	__tablename__ = 'catalogs'

	id = Column(Integer, primary_key=True)
	name = Column(String(80), nullable=False, unique=True)
	created_time = Column(DateTime, nullable=True)


class Item(Base):
	__tablename__ = 'items'

	id = Column(Integer, primary_key=True)
	name = Column(String(80), nullable=False, unique=True)
	cid = Column(Integer, ForeignKey('catalogs.id'))
	created_time = Column(DateTime, nullable=True)
	updated_time = Column(DateTime, nullable=True)
	catalog = relationship(Catalog)

engine = create_engine(`sqlite:///catalog.db`)
Base.metadata.create_all(engine)
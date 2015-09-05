--DROP DATABASE IF EXISTS catalog;
--CREATE DATABASE catalog;
--\c catalog

DROP TABLE IF EXISTS items CASCADE;
CREATE TABLE items(
	id SERIAL PRIMARY KEY,
	name TEXT UNIQUE,
	description TEXT,
	cid SERIAL,
	created_time TIMESTAMP,
	updated_time TIMESTAMP,
	FOREIGN KEY (cid) REFERENCES catalogs(id)
);

DROP TABLE IF EXISTS catalogs CASCADE;
CREATE TABLE catalogs(
	id SERIAL PRIMARY KEY,
	name TEXT UNIQUE,
	created_time TIMESTAMP
);
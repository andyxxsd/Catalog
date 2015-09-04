import psycopg2
import catalog
import traceback
import subprocess

def connect():
	"""Get connection and cursor at the same time"""
	try:
		db = psycopg2.connect("dbname={}".format(catalog.app.config["DATABASE"]))
		cursor = db.cursor()
		return db, cursor
	except:
		traceback.print_exc()

def rebuild():
	"""Rebuild the whole database to initial or debug"""
	conn, cur = connect()
	cur.execute(open(catalog.app.config["REBUILD_SQL"], 'r').read())
	conn.commit()

def test():
	"""Neccessary debug data"""
	c = insert_catalog("Sichuan Dish")
	insert_catalog("Fujian Dish")
	insert_catalog("Guangdong Dish")
	insert_catalog("Zhejiang Dish")
	insert_catalog("Beijing Dish")
	insert_item("Iphone 6 plus", c["id"])
	insert_item("Hot pot", c["id"])
	insert_item("Kong Bao Chicken", c["id"])

def insert_item(name, cid):
	try:
		conn, cur = connect()
		cur.execute("INSERT INTO items (name, cid, created_time, updated_time) VALUES(%s, %s, now(), now()) RETURNING *", (name, cid,))
		conn.commit()
		return (lambda row: dict(id=row[0], name=row[1], catalog=row[2], updated_time=row[3]))(cur.fetchall())
	except:
		traceback.print_exc()

def insert_catalog(name):
	try:
		conn, cur = connect()
		cur.execute("INSERT INTO catalogs (name, created_time) VALUES(%s, now()) RETURNING *", (name,))
		conn.commit()
		return (lambda row: dict(id=row[0], name=row[1]))(cur.fetchone())
	except:
		traceback.print_exc()

def select_catalogs(offset, limit):
	try:
		conn, cur = connect()
		cur.execute("""SELECT catalogs.id, catalogs.name, count(items.id)
			FROM catalogs LEFT JOIN items on items.cid = catalogs.id
			GROUP BY catalogs.id
			ORDER BY catalogs.created_time ASC
		""")
		res = [dict(id=row[0], name=row[1], quantity=row[2]) for row in cur.fetchall()]
		return [] if len(res) == 0 else res
	except:
		traceback.print_exc()

def select_items_by_cid(cid, offset, limit):
	try:
		conn, cur = connect()
		cur.execute("""SELECT items.id, items.name, catalogs.name, items.updated_time
			FROM items, catalogs
			WHERE catalogs.id = %s AND items.cid = catalogs.id
			ORDER BY updated_time
			LIMIT %s OFFSET %s
		""", (cid, limit, offset,))
		res = [dict(id=row[0], name=row[1], catalog=row[2], updated_time=row[3]) for row in cur.fetchall()]
		return [] if len(res) == 0 else res
	except:
		traceback.print_exc()

def select_cid_by_name(name):
	try:
		conn, cur = connect()
		cur.execute("""SELECT catalogs.id 
			FROM catalogs 
			WHERE catalogs.name = %s 
			LIMIT 1 OFFSET 0
		""", (name,))
		cid = cur.fetchone()
		return None if len(cid) != 1 else cid[0]
	except:
		traceback.print_exc()

def select_latest_items(offset, limit):
	try:
		conn, cur = connect()
		cur.execute("""SELECT items.id, items.name, catalogs.name, items.updated_time
			FROM items, catalogs
			WHERE items.cid = catalogs.id
			ORDER BY updated_time DESC
			LIMIT %s OFFSET %s
		""", (limit, offset,))
		res = [dict(id=row[0], name=row[1], catalog=row[2], updated_time=row[3]) for row in cur.fetchall()]
		return [] if len(res) == 0 else res
	except:
		traceback.print_exc()


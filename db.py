import sqlite3

def get_connection(db_file):
	database = sqlite3.connect(db_file)
	database.execute("PRAGMA foreign_keys = 1")
	return database

class DatabaseOperations():
	""" This class handles database operations - who would have thought.
	"""

	def __init__(self, db_file):
		self.db = get_connection(db_file)
		self.db.row_factory = sqlite3.Row
		self.cursor = self.db.cursor()
		self._setup()

	def _setup(self):
		self.cursor.execute('''
			CREATE TABLE IF NOT EXISTS authentication_keys(
				id INTEGER PRIMARY KEY,
				authentication_key TEXT,
				search_quota_left INTEGER,
				generated_at DATETIME
			)
		''')
		self.cursor.execute('''
			CREATE TABLE IF NOT EXISTS search_results(
				id INTEGER PRIMARY KEY,
				path TEXT,
				fb_user_id TEXT,
				fb_phone_number TEXT,
				fb_first_name TEXT,
				fb_last_name TEXT,
				fb_gender TEXT,
				fb_relationship_status TEXT,
				fb_work TEXT,
				fb_hometown TEXT,
				fb_location TEXT,
				fb_country TEXT,
				searched_at DATETIME
			)
		''')
		self.db.commit()

	def insert_new_authentication_key(self, authentication_key, search_quota_left, generated_at):
		self.cursor.execute('''INSERT INTO authentication_keys(authentication_key, search_quota_left, generated_at) VALUES(?,?,?)''', (authentication_key, search_quota_left, generated_at))
		self.db.commit()
		return self.cursor.lastrowid

	def update_authentication_key(self):
		pass

	def get_authentication_key(self, entry_id=None)
		if entry_id != None:
			self.cursor.execute('''SELECT * FROM authentication_keys WHERE search_quota_left > 0''')
        	authentication_key = self.cursor.fetchone()
        else:
			self.cursor.execute('''SELECT * FROM authentication_keys WHERE id =?''', (entry_id))
			authentication_key = self.cursor.fetchone()
		self.db.commit()
		return authentication_key

	def insert_single_search_result(self):
		pass

	def insert_multiple_search_results(self):
		pass

	def delete_database(self):
		pass
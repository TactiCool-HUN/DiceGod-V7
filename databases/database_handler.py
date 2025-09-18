import sqlite3
from icecream import ic


class DatabaseConnection:
	def __init__(self, host):
		self.connection = None
		if host[-3:] == ".db":
			self.host = f"databases/{host}"
		else:
			self.host = f"databases/{host}.db"

	def __enter__(self):
		self.connection = sqlite3.connect(self.host)
		return self.connection

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.connection.commit()
		self.connection.close()


# ENSURE TABLES
with DatabaseConnection("utils") as connection:
	cursor = connection.cursor()
	
	# - - - colors - - -
	cursor.execute(
		'CREATE TABLE IF NOT EXISTS colors('
			'hex_code text,'
			'name text,'
			'PRIMARY KEY (hex_code),'
			'UNIQUE (name)'
		')'
	)
	
	# add base colors
	try:
		with open("databases/base_data/colors.txt") as file:
			colors = file.readlines()
		for color in colors:
			cursor.execute(
				'INSERT INTO colors(hex_code, name) VALUES (?, ?)',
				(
					color.split("=")
				)
			)
	except Exception as e:
		ic(f'base data filling error:\n{e}')

with DatabaseConnection("meta") as connection:
	cursor = connection.cursor()
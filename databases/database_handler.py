import sqlite3
from icecream import ic


class DatabaseConnection:
	def __init__(self, host):
		self.connection = None
		if host[-3:] == '.db':
			self.host = f'databases/{host}'
		else:
			self.host = f'databases/{host}.db'

	def __enter__(self):
		self.connection = sqlite3.connect(self.host)
		return self.connection

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.connection.commit()
		self.connection.close()


# ENSURE TABLES
with DatabaseConnection('data') as connection:
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
	# - - - people - - -
	cursor.execute(
		'CREATE TABLE IF NOT EXISTS people('
		'id integer,'
		'name text,'
		'discord_id integer,'
		'permission_level integer default 0,'
		'color text default "0x000000",'
		'PRIMARY KEY (id),'
		'UNIQUE (discord_id)'
		')'
	)
	# - - - titles - - -
	cursor.execute(
		'CREATE TABLE IF NOT EXISTS titles('
		'title text,'
		'person_id integer not null,'
		'tier text not null,'
		'PRIMARY KEY (title)'
		')'
	)
	# - - - chatbot silences - - -
	cursor.execute(
		'CREATE TABLE IF NOT EXISTS chatbot_silences('
		'id integer,'
		'guild_id integer not null,'
		'sub_id integer not null,'
		'type text not null,'
		'PRIMARY KEY (id),'
		'UNIQUE (guild_id, sub_id, type)'
		')'
	)

	# add creator
	try:
		cursor.execute(
			'INSERT OR IGNORE INTO people(discord_id, permission_level) VALUES (?, ?)',
			(
				282869456664002581,
				4
			)
		)
	except Exception as e:
		ic(f'base data filling error:\n{e}')
	
	# add base colors
	try:
		with open('databases/base_data/colors.txt') as file:
			colors = file.readlines()
		for color in colors:
			cursor.execute(
				'INSERT OR IGNORE INTO colors(hex_code, name) VALUES (?, ?)',
				(
					color.split("=")
				)
			)
	except Exception as e:
		ic(f'base data filling error:\n{e}')
	
	# add base silences
	try:
		cursor.execute(
			'INSERT OR IGNORE INTO chatbot_silences('
			'guild_id, sub_id, type) VALUES (?, ?, ?)',
			(
				996065301055688794,  # dicegod sanctuary
				562373378967732226,  # rpg corner
				'category'
			)
		)
		cursor.execute(
			'INSERT OR IGNORE INTO chatbot_silences('
			'guild_id, sub_id, type) VALUES (?, ?, ?)',
			(
				1032650247622639686,  # void
				562373378967732226,  # rpg corner
				'channel'
			)
		)
	except Exception as e:
		ic(f'base data filling error:\n{e}')

pass

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
	cursor.execute("PRAGMA foreign_keys = ON;")
	# - - - people - - -
	cursor.execute(
		'CREATE TABLE IF NOT EXISTS people('
		'id integer,'
		'name text,'
		'discord_id integer,'
		'permission_level integer default 0,'
		'color text default "0x000000",'
		'chat_ignore integer default 0,'
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
	# - - - responses - - -
	cursor.execute(
		'CREATE TABLE IF NOT EXISTS responses('
		'id integer,'
		'response text,'
		'PRIMARY KEY (id),'
		'UNIQUE(response)'
		')'
	)
	# - - - con_response_people - - -
	cursor.execute(
		'CREATE TABLE IF NOT EXISTS con_response_person('
		'person_id integer not null,'
		'response_id integer not null,'
		'PRIMARY KEY (person_id, response_id),'
		'FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE, '
		'FOREIGN KEY (response_id) REFERENCES responses(id) ON DELETE CASCADE'
		')'
	)
	# - - - silent_area - - -
	cursor.execute(
		'CREATE TABLE IF NOT EXISTS silent_areas('
		'id integer not null,'
		'type text not null,'
		'PRIMARY KEY (id)'
		')'
	)

	# add creator
	try:
		cursor.execute(
			'INSERT OR IGNORE INTO people('
			'name, discord_id, permission_level, color'
			') VALUES (?, ?, ?, ?)',
			(
				'tacticool_',
				282869456664002581,
				4,
				'0x4177b3'
			)
		)
		cursor.execute(
			'INSERT OR IGNORE INTO titles('
			'title, person_id, tier'
			') VALUES (?, (SELECT id FROM people WHERE discord_id = 282869456664002581), ?)',
			(
				'Creator',
				'major'
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

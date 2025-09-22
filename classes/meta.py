import classes.meta_support as cms
import discord
import discord.ext
from databases.database_handler import DatabaseConnection
from utils.bot_setup import bot
import utils.tools as t


class Person:
	def __init__(self, identifier: str | int | discord.ext.commands.Context | discord.Interaction | discord.User | discord.Member = None, db_id: int = -1, **kwargs):
		"""
		:param identifier: str (user_name in db) | int (discord id) | discord.User | discord.Member
		:param db_id:
		"""
		self.db_id: int = db_id
		self.user_name: str = ''
		self.user: discord.User | None = None
		self.member: discord.Member | None = None

		self.permission_level: cms.PermissionLevel | None = None
		self.settings: cms.PersonalSettings = cms.PersonalSettings()

		self._load(identifier, **kwargs)

	def _new(self):
		if self.user is not None:
			user_id = self.user.id
			self.user_name = self.user.name
		else:
			user_id = None

		with DatabaseConnection('data') as con:
			cursor = con.cursor()
			cursor.execute(
				'INSERT INTO people('
				'name,'
				'discord_id'
				') VALUES (?, ?)',
				(
					self.user_name,
					user_id
				)
			)

	def _load(self, identifier: str | int | discord.ext.commands.Context | discord.Interaction | discord.User | discord.Member, **kwargs):
		if isinstance(identifier, discord.Interaction):
			identifier = identifier.user
		if isinstance(identifier, discord.ext.commands.Context):
			identifier = identifier.author
		
		if self.db_id != -1:
			with DatabaseConnection('data') as con:
				cursor = con.cursor()
				cursor.execute(
					'SELECT * FROM people WHERE id = ?',
					(self.db_id,)
				)
				raw: list[list] = cursor.fetchall()

			if len(raw) > 1:
				raise ValueError('Too many People found in database.')
			elif len(raw) == 0:
				raise ValueError(f'Person does not exist in database. (tried to load person from db_id: {self.db_id})')
		else:
			if isinstance(identifier, str):
				self.user_name = identifier
			elif isinstance(identifier, int):
				self.user = bot.get_user(identifier)
				if self.user is None:
					raise ValueError(f"Person class got integer type identifier, but it wasn't a discord ID. (identifier: {identifier})")
			elif isinstance(identifier, discord.User):
				self.user = identifier
			elif isinstance(identifier, discord.Member):
				self.user = bot.get_user(identifier.id)
				if self.user is None:
					raise ValueError(f"Person class got Member type identifier, but it couldn't find a Person based on the Member's ID.")
				self.member = identifier
			else:
				raise TypeError(
					f"Person class identifier is a non-allowed type. (identifier type: {type(identifier)}\nAllowed types: string (as user_name in db), integer (as discord id), discord.User, discord.Member"
				)

			if self.user_name:
				with DatabaseConnection('data') as con:
					cursor = con.cursor()
					cursor.execute(
						'SELECT * FROM people WHERE name = ?',
						(self.user_name,)
					)
					raw: list[list] = cursor.fetchall()
			else:
				with DatabaseConnection('data') as con:
					cursor = con.cursor()
					cursor.execute(
						'SELECT * FROM people WHERE discord_id = ?',
						(self.user.id,)
					)
					raw: list[list] = cursor.fetchall()

			if len(raw) > 1:
				raise ValueError("Too many People found in database.")
			elif len(raw) == 0:
				if self.user:
					self._new()
					self._load(identifier)
					return
				else:
					raise ValueError('Person does not exist in database.')

		raw: list = raw[0]
		self.db_id = raw[0]
		self.user_name = raw[1]
		if raw[2]:
			self.user: discord.User = bot.get_user(raw[2])
		self.permission_level = cms.PermissionLevel(raw[3], **kwargs)
		if raw[4]:
			self.settings.color = raw[4]
		if raw[5]:
			self.settings.chat_ignore = raw[5]

	def update(self):
		with DatabaseConnection('data') as con:
			cursor = con.cursor()
			cursor.execute(
				'UPDATE people '
				'SET permission_level = ?, '
				'chat_ignore = ?, '
				'color = ? '
				'WHERE id = ?',
				(
					int(self.permission_level),
					int(self.settings.chat_ignore),
					str(self.settings.color),
					self.db_id
				)
			)

	def get_titles(self):
		with DatabaseConnection('data') as con:
			cursor = con.cursor()
			cursor.execute(
				'SELECT title, tier FROM titles WHERE person_id = ?',
				(self.db_id,)
			)
			return cursor.fetchall()

	def get_random_title(self, include_name: bool = False) -> str:
		titles = self.get_titles()

		if titles:
			temp = dict()
			for person_title in titles:
				temp[person_title[0]] = int(person_title[1] == 'major') + 1
			temp = t.choice(temp)
			if temp[:4].lower() == 'the':
				title = f'{temp}'
			else:
				title = f'the {temp}'
		else:
			title = ''

		if include_name:
			if title:
				return f'{self.user.display_name}, {title}'
			else:
				return f'{self.user.display_name}, *an* Untitled'
		else:
			return title

	def add_response(self, response):
		for line in self.get_responses():
			if response == line[0]:
				return False

		with DatabaseConnection('data') as con:
			cursor = con.cursor()
			cursor.execute(
				'SELECT response FROM responses WHERE response = ?',
				(response,)
			)
			if len(cursor.fetchall()) == 0:
				cursor.execute(
					'INSERT INTO responses(response) VALUES (?)',
					(response,)
				)

			cursor.execute(
				'SELECT id FROM responses WHERE response = ?',
				(response,)
			)
			response_id = cursor.fetchone()

			cursor.execute(
				'INSERT INTO con_response_person('
				'response_id, person_id) VALUES (?, ?)',
				(
					response_id[0],
					self.db_id
				)
			)

		return True

	def get_responses(self):
		with DatabaseConnection('data') as con:
			cursor = con.cursor()
			cursor.execute(
				'SELECT response '
				'FROM responses re '
				'JOIN con_response_person con '
				'ON re.id = con.response_id '
				'JOIN people pe '
				'ON con.person_id = pe.id '
				'WHERE pe.id = ?',
				(self.db_id,)
			)
			return cursor.fetchall()


pass

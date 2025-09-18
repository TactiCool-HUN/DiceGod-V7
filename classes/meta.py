import classes.meta_support as cms
import discord
from databases.database_handler import DatabaseConnection
from utils.bot_setup import bot


class Person:
	def __init__(self, identifier: str | int | discord.User | discord.Member = None, db_id: int = -1, **kwargs):
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
	
	def _load(self, identifier: str | int | discord.User | discord.Member, **kwargs):
		if self.db_id != -1:
			with DatabaseConnection('meta') as con:
				cursor = con.cursor()
				cursor.execute(
					'SELECT * FROM people WHERE id = ?',
					(self.db_id,)
				)
				raw: list[list] = cursor.fetchall()

			if len(raw) > 1:
				raise ValueError('Too many People found in database.')
			elif len(raw) == 0:
				raise ValueError('Person does not exist in database.')
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
				with DatabaseConnection('meta') as con:
					cursor = con.cursor()
					cursor.execute(
						'SELECT * FROM people WHERE user_name = ?',
						(self.user_name,)
					)
					raw: list[list] = cursor.fetchall()
			else:
				with DatabaseConnection('meta') as con:
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
		self.active_character = raw[4]
		self.settings.color = raw[5]

pass

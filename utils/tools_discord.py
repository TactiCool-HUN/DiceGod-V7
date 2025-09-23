import discord.ext
import classes.meta as cm
import classes.dicebot as cd
import utils.tools as t
import databases.constants as c


async def send_message(
		identifier: discord.TextChannel | discord.Message | discord.Interaction | discord.ext.commands.Context | discord.Member | cm.Person,
		text: str = '',
		**kwargs
) -> discord.Message:
	"""
	:param identifier: TextChannel | Message | Interaction | Context | Member | Person
	:param text: str
	:key ephemeral: bool
	:key reply: bool
	:key silent: bool
	:key embed: embed
	:key edit_original_response: bool
	:return: discord.Message
	"""
	ephemeral: bool = kwargs.get('ephemeral', False)
	reply: bool = kwargs.get('reply', False)
	silent: bool = kwargs.get('silent', True)
	embed: discord.Embed | None = kwargs.get('embed', None)
	poll: discord.Poll | None = kwargs.get('poll', None)
	edit_original_response: bool = kwargs.get('edit_original_response', False)

	sent: discord.Message | None = None

	match type(identifier):
		case discord.Interaction:
			identifier: discord.Interaction
			try:
				# noinspection PyUnresolvedReferences
				sent: discord.Message = await identifier.response.send_message(
					content = text,
					embed = embed,
					poll = poll,
					silent = silent,
					ephemeral = ephemeral,
				)
			except discord.InteractionResponded:
				if edit_original_response:
					sent: discord.Message = await identifier.edit_original_response(
						content = text,
						embed = embed,
						poll = poll,
					)
				else:
					sent: discord.Message = await identifier.followup.send_message(
						content = text,
						embed = embed,
						poll = poll,
						silent = silent,
						ephemeral = ephemeral
					)
		case discord.ext.commands.Context | discord.Message:
			if isinstance(identifier, discord.Message):
				reply = True
				identifier: discord.Message
			else:
				identifier: discord.ext.commands.Context

			if reply:
				sent: discord.Message = await identifier.reply(
					content = text,
					embed = embed,
					poll = poll,
					silent = silent
				)
			else:
				sent: discord.Message = await identifier.send(
					content = text,
					embed = embed,
					poll = poll,
					silent = silent
				)
		case discord.User | discord.Member | cm.Person:
			if isinstance(identifier, cm.Person):
				user: discord.User = identifier.user
			else:
				user: discord.User | discord.Member = identifier

			channel = await user.create_dm()
			sent: discord.Message = await channel.send(
				content = text,
				embed = embed,
				poll = poll,
				silent = silent
			)
		case discord.TextChannel:
			identifier: discord.TextChannel
			sent: discord.Message = await identifier.send(
				content = text,
				embed = embed,
				poll = poll,
				silent = silent
			)
		case _:
			raise TypeError(f"invalid Identifier type in dt.send_message()\nIdentifier type: {type(identifier)}\nIdentifier: {identifier}")

	if sent is None:
		raise ValueError('sent is none?!')
	else:
		return sent


def roll_recursive_builder(roll_pieces: list[cd.RollPiece]) -> str:
	builder = []
	for part in roll_pieces:
		if part.type == 'roll_piece':
			builder.append(roll_recursive_builder(part.value))
		elif part.type == 'die':
			builder.append(str(part.value))
		else:
			builder.append(str(part.value))
		if part.damage_type is not None:
			builder.append(c.DAMAGE_TYPES[part.damage_type])
	
	return f"({' '.join(builder)})"


async def send_roll(
		identifier: discord.Interaction | discord.ext.commands.Context,
		roll_pieces: list[list[cd.RollPiece]]
):
	roll_summary = roll_pieces[1]
	roll_pieces = roll_pieces[0]
	
	builder = []
	for part in roll_summary:
		if part.type == 'operator':
			if part == '-':
				builder.append(':no_entry:')
			else:
				builder.append(f'**{part}**')
		else:
			builder.append(t.num2emoji(int(part.value)))
			if part.damage_type is not None:
				builder.append(c.DAMAGE_TYPES[part.damage_type])
	
	title = f'**Roll Result:** {"".join(builder)}'
	
	description = roll_recursive_builder(roll_pieces)[1:-1].replace('*', '\*')
	if description[0] == '-':
		description = '\\' + description

	person = cm.Person(identifier)

	embed = discord.Embed(
		title = title,
		description = description,
		color = person.settings.color
	)
	
	for piece in roll_pieces:
		if piece.type == 'die':
			die = piece.value
			embed.add_field(name = f'{die.amount}d{die.size}', value = '')

	embed.set_footer(text = f'{person.get_random_title(include_name = True)}', icon_url = person.user.avatar.url)

	await send_message(
		identifier,
		'',
		embed = embed,
		reply = True
	)


async def send_pack(
		identifier: discord.Interaction | discord.ext.commands.Context,
		packed_roll_pack: list[list[list[cd.RollPiece]]]
):
	pass



class Load:
	"""
	Displays loading, sends error message before throwing the exception
	"""
	def __init__(self, interaction: discord.Interaction | discord.ext.commands.Context, text: str):
		self.interaction = interaction
		self.text = text

	async def __aenter__(self):
		if isinstance(self.interaction, discord.Interaction):
			# noinspection PyUnresolvedReferences
			await self.interaction.response.defer()
		else:
			self.message = await send_message(self.interaction, f'``LOADING``\n``{self.text}``')

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		error = f'DiceGod encountered an error during the processing of:\n``{self.text}``.\n```py\n{exc_type}```Error value```py\n{exc_val}```'
		if exc_type is not None:
			if isinstance(self.interaction, discord.Interaction):
				await self.interaction.edit_original_response(content = error)
			else:
				await self.message.edit(content = error)
		else:
			if isinstance(self.interaction, discord.Interaction):
				pass
			else:
				await self.message.delete()


pass

import discord.ext
import classes.meta as cm
import classes.dicebot as cd
import utils.tools as t


async def send_message(
		identifier: discord.Message | discord.Interaction | discord.ext.commands.Context | discord.Member | cm.Person,
		text: str = '',
		**kwargs
) -> discord.Message:
	"""
	:param identifier: message | interaction | context | member | person
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
	edit_original_response: bool = kwargs.get('edit_original_response', False)

	match type(identifier):
		case discord.Interaction:
			identifier: discord.Interaction
			try:
				# noinspection PyUnresolvedReferences
				sent: discord.Message = await identifier.response.send_message(
					content = text,
					embed = embed,
					silent = silent,
					ephemeral = ephemeral
				)
			except discord.InteractionResponded:
				if edit_original_response:
					sent: discord.Message = await identifier.edit_original_response(
						content = text,
						embed = embed,
					)
				else:
					sent: discord.Message = await identifier.followup.send_message(
						content = text,
						embed = embed,
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
					silent = silent
				)
			else:
				sent: discord.Message = await identifier.send(
					content = text,
					embed = embed,
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
				silent = silent
			)
		case _:
			raise TypeError(f"invalid Identifier type in dt.send_message()\nIdentifier type: {type(identifier)}\nIdentifier: {identifier}")

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
			builder.append(t.get_damage_type_emoji(part.damage_type))
	
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
			builder.append(f'**{part}**')
		else:
			builder.append(t.num2emoji(int(part.value)))
			if part.damage_type is not None:
				builder.append(t.get_damage_type_emoji(part.damage_type))
	
	title = f'**Roll Result:** {"".join(builder)}'
	
	description = roll_recursive_builder(roll_pieces)[1:-1].replace('*', '\*')
	
	embed = discord.Embed(
		title = title,
		description = description,
		#color = color
	)
	
	await send_message(
		identifier,
		'',
		embed = embed
	)


class DeferInteraction:
	"""
	Displays loading or error messages on slash commands even through exceptions.
	"""
	def __init__(self, interaction: discord.Interaction):
		self.interaction = interaction

	async def __aenter__(self):
		# noinspection PyUnresolvedReferences
		await self.interaction.response.defer()

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		if exc_type is not None:
			await self.interaction.edit_original_response(content = f'DiceGod encountered an error.\n```py\n{exc_type}```Error value```py\n{exc_val}```')


pass

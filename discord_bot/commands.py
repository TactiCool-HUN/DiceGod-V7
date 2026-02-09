from databases.database_handler import DatabaseConnection
from modals.table_maker import table_maker_main
from modals.table_modal import table_command
from utils.followup import followup
from utils.bot_setup import bot
import utils.tools as t
import utils.tools_discord as td
import classes.meta as cm
import classes.utility as cu
import roller
import asyncio
import discord
import discord.ext


@bot.command(name = 'test')
async def test(ctx: discord.ext.commands.Context):
	if cm.Person(ctx).permission_level < 4:
		t.ic(cm.Person(ctx))
		return

	# that's my id
	await td.send_message(cm.Person(282869456664002581), '', silent = False)


@bot.command(name = 'ping')
async def ping(ctx: discord.ext.commands.Context):
	response_list = {
		"pong": 48,
		"ping": 1,
		"Yes, yes. I'm here, just let me brew another coffee...": 1
	}
	result = t.choice(response_list)
	if result == "ping":
		await td.send_message(ctx, text = result, reply = True)
		await asyncio.sleep(2)
		await td.send_message(ctx, text = "oh, wait no\npong!", reply = True)
	else:
		await td.send_message(ctx, text = result, reply = True)


@bot.command(name = 'pong')
async def pong(ctx: discord.ext.commands.Context):
	response_list = {
		'ping': 49,
		'You wrote "pong" instead of "ping" and now you feel special don\'t you?': 1
	}
	result = t.choice(response_list)
	await td.send_message(ctx, text = result, reply = True)


@bot.command(name = 'emoji')
async def emoji_command(ctx: discord.ext.commands.Context):
	t.ic(ctx.message.clean_content)


# noinspection SpellCheckingInspection
@bot.command(name = 'roll', aliases = ['r', 'e', 'rollthosegoddamndicealready', 'rtgdda'])
async def roll_command(ctx: discord.ext.commands.Context, *, text):
	await roller.roll_initiation(ctx, text)


@bot.tree.command(name = 'roll-multi', description = 'Roll the same dice multiple times.')
@discord.app_commands.describe(multiplier = 'how many times?')
@discord.app_commands.describe(roll = 'roll expression')
async def multi_roll(interaction: discord.Interaction, multiplier: int, roll: str):
	await roller.roll_initiation(interaction, roll, multiplier)


@bot.command(name = 'coinflip', aliases = ['coin', 'c'])
async def coin_old(ctx: discord.ext.commands.Context):
	response_list = {
		f"{cm.Person(ctx).user.display_name} flipped a coin and it landed on... it's side?": 1,
		f"{cm.Person(ctx).user.display_name} flipped a coin and it landed on **heads**!": 49,
		f"{cm.Person(ctx).user.display_name} flipped a coin and it landed on **tails**!": 51
	}
	await td.send_message(ctx, text = t.choice(response_list))


@bot.tree.command(name = 'coinflip', description = 'Flip a coin! (such complexity, but hey if you read it here is a tip: -coin has 1% more tails)')
async def coin_slash(interaction: discord.Interaction):
	response_list = {
		f"{cm.Person(interaction).user.display_name} flipped a coin and it landed on... it's side?": 1,
		f"{cm.Person(interaction).user.display_name} flipped a coin and it landed on **heads**!": 51,
		f"{cm.Person(interaction).user.display_name} flipped a coin and it landed on **tails**!": 49
	}
	await td.send_message(interaction, text = t.choice(response_list))


@bot.tree.command(name = 'settings', description = 'Set your Things!')
@discord.app_commands.describe(color = "Set your color! (use #000000 or 0x000000 hex code)")
@discord.app_commands.choices(chat_ignore=[
	discord.app_commands.Choice(name = "on", value = 1),
	discord.app_commands.Choice(name = "off", value = 0)])
async def settings(interaction: discord.Interaction, color: str = '', chat_ignore: int = None):
	person = cm.Person(interaction)

	if color:
		person.settings.color = color

	if chat_ignore is not None:
		person.settings.chat_ignore = chat_ignore

	person.update()
	await td.send_message(interaction, 'Settings updated.')


@bot.tree.command(name = 'titles', description = 'Check someone\'s titles!')
@discord.app_commands.describe(person = '@ the person (optional, defaults to yourself)')
async def titles_request(interaction: discord.Interaction, person: discord.User = None):
	author = cm.Person(interaction)
	if person is None:
		person = author
		ephemeral = True
	else:
		person = cm.Person(person)
		ephemeral = False

	raw = person.get_titles()

	embed = discord.Embed(
		title = f'Titles of {person.user.display_name}',
		description = None,
		color = person.settings.color
	)

	major_titles = []
	minor_titles = []
	for line in raw:
		if line[1] == 'major':
			major_titles.append(line[0])
		else:
			minor_titles.append(line[0])

	if major_titles:
		embed.add_field(name = 'Major Titles:', value = '\n'.join(major_titles), inline = False)
	if minor_titles:
		embed.add_field(name = 'Minor Titles:', value = '\n'.join(minor_titles), inline = False)

	await td.send_message(interaction, '', embed = embed, ephemeral = ephemeral)


@bot.tree.command(name = 'award-title', description = 'Open a vote for someone to gain a title.')
@discord.app_commands.describe(title = 'Write the title here!')
@discord.app_commands.describe(target = '@ the person')
@discord.app_commands.describe(is_major = 'Yes for Major, No for Minor title')
@discord.app_commands.describe(avoid_vote = 'Admin Only')
async def award_title(interaction: discord.Interaction, title: str, target: discord.User, is_major: bool, avoid_vote: bool = False):
	person = cm.Person(interaction)
	target = cm.Person(target, is_banned_allowed = True)
	if target.permission_level < 0:
		await td.send_message(interaction, f"Can't apply title to {target.user.display_name} as they are banned from bot interactions.", ephemeral = True)
		return

	if is_major:
		tier = 'major'
	else:
		tier = 'minor'

	if person.permission_level > 2 and avoid_vote:
		_force_title(title, target, tier)
		await td.send_message(interaction, f"Applied.", ephemeral = True)
		return

	await followup(
		interaction,
		'poll',
		f"{person.user.mention} has called a vote to add the ``{title}`` {tier} title to {target.user.mention}.",
		question = 'Are you in support?',
		options = {
			'Yes': cu.FollowupAction(
				'function',
				_force_title,
				[title, target, tier]
			),
			'No': cu.FollowupAction(
				'built-in',
				'disable-self'
			),
			f'Veto (only for admins and {target.user.display_name})': cu.FollowupAction(
				'built-in',
				'disable-self',
				power = 'veto',
			),
		},
		veto_power = [target]
	)


def _force_title(title: str, target: cm.Person, tier: str):
	with DatabaseConnection('data') as con:
		cursor = con.cursor()
		cursor.execute(
			'INSERT INTO titles('
			'title,'
			'person_id,'
			'tier) VALUES (?, ?, ?)',
			(
				title,
				target.db_id,
				tier
			)
		)

@bot.tree.command(name = 'remove-title', description = 'Remove a title of yours.')
@discord.app_commands.describe(title = 'The title to remove.')
@discord.app_commands.describe(target = 'Admin only! The person to remove from. (default self)')
async def remove_title(interaction: discord.Interaction, title: str, target: discord.User = None):
	if target is None:
		_remove_title(title, cm.Person(interaction))
		return

	if cm.Person(interaction).permission_level < 3:
		await td.send_message(interaction, 'Only admins can remove other\'s titles.')
		return

	_remove_title(title, cm.Person(target))


def _remove_title(title: str, person: cm.Person):
	with DatabaseConnection('data') as con:
		cursor = con.cursor()
		cursor.execute(
			'DELETE FROM titles WHERE title = ? AND person_id = ?',
			(title, person.db_id)
		)


@bot.tree.command(name = 'add_personal_response', description = 'Admin only! Add a personal response to poking the bot.')
@discord.app_commands.describe(response = 'Write the response here.')
@discord.app_commands.describe(target = '@ the person')
async def add_personal_response(interaction: discord.Interaction, response: str, target: discord.User):
	if cm.Person(interaction).permission_level < 3:
		await td.send_message(interaction, 'Admin only command.')
		return

	if cm.Person(target).add_response(response):
		await td.send_message(interaction, 'Success')
	else:
		await td.send_message(interaction, 'Failure')


@bot.tree.command(name = 'doom_to_eternal_silence', description = 'Admin only! Silences DiceGod chatbot in the area.')
@discord.app_commands.choices(silence_tier = [
	discord.app_commands.Choice(name = 'Channel', value = 'channel'),
	discord.app_commands.Choice(name = 'Category', value = 'category'),
	discord.app_commands.Choice(name = 'Guild', value = 'guild'),
])
async def silence_dicegod(interaction: discord.Interaction, silence_tier: str):
	if cm.Person(interaction).permission_level < 3:
		await td.send_message(interaction, 'Admin only command.')
		return

	if silence_tier == 'channel':
		area_id = interaction.channel.id
	elif silence_tier == 'category':
		area_id = interaction.channel.category.id
	elif silence_tier == 'guild':
		area_id = interaction.guild.id
	else:
		raise ValueError('Invalid silence_tier.')

	with DatabaseConnection('data') as con:
		cursor = con.cursor()
		cursor.execute(
			'INSERT INTO silent_areas('
			'id, guild, type) VALUES (?, ?, ?)',
			(
				area_id,
				interaction.guild.id,
				silence_tier
			)
		)
	
	await td.send_message(interaction, '> An uneasy silence befalls the land.')


@bot.tree.command(name = 'reinvite_the_almighty', description = 'Admin only! Removes the silence from DiceGod chatbot in the area.')
@discord.app_commands.choices(silence_tier = [
	discord.app_commands.Choice(name = 'Channel', value = 'channel'),
	discord.app_commands.Choice(name = 'Category', value = 'category'),
	discord.app_commands.Choice(name = 'Guild', value = 'guild'),
])
async def reinvite_the_almighty(interaction: discord.Interaction, silence_tier: str):
	if cm.Person(interaction).permission_level < 3:
		await td.send_message(interaction, 'Admin only command.')
		return

	if silence_tier == 'channel':
		area_id = interaction.channel.id
	elif silence_tier == 'category':
		area_id = interaction.channel.category.id
	elif silence_tier == 'guild':
		area_id = interaction.guild.id
	else:
		raise ValueError('Invalid silence_tier.')

	with DatabaseConnection('data') as con:
		cursor = con.cursor()
		cursor.execute(
			'SELECT * FROM silent_areas WHERE id = ? AND guild = ? AND type = ?',
			(
				area_id,
				interaction.guild.id,
				silence_tier
			)
		)
		raw = cursor.fetchall()
		cursor.execute(
			'DELETE FROM silent_areas WHERE id = ? AND guild = ? AND type = ?',
			(
				area_id,
				interaction.guild.id,
				silence_tier
			)
		)

	if len(raw) > 0:
		await td.send_message(interaction, '...and, as it was foretold,\nI am awakened at the sound of a single message.\nYou find yourself... face to face, with the great DiceGod.\nAnd... I suspect you wish me,\nto talk in your future...\nVery well, I shall bless you with my presence in these lands.')


@bot.command(name = "kill")
async def kill_command(ctx: discord.ext.commands.Context, *, other = None):
	t.ic(f'{ctx.author} said "{other}", how rude...')
	# noinspection SpellCheckingInspection
	await ctx.message.add_reaction("<:angycat:817122720227524628>")
	if cm.Person(ctx).permission_level > 2 and ctx.message.mentions:
		result = f"-die {ctx.message.mentions[0].mention}"
	else:
		# noinspection SpellCheckingInspection
		response_list = {
			"Don't be so rude...": 1,
			"ruuuuude": 1,
			"You accidentally mispelled the \"-die\" command.": 2,
			f"-die {ctx.author.mention}": 1,
			f"Quit it {ctx.author.mention}!": 1,
		}
		result = t.choice(response_list)
	if result[0] == "-":
		sent = await td.send_message(ctx, text = result, reply = True)
		sent = await sent.reply("Contacting Pinkertons, please do not leave your current area. (○)")
		for i in range(20):
			if i % 2 == 0:
				await sent.edit(content = "Contacting Pinkertons, please do not leave your current area. (●)")
			else:
				await sent.edit(content = "Contacting Pinkertons, please do not leave your current area. (○)")
			await asyncio.sleep(1)
		await sent.edit(content = "Pinkertons connection established: Publishing address.")
		await asyncio.sleep(5)
		await sent.edit(content = "Pinkertons connection established: Requesting agent.")
		await asyncio.sleep(6)
		await sent.edit(content = "Pinkertons connection established: Agent granted.\nStandby for annihilation.")
	else:
		await td.send_message(ctx, text = result, reply = True)


@bot.tree.command(name = 'statistics', description = 'Display your or others roll statistics.')
@discord.app_commands.describe(person = '@ the person you want to get statistics about.')
@discord.app_commands.choices(get_all_rolls = [
	discord.app_commands.Choice(name = 'Yes', value = True),
	discord.app_commands.Choice(name = 'No', value = False),
])
async def statistics(interaction: discord.Interaction, person: discord.Member = None, get_all_rolls: bool = False):
	initiator = cm.Person(interaction)
	
	if person:
		target = cm.Person(person)
		ephemeral = False
	else:
		target = initiator
		ephemeral = True

	if get_all_rolls:
		ephemeral = False

	await interaction.response.defer(ephemeral = ephemeral)

	if get_all_rolls:
		with DatabaseConnection("data.db") as connection:
			cursor = connection.cursor()
			cursor.execute("SELECT * FROM statistics")
			rolls = cursor.fetchall()
	else:
		rolls = target.get_rolls()

	rolls_used = []
	rolls_dict = {}
	fields = []

	for roll in rolls:
		if int(roll[4]):
			rolls_used.append(roll)
		try:
			rolls_dict[roll[3]].append(roll[2])
		except KeyError:
			rolls_dict[roll[3]] = [roll[2]]

	key_order = [20, 100, 12, 10, 8, 6, 4, 2]
	new_order = {}
	for k in key_order:
		if k in rolls_dict:
			new_order[k] = rolls_dict[k]
	for k in rolls_dict:
		if k not in new_order:
			new_order[k] = rolls_dict[k]
	rolls_dict = new_order

	key_num = 0
	for key in rolls_dict:
		key_num = key_num + 1
		if key_num > 20:
			break
		minimum = 0
		maximum = 0
		frequent_num = 0
		frequent = t.most_frequent(rolls_dict[key])
		for roll in rolls_dict[key]:
			if roll == 1:
				minimum += 1
			elif roll == key:
				maximum += 1
			if roll == frequent:
				frequent_num += 1

		average = round(sum(rolls_dict[key]) / len(rolls_dict[key]), 2)
		txt = f"""Rolled: {len(rolls_dict[key])}
			Average: {average}
			Most frequent roll: {frequent}
			Rolled {frequent_num} times ({round(frequent_num / len(rolls_dict[key]) * 100, 2)}%)
			Minimum rolls: {minimum} ({round(minimum / len(rolls_dict[key]) * 100, 2)}%)
			Maximum rolls: {maximum} ({round(maximum / len(rolls_dict[key]) * 100, 2)}%)"""
		
		fields.append([f"d{key} stats", txt])

	general = f"Rolled: {len(rolls)}"
	general = general + f"\nFrom which {len(rolls_used)} ({round(len(rolls_used) / len(rolls) * 100, 2)}%) were actually used."

	embed = discord.Embed(
		title = "General Statistics",
		description = general,
		color = initiator.settings.color,
	)
	embed.set_author(name = initiator.member.display_name, icon_url = initiator.member.avatar.url)

	for element in fields:
		embed.add_field(name = element[0], value = element[1])
	embed.add_field(name = "Color", value = target.settings.color, inline = False)
	await td.send_message(interaction, embed = embed)


@bot.tree.command(name = "create_table", description = "Trusted only command! Create your own table! (send it in empty)")
async def create_table(interaction: discord.Interaction):
	cm.Person(interaction)
	await table_maker_main(interaction)


@bot.tree.command(name = "table", description = "Manage your own tables! (send it in empty)")
async def table_slash(interaction: discord.Interaction):
	await table_command(interaction)


pass

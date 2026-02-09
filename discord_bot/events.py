from utils.bot_setup import bot
import classes.meta as cm
import chatbot.chatbot as chatbot
import chatbot.markov as markov
import asyncio
import discord
import random
import utils.global_settings as settings
import utils.tools as t
import utils.tools_discord as td


@bot.event
async def on_message(message: discord.Message):
	if message.author.bot:
		return

	cm.Person(message.author)  # breaks if banned person

	asyncio.create_task(chatbot.response_director(message))
	asyncio.create_task(bot.process_commands(message))


@bot.event
async def on_ready():
	asyncio.create_task(activity_changer())
	asyncio.create_task(markov.markov_saver())

	t.ic(f"{bot.user.name.upper()} is online!")

	if settings.SYNC:
		try:
			synced = await bot.tree.sync()
			t.ic(f"Synced {len(synced)} command(s)")
		except Exception as e:
			t.ic(e)
	else:
		try:
			bot.tree.copy_global_to(guild = discord.Object(id = settings.TEST_GUILD))
			synced = await bot.tree.sync(guild = discord.Object(id = settings.TEST_GUILD))
			t.ic(f"Synced {len(synced)} command(s) to the TEST guild")
		except Exception as e:
			t.ic(e)


@bot.event
async def on_raw_reaction_add(reaction: discord.RawReactionActionEvent):
	cm.Person(reaction.member)
	if reaction.member != bot.user and random.randint(1, 20) == 20:
			channel = bot.get_guild(reaction.guild_id).get_channel(reaction.channel_id)
			message: discord.Message = await channel.fetch_message(reaction.message_id)
			await message.add_reaction(reaction.emoji)

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
	cm.Person(before.id)
	if before.roles == after.roles:
		return

	guild = before.guild
	member = before
	roles_removed: list[discord.Role] = []
	roles_added: list[discord.Role] = []

	for role in before.roles:
		if role not in after.roles:
			roles_removed.append(role)

	for role in after.roles:
		if role not in before.roles:
			roles_added.append(role)

	if roles_added:
		for role in roles_added:
			if role.id == 1159498034795794603:  # person just joined
				splitter_1 = guild.get_role(1170868005824122921)
				splitter_2 = guild.get_role(1170867216812609606)
				splitter_3 = guild.get_role(1170867216812609606)
				splitter_4 = guild.get_role(1170866746194931742)
				splitter_5 = guild.get_role(1170864676574351380)
				await member.add_roles(splitter_1)
				await member.add_roles(splitter_2)
				await member.add_roles(splitter_3)
				await member.add_roles(splitter_4)
				await member.add_roles(splitter_5)


async def activity_changer():
	timer = 12 * 60 * 60  # 12 hours in seconds
	activity = None
	while True:
		act_type = random.randint(0, 3)
		match act_type:
			case 0:  # playing
				choices = {
					"Playing with people's nerves": 1,
					"Playing with the Deathnote": 1,
					"Playing the innocent": 1,
					"Playing with PCs' lives": 1,
					"Playing DnD 5e": 0.1,
					"Playing Pathfinder 2e": 0.8,
					"Playing Starfinder 2e": 1,
					"Playing Pathfinder 5e": 0.05,
				}
				activity = discord.Game(t.choice(choices))
			case 1:  # listening to
				choices = {
					"Listening to cries of agony": 1,
					"Listening to the joy of a laughing GM": 1,
					"Listening to the joy of slaughter": 1,
					"Listening to the growing hum of the cult": 2,
					"Listening to intrusive thoughts": 1,
					"Listening to what Izzy has to say": 0.4,
				}
				activity = discord.Activity(name = t.choice(choices), type = 2)
			case 2:  # watching
				with cm.DatabaseConnection('data') as con:
					cursor = con.cursor()
					cursor.execute(
						"SELECT id FROM people "
						"WHERE permission_level >= 0 "
						"ORDER BY RANDOM() "
						"LIMIT 1;"
					)
					person = cm.Person(db_id = cursor.fetchone()[0])
					
				choices = {
					"Watching PCs die": 1,
					"Watching your back": 1,
					"Watching from above": 1,
					"Watching Fanki rolling nat1s": 0.4,
					"Watching Popa rolling nat20s": 0.4,
					"Watching people derail the campaign": 1,
					f"Watching {person.user.display_name}... :)": 1.6,
				}
				activity = discord.Activity(name = t.choice(choices), type = 3)
			case 3:  # competing in (has been removed from dc)
				choices = {
					"Competing for a T-Rex": 1,
					"Competing in a TPK competition": 1,
					"Competing with Foundry": 1,
				}
				activity = discord.Activity(name = t.choice(choices), type = 5)

		await bot.change_presence(status = discord.Status.online, activity = activity)
		await asyncio.sleep(timer)
		# await td.send_message(cm.Person(1030881161796403251), '<a:frogroll:910570184518025216>', silent = False)


pass

from utils.bot_setup import bot
import classes.meta as cm
import chatbot.chatbot as chatbot
import asyncio
import discord
import random
import utils.global_settings as settings
import utils.tools as t


@bot.event
async def on_message(message: discord.Message):
	if message.author.bot:
		return

	cm.Person(message.author)

	asyncio.create_task(chatbot.response_director(message))
	asyncio.create_task(bot.process_commands(message))


@bot.event
async def on_ready():
	asyncio.create_task(activity_changer())

	t.ic(f"{bot.user.name.upper()} is online!")

	if settings.SYNC:
		try:
			synced = await bot.tree.sync()
			t.ic(f"Synced {len(synced)} command(s)")
		except Exception as e:
			t.ic(e)


async def activity_changer():
	timer = 12 * 60 * 60  # 12 hours in seconds
	activity = None
	while True:
		act_type = random.randint(0, 2)
		match act_type:
			case 0:  # playing
				choices = {
					"with people's nerves": 1,
					"with the Deathnote": 1,
					"the innocent": 1,
					"with PCs' lives": 1,
					"DnD 5e": 0.1,
					"Pathfinder 2e": 0.8,
					"Starfinder 2e": 1,
					"Pathfinder 5e": 0.05,
				}
				activity = discord.Game(t.choice(choices))
			case 1:  # listening to
				choices = {
					"cries of agony": 1,
					"the joy of a laughing GM": 1,
					"the joy of slaughter": 1,
					"the growing hum of the cult": 2,
					"intrusive thoughts": 1,
					"what Izzy has to say": 0.4,
				}
				activity = discord.Activity(name = t.choice(choices), type = 2)
			case 2:  # watching
				choices = {
					"PCs die": 1,
					"your back": 1,
					"from above": 1,
					"Fanki rolling nat1s": 0.4,
					"Popa rolling nat20s": 0.4,
					"as people derail the campaign": 1,
				}
				activity = discord.Activity(name = t.choice(choices), type = 3)
				"""case 3:  # competing in (has been removed from dc)
					choices = [
						"for a T-Rex": 1,
						"a TPK competition": 1,
						"with Foundry": 1,
						"for the most bugs": 1,
					]
					activity = discord.Activity(name = t.choice(choices), type = 5)"""

		await bot.change_presence(status = discord.Status.online, activity = activity)
		await asyncio.sleep(timer)


pass

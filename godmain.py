from databases.constants import LAUNCH_GOD
import utils.bot_setup as bot
import discord_bot.commands
import discord_bot.events
import logging


logging.getLogger("discord.gateway").setLevel(logging.WARNING)
if LAUNCH_GOD:
	bot.run_bot()  # nothing after this is run

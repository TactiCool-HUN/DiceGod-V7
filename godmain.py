from utils.global_settings import LAUNCH_GOD
import utils.bot_setup as bot
import discord_bot.commands

if LAUNCH_GOD:
	bot.run_bot()  # nothing after this is run

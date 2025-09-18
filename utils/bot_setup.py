from discord.ext import commands
import discord

with open("tokens/prefix.txt", "r") as file:
	prefix = file.readline().strip()

intents = discord.Intents().all()
bot: commands.Bot = commands.Bot(command_prefix = prefix, intents = intents)

bot.remove_command("help")


async def start_bot():
	print('Starting Bot')
	with open("tokens/token.txt", "r") as f:
		_lines_ = f.readlines()

	token = _lines_[0].strip()

	await bot.start(token)


def run_bot():
	print('Starting Bot')
	with open("tokens/token.txt", "r") as f:
		_lines_ = f.readlines()

	token = _lines_[0].strip()
	bot.run(token)


pass

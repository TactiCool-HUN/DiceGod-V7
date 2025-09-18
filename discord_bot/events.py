from utils.bot_setup import bot
#import chatbot.chatbot as chatbot
import asyncio
import discord


@bot.event
async def on_message(message: discord.Message):
	if message.author.bot:
		return

	#asyncio.create_task(chatbot.bot_responses(message))
	asyncio.create_task(bot.process_commands(message))
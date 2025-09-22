import discord
import discord.ext
import classes.meta as cm

async def respond_director(message: discord.Message):
	person = cm.Person(message.author)
	if person.settings.chat_ignore:
		return

	eval('print("hi")')





pass

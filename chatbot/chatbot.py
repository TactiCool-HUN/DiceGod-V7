from utils.bot_setup import bot
from databases.database_handler import DatabaseConnection
import databases.constants as c
import classes.meta as cm
import chatbot.markov as markov
import utils.tools_discord as td
import utils.tools as t
import random
import discord
import asyncio


def in_silent_area(message: discord.Message) -> bool:
	with DatabaseConnection('data') as con:
		cursor = con.cursor()
		cursor.execute(
			'SELECT * FROM silent_areas'
		)
		raw = cursor.fetchall()

	for line in raw:
		if line[2] == 'channel' and message.guild.id == line[1] and message.channel.id == line[0]:
			return True
		elif line[2] == 'category' and message.guild.id == line[1] and message.channel.category.id == line[0]:
			return True
		elif line[2] == 'guild' and message.guild.id == line[0]:
			return True

	return False


def text_rando(text: str, **kwargs) -> str:
	case_rando = kwargs.get('case_rando', True)
	ending_rando = kwargs.get('ending_rando', True)

	if case_rando:
		match random.randint(1, 6):
			case 1:
				text = text.upper()
			case 2:
				text = text.capitalize()
			case _:
				pass

	if ending_rando:
		match random.randint(1, 8):
			case 1:
				text += '.'
			case 2:
				text += '!'
			case 3:
				text += '?'
			case 4:
				text += '?!'
			case _:
				pass

	return text


async def stealthifier(content: str, message: discord.Message, text_to_send: str) -> None:
	if content[0] == '(' and content[-1] == ')':
		text_to_send = '(' + text_to_send + ')'

	await td.send_message(message, text_to_send)


async def response_director(message: discord.Message):
	person = cm.Person(message.author)
	if person.settings.chat_ignore:
		return

	# noinspection PyTypeChecker
	content: str = message.clean_content
	if message.guild.id is not None:
		asyncio.create_task(markov.markov_learner(content, message.guild.id))

	if in_silent_area(message):
		return
	chatty_triggered = False

	if bot.user.mentioned_in(message):
		chatty_triggered = True
	elif 'dicegod' in content.replace(' ', '').lower():
		chatty_triggered = True
	elif 'dg' in content.replace(' ', '').lower():
		chatty_triggered = True

	temp = text_rando('{random_title(True)} has spoken', case_rando = False) + '"'
	temp2 = text_rando('{display_name} has spoken', case_rando = False) + '"'
	if chatty_triggered:
		responses = {
			text_rando('yes'): int(person.permission_level),
			text_rando('no'): 4 - int(person.permission_level),
			text_rando('maybe'): 1,
			'f"' + temp: 0.8,
			'f"' + temp2: 0.2,
			'f"{markov.markovifier()}"': 2,
		}
		for line in person.get_responses():
			responses[line[0]] = 1

		response = t.choice(responses)
		if response[:2] == 'f"':
			response = t.eval_safe(response, {
				'random_title': person.get_random_title,
				'display_name': person.user.display_name,
				'markov.markovifier': markov.markovifier,
				'markov': markov,
			})
		await stealthifier(content, message, response)

	if '69' in content:
		await stealthifier(content, message, text_rando('nice'))
	if 'meme' in content:
		await stealthifier(content, message, text_rando('the DNA of the soul'))
	if 'say what?' in content:
		await stealthifier(content, message, text_rando('what?', ending_rando = False))
	if 'no u' in content or 'no you' in content and random.randint(1, 5) == 1:
		await stealthifier(content, message, text_rando('no u'))

	if random.randint(1, 250) == 169:
		await message.add_reaction(t.choice(c.DG_FAVOURITE_EMOJIS))


pass

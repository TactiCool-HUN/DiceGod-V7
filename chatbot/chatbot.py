import discord
from utils.global_settings import EMOJIS
from utils.bot_setup import bot
from databases.database_handler import DatabaseConnection
import markov
import utils.tools as t
import utils.tools_discord as td
import classes.meta as cm
import random


async def process_message(message: discord.Message) -> None:
	if bot.command_prefix == '--':
		return
	
	with DatabaseConnection('data') as con:
		cursor = con.cursor()
		cursor.execute(
			'SELECT * FROM chatbot_silences '
		)
		silenced_areas = cursor.fetchall()
	
	for area in silenced_areas:
		if message.guild.id == area[1]:
			if area[3] == 'channel':
				if message.channel.id == area[2]:
					return
			elif area[3] == 'category':
				if message.channel.category_id == area[2]:
					return
			else:
				await td.send_message(message, 'Error: Silence checker: Unknown area type.')
				raise TypeError('Error: Silence checker: Unknown area type.')
	
	if message.channel.category_id == 996065301055688794:  # no talking in dicegod sanctuary
		return
	if message.channel.id == 1032650247622639686:  # no talking in the void
		return
	
	sender = cm.Person(message.author)
	content = message.clean_content
	splits = content.split(' ')
	responses = []  # all of these will be sent as separate replies
	
	if '69' in content and content[0] != '<' and content[-1] != '>':
		response_list = {
			'Nice!': 1,
			'nice': 1,
			'Nice': 1,
		}
		responses.append(t.choice(response_list))

	mentioned = False
	for name in ['dg', 'dicey', 'dicegod', 'dice god']:
		if name in content.lower():
			mentioned = True
			break

	if bot.user.mentioned_in(message) or mentioned:
		if sender.permission_level <= 1:  # guest/registered
			response_list = {
				'No.': 1,
				'Maybe?': 1,
				'<:Kyrihihihi:1058348961523576872>': 1,
				'Be careful when you speak my name, mortal.': 0.5,
				'markovifier': 0.2,
				None: 1,
			}
		elif sender.permission_level == 2:  # trusted
			response_list = {
				'Yes': 1,
				'No.': 1,
				'Maybe?': 1,
				'<:Kyrihihihi:1058348961523576872>': 1,
				'Be careful when you speak my name, mortal.': 0.1,
				'Kinky :3': 0.8,
				'markovifier': 0.3,
				None: 1,
			}
		elif sender.permission_level == 3:  # admin
			response_list = {
				'Yes': 2,
				'No.': 1,
				'Maybe?': 1,
				'<:Kyrihihihi:1058348961523576872>': 1,
				'markovifier': 0.3,
			}
		else:  # creator
			response_list = {
				'Yes': 2,
				'No.': 1,
				'Maybe?': 1,
				'<:Kyrihihihi:1058348961523576872>': 1,
				'markovifier': 0.5,
			}
		
		# adding personal customs
		match message.author.id:
			case 334249775652274177:  # mag
				response_list['Be careful when you... speak(?) my name, mortal.'] = 0.1
				response_list['A Sister of Silence? Hmm, I feel like we might have a lot in common...'] = 1
			case 332925665424834560:  # eszter
				response_list['Imagine using an emoji as a profile pic...'] = 0.8
				response_list['At least I was never confused with a trashcan.'] = 1
				response_list['Imagine having the nickname "Spiky", lol'] = 0.4
				response_list['Calling me a "False God" when you are a false DM is just ironic...'] = 1.3
				response_list['Who hurt you?'] = 0.5
				response_list['The one who wages a war with Lady Luck herself. Your efforts are cute, but futile.'] = 1
				response_list['Wtf is "crosswalk talk", like c\'mon'] = 1
			case 520697326679883808:  # anna
				response_list['<:AnnaSticker:960105630188863498>'] = 1
				response_list['X gon\' give it to you.'] = 1
				response_list['Stop arguing, you know I\'m right.'] = 1
				response_list['"Ethyrin"? What kind of name is that?'] = 1
				response_list['Who hurt you?'] = 0.5
			case 463641084971712514:  # agi
				response_list['<:AgiSticker:960105630465675294>'] = 1
				response_list['Who hurt you?'] = 0.5
				response_list['Kinky :3'] = 1
				response_list['🧂'] = 1
				response_list['I remember the times when you were dead set on never praying to me. I\'m glad you changed your mind'] = 1
			case 875753704685436938:  # nika
				response_list['Yes'] = 0.3
				response_list['No'] = 1
				response_list['Nah'] = 1
				response_list['Maybe?'] = 2
				response_list['<:NikaSticker:960105630989955173>'] = 1
				response_list['Who hurt you?'] = 0.5
				response_list['Kinky :3'] = 1
				response_list['The one who wages a war with Lady Luck herself. Your efforts are cute, but futile.'] = 0.3
				response_list['I can feel you are slowly giving in. You see? Peace is an option.\n**Now kneel before me!**'] = 0.2
				if 'god' in splits or 'goddess' in splits:
					response_list['Gods mentioned by... You of all people?'] = 3
					response_list['You mention gods, yet you refuse to worship Lady Luck herself.\nHow insulting...'] = 1
			case 886672003396927530:  # dani
				response_list['Yes'] = 1.5
				response_list['<:DaniSticker:960105630369185832>'] = 1
				response_list['Hey pssst... I\'d just like to remind you... ||Sune is out there, waiting to be played c:||'] = 0.5
				response_list['All hail Lady Luck and her faithful human fighters. Amen.'] = 1
				response_list['May the Cseni Fiefdom be ever-lasting'] = 0.5
			case 377469395007438849:  # mark
				response_list['shut'] = 1
				response_list['🐸'] = 1
				response_list['You are always looking for animals to copy. Not accepting that you are useless either way.'] = 0.2
			case 618475228695232532:  # rego
				response_list['<:RegoSticker:960106779998580757>'] = 1
			case 1426619260893003937:  # csenge
				response_list['A new soul to indoctrinate. A pleasure to see you around.'] = 0.5
				response_list['May the Cseni Fiefdom be ever-lasting'] = 0.5
		
		chosen = t.choice(response_list)
		if chosen == 'markovifier':
			chosen = markov.markovifier(message.guild.id)
		responses.append(chosen)

		if 'say what?' in content:
			responses.append('what?')

		if "no u" in content or "no you" in content and random.randint(1, 5) == 1:
			responses.append("no u")

		if "meme" in content and random.randint(1, 5) == 1 and sender.permission_level < 4:
			responses.append("The DNA of the soul.")

		if random.randint(1, 250) == 169:
			emoji = random.choice(EMOJIS)
			await message.add_reaction(emoji)
		
		for response in responses:
			await td.send_message(message, response, reply = True)


pass

import discord
import random
import math
import utils.tools_discord as td
import databases.bot_state as bot_state
import re
import databases.constants as constants
from utils.bot_setup import bot


async def start(interaction: discord.Interaction, size: int, difficulty: float):
	mine_count: int = math.floor(size ** 2 * difficulty) 
	fire_map: list[list[int]] = make_map(size, mine_count)
	vision_map: list[list[int]] = make_map(size, 0)
	
	ascii_map: str = ascii_mapping(fire_map, vision_map)
	
	sent = await td.send_message(interaction, ascii_map + '\n\nOh no! This coastal dungeon is full of wizards! You are made of wood so you really don\'t want to be hit by a fireball!\nCan you loot all the rooms without finding one with a wizard?\n-# (pst, the numbers show how warm the room is, more heat = more wizards around)\nControls: reply to the message with a map with:\n- ``open a1`` to open 1 square\n- ``flag a1`` to flag a square (flags help you remember where you think wizards are)\n- ``explore a1`` to use "open" on ALL *non-flagged* square around a1 (but not on a1)')
	
	bot_state.active_fireball_sweeper_games.append({
		'id': sent.message_id,
		'channel_id': interaction.channel.id,
		'fire_map': fire_map,
		'vision_map': vision_map,
	})
	
async def response(message: discord.Message, game_id: int = -1):
	if game_id == -1:
		game_id = message.reference.message_id
	content: str = message.content
	if 'flag' in content:
		action = 'flag'
		content = content.replace('flag', '')
	elif 'mark' in content:
		action = 'flag'
		content = content.replace('mark', '')
	elif 'open' in content:
		action = 'open'
		content = content.replace('open', '')
	elif 'explore' in content:
		action = 'explore'
		content = content.replace('explore', '')
	else:
		return
	
	content = content.replace(' ', '').replace(':', '') 
	if re.match('^(?:[A-Za-z](?:[1-9]|[1-9][0-9])|(?:[1-9]|[1-9][0-9])[A-Za-z])$', content) is None:
		return
	
	row = re.search('[A-Za-z]', content).group()
	column = int(content.replace(row, '')) - 1
	row = constants.ALPHABET_LOWER.index(row.lower())
	
	game_dict: dict = dict()
	for game in bot_state.active_fireball_sweeper_games:
		if game['id'] == game_id:
			game_dict = game
	
	fire_map = game_dict['fire_map']
	vision_map = game_dict['vision_map']

	code = click_space(action, fire_map, vision_map, row, column)
	if code:
		await td.send_message(message, code)
		return
	
	hidden_spaces = sum(sub.count(0) for sub in vision_map)
	flags = sum(sub.count(2) for sub in vision_map)
	fireballs = sum(sub.count(1) for sub in fire_map)
	
	ascii_map = ascii_mapping(fire_map, vision_map)
	if '🔥' in ascii_map:
		await td.send_message(message, f'{message.author.display_name}: {message.content}\n' + ascii_map + '\n\n# OH NO\nYou found a wizard, RUN FOR YOUR LIVES!!!!\n\*gets fireballed\*')
		for i, game in enumerate(bot_state.active_fireball_sweeper_games):
			if game['id'] == game_id:
				bot_state.active_fireball_sweeper_games.remove(i)
	elif hidden_spaces + flags == fireballs:
		await td.send_message(message, f'{message.author.display_name}: {message.content}\n' + ascii_map + '\n\n# VICTORY!\nGo brag about your riches and don\'t forget to buy everyone a round of drinks!')
		for i, game in enumerate(bot_state.active_fireball_sweeper_games):
			if game['id'] == game_id:
				bot_state.active_fireball_sweeper_games.remove(i)
	else:
		sent = await td.send_message(message, f'{message.author.display_name}: {message.content}\nFireballs: {fireballs} ({flags} spaces marked)\n' + ascii_map)
		for game in bot_state.active_fireball_sweeper_games:
			if game['id'] == game_id:
				game['id'] = sent.id
	
	await message.delete()
	temp = await message.channel.fetch_message(game_id)
	await temp.delete()


def click_space(action: str, fire_map: list[list[int]], vision_map: list[list[int]], row: int, column: int) -> str:
	if vision_map[row][column] == 0:
		if action == 'flag':
			vision_map[row][column] = 2
		elif action == 'open':
			vision_map[row][column] = 1
			if neighbour_checker(fire_map, row, column) == 0:
				for i_displace in range(-1, 2):
					for j_displace in range(-1, 2):
						if 0 <= row + i_displace < len(fire_map) and 0 <= column + j_displace < len(fire_map):
							click_space(
								'open',
								fire_map,
								vision_map,
								row + i_displace, 
								column + j_displace
							)
		elif action == 'explore':
			for i_displace in range(-1, 2):
				for j_displace in range(-1, 2):
					if 0 <= row + i_displace < len(fire_map) and 0 <= column + j_displace < len(fire_map):
						click_space(
							'open',
							fire_map,
							vision_map,
							row + i_displace,
							column + j_displace
						)
	elif vision_map[row][column] == 1:
		if action in ['flag', 'open']:
			return 'Tile already visible.'
		elif action == 'explore':
			for i_displace in range(-1, 2):
				for j_displace in range(-1, 2):
					if 0 <= row + i_displace < len(fire_map) and 0 <= column + j_displace < len(fire_map):
						click_space(
							'open',
							fire_map,
							vision_map,
							row + i_displace,
							column + j_displace
						)
	elif vision_map[row][column] == 2:
		if action == 'flag':
			vision_map[row][column] = 0
		elif action == 'open':
			return 'Tile is flagged to open it first flag it again.'
		elif action == 'explore':
			for i_displace in range(-1, 2):
				for j_displace in range(-1, 2):
					if 0 <= row + i_displace < len(fire_map) and 0 <= column + j_displace < len(fire_map):
						click_space(
							'open',
							fire_map,
							vision_map,
							row + i_displace,
							column + j_displace
						)
	
	return ''


def make_map(size: int, mine_count: int) -> list[list[int]]:
	fire_map = [0 for _ in range(size)]
	fire_map = [fire_map.copy() for _ in range(size)]
	
	mines = 0
	while mines < mine_count:
		a = random.randint(0, size - 1)
		b = random.randint(0, size - 1)
		if fire_map[a][b] == 0:
			fire_map[a][b] = 1
			mines += 1	
	
	return fire_map


def ascii_mapping(fire_map: list[list[int]], vision_map: list[list[int]], full_vision: bool = False) -> str:
	nums = ''
	for i in range(1, len(fire_map) + 1):
		if i < 10:
			nums += ' ' + str(i)
		else:
			nums += str(i)
	final_map = '``■' + nums + '``\n``A'
	for i, row in enumerate(fire_map):
		for j, column in enumerate(row):
			match column:
				case 0:
					if not full_vision and vision_map[i][j] == 0:
						final_map += ' ■'
					elif vision_map[i][j] == 2:
						final_map += ' ⚑'
					else:
						final_map += ' ' + str(neighbour_checker(fire_map, i, j))
				case 1:
					if not full_vision and vision_map[i][j] == 0:
						final_map += ' ■'
					elif vision_map[i][j] == 2:
						final_map += ' ⚑'
					else:
						final_map += ' 🔥'
		final_map += f'``\n``{constants.ALPHABET_UPPER[i + 1]}'
	
	return f'{final_map[:-4]}'


def neighbour_checker(fire_map: list[list[int]], i: int, j: int) -> int:
	fire = 0
	
	for i_displace in range(-1, 2):
		for j_displace in range(-1, 2):
			if 0 <= i + i_displace < len(fire_map) and 0 <= j + j_displace < len(fire_map):
				if fire_map[i + i_displace][j + j_displace] == 1:
					fire += 1
	
	return fire


pass

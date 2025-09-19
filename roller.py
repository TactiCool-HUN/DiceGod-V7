import discord.ext
from discord.ext.commands import param
from utils.bot_setup import bot
import utils.tools_discord as td
import classes.dicebot as cd


async def roll_initiation(
		identifier: discord.Interaction | discord.ext.commands.Context,
		text: str
):
	text = text.lower().replace(' ', '').replace('\\', '')

	if text[:4] in ['coinflip', 'coin']:
		if isinstance(identifier, discord.Interaction):
			from discord_bot.commands import coin_slash
			await coin_slash(identifier)
		else:
			command = bot.get_command('coinflip')
			# noinspection PyTypeChecker
			await identifier.invoke(command)
		return

	async with td.Load(interaction = identifier, text = text):
		roll_pack = roll_resolve(text)
		await td.send_roll(identifier, roll_pack)
		

def roll_resolve(roll_text_og: str):
	roll_pieces: list[cd.RollPiece] = create_roll_pieces(roll_text_og)
	
	roll_pieces = create_dice(roll_pieces)
	
	# noinspection PyTypeChecker
	# my editor is dumb
	roll_pieces = parentheses_solver(roll_pieces)
	
	roll_summary = evaluate(roll_pieces)
	
	return [roll_pieces, roll_summary]


def create_roll_pieces(incoming_text: str) -> list[cd.RollPiece]:
	current_sequence = None
	roll_pieces: list[cd.RollPiece] = []

	for char in incoming_text:
		if current_sequence == 'number':
			if char.isnumeric():
				# noinspection PyUnboundLocalVariable
				# this variable will always exist if current_sequence has a value
				piece.value += char
				continue
			else:
				piece.value = int(piece.value)
				roll_pieces.append(piece)
				current_sequence = None
		
		if current_sequence == 'damage_type':
			if char == ']':
				roll_pieces.append(piece)
				current_sequence = None
				continue
			else:
				piece.value += char
				continue
		
		if current_sequence == 'roll_modifier':
			if char not in ['+', '-', '*', '/', '(', ')']:
				piece.value += char
				continue
			else:
				roll_pieces.append(piece)
				current_sequence = None
				
		if current_sequence is None:
			if char.isnumeric():
				current_sequence = 'number'
				piece = cd.RollPiece(current_sequence, char)
				continue
			elif char in ['+', '-', '*', '/', 'd']:
				roll_pieces.append(cd.RollPiece('operator', char))
				continue
			elif char == '[':
				current_sequence = 'damage_type'
				piece = cd.RollPiece(current_sequence, '')
				continue
			elif char in ['(', ')']:
				roll_pieces.append(cd.RollPiece('parentheses', char))
			elif roll_pieces[-1].type == 'number' and roll_pieces[-2].type == 'operator' and roll_pieces[-2] == 'd':
				current_sequence = 'roll_modifier'
				piece = cd.RollPiece(current_sequence, char)
				continue
			else:
				raise ValueError('Unexpected value at: roll_resolve() -> new sequence')

	roll_pieces.append(piece)
	return roll_pieces


def create_dice(roll_pieces: list[cd.RollPiece]) -> list[cd.RollPiece]:
	i = 0
	while i < len(roll_pieces):
		if roll_pieces[i].type == 'operator' and roll_pieces[i] == 'd':
			if roll_pieces[i - 1].type == 'number':
				amount = roll_pieces[i - 1]
			elif roll_pieces[i - 1] == ')':
				raise ValueError(f'Cannot process parentheses calculations for dice.')
			else:
				raise ValueError(f'Unexpected non-numeric value next to operational \'d\'!\nValue: {roll_pieces[i - 1]}')
			if roll_pieces[i + 1].type == 'number':
				size = roll_pieces[i + 1]
			elif roll_pieces[i + 1] == '(':
				raise ValueError(f'Cannot process parentheses calculations for dice.')
			else:
				raise ValueError(f'Unexpected non-numeric value next to operational \'d\'!\nValue: {roll_pieces[i + 1]}')
			
			die = cd.Die(amount, size)
			try:
				if roll_pieces[i + 2].type == 'roll_modifier':
					die.modifiers = roll_pieces[i + 2].value
					roll_pieces = roll_pieces[:i - 1] + [cd.RollPiece('die', die)] + roll_pieces[i + 3:]
				else:
					roll_pieces = roll_pieces[:i - 1] + [cd.RollPiece('die', die)] + roll_pieces[i + 2:]
			except IndexError:
				roll_pieces = roll_pieces[:i - 1] + [cd.RollPiece('die', die)] + roll_pieces[i + 2:]
			return create_dice(roll_pieces)

		i += 1

	return roll_pieces


def parentheses_solver(roll_pieces: list[cd.RollPiece]) -> cd.RollPiece:
	i = 0
	start = None
	while i < len(roll_pieces):
		if roll_pieces[i] == '(':
			start = i
		if roll_pieces[i] == ')':
			layer_piece = cd.RollPiece('roll_piece', roll_pieces[start+1:i])
			
			if roll_pieces[i + 1].type == 'damage_type':
				layer_piece.damage_type = roll_pieces[i + 1].value
				roll_pieces = roll_pieces[:start] + [layer_piece] + roll_pieces[i+2:]
			else:
				roll_pieces = roll_pieces[:start] + [layer_piece] + roll_pieces[i+1:]
			i = 0
			continue
		if roll_pieces[i].type == 'damage_type':
			roll_pieces[i - 1].damage_type = roll_pieces[i].value
			del roll_pieces[i]
			continue
		i += 1
	
	return roll_pieces


def evaluate(roll_pieces: list[cd.RollPiece]) -> list[cd.RollPiece]:
	for piece in roll_pieces:
		if piece.type == 'die':
			piece.value.evaluate()
	
	i = 0
	while i < len(roll_pieces):
		if roll_pieces[i].type == 'roll_piece':
			temp = evaluate(roll_pieces[i].value)
			if roll_pieces[i].damage_type is not None:
				for roll_piece in temp:
					roll_piece.damage_type = roll_pieces[i].damage_type
			roll_pieces = roll_pieces[:i] + temp + roll_pieces[i + 1:]
			continue
		i += 2

	i = 1
	while i < len(roll_pieces):
		if roll_pieces[i] == '*':
			temp = cd.RollPiece('number', roll_pieces[i - 1] * roll_pieces[i + 1])
			if roll_pieces[i - 1].damage_type == roll_pieces[i + 1].damage_type:
				temp.damage_type = roll_pieces[i - 1].damage_type
			elif roll_pieces[i - 1].damage_type is None:
				temp.damage_type = roll_pieces[i + 1].damage_type
			elif roll_pieces[i + 1].damage_type is None:
				temp.damage_type = roll_pieces[i - 1].damage_type
			roll_pieces = roll_pieces[:i - 1] + [temp] + roll_pieces[i + 2:]
			continue
		if roll_pieces[i] == '/':
			temp = cd.RollPiece('number', roll_pieces[i - 1] / roll_pieces[i + 1])
			if roll_pieces[i - 1].damage_type == roll_pieces[i + 1].damage_type:
				temp.damage_type = roll_pieces[i - 1].damage_type
			roll_pieces = roll_pieces[:i - 1] + [temp] + roll_pieces[i + 2:]
			continue
		i += 2

	i = 1
	while i < len(roll_pieces):
		if roll_pieces[i] == '+':
			if roll_pieces[i - 1].damage_type == roll_pieces[i + 1].damage_type:
				temp = cd.RollPiece('number', roll_pieces[i - 1] + roll_pieces[i + 1])
				temp.damage_type = roll_pieces[i - 1].damage_type
				roll_pieces = roll_pieces[:i - 1] + [temp] + roll_pieces[i + 2:]
				continue
		if roll_pieces[i] == '-':
			if roll_pieces[i - 1].damage_type == roll_pieces[i + 1].damage_type:
				temp = cd.RollPiece('number', roll_pieces[i - 1] - roll_pieces[i + 1])
				temp.damage_type = roll_pieces[i - 1].damage_type
				roll_pieces = roll_pieces[:i - 1] + [temp] + roll_pieces[i + 2:]
				continue
		i += 2
		
	return roll_pieces


if __name__ == '__main__':
	roll_resolve('2*(1d20adv-(2*1d4))[void]+5[piercing]+4d4/2')


pass

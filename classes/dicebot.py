from utils.errors import ResolvedError, NotResolvedError
import random


class Die:
	def __init__(self, amount, size):
		self.amount: int = int(amount)
		self.size: int = int(size)
		self.is_resolved: bool = False
		# each roll in rolls is [number, bool]
		# where bool if it is used for the total or not
		self.rolls: list[int] = []
		self.total: int | None = None
		self.modifiers: str = ''
		
	def evaluate(self, ignore_resolve_error: bool = False):
		if self.is_resolved and not ignore_resolve_error:
			raise ResolvedError()
		
		actual_amount = self.amount
		rolls_temp = []
		
		if 'adv' in self.modifiers and actual_amount < 2:
			actual_amount = 2
		elif 'dis' in self.modifiers and actual_amount < 2:
			actual_amount = 2
		elif 'emp' in self.modifiers and actual_amount < 2:
			actual_amount = 2
		
		for _ in range(actual_amount):
			roll = random.randint(1, self.size)
			rolls_temp.append([roll, True])
		
		if 'adv' in self.modifiers:
			current = [0, 0]
			for i, roll in enumerate(rolls_temp):
				if roll[1] and roll[0] > current[1]:
					current = [i, roll[0]]
			for i, roll in enumerate(rolls_temp):
				if i != current[0]:
					rolls_temp[i][1] = False
		elif 'dis' in self.modifiers:
			current = [0, rolls_temp + 1]
			for i, result in enumerate(rolls_temp):
				if result[1] and result[0] < current[1]:
					current = [i, result[0]]
			for i, result in enumerate(rolls_temp):
				if i != current[0]:
					rolls_temp[i][1] = False
		elif 'emp' in self.modifiers:
			midpoint = self.size / 2
			current = [0, midpoint]
			for i, result in enumerate(rolls_temp):
				if result[1] and abs(midpoint - result[0]) > abs(midpoint - current[1]):
					current = [i, result[0]]
			for i, result in enumerate(rolls_temp):
				if i != current[0]:
					rolls_temp[i][1] = False
		
		self.total = 0
		for roll in rolls_temp:
			if roll[1]:
				self.total += roll[0]
		
		self.is_resolved = True
	
	def __repr__(self):
		return f'Die({str(self)})'
	
	def __str__(self):
		if self.is_resolved:
			return f'{self.total} [{self.amount}d{self.size}{self.modifiers}]'
		else:
			return f'{self.amount}d{self.size}{self.modifiers}'
	
	def __int__(self):
		if self.is_resolved:
			return self.total
		else:
			raise NotResolvedError
	
	def __eq__(self, other):
		return self.total == other


class RollPiece:
	def __init__(self, my_type: str, my_value):
		self.type: str = my_type
		self.value: int | str | Die | list[RollPiece] = my_value
		self.damage_type: str | None = None
	
	def __repr__(self):
		return f'RollPiece(type = \'{self.type}\', value = {self.value.__repr__()}, damage_type = {self.damage_type})'
	
	def __str__(self):
		return str(self.value)
	
	def __int__(self):
		if self.type in ['number']:
			return int(self.value)
		elif self.type == 'die':
			if self.value.is_resolved:
				return self.value.total
			else:
				raise NotResolvedError
		raise TypeError(f'RollPiece of type \'{self.type}\' cannot be interpreted as an integer.')
	
	def __eq__(self, other):
		return self.value == other
	
	def __add__(self, other):
		return int(self.value) + int(other)
	
	def __sub__(self, other):
		return int(self.value) - int(other)
	
	def __rsub__(self, other):
		return int(other) - int(self.value)

	def __mul__(self, other):
		return int(self.value) * int(other)
	
	def __rmul__(self, other):
		return int(self.value) * int(other)
	
	def __truediv__(self, other):
		return int(self.value) // int(other)
	
	def __rtruediv__(self, other):
		return int(other) // int(self.value)


class Roll:
	def __init__(self, roll_pieces):
		self.roll_pieces: list[RollPiece] = roll_pieces
		self.damage_by_type: dict[str: int]
		
		
	def total(self):
		return sum(self.damage_by_type.values())
		

pass

import string
import random
from icecream import ic
from typing import Any


def split_keep(text: str, separators: str | list[str]) -> list[str]:
	"""
	Will split the string given into a list of strings based on the separator.
	The separator is added to the next substring.
	
	Example: split_keep('1d20', 'd') -> ['1', 'd20']
	
	:param text: string to split
	:param separators: string or list of strings to separate by
	:return: list of strings after split
	"""
	if isinstance(separators, str):
		separators = [separators]
	
	output = []
	builder = ''
	
	for char in text:
		if char in separators:
			output.append(builder)
			builder = char
		else:
			builder = f'{builder}{char}'
	
	output.append(builder)

	return output


def col2num(col: str) -> int:
	"""
	Converts spreadsheet column lettering to index.
	:param col: column letter
	:return: index (0 based)
	"""
	num = 0
	for letter in col:
		if letter in string.ascii_letters:
			num = num * 26 + (ord(letter.upper()) - ord('A')) + 1
	return num - 1


def score2mod(score: int) -> int:
	"""
	Turns D&D type score number to modifier number.
	:param score: score number
	:return: modifier number
	"""
	return (score - 10) // 2


def _num2emoji_recursion(num: int) -> str:
	numbers = [":zero:", ":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:", ":ten:"]
	if num < 10:
		return numbers[num]
	else:
		return f'{_num2emoji_recursion(num // 10)}{numbers[num % 10]}'


def num2emoji(num: int) -> str:
	"""
	Turns a given integer into a string of continuous discord emojis.
	:param num:
	:return:
	"""
	if num < 0:
		negative = True
		num = -1 * num
	else:
		negative = False

	word = _num2emoji_recursion(num)

	if negative:
		word = f':no_entry:{word}'
	return word


def int_get(to_change, on_error = None) -> Any:
	"""
	Acts similarly to a dictionary's .get() but for the int() function.
	Tries to do int(to_change), if fails returns on_error.
	:param to_change: integer-like
	:param on_error: defaults to None
	:return:
	"""
	try:
		return int(to_change)
	except Exception:
		return on_error


def choice(incoming: dict):
	"""
	Weighted random choice.
	:param incoming: dict with keys as choices and their values: int as the weights
	:return:
	"""
	return random.choices(list(incoming.keys()), weights = list(incoming.values()))[0]


def sql_standardizer(value_to_change, output = None):
	"""
	Turns the following data:

	"",

	[],

	[""];

	to the given value in "output".
	:param value_to_change:
	:param output: defaults to None
	:return:
	"""
	none_ables = [
		"",
		[],
		[""]
	]
	if value_to_change in none_ables:
		return output
	else:
		return value_to_change


def eval_safe(template: str, safe_locals: dict = None):
	safe_globals = {
		"__builtins__": {
			"str": str,
			"int": int,
			"float": float,
			"bool": bool,
			"dict": dict,
			"list": list,
			"tuple": tuple,
			"set": set,
		}
	}
	if safe_locals is None:
		safe_locals = dict()

	return eval(template, safe_globals, safe_locals)  # safety-wrapper-eval


class ListIterator:
	"""
	Just required for some python class construction
	"""
	def __init__(self, list_to_iter: list):
		self.i = 0
		self.list_to_iter = list_to_iter

	def __iter__(self):
		return self

	def __next__(self):
		self.i += 1

		try:
			return self.list_to_iter[self.i - 1]
		except IndexError:
			self.i = 0
			raise StopIteration


pass

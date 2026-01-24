import discord


class PersonalSettings:
	def __init__(self):
		self._color: discord.Color | None = None
		self._chat_ignore: bool = False

	@property
	def color(self) -> discord.Color | None:
		return self._color

	@color.setter
	def color(self, value: str):
		self._color = discord.Color.from_str(value)

	@property
	def chat_ignore(self) -> bool:
		return self._chat_ignore

	@chat_ignore.setter
	def chat_ignore(self, value: bool):
		self._chat_ignore = bool(value)


class PermissionLevel:
	def __init__(self, permission: str | int, **kwargs):
		self._permission_level: int = 0

		self._str_to_int: dict[str, int] = {
			'banned': -1,
			'guest': 0,
			'registered': 1,
			'trusted': 2,
			'admin': 3,
			'creator': 4
		}
		self._int_to_str: dict[int, str] = {v: k for k, v in self._str_to_int.items()}
		
		self.permission_level = permission
		if self == -1 and not kwargs.get('is_banned_allowed', False):
			raise PermissionError('Person is banned. If you want to supress this error pass "is_banned_allowed = True" when initiating the Person of PermissionLevel class.')
	
	@property
	def permission_level(self):
		return self._permission_level
	
	@permission_level.setter
	def permission_level(self, new_value: int | str):
		if isinstance(new_value, str):
			new_value = self._str_to_int[new_value]
		if isinstance(new_value, int):
			if self.min() <= new_value <= self.max():
				self._permission_level = new_value
			else:
				raise ValueError(f'PermissionLevel cannot set {new_value} as it is not in the range [{self.min()}, {self.max()}].')
		else:
			raise TypeError(f'PermissionLevel can only be initiated with string or integer')

	def min(self) -> int:
		return min(self._str_to_int.values())
	
	def max(self) -> int:
		return max(self._str_to_int.values())

	def __str__(self):
		return self._int_to_str[self.permission_level]

	def __int__(self):
		return self.permission_level

	def __float__(self):
		return float(self.permission_level)

	def __lt__(self, other):
		return int(self) < int(other)

	def __le__(self, other):
		return int(self) <= int(other)

	def __gt__(self, other):
		return int(self) > int(other)

	def __ge__(self, other):
		return int(self) >= int(other)

	def __eq__(self, other):
		return (int(self) == int(other)) or (str(self) == str(other))

	def __ne__(self, other):
		return not (self == other)


pass

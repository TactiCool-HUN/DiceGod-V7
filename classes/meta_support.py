class PersonalSettings:
	def __init__(self):
		self.color: int | None = None


class PermissionLevel:
	def __init__(self, permission: str | int, **kwargs):
		# swap between name and number
		self._str_to_int: dict[str, int] = {
			'banned': -1,
			'guest': 0,
			'registered': 1,
			'trusted': 2,
			'admin': 3
		}
		self._int_to_str: dict[int, str] = {v: k for k, v in self._str_to_int.items()}
		# ----------------------------

		if isinstance(permission, str):
			self._name: str = permission
			self._num: int = self._str_to_int[self._name]
		elif isinstance(permission, int):
			self._num: int = permission
			self._name: str = self._int_to_str[self._num]
		else:
			raise TypeError(f'PermissionLevel can only be initiated with string or integer')

		if self._num == -1 and not kwargs.get('is_banned_allowed', False):
			raise PermissionError('Person is banned. If you want to supress this error pass "is_banned_allowed = True" when initiating the Person of PermissionLevel class.')

	def __str__(self):
		return self._name

	def __int__(self):
		return self._num

	def __float__(self):
		return self._num

	def __lt__(self, other):
		if isinstance(other, PermissionLevel):
			return self._num < other._num
		else:
			return self._num < other

	def __le__(self, other):
		if isinstance(other, PermissionLevel):
			return self._num <= other._num
		else:
			return self._num <= other

	def __gt__(self, other):
		if isinstance(other, PermissionLevel):
			return self._num > other._num
		else:
			return self._num > other

	def __ge__(self, other):
		if isinstance(other, PermissionLevel):
			return self._num >= other._num
		else:
			return self._num >= other

	def __eq__(self, other):
		if isinstance(other, PermissionLevel):
			return self._num == other._num
		else:
			return self._num == other or self._name == other

	def __ne__(self, other):
		return not (self == other)


pass

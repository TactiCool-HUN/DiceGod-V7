class VersionError(Exception):
	def __init__(self, message):
		super().__init__(message)


class DBError(Exception):
	def __init__(self, message):
		super().__init__(message)


class ResolvedError(Exception):
	def __init__(self, message = 'Die has already been resolved.'):
		super().__init__(message)


class NotResolvedError(Exception):
	def __init__(self, message = 'Die has not been resolved yet.'):
		super().__init__(message)


pass

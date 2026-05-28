import discord


class FollowupAction:
	def __init__(self, action_type: str, value, sub_values = '', note: str = ''):
		"""
		:param action_type: str (function, async-function, built-in)
		:param value: function, async-function, disable-self, str
		:param sub_values: function parameters
		:param note:
		"""
		self.type: str = action_type
		self.value = value
		self.sub_values = sub_values
		self.note: str = note
	
	def __repr__(self):
		return f'FollowupAction(type = {self.type}, value = {self.value})'
	
	def __str__(self):
		if isinstance(self.value, str):
			return f'FollowupAction(type = {self.type}, value = {self.value})'
		else:
			return f'FollowupAction(type = {self.type}, value = {str(self.value)})'


class FollowupView(discord.ui.View):
	def __init__(self):
		super().__init__(timeout = 2 * (24 * 60 * 60))  # 2 * day
		self.message: discord.Message | None = None

	async def on_timeout(self) -> None:
		for button in self.children:
			button.disabled = True
		await self.message.edit(view = self)


pass

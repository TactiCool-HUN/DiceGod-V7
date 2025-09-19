class FollowupAction:
	def __init__(self, action_type: str, value, sub_values = '', power: str = ''):
		self.type: str = action_type
		self.value = value
		self.sub_values = sub_values
		self.power: str = power
	
	def __repr__(self):
		return f'FollowupAction(type = {self.type}, value = {self.value}'


pass

import asyncio
import discord
import discord.ext
from databases.database_handler import DatabaseConnection
import utils.tools_discord as td
import utils.tools as t
from roller import roll_initiation
from utils.bot_setup import bot
import classes.meta as cm
import classes.followup_support as cfs
from datetime import timedelta


def save_followup(
		guild_id: int, channel_id: int, message_id: int,
		followup_type: str,
		options: dict[str, cfs.FollowupAction],
		veto_power: list[cm.Person],
) -> None:
	with DatabaseConnection('data') as con:
		cursor = con.cursor()
		cursor.execute(
			'INSERT INTO followup_saves('
			'guild_id, channel_id, message_id,'
			'followup_type,'
			'options,'
			'veto_power'
			') VALUES (?, ?, ?, ?, ?, ?)',
			(
				guild_id, channel_id, message_id,
				followup_type,
				[f'{key}: {str(options[key])}' for key in options.keys()],
				', '.join([str(person.user.id) for person in veto_power])
			)
		)


class FollowupButton(discord.ui.Button):
	def __init__(self, emoji, label, followup_action: cfs.FollowupAction, style: discord.ButtonStyle = discord.ButtonStyle.blurple):
		"""temp = bot.get_emoji(emoji)
		if temp:
			super().__init__(emoji = temp, style = style, label = label)
		else:"""
		super().__init__(emoji = emoji, style = style, label = label)

		self.followup_action: cfs.FollowupAction = followup_action

	async def callback(self, interaction: discord.Interaction):
		action = await execute_followup(
			self.followup_action,
			button_interaction = interaction
		)
		if action == 'disable-self':
			for button in self.view.children:
				button.disabled = True
			await interaction.message.edit(view = self.view)
		await interaction.response.defer()


async def followup(
		identifier: discord.TextChannel | discord.Message | discord.Interaction | discord.ext.commands.Context | discord.Member | cm.Person,
		user_input: str,
		text: str,
		**kwargs
):
	# noinspection GrazieInspection
	"""
	:param identifier: TextChannel | Message | Interaction | Context | Member | Person
	:param user_input: str ('poll', 'button')
	:param text: str (message sent)
	:key options: dict[str, FollowupAction] (for 'poll' or 'button' followup type)
	:key question: str (for 'poll' followup type)
	:key veto_power: list[Person] (for 'poll' followup type)
	:return:
	"""
	if user_input == 'poll':
		time = timedelta(hours = 24)
		poll = discord.Poll(
			duration = time,
			question = kwargs.get('question'),
		)
		
		options: dict[str, cfs.FollowupAction] = kwargs.get('options')
		if options is None:
			raise KeyError('followup -> poll requires the "options" key in kwargs')
		
		for option in options.keys():
			poll.add_answer(text = option)
		
		sent = await td.send_message(identifier, text, poll = poll)
		veto_power: list[cm.Person] = kwargs.get('veto_power', [])
		
		# TODO: re-enable once loading is done
		# save_followup(sent.guild.id, sent.channel.id, sent.id, followup_type, options, veto_power)
		
		await asyncio.sleep(time.total_seconds())
		
		temp = None
		currently_a_tie = False
		veto = False
		for answer in sent.poll.answers:
			if veto:
				break
			if options.get(answer.text).note == 'veto':
				async for voter in answer.voters():
					if cm.Person(voter).permission_level > 2:
						veto = True
						break
					for person in veto_power:
						if voter.id == person.user.id:
							veto = True
							break
				
				if veto:
					temp = answer
					currently_a_tie = False
					break

				continue
			
			if temp is None:
				temp = answer
				continue
			
			if answer.vote_count == temp.vote_count:
				currently_a_tie = True
			elif answer.vote_count > temp.vote_count:
				temp = answer
				currently_a_tie = False
		
		if currently_a_tie:
			await td.send_message(sent, 'Tied poll, no action taken.')
			return
		
		action: cfs.FollowupAction = options.get(temp.text)
	else:
		raise ValueError(f'Unknown followup type: ``{user_input}``.')
	
	await execute_followup(action)


async def execute_followup(
		action: cfs.FollowupAction,
		button_interaction: discord.Interaction = None
) -> str | None:
	if action.type == 'function':
		action.value(*action.sub_values)
	elif action.type == 'async-function':
		if action.value == roll_initiation:
			action.sub_values[0].author = button_interaction.user
		await action.value(*action.sub_values)
	elif action.type == 'built-in':
		if action.value == 'disable-self':
			return 'disable-self'

	return None


def get_followup_view(followups: list[FollowupButton]) -> discord.ui.View:
	view: discord.ui.View = cfs.FollowupView()
	for item in followups:
		view.add_item(item)
	return view


pass

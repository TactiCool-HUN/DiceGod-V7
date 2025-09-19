import asyncio
import discord
import discord.ext
import utils.tools as t
import utils.tools_discord as td
import classes.meta as cm
import classes.utility as cu
from datetime import timedelta


async def followup(
		identifier: discord.TextChannel | discord.Message | discord.Interaction | discord.ext.commands.Context | discord.Member | cm.Person,
		followup_type: str,
		text: str,
		**kwargs
):
	# noinspection GrazieInspection
	"""
	:param identifier: TextChannel | Message | Interaction | Context | Member | Person
	:param followup_type: str
	:param text: str
	:key options: dict[str, FollowupAction]
	:key question: str
	:key veto_power: list[Person]
	:return: 
	"""
	if followup_type == 'poll':
		time = timedelta(hours = 24)
		poll = discord.Poll(
			duration = time,
			question = kwargs.get('question'),
		)
		
		options: dict[str, cu.FollowupAction] = kwargs.get('options')
		if options is None:
			raise KeyError('followup -> poll requires the "options" key in kwargs')
		
		for option in options.keys():
			poll.add_answer(text = option)
		
		sent = await td.send_message(identifier, text, poll = poll)
		await asyncio.sleep(time.total_seconds())
		#await sent.poll.end()
		
		veto_power: list[cm.Person] = kwargs.get('veto_power', [])
		temp = None
		currently_a_tie = False
		for answer in sent.poll.answers:
			if options.get(answer.text).power == 'veto':
				veto = False
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
		
		action: cu.FollowupAction = options.get(temp.text)
	else:
		raise ValueError(f'Unknown followup type: ``{followup_type}``.')
	
	if action.type == 'function':
		action.value(*action.sub_values)
	elif action.type == 'async-function':
		await action.value(*action.sub_values)
	elif action.type == 'built-in':
		if action.value == 'disable-self':
			t.ic('disable-self')
			return


pass

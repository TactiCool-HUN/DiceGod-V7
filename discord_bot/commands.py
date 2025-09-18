from utils.bot_setup import bot
import utils.tools_discord as td
import utils.tools as t
import classes.meta as cm
import roller
import asyncio
import discord


@bot.command(name = 'ping')
async def ping(ctx: discord.ext.commands.Context):
	response_list = {
		"pong": 48,
		"ping": 1,
		"Yes, yes. I'm here, just let me brew another coffee...": 1
	}
	result = t.choice(response_list)
	if result == "ping":
		await td.send_message(ctx, text = result, reply = True)
		await asyncio.sleep(2)
		await td.send_message(ctx, text = "oh, wait no\npong!", reply = True)
	else:
		await td.send_message(ctx, text = result, reply = True)


@bot.command(name = 'pong')
async def pong(ctx: discord.ext.commands.Context):
	response_list = {
		'ping': 49,
		'You wrote "pong" instead of "ping" and now you feel special don\'t you?': 1
	}
	result = t.choice(response_list)
	await td.send_message(ctx, text = result, reply = True)


@bot.command(name = 'emoji')
async def emoji_command(ctx: discord.ext.commands.Context):
	t.ic(ctx.message.clean_content)


@bot.command(name = 'roll', aliases = ['r', 'e', 'rollthosegoddamndicealready'])
async def roll(ctx: discord.ext.commands.Context, *, text):
	await roller.roll_initiation(ctx, text)


@bot.command(name = 'coinflip', aliases = ['coin', 'c'])
async def coin_old(ctx: discord.ext.commands.Context):
	response_list = {
		f"{cm.Person(ctx).user.display_name} flipped a coin and it landed on... it's side?": 1,
		f"{cm.Person(ctx).user.display_name} flipped a coin and it landed on **heads**!": 49,
		f"{cm.Person(ctx).user.display_name} flipped a coin and it landed on **tails**!": 51
	}
	await td.send_message(ctx, text = t.choice(response_list))

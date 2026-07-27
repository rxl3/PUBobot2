__all__ = [
	'noadds', 'noadd', 'forgive', 'rating_seed', 'rating_penality', 'rating_hide',
	'rating_reset', 'rating_snap', 'stats_reset', 'stats_reset_player', 'stats_replace_player',
	'phrases_add', 'phrases_clear', 'undo_match', 'get_all_immunity', 'seed_immunity', 'book', 'VoteMap'
]

from time import time
from datetime import timedelta
from nextcord import Member, Message, TextChannel

from bot.autobook import book_serveme
from bot.match.match import MAPS, Match
from core.utils import seconds_to_str, get_nick

import bot

import random

import nextcord
from nextcord import Member, User
from typing import List


async def noadds(ctx):
	data = await bot.noadds.get_noadds(ctx)
	now = int(time())
	s = "```markdown\n"
	s += ctx.qc.gt(" ID | Prisoner | Left | Reason")
	s += "\n----------------------------------------\n"
	if len(data):
		s += "\n".join((
			f" {i['id']} | {i['name']} | {seconds_to_str(max(0, (i['at'] + i['duration']) - now))} | {i['reason'] or '-'}"
			for i in data
		))
	else:
		s += ctx.qc.gt("Noadds are empty.")
	await ctx.reply(s + "\n```")


async def noadd(ctx, player: Member, duration: timedelta, reason: str = None):
	ctx.check_perms(ctx.Perms.MODERATOR)
	if not duration:
		duration = timedelta(hours=2)
	if duration > timedelta(days=365*100):
		raise bot.Exc.ValueError(ctx.qc.gt("Specified duration time is too long."))
	await bot.noadds.noadd(
		ctx=ctx, member=player, duration=int(duration.total_seconds()), moderator=ctx.author, reason=reason
	)
	await ctx.success(ctx.qc.gt("Banned **{member}** for `{duration}`.").format(
		member=get_nick(player),
		duration=duration.__str__()
	))


async def forgive(ctx, player: Member):
	ctx.check_perms(ctx.Perms.MODERATOR)
	if await bot.noadds.forgive(ctx=ctx, member=player, moderator=ctx.author):
		await ctx.success(ctx.qc.gt("Done."))
	else:
		raise bot.Exc.NotFoundError(ctx.qc.gt("Specified member is not banned."))


async def rating_seed(ctx, player: str, rating: int, deviation: int = None):
	ctx.check_perms(ctx.Perms.MODERATOR)
	if (player := await ctx.get_member(player)) is None:
		raise bot.Exc.SyntaxError(f"Specified member not found on the server.")
	if not 0 < rating < 10000 or not 0 < (deviation or 1) < 3000:
		raise bot.Exc.ValueError("Bad rating or deviation value.")

	await ctx.qc.rating.set_rating(player, rating=rating, deviation=deviation, reason="manual seeding")
	await ctx.qc.update_rating_roles(player)
	await ctx.success(ctx.qc.gt("Done."))


async def rating_penality(ctx, player: str, penality: int, reason: str = None):
	ctx.check_perms(ctx.Perms.MODERATOR)
	if (player := await ctx.get_member(player)) is None:
		raise bot.Exc.SyntaxError(f"Specified member not found on the server.")
	if abs(penality) > 10000:
		raise ValueError("Bad penality value.")
	reason = "penality: " + reason if reason else "penality by a moderator"

	await ctx.qc.rating.set_rating(player, penality=penality, reason=reason)
	await ctx.qc.update_rating_roles(player)
	await ctx.success(ctx.qc.gt("Done."))


async def rating_hide(ctx, player: str, hide: bool = True):
	ctx.check_perms(ctx.Perms.MODERATOR)
	if (player := await ctx.get_member(player)) is None:
		raise bot.Exc.SyntaxError(f"Specified member not found on the server.")
	await ctx.qc.rating.hide_player(player.id, hide=hide)
	await ctx.success(ctx.qc.gt("Done."))


async def rating_reset(ctx):
	ctx.check_perms(ctx.Perms.ADMIN)
	await ctx.qc.rating.reset()
	await ctx.success(ctx.qc.gt("Done."))


async def rating_snap(ctx):
	ctx.check_perms(ctx.Perms.ADMIN)
	await ctx.qc.rating.snap_ratings(ctx.qc._ranks_table)
	await ctx.success(ctx.qc.gt("Done."))


async def stats_reset(ctx):
	ctx.check_perms(ctx.Perms.ADMIN)
	await bot.stats.reset_channel(ctx.qc.id)
	await ctx.success(ctx.qc.gt("Done."))


async def stats_reset_player(ctx, player: str):
	ctx.check_perms(ctx.Perms.MODERATOR)
	if (player := await ctx.get_member(player)) is None:
		raise bot.Exc.SyntaxError(f"Specified member not found on the server.")

	await bot.stats.reset_player(ctx.qc.id, player.id)
	await ctx.success(ctx.qc.gt("Done."))


async def stats_replace_player(ctx, player1: str, player2: str):
	ctx.check_perms(ctx.Perms.ADMIN)
	if (player1 := await ctx.get_member(player1)) is None:
		raise bot.Exc.SyntaxError(f"Specified member not found on the server.")
	if (player2 := await ctx.get_member(player2)) is None:
		raise bot.Exc.SyntaxError(f"Specified member not found on the server.")

	await bot.stats.replace_player(ctx.qc.id, player1.id, player2.id, get_nick(player2))
	await ctx.success(ctx.qc.gt("Done."))


async def phrases_add(ctx, player: Member, phrase: str):
	ctx.check_perms(ctx.Perms.MODERATOR)
	await bot.noadds.phrases_add(ctx, player, phrase)
	await ctx.success(ctx.qc.gt("Done."))


async def phrases_clear(ctx, player: Member):
	ctx.check_perms(ctx.Perms.MODERATOR)
	await bot.noadds.phrases_clear(ctx, member=player)
	await ctx.success(ctx.qc.gt("Done."))


async def undo_match(ctx, match_id: int):
	ctx.check_perms(ctx.Perms.MODERATOR)

	result = await bot.stats.undo_match(ctx, match_id)
	if result:
		await ctx.success(ctx.qc.gt("Done."))
	else:
		raise bot.Exc.NotFoundError(ctx.qc.gt("Could not find match with specified id."))

async def get_all_immunity(ctx, channel_id, num):
	ctx.check_perms(ctx.Perms.MODERATOR)

	result = await bot.stats.get_all_immunity(ctx, channel_id, num)
	if result:
		await ctx.success(ctx.qc.gt("\n".join([f"<@{i}> IMMUNITY: x{result[i]}" for i in result])))
	else:
		raise bot.Exc.NotFoundError(ctx.qc.gt("Failed"))

async def seed_immunity(ctx, channel_id, num):
	ctx.check_perms(ctx.Perms.ADMIN)

	result = await bot.stats.seed_immunity(ctx, channel_id, num)
	if result:
		await ctx.success(ctx.qc.gt("\n".join([f"<@{i}> IMMUNITY: x{result[i]}" for i in result])))
	else:
		raise bot.Exc.NotFoundError(ctx.qc.gt("Failed"))

async def book(ctx):
	str_msg = await book_serveme(ctx)
	
	await ctx.success(ctx.qc.gt(str_msg))
# async def save_bot_state(ctx):

# class VoteMap:

# 	def __init__(self):
# 		self.vmm: Message
# 		self.tfmap = ""

# 	def set_tfmap(self, tfmap):
# 		self.tfmap = tfmap

async def vote_map_msg(ctx, users: List[User | Member], vmm: Message | None = None, step = 0):
	c: TextChannel = ctx.channel
	if step == 0:
		return await c.send(users[0].name + "'s turn to ban a map")
	elif step == 1 and vmm:
		await vmm.edit(content=users[1].name + "'s turn to ban a map")
	elif step == 2 and vmm:
		await vmm.edit(content="map picked")

async def vote_map(ctx, users, lastmap, vmm: Message | None = None):
	vmm = await vote_map_msg(ctx, users, step=0)

	print(users)
	
	rolls = random.sample(list(filter(lambda m: m != lastmap, MAPS)), 3) # replace string with lastmap

	opts = set(rolls)

	class Buttons(nextcord.ui.View):
		def __init__(self):
			# super().__init__()
			self.value = None
			self.count = 0
			self.turn = 0
			self.users = users
			self.vmm = vmm
			print(self.users)
		
		@nextcord.ui.button(label=rolls[0], style=nextcord.ButtonStyle.blurple)
		async def button1(self, button: nextcord.ui.Button, interact: nextcord.Interaction):
			if len(self.users) < self.turn + 1:
				print('user length error')
				return
			# user: User | Member = interact.user
			if interact.user != self.users[self.turn]:
				await interact.response.send_message(ephemeral=True, content="not your turn")
				return
			if self.count < 2:
				self.turn += 1
				button.style = nextcord.ButtonStyle.gray
				button.disabled = True
				self.count += 1
				opts.remove(rolls[0])
				await vote_map_msg(ctx, self.users, vmm=self.vmm, step=1)
			if self.count >= 2:
				for c in self.children:
					if isinstance(c, nextcord.ui.Button):
						c.disabled = True
				self.stop()
				# set_tfmap(opts.pop())
				await vote_map_msg(ctx, self.users, vmm=self.vmm, step=2)
			await interact.response.edit_message(view=self)

		@nextcord.ui.button(label=rolls[1], style=nextcord.ButtonStyle.blurple)
		async def button2(self, button: nextcord.ui.Button, interact: nextcord.Interaction):
			if len(self.users) < self.turn + 1:
				return
			if interact.user != self.users[self.turn]:
				await interact.response.send_message(ephemeral=True, content="not your turn")
				return
			if self.count < 2:
				self.turn += 1
				button.style = nextcord.ButtonStyle.gray
				button.disabled = True
				self.count += 1
				opts.remove(rolls[1])
				await vote_map_msg(ctx, self.users, vmm=self.vmm, step=1)
			if self.count >= 2:
				for c in self.children:
					if isinstance(c, nextcord.ui.Button):
						c.disabled = True
				self.stop()
				# self.parent.set_tfmap(opts.pop())
				await vote_map_msg(ctx, self.users, vmm=self.vmm, step=2)
			await interact.response.edit_message(view=self)

		@nextcord.ui.button(label=rolls[2], style=nextcord.ButtonStyle.blurple)
		async def button3(self, button: nextcord.ui.Button, interact: nextcord.Interaction):
			if len(self.users) < self.turn + 1:
				return
			if interact.user != self.users[self.turn]:
				await interact.response.send_message(ephemeral=True, content="not your turn")
				return
			if self.count < 2:
				self.turn += 1
				button.style = nextcord.ButtonStyle.gray
				button.disabled = True
				self.count += 1
				opts.remove(rolls[2])
				await vote_map_msg(ctx, self.users, vmm=self.vmm, step=1)
			if self.count >= 2:
				for c in self.children:
					if isinstance(c, nextcord.ui.Button):
						c.disabled = True
				self.stop()
				# self.parent.set_tfmap(opts.pop())
				await vote_map_msg(ctx, self.users, vmm=self.vmm, step=2)
			await interact.response.edit_message(view=self)
	view = Buttons()
	await ctx.notice(view=view)
	print('votemap')
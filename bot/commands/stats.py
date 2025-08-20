__all__ = ['last_game', 'stats', 'top', 'luck', 'rank', 'leaderboard', 'set_immunity', 'set_forced_med']

from time import time
from nextcord import Member, Embed, Colour

from core.utils import get, find, seconds_to_str, get_nick, discord_table
from core.database import db

import bot
import collections


async def last_game(ctx, queue: str = None, player: Member = None, match_id: int = None):
	lg = None

	if match_id:
		lg = await db.select_one(
			['*'], "qc_matches", where=dict(channel_id=ctx.qc.id, match_id=match_id), order_by="match_id", limit=1
		)

	elif queue:
		if queue := find(lambda q: q.name.lower() == queue.lower(), ctx.qc.queues):
			lg = await db.select_one(
				['*'], "qc_matches", where=dict(channel_id=ctx.qc.id, queue_id=queue.id), order_by="match_id", limit=1
			)

	elif player and (member := await ctx.get_member(player)) is not None:
		if match := await db.select_one(
			['match_id'], "qc_player_matches", where=dict(channel_id=ctx.qc.id, user_id=member.id),
			order_by="match_id", limit=1
		):
			lg = await db.select_one(
				['*'], "qc_matches", where=dict(channel_id=ctx.qc.id, match_id=match['match_id'])
			)

	else:
		lg = await db.select_one(
			['*'], "qc_matches", where=dict(channel_id=ctx.qc.id), order_by="match_id", limit=1
		)

	if not lg:
		raise bot.Exc.NotFoundError(ctx.qc.gt("Nothing found"))

	players = await db.select(
		['user_id', 'nick', 'team'], "qc_player_matches",
		where=dict(match_id=lg['match_id'])
	)
	embed = Embed(colour=Colour(0x50e3c2))
	embed.add_field(name=lg['queue_name'], value=seconds_to_str(int(time()) - lg['at']) + " ago")
	if len(team := [p['nick'] for p in players if p['team'] == 0]):
		embed.add_field(name=lg['alpha_name'], value="`" + ", ".join(team) + "`")
	if len(team := [p['nick'] for p in players if p['team'] == 1]):
		embed.add_field(name=lg['beta_name'], value="`" + ", ".join(team) + "`")
	if len(team := [p['nick'] for p in players if p['team'] is None]):
		embed.add_field(name=ctx.qc.gt("Players"), value="`" + ", ".join(team) + "`")
	if lg['ranked']:
		if lg['winner'] is None:
			winner = ctx.qc.gt('Draw')
		else:
			winner = [lg['alpha_name'], lg['beta_name']][lg['winner']]
		embed.add_field(name=ctx.qc.gt("Winner"), value=winner)
	await ctx.reply(embed=embed)


async def stats(ctx, player: Member = None):
	if player:
		if (member := await ctx.get_member(player)) is not None:
			data = await bot.stats.user_stats(ctx.qc.id, member.id)
			target = get_nick(member)
		else:
			raise bot.Exc.NotFoundError(ctx.qc.gt("Specified user not found."))
	else:
		data = await bot.stats.qc_stats(ctx.qc.id)
		target = f"#{ctx.channel.name}"

	embed = Embed(
		title=ctx.qc.gt("Stats for __{target}__").format(target=target),
		colour=Colour(0x50e3c2),
		description=ctx.qc.gt("**Total matches: {count}**").format(count=data['total'])
	)
	for q in data['queues']:
		embed.add_field(name=q[0]['queue_name'], value=str(q[0]['count']), inline=True)
		embed.add_field(name='Red wins', value=str(q[1]['count']), inline=True)
		embed.add_field(name='Blu wins', value=str(q[2]['count']), inline=True)

	await ctx.reply(embed=embed)


async def top(ctx, period=None):
	if period in ["day", ctx.qc.gt("day")]:
		time_gap = int(time()) - (60 * 60 * 24)
	elif period in ["week", ctx.qc.gt("week")]:
		time_gap = int(time()) - (60 * 60 * 24 * 7)
	elif period in ["month", ctx.qc.gt("month")]:
		time_gap = int(time()) - (60 * 60 * 24 * 30)
	elif period in ["year", ctx.qc.gt("year")]:
		time_gap = int(time()) - (60 * 60 * 24 * 365)
	else:
		time_gap = None

	data = await bot.stats.top(ctx.qc.id, time_gap=time_gap)
	embed = Embed(
		title=ctx.qc.gt("Top 10 players for __{target}__").format(target=f"#{ctx.channel.name}"),
		colour=Colour(0x50e3c2),
		description=ctx.qc.gt("**Total matches: {count}**").format(count=data['total'])
	)
	for p in data['players']:
		embed.add_field(name=p['nick'], value=str(p['count']), inline=True)
	await ctx.reply(embed=embed)


async def luck(ctx, rows=10, min_games=10):
	# Mods only (too spammy)
	ctx.check_perms(ctx.Perms.MODERATOR)
	
	# Absolute Maximum of 10
	rows = 10 if int(rows) > 10 else rows

	# Get data
	data = await bot.stats.luck(ctx,min_games,rows)

	# UNLUCKY
	unlucky = Embed(
		title=ctx.qc.gt("Unluckiest {rows} players for __{target}__").format(
			target=f"#{ctx.channel.name}",
			min_games=min_games,
			rows=rows
		),
		colour=Colour(0xff0000),
		description=ctx.qc.gt("Highest percentage of Captain to Non-Captain games for players who have played at least {min_games} games").format(min_games=min_games)
	)
	for index,p in enumerate(data['unlucky']):
		percent = '{0:.2f}'.format(p['ratio']*100)
		unlucky.add_field(
			name=f"**#{index+1}. {p['nick']}**", 
			value=f"Captained {p['captain_games']} out of {p['total_games']} games played (**{percent}%**)",
			inline=False
		)

	# LUCKY
	lucky = Embed(
		title=ctx.qc.gt("Luckiest {rows} players for __{target}__").format(
			target=f"#{ctx.channel.name}",
			min_games=min_games,
			rows=rows
		),
		colour=Colour(0x00ff00),
		description=ctx.qc.gt("Lowest percentage of Captain to Non-Captain games for players who have played at least {min_games} games").format(min_games=min_games)
	)
	for index,p in enumerate(data['lucky']):
		percent = '{0:.2f}'.format(p['ratio']*100)
		lucky.add_field(
			name=f"**#{index+1}. {p['nick']}**", 
			value=f"Captained {p['captain_games']} out of {p['total_games']} games played (**{percent}%**)",
			inline=False
		)

	# Send Messages
	await ctx.reply(embed=unlucky)
	await ctx.reply(embed=lucky)


async def set_immunity(ctx, player: Member = None, immunity=0):
	ctx.check_perms(ctx.Perms.MODERATOR)

	target = ctx.author if not player else await ctx.get_member(player)
	if not target:
		raise bot.Exc.SyntaxError(ctx.qc.gt("Specified user not found."))

	await db.update(
		"qc_players",
		dict(immunity=immunity),
		keys=dict(channel_id=ctx.qc.id, user_id=target.id, nick=get_nick(target))
	)

	await ctx.reply(embed=
		Embed(
			title=ctx.qc.gt("Immunity Updated!"),
			colour=Colour(0x00ff00),
			description=ctx.qc.gt("Set {target}'s immunity to {immunity}").format(
				target=f"{get_nick(target)}",
				immunity=immunity
			),
		)
	)


async def set_forced_med(ctx, player: Member = None, count=0):
	ctx.check_perms(ctx.Perms.MODERATOR)

	target = ctx.author if not player else await ctx.get_member(player)
	if not target:
		raise bot.Exc.SyntaxError(ctx.qc.gt("Specified user not found."))

	await db.update(
		"qc_players",
		dict(force_med=count),
		keys=dict(channel_id=ctx.qc.id, user_id=target.id, nick=get_nick(target))
	)

	await ctx.reply(embed=
		Embed(
			title=ctx.qc.gt("Forced Med Count Updated!"),
			colour=Colour(0x00ff00),
			description=ctx.qc.gt("Set {target}'s forced med games to {count}").format(
				target=f"{get_nick(target)}",
				count=count
			),
		),
		ephemeral=True
	)


async def rank(ctx, player: Member = None):
	target = ctx.author if not player else await ctx.get_member(player)
	if not target:
		raise bot.Exc.SyntaxError(ctx.qc.gt("Specified user not found."))

	data = await ctx.qc.get_lb()
	# Figure out leaderboard placement
	if p := find(lambda i: i['user_id'] == target.id, data):
		place = data.index(p) + 1
	else:
		data = await db.select(
			['user_id', 'rating', 'deviation', 'channel_id', 'wins', 'losses', 'draws', 'is_hidden', 'streak', 'immunity', 'force_med'],
			"qc_players",
			where={'channel_id': ctx.qc.rating.channel_id}
		)
		p = find(lambda i: i['user_id'] == target.id, data)
		place = "?"

	# Do some cool data analysis
	myMatches = await db.fetchall("SELECT qcpm.match_id FROM qc_player_matches qcpm JOIN qc_matches qcm ON qcpm.match_id = qcm.match_id WHERE qcpm.user_id = {id}".format(id=target.id))
	matchIds = ", ".join(str(match['match_id']) for match in myMatches)
	matchData = await db.fetchall("SELECT qcpm.match_id, user_id, team, winner, nick FROM qc_player_matches qcpm JOIN qc_matches qcm ON qcpm.match_id = qcm.match_id WHERE qcpm.match_id IN ({matches})".format(matches=matchIds))

	me = [x for x in matchData if x['user_id'] == target.id]
	wlfdict = {}
	wledict = {}

	for my in me:
		for m in matchData:
			uid = m['user_id']

			if m['match_id'] != my['match_id'] or uid == target.id:
				continue
			
			if m['team'] == my['team']: # if they are a teammate
				if m['team'] == m['winner']:  # we won!
					if uid in wlfdict:
						wlfdict[uid]['wins'] += 1
					else:
						wlfdict[uid] = {
							"wins": 1,
							"losses": 0,
							"total": 0
						}
				else: # we lost :(
					if uid in wlfdict:
						wlfdict[uid]['losses'] += 1
					else:
						wlfdict[uid] = {
							"wins": 0,
							"losses": 1,
							"total": 0
						}
				wlfdict[uid]['total'] += 1
			else: ## they are on enemy team
				if m['team'] == m['winner']: # enemy won, means I lost
					if uid in wledict:
						wledict[uid]['wins'] += 1
					else:
						wledict[uid] = {
							"wins": 1,
							"losses": 0,
							"total": 0
						}
				else: # enemy lost, means I won
					if uid in wledict:
						wledict[uid]['losses'] += 1
					else:
						wledict[uid] = {
							"wins": 0,
							"losses": 1,
							"total": 0
						}
			
				wledict[uid]['total'] += 1
	
	topTeammates = sorted(wlfdict.items(), key=lambda item: item[1]['total'], reverse=True)[:4]
	topEnemies = sorted(wledict.items(), key=lambda item: item[1]['total'], reverse=True)[:4]

	if p:
		embed = Embed(title=f"__{get_nick(target)}__", colour=Colour(0x7289DA))
		embed.add_field(name="№", value=f"**{place}**", inline=True)
		embed.add_field(name=ctx.qc.gt("Matches"), value=f"**{(p['wins'] + p['losses'] + p['draws'])}**", inline=True)
		if p['rating']:
			embed.add_field(name=ctx.qc.gt("Rank"), value=f"**{ctx.qc.rating_rank(p['rating'])['rank']}**", inline=True)
			embed.add_field(name=ctx.qc.gt("Rating"), value=f"**{p['rating']}**±{p['deviation']}")
		else:
			embed.add_field(name=ctx.qc.gt("Rank"), value="**〈?〉**", inline=True)
			embed.add_field(name=ctx.qc.gt("Rating"), value="**?**")
		embed.add_field(
			name="W/L/D/S",
			value="**{wins}**/**{losses}**/**{draws}**/**{streak}**".format(**p),
			inline=True
		)
		embed.add_field(name=ctx.qc.gt("Winrate"), value="**{}%**\n\u200b".format(
			int(p['wins'] * 100 / (p['wins'] + p['losses'] or 1))
		), inline=True)
		if target.display_avatar:
			embed.set_thumbnail(url=target.display_avatar.url)

		games_as_captain = await db.select(['COUNT(*) as count'], "qc_player_matches",
			where=dict(channel_id=ctx.qc.rating.channel_id, user_id=target.id, captain=1))
		embed.add_field(name="Games as Captain", value=f"**{games_as_captain[0]['count']}**", inline=True)

		embed.add_field(name="Immunity", value=f"**{p['immunity']}**", inline=True)
		
		embed.add_field(name="Med games remaining", value=f"**{p['force_med']}**", inline=True)

		changes = await db.select(
			('at', 'rating_change', 'match_id', 'reason'),
			'qc_rating_history', where=dict(user_id=target.id, channel_id=ctx.qc.rating.channel_id),
			order_by='id', limit=5
		)
		if len(changes):
			embed.add_field(
				name=ctx.qc.gt("Last changes:"),
				value="\n".join(("\u200b \u200b **{change}** \u200b | {ago} ago | {reason}{match_id}".format(
					ago=seconds_to_str(int(time() - c['at'])),
					reason=c['reason'],
					match_id=f"(__{c['match_id']}__)" if c['match_id'] else "",
					change=("+" if c['rating_change'] >= 0 else "") + str(c['rating_change'])
				) for c in changes)),
				inline=False
			)

		if len(topTeammates):
			embed.add_field(
				name="Teammates",
				value="\n".join("{name} ({percent}%, {count} games)".format(
					name=[x for x in matchData if x['user_id'] == t[0]][0]['nick'],
					percent=int(100 * t[1]['wins'] / (t[1]['total'] or 1)),
					count=t[1]['total']
				) for t in topTeammates),
				inline=True
			)

		if len(topEnemies):
			embed.add_field(
				name="Enemies",
				value="\n".join("{name} ({percent}%, {count} games)".format(
					name=[x for x in matchData if x['user_id'] == t[0]][0]['nick'],
					percent=int(100 * t[1]['losses'] / (t[1]['total'] or 1)), # using losses because this tracks enemy team losses, and we want to display our winrate still
					count=t[1]['total']
				) for t in topEnemies),
				inline=True
			)

		await ctx.reply(embed=embed)
	else:
		raise bot.Exc.ValueError(ctx.qc.gt("No rating data found."))


async def leaderboard(ctx, page: int = 1):
	page = (page or 1) - 1
	rawdata = await ctx.qc.get_lb()

	if len(rawdata):
		embed = await bot.stats.generate_lb_page(ctx, rawdata, page)
		await ctx.reply(
			embed=embed
		)
	else:
		raise bot.Exc.NotFoundError(ctx.qc.gt("Leaderboard is empty."))
	
	await bot.stats.update_leaderboard(ctx)

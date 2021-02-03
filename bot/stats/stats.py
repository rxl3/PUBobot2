# -*- coding: utf-8 -*-
import time
from core.database import db
from core.utils import iter_to_dict, find

db.ensure_table(dict(
	tname="players",
	columns=[
		dict(cname="user_id", ctype=db.types.int),
		dict(cname="name", ctype=db.types.str),
		dict(cname="allow_pm", ctype=db.types.bool),
		dict(cname="expire", ctype=db.types.int)
	],
	primary_keys=["user_id"]
))

db.ensure_table(dict(
	tname="qc_players",
	columns=[
		dict(cname="channel_id", ctype=db.types.int),
		dict(cname="user_id", ctype=db.types.int),
		dict(cname="nick", ctype=db.types.str),
		dict(cname="is_hidden", ctype=db.types.bool, default=0),
		dict(cname="rating", ctype=db.types.int, notnull=True),
		dict(cname="deviation", ctype=db.types.int, notnull=True),
		dict(cname="wins", ctype=db.types.int, notnull=True, default=0),
		dict(cname="losses", ctype=db.types.int, notnull=True, default=0),
		dict(cname="draws", ctype=db.types.int, notnull=True, default=0)
	],
	primary_keys=["user_id", "channel_id"]
))

db.ensure_table(dict(
	tname="qc_rating_history",
	columns=[
		dict(cname="id", ctype=db.types.int, autoincrement=True),
		dict(cname="channel_id", ctype=db.types.int),
		dict(cname="user_id", ctype=db.types.int),
		dict(cname="at", ctype=db.types.int),
		dict(cname="rating_before", ctype=db.types.int),
		dict(cname="rating_change", ctype=db.types.int),
		dict(cname="deviation_before", ctype=db.types.int),
		dict(cname="deviation_change", ctype=db.types.int),
		dict(cname="match_id", ctype=db.types.int),
		dict(cname="reason", ctype=db.types.str)
	],
	primary_keys=["id"]
))

db.ensure_table(dict(
	tname="qc_matches",
	columns=[
		dict(cname="match_id", ctype=db.types.int),
		dict(cname="channel_id", ctype=db.types.int),
		dict(cname="queue_id", ctype=db.types.int),
		dict(cname="queue_name", ctype=db.types.str),
		dict(cname="at", ctype=db.types.int),
		dict(cname="alpha_name", ctype=db.types.str),
		dict(cname="beta_name", ctype=db.types.str),
		dict(cname="ranked", ctype=db.types.bool),
		dict(cname="winner", ctype=db.types.bool),
		dict(cname="maps", ctype=db.types.str)
	],
	primary_keys=["match_id"]
))

db.ensure_table(dict(
	tname="qc_player_matches",
	columns=[
		dict(cname="match_id", ctype=db.types.int),
		dict(cname="user_id", ctype=db.types.int),
		dict(cname="team", ctype=db.types.bool)
	],
	primary_keys=["match_id", "user_id"]
))


async def last_match_id():
	m = await db.select_one(('match_id',), 'qc_matches', order_by='match_id', limit=1)
	print(m)
	return m['match_id'] if m else 0


async def register_match_unranked(m):
	await db.insert('qc_matches', dict(
		match_id=m.id, channel_id=m.qc.channel.id, queue_id=m.queue.cfg.p_key, queue_name=m.queue.name,
		at=int(time.time()), ranked=0, winner=None, maps="\n".join(m.maps)
	))

	await db.insert_many('qc_players', (
		dict(channel_id=m.qc.channel.id, user_id=p.id, rating=m.qc.rating.init_rp, deviation=m.qc.rating.init_deviation)
		for p in m.players
	), on_dublicate="ignore")

	for p in m.players:
		await db.update(
			"qc_players",
			dict(nick=p.nick or p.name),
			keys=dict(channel_id=m.qc.channel.id, user_id=p.id)
		)

		if p in m.teams[0]:
			team = 0
		elif p in m.teams[1]:
			team = 1
		else:
			team = None

		await db.insert('qc_player_matches', dict(match_id=m.id, user_id=p.id, team=team))


async def register_match_ranked(m):
	await db.insert('qc_matches', dict(
		match_id=m.id, channel_id=m.qc.channel.id, queue_id=m.queue.cfg.p_key, queue_name=m.queue.name,
		at=int(time.time()), ranked=1, winner=None, maps="\n".join(m.maps)
	))

	await db.insert_many('qc_players', (
		dict(channel_id=m.qc.channel.id, user_id=p.id, rating=m.qc.rating.init_rp, deviation=m.qc.rating.init_deviation)
		for p in m.players
	), on_dublicate="ignore")

	before = [
		await m.qc.rating.get_players((p.id for p in m.teams[0])),
		await m.qc.rating.get_players((p.id for p in m.teams[1])),
	]

	after = m.qc.rating.rate(
		winners=before[int(m.winner)],
		losers=before[abs(int(m.winner)-1)],
		draw=m.winner is None
	)

	after = iter_to_dict(after, key='user_id')
	before = iter_to_dict((*before[0], *before[1]), key='user_id')

	for p in m.players:
		team = 0 if p in m.teams[0] else 1

		if m.winner is None:
			after[p.id]['draws'] += 1
		elif m.winner == team:
			after[p.id]['wins'] += 1
		else:
			after[p.id]['losses'] += 1

		await db.update(
			"qc_players",
			dict(
				nick=p.nick or p.name,
				rating=after[p.id]['rating'],
				deviation=after[p.id]['deviation'],
				wins=after[p.id]['wins'],
				losses=after[p.id]['losses'],
				draws=after[p.id]['draws']
			),
			keys=dict(channel_id=m.qc.channel.id, user_id=p.id)
		)

		await db.insert('qc_player_matches', dict(match_id=m.id, user_id=p.id, team=team))
		await db.insert('qc_rating_history', dict(
			channel_id=m.qc.channel.id,
			user_id=p.id,
			at=int(time.time()),
			rating_before=before[p.id]['rating'],
			rating_change=after[p.id]['rating']-before[p.id]['rating'],
			deviation_before=before[p.id]['deviation'],
			deviation_change=after[p.id]['deviation']-before[p.id]['deviation'],
			match_id=m.id,
			reason=m.queue.name
		))

	await m.print_rating_results(before, after)

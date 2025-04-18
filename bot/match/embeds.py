from nextcord import Embed, Colour, Streaming
from core.client import dc
from core.utils import get_nick, get_mention, get_div_role, get_class_roles, join_and, get_class_role_icons
from core import config
import random

class Embeds:
	""" This class generates discord embeds for various match states """

	def __init__(self, match):
		self.m = match
		# self.
		self.footer = dict(
			text=f"Match id: {self.m.id}",
			icon_url=dc.user.avatar.with_size(32)
			# icon_url="https://cdn.discordapp.com/avatars/240843400457355264/a51a5bf3b34d94922fd60751ba1d60ab.png?size=64"
		)

	def check_in(self, not_ready):
		embed = Embed(
			colour=Colour(0xf5d858),
			title=self.m.gt("__**{queue}** is now on the check-in stage! __").format(
				queue=self.m.queue.name[0].upper()+self.m.queue.name[1:]
			)
		)
		if self.m.cfg['show_checkin_timer'] and self.m.check_in.timeout != 0:
			embed.add_field(
				name="",
				value=self.m.gt("Expires in <{t}s if players do not ready up").format(
					t=int(self.m.check_in.time_to_timeout)
				),
				inline=False
			)
		embed.add_field(
			name=self.m.gt("Waiting on:"),
			value="\n".join((f" \u200b <@{p.id}>" for p in not_ready)),
			inline=False
		)
		embed.add_field(
			name=self.m.gt("Ready to play:"),
			value="\n".join((f" \u200b `{get_nick(p)}`" for p in self.m.check_in.ready_players)),
			inline=False
		)

		if not len(self.m.check_in.maps):
			embed.add_field(
				name="—",
				value=self.m.gt(
					"Please react with {ready_emoji} to **check-in** or {not_ready_emoji} to **abort**!").format(
					ready_emoji=self.m.check_in.READY_EMOJI, not_ready_emoji=self.m.check_in.NOT_READY_EMOJI
				) + "\n\u200b",
				inline=False
			)
		else:
			embed.add_field(
				name="—",
				value="\n".join([
					self.m.gt("Please react with {ready_emoji} or vote for a map to **check-in**.").format(
						ready_emoji=self.m.check_in.READY_EMOJI
					),
					self.m.gt("React with {not_ready_emoji} to **abort**!").format(
						not_ready_emoji=self.m.check_in.NOT_READY_EMOJI
					) + "\n\u200b\nMaps:",
					"\n".join([
						f" \u200b \u200b {self.m.check_in.INT_EMOJIS[i]} \u200b {self.m.check_in.maps[i]}"
						for i in range(len(self.m.check_in.maps))
					])
				]),
				inline=False
			)
		embed.set_footer(**self.footer)

		return embed

	def draft(self):
		embed = Embed(
			colour=Colour(0x8758f5),
			title=self.m.gt("__**{queue}** is now on the draft stage!__").format(
				queue=self.m.queue.name[0].upper()+self.m.queue.name[1:]
			)
		)

		teams_names = [
			f"{t.emoji} \u200b **{t.name}**" +
			(f" \u200b `〈{sum((self.m.ratings[p.id] for p in t))//(len(t) or 1)}〉`" if self.m.ranked else "")
			for t in self.m.teams[:2]
		]
		team_players = [
			" \u200b ".join([
					" \u200b {mention} {role_icons}".format(
						mention=get_mention(p),
						role_icons=get_class_role_icons(p, self.m.cfg['class_roles'])
					)
				for p in t
			]) if len(t) else self.m.gt("empty")
			for t in self.m.teams[:2]
		]
		embed.add_field(name=teams_names[0], value=" \u200b ❲ \u200b " + team_players[0] + " \u200b ❳", inline=False)
		embed.add_field(name=teams_names[1], value=" \u200b ❲ \u200b " + team_players[1] + " \u200b ❳\n\u200b", inline=False)

		# If players are still waiting to be picked
		if len(self.m.teams[2]):

			# Easier to use
			divs = self.m.cfg['division_roles']

			# If teams have captains
			if len(self.m.teams[0]) and len(self.m.teams[1]):
				if len(divs):
					# Sort the unpicked players by Division Role (descending)
					unpicked_list=sorted(
						self.m.teams[2], 
						key=lambda u: divs.index(get_div_role(u,divs))
					)
				else:
					unpicked_list = self.m.teams[2]
				
				# Post-msg 
				msg = self.m.gt("Pick players with `/pick @player` command.")
				pick_step = len(self.m.teams[0]) + len(self.m.teams[1]) - 2
				picker_team = self.m.teams[self.m.draft.pick_order[pick_step]] if pick_step < len(self.m.draft.pick_order)-1 else None
				if picker_team:
					msg += "\n" + self.m.gt("{member}'s turn to pick!").format(member=f"<@{picker_team[0].id}>")

			else:
				# Keep the pre-sorting that we did to the Match.players variable (if any)
				unpicked_list=[p for p in self.m.players if p in self.m.teams[2]]

				# Post-msg
				msg = self.m.gt("Type {cmd} to become a captain and start picking teams.").format(
					cmd=f"`{self.m.qc.cfg.prefix}capfor {'/'.join((team.name.lower() for team in self.m.teams[:2]))}`"
				)

				# Temporary captains (if they exist)
				if len(self.m.temporary_captains) == 2:
					temporary_captains_list = [p for p in unpicked_list if p.id in self.m.temporary_captains]
					plural_msg = " have been rolled as captains" if len(temporary_captains_list) > 1 else " has been rolled as captain"
					embed.add_field(
						name=self.m.gt(""),
						value=" and ".join((
							"{mention}".format(
								mention=get_mention(p)
							)
						) for p in temporary_captains_list) + plural_msg + "\n",
						inline=False
					)

			# Unpicked Players msg
			embed.add_field(
				name=self.m.gt("Unpicked:"),
				value="\n".join((
					(f" \u200b " + self.m.cfg['player_list_format']).format(
						rank=self.m.rank_str(p) if self.m.ranked else "",
						name=get_nick(p),
						mention=get_mention(p),
						div=get_div_role(p, divs),
						classes=get_class_roles(p, self.m.cfg['class_roles']),
						immune=f" - **IMMUNE: x{self.m.immune[int(p.id)]}**" if p.id in self.m.immune else ""
					)
				) for p in unpicked_list),
				inline=False
			)

			# Create the post-msg
			embed.add_field(name="—", value=msg + "\n\u200b", inline=False)

		embed.set_footer(**self.footer)

		return embed

	def final_message(self):
		show_ranks = bool(self.m.ranked and not self.m.qc.cfg.rating_nicks)
		embed = Embed(
			colour=Colour(0x27b75e),
			title=self.m.qc.gt("__**{queue}** has started!__").format(
				queue=self.m.queue.name[0].upper()+self.m.queue.name[1:]
			)
		)

		if len(self.m.teams[0]) == 1 and len(self.m.teams[1]) == 1:  # 1v1
			p1, p2 = self.m.teams[0][0], self.m.teams[1][0]
			players = " \u200b {player1}{rating1}\n \u200b {player2}{rating2}".format(
				rating1=f" \u200b `〈{self.m.ratings[p1.id]}〉`" if show_ranks else "",
				player1=f"<@{p1.id}>",
				rating2=f" \u200b `〈{self.m.ratings[p2.id]}〉`" if show_ranks else "",
				player2=f"<@{p2.id}>",
			)
			embed.add_field(name=self.m.gt("Players"), value=players, inline=False)
		elif len(self.m.teams[0]):  # team vs team
			teams_names = [
				f"{t.emoji} \u200b **{t.name}**" +
				(f" \u200b `〈{sum((self.m.ratings[p.id] for p in t))//(len(t) or 1)}〉`" if self.m.ranked else "")
				for t in self.m.teams[:2]
			]
			team_players = [
				" \u200b " +
				" \u200b ".join([
					(f"`{self.m.rank_str(p)}`" if show_ranks else "") + f"<@{p.id}>"
					for p in t
				])
				for t in self.m.teams[:2]
			]
			team_players[1] += "\n\u200b"  # Extra empty line
			embed.add_field(name=teams_names[0], value=team_players[0], inline=False)
			embed.add_field(name=teams_names[1], value=team_players[1], inline=False)
			if self.m.ranked or self.m.cfg['pick_captains']:
				embed.add_field(
					name=self.m.gt("Captains"),
					value=" \u200b " + join_and([self.m.teams[0][0].mention, self.m.teams[1][0].mention]),
					inline=False
				)

		else:  # just players list
			embed.add_field(
				name=self.m.gt("Players"),
				value=" \u200b " + " \u200b ".join((m.mention for m in self.m.players)),
				inline=False
			)
			if len(self.m.captains) and len(self.m.players) > 2:
				embed.add_field(
					name=self.m.gt("Captains"),
					value=" \u200b " + join_and([m.mention for m in self.m.captains]),
					inline=False
				)

		if len(self.m.maps):
			embed.add_field(
				name=self.m.qc.gt("Map" if len(self.m.maps) == 1 else "Maps"),
				value="\n".join((f"**{i}**" for i in self.m.maps)),
				inline=True
			)
		if self.m.cfg['server']:
			embed.add_field(name=self.m.qc.gt("Server"), value=f"`{self.m.cfg['server']}`", inline=True)

		if self.m.cfg['start_msg']:
			embed.add_field(name="—", value=self.m.cfg['start_msg'] + "\n\u200b", inline=False)

		if self.m.cfg['show_streamers']:
			if len(streamers := [p for p in self.m.players if isinstance(p.activity, Streaming)]):
				embed.add_field(name=self.m.qc.gt("Player streams"), inline=False, value="\n".join([
					f"{p.mention}: {p.activity.url}" for p in streamers
				]) + "\n\u200b")
		embed.set_footer(**self.footer)

		return embed

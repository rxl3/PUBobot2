from core import config
from core.client import dc
from datetime import timedelta
import requests
import bot
import random
import string
import datetime

async def book_serveme(ctx):
	try:
		strings_channel = dc.get_channel(config.cfg.DC_STRINGS_CHANNEL_ID)

		existing_booking = False
		# existing_message = None
		async for message in strings_channel.history(limit=5):
			if message.author == dc.user and datetime.datetime.now(datetime.timezone.utc) - message.created_at < timedelta(minutes=90):
				existing_booking = True
				# existing_message = message
				break

		if existing_booking:
			# await ctx.success(ctx.qc.gt("Connect string: " + existing_message))
			return "Auto-booked server is already in use, please manually book a server."
		else:
			response = requests.get("https://au.serveme.tf/api/reservations/new?api_key=" + config.cfg.SERVEME_API_KEY)

			if response.status_code == 200:
				find_payload = response.json()

				find_response = requests.post("https://au.serveme.tf/api/reservations/find_servers?api_key=" + config.cfg.SERVEME_API_KEY, str(find_payload))
				find_response_json = find_response.json()

				s = string.ascii_letters+string.digits
				server_password = ''.join(random.sample(s, 10))
				rcon_password = ''.join(random.sample(s, 10))

				if len(find_response_json['servers']) > 0:

					serveme_server = find_response_json['servers'][0]

					requests.post('https://au.serveme.tf/api/reservations?api_key=' + config.cfg.SERVEME_API_KEY, json={
						"reservation": {
							"starts_at": find_payload['reservation']['starts_at'],
							"ends_at": find_payload['reservation']['ends_at'],
							"server_id": serveme_server['id'],
							"password": server_password,
							"rcon": rcon_password,
							"first_map": "cp_process_f12"
						}
					})

					string_message = "```markdown\n"
					string_message += "connect " + serveme_server['ip_and_port'] + "; password \"" + server_password + "\";"
					string_message += "```"

					str_msg = await strings_channel.send(content=string_message)
					
					return "Connect string: " + str_msg.jump_url

				else:
					raise bot.Exc.NotFoundError(ctx.qc.gt("No available servers."))

			else:
				print('Error:', response.status_code)
				raise bot.Exc.NotFoundError(ctx.qc.gt("Error booking serveme."))
				
	except requests.exceptions.RequestException as e:
		print('Error:', e)
		raise bot.Exc.NotFoundError(ctx.qc.gt("Error booking serveme."))

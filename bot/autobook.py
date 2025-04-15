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
        rcon_channel = dc.get_channel(config.cfg.DC_RCON_CHANNEL_ID)
		
        matches = [m for m in bot.active_matches if m.qc.id == ctx.qc.id]

        existing_booking = False
        existing_message = None
        async for message in strings_channel.history(limit=5):
            if message.author == dc.user and datetime.datetime.now(datetime.timezone.utc) - message.created_at < timedelta(minutes=90):
                existing_booking = True
                existing_message = message
                break

        if existing_booking:
            if len(matches) > 0:
                return "Auto-booked server is already in use, please manually book a server."
            else:
                return "Connect string: " + existing_message.jump_url
        else:
            response = requests.get("https://au.serveme.tf/api/reservations/new?api_key=" + config.cfg.SERVEME_API_KEY)

            if response.status_code == 200:
                find_payload = response.json()

                find_response = requests.post("https://au.serveme.tf/api/reservations/find_servers?api_key=" + config.cfg.SERVEME_API_KEY, str(find_payload))
                find_response_json = find_response.json()

                s = string.ascii_letters+string.digits
                server_password = ''.join(random.sample(s, 10))
                rcon_password = ''.join(random.sample(s, 10))

                if find_response.status_code == 200 and len(find_response_json['servers']) > 0:

                    serveme_server = find_response_json['servers'][0]

                    book_response = requests.post('https://au.serveme.tf/api/reservations?api_key=' + config.cfg.SERVEME_API_KEY, json={
                        "reservation": {
                            "starts_at": find_payload['reservation']['starts_at'],
                            "ends_at": find_payload['reservation']['ends_at'],
                            "server_id": serveme_server['id'],
                            "password": server_password,
                            "rcon": rcon_password,
                            "first_map": "cp_process_f12",
                            "server_config": "ozfortress_6v6_5cp"
                        }
                    })

                    if book_response.status_code == 200:

                        string_message = "```markdown\n"
                        string_message += "connect " + serveme_server['ip_and_port'] + "; password \"" + server_password + "\";"
                        string_message += "```"

                        rcon_message = "```markdown\n"
                        rcon_message += "rcon_address " + serveme_server['ip_and_port'] + "; rcon_password \"" + rcon_password + "\";"
                        rcon_message += "```"

                        str_msg = await strings_channel.send(content=string_message)
                        rcon_msg = await rcon_channel.send(content=rcon_message)
                        
                        return "Connect string: " + str_msg.jump_url
                    else:
                        return "Auto-booking didn't work :( please manually book a server."


                else:
                    raise bot.Exc.NotFoundError(ctx.qc.gt("No available servers."))

            else:
                print('Error:', response.status_code)
                raise bot.Exc.NotFoundError(ctx.qc.gt("Error booking serveme."))
				
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        raise bot.Exc.NotFoundError(ctx.qc.gt("Error booking serveme."))

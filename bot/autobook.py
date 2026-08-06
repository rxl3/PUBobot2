from core import config
from core.client import dc
from datetime import timedelta
import requests
import bot
import random
import string
import datetime

from rcon.source import Client

tfmap_name_dict = {
    "cp_process": "cp_process_f12", 
    "cp_snakewater": "cp_snakewater_final1", 
    "cp_sunshine": "cp_sunshine", 
    "cp_gullywash": "cp_gullywash_f9", 
    "cp_reckoner": "cp_reckoner", 
    "cp_metalworks": "cp_metalworks_f7",
    "koth_product": "koth_product_final", 
    "koth_bagel": "koth_bagel_rc13"
}

tfmap_rcon_dict = {
    "cp_process": "process", 
    "cp_snakewater": "snakewater", 
    "cp_sunshine": "sunshine", 
    "cp_gullywash": "gullywash", 
    "cp_reckoner": "reckoner", 
    "cp_metalworks": "metalworks",
    "koth_product": "product", 
    "koth_bagel": "bagel"
}

async def book_serveme(ctx, match_id=None, tfmap="cp_process"):
    try:
        strings_channel = dc.get_channel(config.cfg.DC_STRINGS_CHANNEL_ID)
        rcon_channel = dc.get_channel(config.cfg.DC_RCON_CHANNEL_ID)
		
        matches = [m for m in bot.active_matches if m.qc.id == ctx.qc.id and m.id != match_id]

        existing_booking = False
        existing_message = None
        existingR = requests.get("https://au.serveme.tf/api/reservations?api_key=" + config.cfg.SERVEME_API_KEY + "&limit=1")
        if existingR.status_code == 200:
            existingJson = existingR.json()
            existing_booking = len(existingJson['reservations']) > 0 and existingJson['reservations'][0]['status'] == "Ready"
        async for message in strings_channel.history(limit=5):
            if message.author == dc.user:
                existing_message = message
                break

        if existing_booking:
            booked_server = existingJson['reservations'][0]
            serveme_server = booked_server['server']
            if len(matches) > 1: 
                return {
                    "connect": "Auto-booked server is already in use, please manually book a server.",
                    "resolved_ip": serveme_server['resolved_ip'],
                    "port": serveme_server['port'],
                    "password": booked_server['password'],
                    "rcon_password": booked_server['rcon'],
                    "success": True
                }
            else:
                return {
                    "connect": "Connect string: " + existing_message.jump_url,
                    "resolved_ip": serveme_server['resolved_ip'],
                    "port": serveme_server['port'],
                    "password": booked_server['password'],
                    "rcon_password": booked_server['rcon'],
                    "success": True
                }
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
                            "first_map": tfmap_name_dict[tfmap] if tfmap_name_dict[tfmap] else "cp_process_f12",
                            "server_config_id": 1 # 1 = ozfortress_6v6_5cp, 2 = ozfortress_6v6_koth, 21 = ozfortress_6v6_pug
                        }
                    })

                    if book_response.status_code == 200:

                        string_message = "```markdown\n"
                        string_message += "connect " + serveme_server['resolved_ip'] + ":" + serveme_server['port'] + "; password \"" + server_password + "\";"
                        string_message += "```"

                        rcon_message = "```markdown\n"
                        rcon_message += "rcon_address " + serveme_server['resolved_ip'] + ":" + serveme_server['port'] + "; rcon_password \"" + rcon_password + "\";"
                        rcon_message += "```"

                        str_msg = await strings_channel.send(content=string_message)
                        rcon_msg = await rcon_channel.send(content=rcon_message)
                        
                        return {
                            "connect": "Connect string: " + str_msg.jump_url,
                            "resolved_ip": serveme_server['resolved_ip'],
                            "port": serveme_server['port'],
                            "password": server_password,
                            "rcon_password": rcon_password,
                            "success": True
                        }
                    else:
                        return {
                            "connect": "Auto-booking didn't work :( please manually book a server.",
                            "success": False
                        }
                else:
                    raise bot.Exc.NotFoundError(ctx.qc.gt("No available servers."))
            else:
                print('Error:', response.status_code)
                raise bot.Exc.NotFoundError(ctx.qc.gt("Error booking serveme."))
				
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        raise bot.Exc.NotFoundError(ctx.qc.gt("Error booking serveme."))


async def rcon_cmd_exec(ctx, ip: str, port: str, pwd: str, cmd: str):
	try:
		# strings = rcon_str.split(' ')
		# ip_and_port = strings[1].split(':')
		# ip = ip_and_port[0]
		# port = ip_and_port[1]
		# pwd = strings[3].replace('"', '')
		with Client(ip, port, passwd=pwd) as client:
			response = client.run(cmd)
			print(response)
			await ctx.success(ctx.qc.gt("Done."))
	except:
		await ctx.error(ctx.qc.gt("Could not parse command."))
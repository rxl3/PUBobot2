# PUBobot2 (Pride Pugs modifications by Chungus McBungus)
**PUBobot2** is a Discord bot for pickup games organisation. PUBobot2 have a remarkable list of features such as rating matches, rank roles, drafts, map votepolls and more!

## This is a forked version with modifications - Designed for the Pride Pugs TF2 Community
This version contains QoL modifications specifically aimed at improving the overall experience in TF2 pugging (See the Context section below)

I eventually hope to have these changes implemented in a way that is convenient, fully configurable, and does not interfere with the existing flow of PUBobot2 so that the fork can be merged in to the original bot as useful optional features

__**Changes:**__
- Database can now track when a player is a "Captain" in their match
- Players can be given **Immunity** for x number of games after playing Captain
- Drafting Stage:
  - (If either team does not yet have a Captain) Player list can now be randomised while also filtering **Immune** players to the bottom of the list
  - (When both teams have a Captain) Player list can now be re-ordered based on Division Roles to aid team selection
  - Player name format can be configured to any string, with variables for Division and Class Roles, Mention, Nickname, Immunity, etc
- Check-In Lifetime can now be made visible (Time remaining until check-in is discarded)
- Configurable variables for the above features
- Games which have ended automatically due to time-out report a "Draw" instead of giving an Error message (Necessary for the game to be logged to DB for Immunity tracking)
- ENV variables can now come from a .env file OR the config.cfg file (This is necessary for most web hosting services, unless you want your private discord Tokens on github)

__**Context:**__
The TF2 community was previously using PUBobot in the following way:
1) All 12 players add and ready up, we enter the Draft stage
2) We use Dyno bot's /roll command to determine which players will be forced to play Medic (Get 5 random numbers ranging from 1-12)
   - If the first die rolls "5" and you are the 5th player in the list, then you are the Medic (and Captain)
   - After someone plays Medic in a pug, they are Immune from playing Medic for 2 games
3) If either of the rolled players had played Medic in the last 2 games, they will type "Immune" and post a link to a match log as evidence
4) We then move down the dice roll list to see who will be captain...
5) Once captains are finally decided, they take turns picking players for their teams
6) If a newer player (or someone who doesn't know the other players very well) is captain then they will need to ask others to help them pick the best players

As you can see this can be a hassle for 3 main reasons:
- Manual dice roll (and non-unique results, ie your 5 12-sided dice rolls might return "5 12 5 5 12")
- A lot of back-and-forth when players claim to be Immune: Players have to dig up their match logs, Mods have to confirm that the player is not lying, Players who were further down the dice roll list sometimes go AFK because they think they aren't captain, etc
- It can be very difficult to pick a balanced team unless you know everyone on the server (and sometimes people who offer to "help" you pick can be trolls)

__**TODO List:**__
- Auto-ready players for x minutes after adding
- Auto-ready when already auto-readied should update instead of disable the current auto-ready (maybe we can disable it explicitly with /auto_ready off)
- Auto-ready default to minutes if nothing specified (eg: `!ar 15` should do the same as `!ar 15m`)
- Change the useless error message if someone does `!ar 20m` when `15m` is the max
- Times added to the Match Results print-out: Time taken to pick teams, Time taken to play game
- Option to save games to the database even when they are unranked (current workaround is to use flat ranking system gaining 0.1 per win)
- Map voting AFTER teams have readied up
- Configurable variables for all of the above (to toggle on/off)
- 
# Original PUBobot2 Readme content:

### Using the public bot instance
If you want to test the bot, feel free to join [**Pubobot2-dev** discord server](https://discord.gg/rjNt9nC).  
All the bot settings can be found and configured on the [Web interface](https://pubobot.leshaka.xyz/).  
For the complete list of commands see [COMMANDS.md](https://github.com/Leshaka/PUBobot2/blob/main/COMMANDS.md).  
You can invite the bot to your discord server from the [web interface](https://pubobot.leshaka.xyz/) or use the direct [invite link](https://discord.com/oauth2/authorize?client_id=177021948935667713&scope=bot).

### Support (Original Developer
Hosting the service for everyone is not free, not mentioning the actual time and effort to develop the project. If you enjoy the bot please subscribe on [Boosty](https://boosty.to/leshaka).

## Hosting the bot yourself

### Requirements
* **Python 3.9+** 
* **MySQL**.
* **gettext** for multilanguage support.

### Installing
* Create mysql user and database for PUBobot2:
* * `sudo mysql`
* * `CREATE USER 'pubobot'@'localhost' IDENTIFIED BY 'your-password';`
* * `CREATE DATABASE pubodb CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;`
* * `GRANT ALL PRIVILEGES ON pubodb.* TO 'pubobot'@'localhost';`
* Install required modules and configure PUBobot2:
* * `git clone https://github.com/Leshaka/PUBobot2`
* * `cd PUBobot2`
* * `pip3 install -r requirements.txt`
* * `cp config.example.cfg config.cfg`
* * `nano config.cfg` - Fill config file with your discord bot instance credentials and mysql settings and save.
* * Optionally, if you want to use other languages, run script to compile translations: `./compile_locales.sh`.
* * `python3 PUBobot2.py` - If everything is installed correctly the bot should launch without any errors and give you CLI.

## Credits
Developer: **Leshaka**. Contact: leshkajm@ya.ru.  
Used libraries: [discord.py](https://github.com/Rapptz/discord.py), [aiomysql](https://github.com/aio-libs/aiomysql), [emoji](https://github.com/carpedm20/emoji/), [glicko2](https://github.com/deepy/glicko2), [TrueSkill](https://trueskill.org/), [prettytable](https://github.com/jazzband/prettytable).

## License
Copyright (C) 2020 **Leshaka**.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License version 3 as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

See 'GNU GPLv3.txt' for GNU General Public License.

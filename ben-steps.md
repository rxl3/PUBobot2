Steps Ben had to follow to get PUBobot2 working on a Windows 11 pc

# Required Programs, Environment vars, and DB Setup

1) Install Python 3.9+
2) Install MariaDB (as MySQL is not free), configure the root user
3) Add the Environment variables to System Path in windows settings (Scripts folder is for `pip` to work)
    - E:\Installed Programs\Python
    - E:\Installed Programs\MariaDB 11.3\bin
    - E:\Installed Programs\Python\Scripts
4) Close your cmd terminal and reopen it so the Environment Path updates, check it with `echo $env:path` (in PowerShell) or `echo %Path%` (in cmd)
5) Setup the user and db on MariaDB for PUBobot2
    `mariadb`
    `CREATE USER 'pubobot'@'localhost' IDENTIFIED BY 'your-password';`
    `CREATE DATABASE pubodb CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;`
    `GRANT ALL PRIVILEGES ON pubodb.* TO 'pubobot'@'localhost';`
    Exit out of maridb (Ctrl+Z, then Enter)

# Get a clone of PUBobot2 on your pc

1) Clone the git repo, or download your clone (Mine is at https://github.com/benoz11/PUBobot2.git)
2) Open folder in vscode

# Create the Discord bot instance

1) Steps here https://www.writebots.com/discord-bot-token/ 
2) Make sure the bot application has been invited to your server

# Configure the bot locally

1) Edit config.cfg and add in your Discord bot application settings
    - DC_BOT_TOKEN      (Bot -> Reset Token -> Copy Token)
    - DC_CLIENT_ID      (OAuth2 -> Client ID -> Copy)
    - DC_CLIENT_SECRET  (OAuth2 -> Client Secret -> Reset Secret -> Copy)
    - DC_INVITE_LINK    (UNSURE - TODO?)
    - DC_OWNER_ID       (Your personal Discord user ID)
    - DC_SLASH_SERVERS  (UNSURE - TODO?)
    - DB_URI            ("mysql://pubobot:your-password-here@localhost:3306/pubodb")
    - Other Items to be configured after getting a hosting service

# Install Requirements

Original README steps:

1) `pip3 install -r requirements.txt`

I also needed to do the following:

1) `pip3 install python-gettext`
2) `pip3 install setuptools`
3) `pip3 install mariadb`
4) Edit the pyreadline library to avoid the "has no attribute 'Callable'" error (See https://stackoverflow.com/a/73353426)

# Configure the bot settings on Discord Server (can't use web interface when self hosting)

### Quick channel config
`/channel enable`
`/channel set variable: prefix value: /`

### Quick queue config
`/queue create_pickup name: test size: 4`
`/queue set queue: test variable: pick_teams value: draft`
`/queue set queue: test variable: pick_captains value: no captains`
`/queue set queue: test variable: pick_order value: ababbababa`
`/queue set queue: test variable: team_names value: RED BLU`
`/queue set queue: test variable: team_emojis value: :red_circle: :blue_circle:`
`/queue set queue: test variable: captain_immunity_games value: 2`

# Power on
`python3 PUBobot2.py` or `py PUBobot2.py`

# WEB HOSTING
This was a whole thing as a lot of the self-deploying web hosts use something like Docker on Linux to run Python, which is going to have a lot of different dependencies compared to self hosting on Windows PC

Currently hosting on Railway app with ENV vars set up 
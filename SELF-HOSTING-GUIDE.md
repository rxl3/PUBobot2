# Self-Hosting Guide (Windows 10)

> The steps given in the original Readme by Leshaka did not entirely work for my Windows 10 PC
> 
>  I have added all of the original + additional steps to this document, hopefully it is useful for someone
>
> *\- Chungus McBungus*

**<u>Table of Contents</u>**
- [Self-Hosting Guide (Windows 10)](#self-hosting-guide-windows-10)
- [Getting Started](#getting-started)
  - [☀️ Required Programs](#️-required-programs)
  - [☀️ Local Environment \& Database Setup](#️-local-environment--database-setup)
  - [☀️ Clone the git Repository](#️-clone-the-git-repository)
  - [☀️ Create a Discord Bot instance](#️-create-a-discord-bot-instance)
  - [☀️ Configure the Bot locally](#️-configure-the-bot-locally)
  - [☀️ Install the Dependencies](#️-install-the-dependencies)
  - [☀️ Start the Bot Python program (Cross your fingers and toes)](#️-start-the-bot-python-program-cross-your-fingers-and-toes)
- [Common Errors](#common-errors)
- [Further Configuration](#further-configuration)
  - [☀️ Configure the bot settings on Discord Server (can't use web interface when self hosting)](#️-configure-the-bot-settings-on-discord-server-cant-use-web-interface-when-self-hosting)
- [WEB HOSTING](#web-hosting)
  - [☀️ How Chungus McBungus is currently hosting the bot (privately)](#️-how-chungus-mcbungus-is-currently-hosting-the-bot-privately)
    - [Hosting Provider](#hosting-provider)
    - [Steps](#steps)

# Getting Started

## ☀️ Required Programs

You will need the following programs, or some equivalent. The program I have used for each is listed in parentheses (like this):
- Text Editor (Visual Studio Code)
- Your choice of terminal (Powershell - Comes with Windows 10)
- Git
- Python 3.9+ (Python 3.12.3)
- MariaDB / MySQL (MariaDB 11.3.2)

## ☀️ Local Environment & Database Setup

1) Ensure Python and MariaDB are installed Install, and the MariaDB **root** user has been set up
2) Add the following 3 items to your ***System*** Environment Variables (Not ***User*** Variables) for `Path` in [Windows settings](https://www.opentechguides.com/how-to/article/windows-10/113/windows-10-set-path.html)
       
    `E:\Installed Programs\Python`

    `E:\Installed Programs\MariaDB 11.3\bin`

    `E:\Installed Programs\Python\Scripts`
        


3) Close your terminal and re-open it to update the Environment Variables
   - Check that it is working by using `echo $env:path` (in PowerShell) or `echo %Path%` (in cmd)
4) Setup the **USER** and **DATABASE** on MariaDB for PUBobot2
    - Login as root to MariaDB (using whatever password you originally set, or blank if no password)
        ```bash
        mariadb -uroot -p
        ```
    - Create the `pubobot` User & `pubodb` Database (replace `your-password-here` with a password you wish to use for the bot)
        ```sql
        CREATE USER 'pubobot'@'localhost' IDENTIFIED BY 'your-password-here';
        CREATE DATABASE pubodb CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
        GRANT ALL PRIVILEGES ON pubodb.* TO 'pubobot'@'localhost';
        ```
    - Exit out of MariaDB (Ctrl+Z, then Enter - depending on your terminal)

## ☀️ Clone the git Repository

You can download the zip from Github or use the `git clone` command

- Pride Pugs fork https://github.com/chungusmcbungus/PUBobot2/tree/master
- Original Leshaka version https://github.com/Leshaka/PUBobot2 

## ☀️ Create a Discord Bot instance

1) Steps here https://www.writebots.com/discord-bot-token/ 
2) Make sure the Bot application has been invited to your server
3) Make sure it has all the Discord permissions it needs

## ☀️ Configure the Bot locally

Discord Bot variables can be found on Developer Portal [Applications Page](https://discord.com/developers/applications) for your Bot instance

1) Within the Pubobot2 folder Create (or Edit) the file `config.cfg` (or `.env`) and add in your Discord Bot application settings
    - `DC_BOT_TOKEN`      (Bot -> Reset Token -> Copy Token)
    - `DC_CLIENT_ID`      (OAuth2 -> Client ID -> Copy)
    - `DC_CLIENT_SECRET`  (OAuth2 -> Client Secret -> Reset Secret -> Copy)
    - `DC_INVITE_LINK`    (UNSURE - TODO?)
    - `DC_OWNER_ID`       (Your personal Discord user ID)
    - `DC_SLASH_SERVERS`  (UNSURE - TODO?)
    - `DB_URI`            (`"mysql://pubobot:your-password-here@localhost:3306/pubodb"`)
    - *Other Items to be configured after getting a hosting service*

This allows the Python program running on your computer to talk to the Discord Bot instance

See [Leshaka's Example config file](https://github.com/Leshaka/PUBobot2/blob/main/config.example.cfg) for a template

## ☀️ Install the Dependencies

> Original README steps:

1. 
    ```bash
    pip3 install -r requirements.txt
    ```

> I also needed to do the following:

2. 
    ```bash
    pip3 install python-gettext && pip3 install setuptools && pip3 install mariadb
    ```
3. [Edit the pyreadline library](https://stackoverflow.com/a/73353426) to avoid the "has no attribute 'Callable'" error

## ☀️ Start the Bot Python program (Cross your fingers and toes)

> Depending on your python version and install method you may need to use either `python3` or `py` to run python programs

1. Run one of the following commands in your terminal
    ```bash
    python3 PUBobot2.py
    # or 
    py PUBobot2.py
    ```

---
# Common Errors

**TODO:** Fill this out

- peepee
- poopoo

---
# Further Configuration

## ☀️ Configure the bot settings on Discord Server (can't use web interface when self hosting)

Run these slash commands within Discord on your server which is running the Bot

- Quick channel config

    `/channel enable`

    `/channel set variable: prefix value: !`

-  Quick queue config
  
    `/queue create_pickup name: test size: 4`
    
    `/queue set queue: test variable: pick_teams value: draft`
    
    `/queue set queue: test variable: pick_captains value: no captains`
    
    `/queue set queue: test variable: pick_order value: ababbababa`
    
    `/queue set queue: test variable: team_names value: RED BLU`
    
    `/queue set queue: test variable: team_emojis value: :red_circle: :blue_circle:`
    
    `/queue set queue: test variable: captain_immunity_games value: 2`

    **TODO:** - Add the rest of these in to the document

---


# WEB HOSTING

> This was a PAIN IN THE ASS to do the first time around
>
> Leshaka's version of the program uses a `config.cfg` file for all the discord bot tokens, which meant that to host this bot I would need to either 
> - Have my private discord tokens publicly available on my github repo (bad), OR
> - Use a hosting service that lets me work entirely from the backend files (difficult)
>
> For whatever reason I decided instead to modify the program so that it can use Environment Variables if no `config.cfg` file is present
>
> Locally this would load from a `.env` file, but when web hosting this would be under your Projects "System Environment Variables"
>
> Use whatever method you prefer
>
> *\- Chungus McBungus*


## ☀️ How Chungus McBungus is currently hosting the bot (privately)

### Hosting Provider

Using [Railway](https://railway.app/)
- Hobby Plan ($5 per month)
- 2 Architecture items
  - **Github Repo** (pointing to my repo)
  - **MySQL Database**

### Steps

1. Set up the 2 items under Architecture (**Github Repo** + **MySQL Database**)
2. Edit Settings for the **Github Repo** item
    - Make sure it points to the correct branch
    - Use Private Networking
    - Builder "Nixpax"
    - Provider "Python"
    - Custom Start Command `sleep 3 && python PUBobot2.py` (This is needed or bot will just keep crashing on deploy)
3. Edit Settings for the MySQL item
   - Custom Start Command `docker-entrypoint.sh mysqld --performance_schema=0` (Apparently helps keep usage down)
4. Add Service Variables to the **Github Repo** item (Pubobot2 -> Variables -> New Variable)
    - Add the `DC_` Tokens from `.env`
    - Add one named `DB_URI` and copy in the value from the MySQL database variable `MYSQL_PRIVATE_URL`
5. Deploy **MySQL Database**
6. Deploy **Github Repo** (Cross your fingers and toes)

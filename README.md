<h3 align="center">Man-chan Discord Bot</h3>


Manchan is a discord bot made by three friends intended to be used by a small group of friends or users in a server.

This bot is not hosted and cannot be added to a server. It is intended to be self-hosted with whatever method by cloning this repo.

## Features:

### **Shared Login**
If you share accounts between others in the server, Manchan offers a way to list all the shared accounts usernames/password discreetly via command. (*Note: Currently no way to blacklist/whitelist users*). A `login.json` file is needed to store the login information, the structure on how is at the bottom of the page.

`!login` - Starts login sharing.

### **Social Credit**
By providing emoji names representing upvotes/downvotes, users that react with corresponding emoji to a message will influence the sender's social score. Leaderboard included.

`!score` - Displays self score.

`!score @username` - Displays score of user.

`!leaderboard` || `!lb` - Displays leaderboard of all users in server.

### **Anilist Integration**
Uses Anilist API to search for anime for sharing info. Register your anilist account (only username needed) and you can display your anime ratings as well.

`!anime <title>` || `!ani`: Searches for an anime.

`!manga <title>` || `!man`: Searches for a manga.

`!novel <title>` || `!nov`: Searches for a novel.

```
Example: !ani one piece
```

`!account` || `!acc`: Creates an embed where you provide your Anilist username. Database must be enabled.

`!anilb` || `!alb`: Displays leaderboard of most view time and read amount for all registered users.

### **Spotify Share Link**
Share a song from spotify.

`!track`: Share track via search keywords.

`!album`: Share album via album name.

```
Examples:
!track magnolia playboi carti
!album whole lotta red
```

### **Fun**
Random commands.

`!choose`: Randomly choose one of the options. Delimited by commas.
```
Example: !choose pizza, chicken and waffles, burger
> chicken and waffles
```

### **Plugins**
Allows you to load exterior commands outside of the main functionality.
List these under a `/plugins` folder.

For example, let's say you have two github repos with sets of commands that are compatible with ManChan bot: `images` and `encoder`.

Add those to the plugins folder like so:
`/plugins/image/generator.py`
`/plugins/image/formatter.py`
`/plugins/encoder/encode.py`

Each of those modules will be loaded like any other Cog.

## Coming soon:
### **Money Ledger**
Keep track of what each person owes money too. Useful for social events where one person pays for everyone and stuff.

### **Letterbox Integration**
Same as Anilist, but movies.

### **Backloggd Integration**
Same as Anilist and Letterbox, but games.

### **Youtube Music Streaming**
Listen to music while in voice chat.

# Setup

## Virtual Environment
Use your favorite method to setup the virtual environment. Here will be a quick rundown using the `virtualenv` package.

1. `pip install virtualenv`
2. `python -m virtualenv venv`

3. If on Windows:

    `.\venv\Scripts\activate`
    
    Note that if using powershell, you may have to enable scripts to be runnable.

    If on Linux:

    `source ./venv/bin/activate`

    If you are using VsCode, you will be prompted if you want to enable this virtual environment as default. Click yes so you do not run above every time.

4. `pip install -r requirements.txt`


## Database
You need to specify the database location in the configs file (more detail below).

Run this to update the current db. <u>**Do this every time you pull to keep the database updated**</u>:

`alembic upgrade head`

Run this to create a new revision on changes:

`alembic revision --autogenerate -m "revision name"`


# Usage

### How to create your own discord bot
Read any tutorial on making your own discord bot with its keys.
https://discordpy.readthedocs.io/en/stable/discord.html

### Configuration
Create a file called `configs.yaml` and place it at the root of the directory. This is needed to disable or enable features you want to use as well as provide API keys and Discord tokens. The template is at the bottom of this page; copy its contents and paste it into `configs.yaml` and change the variables as you wish.

The following commands/cogs need the following configs or jsons setup (structure at bottom of the page):
- `login`: Needs `login.json` file at the root directory.

### Run bot
With a terminal or as execution for docker:
```
python main.py
```

# Development Guide
Manchan uses the [Disnake](https://docs.disnake.dev/en/stable/) library for development.

## Directory Structure
The Manchan system is separated to the following structured

### **/cogs**
Directory where files containing the discord command interface

Each cog file must contain a class that inherits from `CommandBase`. 

This class must have:
```python
@classmethod
  def is_enabled(cls, configs: Dict[str, Any] = {}) -> bool:
```
This function should check the config file and verify that it has the appropriate variables needed to operate as well check if the command is enabled. For example, if `ENABLE_SOCIAL_CREDIT` is true, but `UPVOTE_EMOJI_NAME` is missing, the Social Credit should not be enabled.

In order for Cogs to be loaded via Disnake, each Cog file must have a global function:
```python
def setup(bot: ManChanBot):
  if Cog.is_enabled(bot.configs):
    bot.add_cog(Cog(bot))
  else:
    logging.warn("SKIPPING: cogs.cogname")
```
That function will run as the bot is starting up from `main.py`.

As a general rule, keep code here to a minimum for simplicity. Treat Cogs as if they were API endpoints for Cog commands. All the backend heavy-work should take place in **/service**.

### **/db**
Directory for database interactions using [SQLAlchemy](https://www.sqlalchemy.org/).

Remember to run this whenever you modify the database to create a new migration:

`alembic revision --autogenerate -m "revision name"`

Also remember to run this whenever you pull changes to keep your local database up to date:

`alembic upgrade head`

### **/fetcher**
Directory for modules involved with third-party API fetching.

### **/models**
Directory with templated queries or other data models. For example, the Anilist grapghql queries are stored here.

### **/service**
Directory that creates the backbone of all the Cog logic. For best practice, create a folder named after the Cog that contains the different types of services it can do.

For Discord UI interactionm base classes are provided: `ServiceBase` and `CallbackBase`.

**ServiceBase** is what will initialize the interaction and create the appropriate embeds, views, etc. If one of these would have a callback that would take the user to a new page, the callback can be stored in **CallbackBase**.

**CallbackBase** acts as a linked list for the history of interactions, like a web page, so that previous and forward functionality can be implemented.

Another general rule for good practice, you can inherit from Disnake's UI objects like Embed or Views to keep logic containerized and easy to follow.

### **/utils**
Random useful tools when developing. One thing to point out is the `config_mapper.py` that maps the config keys into global variables for reusability.

## Formatting
A formatting python script has been added to keep formatting consistent. Before pushing up to your branch, make sure you run:

`python fmt.py`

and fix any typing errors that it throws at you.

# Config File
ManChan will read from a provided `configs.yaml` in the root folder that you must fill out yourself. Recommended structure is below:

```yaml
# Discord Bot Settings
DISCORD_TOKEN: "Provide your own"
COMMAND_PREFIX: "!"
PRESENCE_TEXT: "" # The text shown when online: 'Playing xxx'
DATABASE_URL: "sqlite:///test_magi.db" # Change this as needed
FORCE_DATABASE: true # if true, won't start without a database. Disable if you don't need one.
ADMIN_USERS:
  - Add User Discord ID Here

# Anilist Settings
ENABLE_ANILIST: true

# Social Credit Settings
ENABLE_SOCIAL_CREDIT: true
UPVOTE_EMOJI_NAME: "" # Can use custom guild emojis. Put the name without the colons
DOWNVOTE_EMOJI_NAME: "" # But both must be provided
SOCIAL_CREDIT_WHITELIST: # Guilds to enable this function
  - Add Guild ID Here
SOCIAL_CREDIT_TIME_LIMIT: 86400 # In seconds, 24hr. Won't accept reactions after that time limit

# Login Settings
ENABLE_LOGIN: true
LOGIN_FILE_PATH: "login.json"
LOGIN_INFO_TIMEOUT: 15 # In seconds

#Spotify API Tokens
ENABLE_SHARE_LINK: true
SPOTIFY_CLIENT_ID: "Provide Own"
SPOTIFY_CLIENT_SECRET: "Provide Own"

# Misc Settings
```

# Login format
When adding a source to the `login.json` be sure to follow this format:
```json
  {
    "Site-Name" : {
      "email": "johnwick@gmail.com",
      "password": "password1234",
      "emoji_text": ":emoji_name",
      "emoji" : "🟠",
      "description" : "Description of Streaming Service",
      "link" : "Link to Streaming Service",
      "hex" : "Site Color in Hex Form #111111",
      "provider" : "Person providing this"
    },
    "Site-Name2" : {
      ...
    }
  }
```
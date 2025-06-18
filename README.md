<h3 align="center">Man-chan Discord Bot</h3>


Manchan is a discord bot made by four friends intended to be used for small servers -- such as small friend groups or communities.

**This bot is not hosted publicly and cannot be added to a server.**


It is intended to be self-hosted by cloning this repo or using this as a starting framework for your own discord bot. Feel free to fork this or borrow ideas.

## Features:

### **Shared Login**
If you want to share account logins with others in your server, Manchan offers a way to list all the sharable accounts with the username/password discreetly via command.

A `login.json` file is needed to store the login information. Usage of this fileis at the bottom of this page.

(*Note: Currently no way to blacklist/whitelist users*).

`!login` - Starts login sharing.

### **Social Credit**
By providing emoji names representing upvotes/downvotes, users that react with the corresponding emoji to a message which will influence the sender's social score. Leaderboard included.

`!score` - Displays self score.

`!score @username` - Displays score of user.

`!leaderboard` || `!lb` - Displays leaderboard of all users in server.

### **Anilist Integration**
Uses Anilist API to search for anime for sharing shows watched and user ratings.

Requires linking your Anilist account to the database using only your username. This allows displaying user ratings and public user stats.

(*Note: Currently has issues registering users).

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

### Twitter, Instagram, and TikTok Video Embed
Can automatically detect if a message is a link for a Twitter post, Instagram post, or TikTok video.

For Twitter, a camera reaction emoji will appear where by clicking it, it will convert the message to an embed. This is because not every post needs to automatically embedded.

For Instagram, this is automatic. The API used is unstable however and may not always work.

For TikTok, this is automatic. It uses QuickVids API: https://github.com/quickvids

### Youtube Music Streaming
Allows Manchan to join a voice channel and stream YouTube music. Users can also create custom playlists from songs played or manually add songs to the playlists.

This is all empowered by slash commands and embed interactions.

Requires a database to exist and a designated channel.

Do `/init_music`.

### **Fun**
Random commands.

`!choose`: Randomly choose one of the options. Delimited by commas.
```
Example: !choose pizza, chicken and waffles, burger
> chicken and waffles
```

`!conch` or `!8ball`: Ask a question, get an answer!
Inspired by Spongebob's magic conch shell. But it is not mandatory to use the
conch as part of this command. Supply an image url in the config mapper to
send a custom image, including a conch if you desire.
```
Example: !conch Can I have something to drink?
> No.
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

If a database is required, its own separate `alembic.ini` is required and must be manually managed. This is to avoid revision conflicts with the main features.


## Coming soon:
### **Money Ledger**
Keep track of what each person owes money too. Useful for social events where one person pays for everyone and stuff.

### **Letterbox Integration**
Same as Anilist, but movies.

### **Backloggd Integration**
Same as Anilist and Letterbox, but games.

# Usage

### How to create your own discord bot
Read any tutorial on making your own discord bot and get a discord token.
https://discordpy.readthedocs.io/en/stable/discord.html

### Configuration
Create a file called `configs.yaml` and place it at the root of the directory. This is needed to disable or enable features you want to use as well as provide API keys and Discord tokens. The template is at the bottom of this page; copy its contents and paste it into `configs.yaml` and change the variables as you wish.

For example, `ENABLE_LOGIN: true` will enable the shared login feature.


### Shared Logins
A `login.json` file is needed at the root of the directory if you want to use the shared login feature. An example structure is provided at the bottom of this page.


## Setup

### Docker Setup (Recommended)
No port forwarding required! Only docker is needed to be installed on your machine.

1. Create a `compose.yaml` file. An example on the structure is given on `compose-example.yaml`

2. Create a folder where you want the manchan data to exist. Add the absolute path of this folder to `compose.yaml`

3. Place the following files into the created folder. Any optional files you dont want remove those paths from the `compose.yaml` file to prevent errors:
    - `configs.yaml` (required)
    - `compose.yaml` (required)
    - `login.json` (optional)
    - A sqllite database (optional - for plugins usage)

3. Add a database password to the following locations:
    - `configs.yaml`
    - `alembic.ini`
    - `compose.yaml` (add a port for host computer here too)

4. Build the docker image:

    ```
    docker build . -t manchan
    ```

5. You need to edit the `configs.yaml` file with a discord token and any features you want.

6. Within the created folder in step 2, run:

    ```
    docker compose up -d
    ```

    The `-d` is so that it runs in the background. Don't add it on the first run so you can debug any issues.

**Any time you want to update Manchan**, you must pull this repo again. Then rerun step 4. Then step 6. Database migrations are automatically applied this way.


### No Docker -- Virtual Environment
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

5. Add a database password or modify database url to the following locations:
    - `configs.yaml`
    - `alembic.ini`

    Typically it follows the structure of `<db-type>://<user>:<password>@<url>:<port>/`. **Postgres is highly recommended and is the tested database type.**

6. You need to edit the `configs.yaml` file with a discord token and any features you want.

7. Update the database with `alembic upgrade head`

8. Run with `python main.py`

Anytime you pull the latest changes from this repository, repeat step 7.


# Config File
ManChan will read from a provided `configs.yaml` in the root folder that you must fill out yourself. Recommended structure is below:

```yaml
# Discord Bot Settings
DISCORD_TOKEN: "Provide your own"
COMMAND_PREFIX: "!"
PRESENCE_TEXT: "" # The text shown when online: 'Playing xxx'
DATABASE_URL: "postgresql+psycopg2://postgres:PASSWORD@manchandb/" # Change this as needed. SQLlite example: sqlite:///test_magi.db
FORCE_DATABASE: true # if true, won't start without a database. Disable if you don't need one.
ADMIN_USERS:
  - Add User Discord ID Here

# Anilist Settings
ENABLE_ANILIST: true
ANILIST_URL: 'https://graphql.anilist.co' # Dont modify unless the API path changes

# Social Credit Settings
ENABLE_SOCIAL_CREDIT: true
UPVOTE_EMOJI_NAME: "" # Can use custom guild emojis. Put the name without the colons :
DOWNVOTE_EMOJI_NAME: "" # ...But both must be provided
SOCIAL_CREDIT_WHITELIST: # Guilds to enable this feature
  - Add Guild ID Here
SOCIAL_CREDIT_TIME_LIMIT: 86400 # In seconds, 24hr. Messages after that time limit won't register new reactions to prevent abuse.

# Login Settings
ENABLE_LOGIN: true
LOGIN_FILE_PATH: "login.json"
LOGIN_INFO_TIMEOUT: 15 # Embed timeout, in seconds

#Spotify API Tokens
ENABLE_SHARE_LINK: true
SPOTIFY_CLIENT_ID: "Provide Own"
SPOTIFY_CLIENT_SECRET: "Provide Own"

# Music
ENABLE_MUSIC: true # Enables YouTube music streaming

# Converter Settings
ENABLE_MEDIA_LINK_CONVERTER: true # This automatically embeds Twitter, Instagram, and TikTok

# Misc Settings
CONCH_URL: "" # Url path for the conch image
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

# Development Guide
Manchan uses the [Disnake](https://docs.disnake.dev/en/stable/) library for development.


The following upgrades the database to latest revisions:

```
alembic upgrade head
```

Run this to create a new revision:

```
alembic revision --autogenerate -m "revision name"
```

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


# Why the name "Manchan"
We are uncreative and merged all our names together to somehow create this.
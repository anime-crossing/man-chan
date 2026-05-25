<h3 align="center">Man-chan Discord Bot</h3>


Manchan is a discord bot made by four friends intended to be used for small servers -- such as small friend groups or communities.

This bot is not hosted and cannot be added to a server. It is intended to be self-hosted with whatever method by cloning this repo or to be used as a framework for your own bot.

## Features:
These features can be enabled and disabled via a `configs.yaml`. A sample file is included in the repo and a the bottom of this page.

### **Shared Login**
If you share accounts between others in the server, Manchan offers a way to list all the shared accounts usernames/password discreetly via command. (*Note: Currently no way to blacklist/whitelist users*). A `login.json` file is needed to store the login information. A sample file structure is given at the bottom of this page.

Auth info is shared through an ephemeral message. It is only visible to the user and is deleted after a timeout.

**Command:**
- `!login` - Starts login sharing.

**Config Variables:**
- `ENABLE_LOGIN` - true/false
- `LOGIN_FILE_PATH` - Default `login.json`.
- `LOGIN_INFO_TIMEOUT` - Default 15. Seconds before login info is removed.

### **Social Credit**
A joke way to build a social credit score in your server.

By providing emoji names representing upvotes/downvotes, users that react with corresponding emoji to a message will influence the sender's social score. Leaderboard included.

Database required.

**Commands:**
- `!score` - Displays self score.
- `!score @username` - Displays score of user.
- `!leaderboard` || `!lb` - Displays leaderboard of all users in server.

**Config Variables:**
- `ENABLE_SOCIAL_CREDIT` - true/false
- `UPVOTE_EMOJI_NAME` - Put the emoji name without colons. Custom guild emojis can work too.
- `DOWNVOTE_EMOJI_NAME` - Same as above.
- `SOCIAL_CREDIT_WHITELIST` - Guild IDs to enable this feature on.
- `SOCIAL_CREDIT_TIME_LIMIT` - Time in seconds before a message is no longer counted as social credit. You probably want this on. Default is `86400` (24h).

### **Anilist Integration**
For sharing anime recommendations and ratings.

Uses the Anilist API. To show recommendations, you must first "link" your Discord with Anilist. All this does is save your Anilist user to the database and associate it with your Discord ID (no login needed).

Database required for connecting accounts. But not for fetching anime info.

**Commands:**
- `!anime <title>` || `!ani`: Searches for an anime.
- `!manga <title>` || `!man`: Searches for a manga.
- `!novel <title>` || `!nov`: Searches for a novel.

  ```
  Example: !ani one piece
  ```

- `!account` || `!acc`: Creates an embed where you provide your Anilist username. Database must be enabled.

- `!anilb` || `!alb`: Displays leaderboard of most view time and read amount for all registered users.

**Config Variables:**
- `ENABLE_ANILIST` - true/false


### Twitter/X and Instagram Video Embed
Can automatically detect if a message is a link for a Twitter post or Instagram post and create an embed within the message, making it easy to share videos.

For Twitter, a camera reaction emoji will appear where by clicking it, it will convert the message to an embed. This is because not every post needs to automatically embedded.

For Instagram, this is automatic. The API used is unstable however and may not always work.

Tiktok used to be supported, but due to the difficulty of finding a right API provider and Discord already supporting embeds, this is disabled.
Add the QuickVids bot instead: https://github.com/quickvids

**Config Variables:**
- `ENABLE_MEDIA_LINK_CONVERTER` - true/false

### **Fun Commands**
Random commands.

#### Randomly Choose
`!choose`: Randomly choose one of the options. Delimited by commas.
```
Example: !choose pizza, chicken and waffles, burger
Manchan > chicken and waffles
```

#### Magic Conch Shell
`!conch` or `!8ball`: Ask a question, get an answer!

Inspired by Spongebob's magic conch shell. You can include an image response with whatever image you want, so include an image url of the magic conch shell in the configs.

**Config Variables:**
- `CONCH_URL` - Url to image for the conch message.

```
Example: !conch Can I have something to drink?
> No.
```

### **Plugins**
Allows you to load exterior commands outside of the main functionality and program your own commands.
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

# Setup
## How to create your own discord bot
Read any tutorial on making your own discord bot and get a discord token.
https://discordpy.readthedocs.io/en/stable/discord.html


## Configure Settings
Create a file called `configs.yaml` and place it at the root of the directory. Use the `configs-sample.yaml` in this github as an example.

This config file lets you enable/disable features and customize several settings. This is also where you put your Discord tokens.

If you want to use a database, you can use the database that comes from the docker setup (below) or supply your own. Currently only postgres is configured to work.


A `login.json` file is needed at the root of the directory if you want to use the shared login feature. An example structure is provided at the bottom of this page.

### Docker Setup (Recommended)
The easiest way to run Manchan is using docker. However it requires setting up a few config files.

Docker needs to be installed in your machine.

Then do the following steps.

1. Git clone this project
2. Run the following:

    ```
    docker build . -t manchan
    ```


3. In another directory, create a `docker-compose.yaml` file. A sample file is provided in `compose-sample.yaml`
4. Create a `.env` file. This will contain your database configurations. Right now, only postgres is supported.

    Use the `env-sample` file for reference. You can keep everything but change the password.

5. Create the additional config files. For any optional files you dont want, remove those paths from the `docker-compose.yaml` file to prevent errors:
    - `configs.yaml` (required)
    - `login.json` (optional)
    - `plugins/` (optional - if you are adding plugin commands)
      - A sqllite database (optional - for plugins usage)

6. Run the following:

    ```
    docker compose up
    ```

    Add a `-d` at the end if you want to run it detached (async and independent from the terminal).


NOTE: If you are on SELinux (like Fedora), put a `,Z` at the end of any paths for the volumes in docker compose. Example: `:ro,Z`. Or if no `ro/rw` exists, just `:Z`.

NOTE: If you get permission errors because you are on linux, run these:
```
sudo chown -R 999:999 ./dockerdb
sudo chmod -R 700 ./dockerdb
```

NOTE: If you have plugins and they require extra python libraries, create a `plugin-requirements.txt` file at the root of the directory (where docker build is being run)

Anytime a new version of Manchan is released, pull the latest version from GitHub and rerun the second step. Check if any new features were added that may need additional config variables.

To shut down Manchan:
```
docker compose down
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

Run this to create a new revision for a database migration:

```
alembic revision --autogenerate -m "revision name"
```

Create a postgres database for development:
```
services:
  postgres:
    image: postgres
    container_name: postgres
    environment:
      POSTGRES_USER: manchandb
      POSTGRES_DB: manchandb
      POSTGRES_PASSWORD: 123test
      POSTGRES_HOST: postgres
    volumes:
      - ./dockerdb:/var/lib/postgresql
    ports:
      - 5432:5432
```

And run using
```
python main.py
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


https://discord.com/developers/home
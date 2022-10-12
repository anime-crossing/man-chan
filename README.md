<h3 align="center">Man-chan Discord Bot</h3>


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



# Utilities

## Formatting
A formatting python script has been added to keep formatting consistent. Before pushing up to your branch, make sure you run:

`python fmt.py`

## Alembic
Run this to update the current db:

`alembic upgrade head`

Run this to create a new revision on changes:

`alembic revision --autogenerate -m "revision name"`

# Config File
ManChan will read from a provided `configs.yaml` in the root folder that you must fill out yourself. Recommended structure is below:

```
# Discord Bot Settings
DISCORD_TOKEN: ""
COMMAND_PREFIX: "!"
DATABASE_URL: "sqlite:///test_magi.db"  # Change as needed
FORCE_DATABASE: true  # If true, won't start without a database
ADMIN_USERS:
  - 

# Event listeners
ENABLE_SOCIAL_CREDIT: false
UPVOTE_EMOJI_NAME: ""  # Can use custom guild emojis
DOWNVOTE_EMOJI_NAME: ""  # But both must be provided
SOCIAL_WHITELIST: # Guilds to enable this function
  - 

# Misc Settings

```
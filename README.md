# Discord Album Bot

This bot uses Spotipy and Discord APIs to interact with users to display album information. Originally, this bot was created for me and my friends to complete an "album of the day"-esque challenge, but this fell through and is now used as needed instead. 

## Setup

1. Clone the repository.
2. create a `.env` file in the root of the directory with:
 - `discord_app_id`
 - `discord_public_key`
 - `discord_token`
 - `spotify_client_id`
 - `spotify_client_secret`
3. Make sure `db/` exists in the root. `src/scripts/table_create.py` creates the completed db, and will create `albums.db` if the name is changed on line 7.

## Prerequisites

Requires Python and Docker.

## Commands

| Command | Description |
|---|---|
| `!search <search_parameter>` | Polls the Spotify API for information on albums |
| `!add <album_title>` | Add an album to the "albums" table |
| `!completed <album_title>` | Removes an album from "albums" table and adds it to "completed" table |
| `!finished` | Displays a paginated list of all completed albums |
| `!remove <album_title>` | Remove an album from "completed" table |


## Start the bot

To start the bot, cd into src/docker and run ```docker compose up --build``` to build the container and start the application.

## File Structure
```
ALBUM BOT/
├── db/
│   ├── albums.db
│   └── completed.db
├── src/
│   ├── docker/
│   │   ├── docker-compose.yml
│   │   └── Dockerfile
│   ├── scripts/
│   │   ├── lists/
│   │   │   ├── original_list.txt
│   │   │   └── update_list.txt
│   │   ├── list_create.py
│   │   ├── table_create.py
│   │   └── update_bot.py
│   ├── bot.py
│   └── requirements.txt
├── .dockerignore
├── .env
├── .gitignore
└── README.md
```

## Future Features
Some features I would like to include at some point are:
- Hosting the bot so that it runs without me needing to start it every time.
- Fixing up some of the logic to ensure that the correct albums are added and not random ones (which can happen when polling the Spotify API).

## Additional Information
This repository also holds scripts that I used to update the bots at various points. The ```list_create``` and ```table_create``` files inside of the scripts files were used when I messed up the table and needed to recreate it multiple times to get it correct. The ```update_bot``` file was used in July 2026 to update the bot with albums I finished after falling behind on updating the bot.

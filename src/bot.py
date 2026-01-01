import sqlite3, discord, os, spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
from discord.ext import commands

load_dotenv()
token = os.getenv("discord-token")
spotify_client_id = os.getenv("spotify-client-id")
spotify_client_secret = os.getenv("spotify-client-secret")
client_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

connection = sqlite3.connect('./db/albums.db')
cursor = connection.cursor()

@bot.event
async def on_ready():
    print(f"we have logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

@bot.command(name='search')
async def search(ctx, *, query):
    results = spotify_search(query)
    embed = discord.Embed(
        title=results['name'],
        description=f"Artist: {results['artist']}",
        url=results['spotify_url']
    )
    embed.set_image(url=results['album_art'])
    await ctx.send(embed=embed)

def spotify_search(query):
    album = sp.search(q=query, type='album', limit=1)
    album_data = album['albums']['items'][0]
    return { 'name': album_data['name'],
            'artist': album_data['artists'][0]['name'],
            'release_date': album_data['release_date'],
            'album_art': album_data['images'][0]['url'] if album_data['images'] else None,
            'spotify_url': album_data['external_urls']['spotify'],
            'spotify_id': album_data['id']
        }

# randomizer

# inputter

@bot.command(name='put')
async def put(ctx, *, album):
    result = spotify_search(album)
    if result:
        message = put_album(result)
        await ctx.send(message)
    else:
        await ctx.send("Album not found on Spotify")


def put_album(album):
    try:
        cursor.execute(f"""INSERT INTO albums
                    (spotify_id,
                    name,
                    artist,
                    art_url,
                    release_date
                    )
                       VALUES(?, ?, ?, ?, ?)""", (album["spotify_id"], album["name"], album["artist"], album["album_art"], album["release_date"]))
        connection.commit()
        return {"message": f"Successfully added {album['name']}"}
    except:
        return {"message": f"error, unable to add the album"}
    
# get album
    



if __name__ == "__main__":
    bot.run(token)
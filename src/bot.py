import sqlite3, discord, os, spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
from discord.ext import commands
from discord.ui import Button, View
import random

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

# search spotify bot method
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

# queries spotify, kinda finicky and sometimes won't get what you want
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

# add an album method
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
@bot.command(name="get")
async def get(ctx):
    cursor.execute(f"SELECT COUNT(*) FROM albums")
    length = cursor.fetchone()[0]
    r = random.randint(1, length)
    cursor.execute(f"""SELECT * FROM albums WHERE album_id = ?""",(r,))

    album = cursor.fetchone()
    if album:
        results = spotify_search(album[2])
        
        embed = discord.Embed(
        title=results['name'],
        description=f"Artist: {results['artist']}",
        url=results['spotify_url']
        )
        embed.set_image(url=results['album_art'])
        await ctx.send(embed=embed)
    else:
        await ctx.send("Couldn't find album")

# album list
@bot.command(name='list')
async def list_albums(ctx):
    cursor.execute("SELECT name, artist, release_date FROM albums ORDER BY name")
    albums = cursor.fetchall()

    per_page = 10
    total_pages = (len(albums) + per_page - 1) // per_page
    
    class PaginationView(View):
        def __init__(self):
            super().__init__(timeout=60)
            self.current_page = 0
        
        def get_page(self):
            start = self.current_page * per_page
            end = start + per_page
            page_albums = albums[start:end]
            
            embed = discord.Embed(
                title="Albums",
                description=f"Total albums: {len(albums)}",
                color=discord.Color.blue()
            )
            
            for i, album in enumerate(page_albums, start=start+1):
                embed.add_field(
                    name=f"{i}. {album[0]}",
                    value=f"by {album[1]}, {album[2]}",
                    inline=False
                )
            
            embed.set_footer(text=f"Page {self.current_page + 1}/{total_pages}")
            return embed
        
        @discord.ui.button(label="◀", style=discord.ButtonStyle.primary)
        async def previous_button(self, interaction: discord.Interaction, button: Button):
            if self.current_page > 0:
                self.current_page -= 1
                await interaction.response.edit_message(embed=self.get_page(), view=self)
            else:
                await interaction.response.defer()
        
        @discord.ui.button(label="▶", style=discord.ButtonStyle.primary)
        async def next_button(self, interaction: discord.Interaction, button: Button):
            if self.current_page < total_pages - 1:
                self.current_page += 1
                await interaction.response.edit_message(embed=self.get_page(), view=self)
            else:
                await interaction.response.defer()
    
    view = PaginationView()
    await ctx.send(embed=view.get_page(), view=view)


if __name__ == "__main__":
    bot.run(token)
    
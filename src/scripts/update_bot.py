import spotipy,os, sqlite3
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

script_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.normpath(os.path.join(script_dir, "..", "..", ".env"))
load_dotenv(dotenv_path)

spotify_client_id = os.getenv("spotify-client-id")
spotify_client_secret = os.getenv("spotify-client-secret")

client_credentials_manager = SpotifyClientCredentials(
    client_id=spotify_client_id,
    client_secret=spotify_client_secret
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

albums_path = os.path.normpath(os.path.join(script_dir, "..", "..", "db", "albums.db"))
completed_path = os.path.normpath(os.path.join(script_dir, "..", "..", "db", "completed.db"))


connection = sqlite3.connect(albums_path)
cursor = connection.cursor()
connection2 = sqlite3.connect(completed_path)
cursor2 = connection2.cursor()

def get_album(album, artist):
    query = f"{album} {artist}"
    album = sp.search(q=query, type='album', limit=1)
    album_data = album['albums']['items'][0]
    return { 'name': album_data['name'],
            'artist': album_data['artists'][0]['name'],
            'release_date': album_data['release_date'],
            'album_art': album_data['images'][0]['url'] if album_data['images'] else None,
            'spotify_url': album_data['external_urls']['spotify'],
            'spotify_id': album_data['id']
        }
        
def put_album(album):
    try:
        cursor2.execute(f"""INSERT INTO completed
                    (spotify_id,
                    name,
                    artist,
                    art_url,
                    release_date
                    )
                       VALUES(?, ?, ?, ?, ?)""", (album["spotify_id"], album["name"], album["artist"], album["album_art"], album["release_date"]))
        connection.commit()
        return f"Successfully added {album['name']}"
    except:
        return f"error, unable to add the album"
    
def is_in_database(data) -> bool:
    try:
        cursor2.execute("SELECT * FROM completed WHERE NAME = ? AND ARTIST = ?", (data["name"], data["artist"]))
        result = cursor2.fetchone()
        return result is not None
    except Exception as e:
        print(f"error in is_in_database: {e}")
        return False
    
def add_album_to_database(album_from_spotify):
    cursor.execute(f"SELECT * FROM albums WHERE name = ? AND artist = ?", (album_from_spotify["name"], album_from_spotify["artist"]))
    album = cursor.fetchone()
    if album:
        try:
            cursor.execute(f"DELETE FROM albums WHERE name LIKE ? AND artist = ?", (album_from_spotify["name"], album_from_spotify["artist"]))
            cursor2.execute(f"""INSERT INTO completed
                        (spotify_id,
                        name,
                        artist,
                        art_url,
                        release_date
                        )
                        VALUES(?, ?, ?, ?, ?)""", (album[1], album[2], album[3], album[4], album[5]))
            connection.commit()
            connection2.commit()
            print(f"successfully found {album_from_spotify['name']} and removed it")
        except Exception as e:
            print(f"error after finding {album_from_spotify['name']} in database: {e}")
            connection.rollback()  
            connection2.rollback()
    else:
        album = album_from_spotify
        try:
            cursor2.execute(f"""INSERT INTO completed
                        (spotify_id,
                        name,
                        artist,
                        art_url,
                        release_date
                        )
                        VALUES(?, ?, ?, ?, ?)""", (album["spotify_id"], album["name"], album["artist"], album["album_art"], album["release_date"]))
            connection2.commit()
            print(f"was unable to find {album_from_spotify['name']}, but added it to completed")
        except Exception as e:
            print(f"error adding {album_from_spotify['name']} to database after not finding it: {e}")
            connection.rollback()  
            connection2.rollback()


with open("./lists/update_list.txt", "r") as file:
    lines = [line.strip() for line in file]
    for line in lines:
        album, artist = line.split("|")
        album_from_spotify = get_album(album, artist)
        album_in_database = is_in_database(album_from_spotify)
        if album != album_from_spotify["name"]:
            print(f"{album} and searched album {album_from_spotify['name']} are not the same")
        else:
            if album_in_database:
                print()
            else:
                add_album_to_database(album_from_spotify)
        


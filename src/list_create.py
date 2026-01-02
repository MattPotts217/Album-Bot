from bot import spotify_search, put_album

with open("./original_list.txt", 'r') as f:
    for line in f:
        line = line.strip()
        if "-" in line:
            try:
                result = spotify_search(line)
                put_album(result)
            except:
                print(f'there was an error with {line}')
import os
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="playlist-read-private"
))

def find_titles_bulletproof(playlist_id):
    titles_list = []
    print(f"Pobieranie danych dla ID: {playlist_id}...")
    
    results = sp.playlist_items(playlist_id)
    
    while results:
        raw_items = results.get('items', [])
        
        for item in raw_items:
            # --- INTELIGENTNE WYCIĄGANIE TYTUŁU ---
            # Sposób 1: Standardowa struktura Spotify
            if isinstance(item, dict) and item.get('track') and isinstance(item['track'], dict):
                if item['track'].get('name'):
                    titles_list.append(item['track']['name'])
                    continue
            
            # Sposób 2: Bezpośrednio w elemencie (nowy format API)
            if isinstance(item, dict) and item.get('name'):
                titles_list.append(item['name'])
                continue
                
            # Sposób 3: Awaryjne przeszukiwanie całego obiektu (szukamy klucza 'name')
            # Jeśli struktura jest nietypowa, ten kod znajdzie każdy ukryty tytuł
            try:
                item_str = json.dumps(item)
                item_dict = json.loads(item_str)
                
                # Szukamy głęboko ukrytego obiektu z typem 'track'
                def search_dict(d):
                    for k, v in d.items():
                        if k == 'name' and isinstance(v, str) and d.get('type') == 'track':
                            return v
                        if isinstance(v, dict):
                            res = search_dict(v)
                            if res: return res
                    return None
                    
                found_title = search_dict(item_dict)
                if found_title:
                    titles_list.append(found_title)
            except:
                pass
        
        if results.get('next'):
            results = sp.next(results)
        else:
            break

    print(f"\nOstateczny wynik: wyciągnięto {len(titles_list)} tytułów.")

    # Zapis do pliku JSON
    folder_name = "data_spotify"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    file_path = os.path.join(folder_name, "exotic_titles.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(titles_list, f, ensure_ascii=False, indent=4)
        
    print(f"Dane zostały zapisane w: {file_path}")

# Uruchomienie skryptu
PLAYLIST_ID = "70hZkx6IlOfIdpywgNkp11"
find_titles_bulletproof(PLAYLIST_ID)



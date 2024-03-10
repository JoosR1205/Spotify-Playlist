import spotipy
from spotipy.oauth2 import SpotifyOAuth
from prefect import flow, task
import os

# Asegúrate de que las variables de entorno están configuradas
scope = "user-library-read playlist-modify-public playlist-modify-private"

@task
def autenticar_usuario():
    auth_manager = SpotifyOAuth(scope=scope)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    return sp

@task
def obtener_canciones_liked(sp):
    canciones = []
    results = sp.current_user_saved_tracks(limit=50)
    while results:
        for item in results['items']:
            track = item['track']
            canciones.append({
                'id': track['id'], 
                'name': track['name'], 
                'artists': [artist['name'] for artist in track['artists']],
                'genres': []
            })
        if results['next']:
            results = sp.next(results)
        else:
            break
    return canciones

@task
def organizar_canciones_por_genero(sp, canciones):
    generos = {}
    artistas_procesados = {}
    for cancion in canciones:
        for artist_name in cancion['artists']:
            if artist_name in artistas_procesados:
                generos_artista = artistas_procesados[artist_name]
            else:
                search_result = sp.search(q='artist:' + artist_name, type='artist', limit=1)
                if search_result['artists']['items']:
                    artist = search_result['artists']['items'][0]
                    generos_artista = artist['genres']
                    artistas_procesados[artist_name] = generos_artista
                else:
                    generos_artista = ['Other']
            cancion['genres'].extend(generos_artista)
            for genero in generos_artista:
                if genero not in generos:
                    generos[genero] = []
                generos[genero].append(cancion['id'])

    generos_ordenados = dict(sorted(generos.items(), key=lambda item: len(item[1]), reverse=True)[:50])
    return generos_ordenados

@task
def seleccionar_generos_para_playlists(generos_ordenados):
    print("50 géneros más populares:")
    for i, genero in enumerate(generos_ordenados.keys(), start=1):
        print(f"{i}. {genero}")

    correcto = False
    while not correcto:
        seleccion_usuario = input("Selecciona los números de los géneros para crear playlists (ej. 1,4,7): ")
        indices_seleccionados = [int(x.strip()) for x in seleccion_usuario.split(",") if x.strip().isdigit()]
        if all(1 <= x <= 50 for x in indices_seleccionados):
            correcto = True
        else:
            print("Algunos números son inválidos o están fuera de rango. Inténtalo de nuevo.")
    
    generos_seleccionados = {list(generos_ordenados.keys())[i-1]: generos_ordenados[list(generos_ordenados.keys())[i-1]] for i in indices_seleccionados}

    return generos_seleccionados

@task
def crear_playlists_por_genero(sp, generos_seleccionados, user_id):
    for genero, tracks in generos_seleccionados.items():
        if tracks:  # Verifica que haya canciones en este género
            playlist = sp.user_playlist_create(user_id, f'Liked Songs - {genero}', public=True)
            # Dividir la lista de tracks en subgrupos de 100
            for i in range(0, len(tracks), 100):
                chunk = tracks[i:i+100]
                sp.playlist_add_items(playlist['id'], chunk)

@flow
def main():
    sp = autenticar_usuario()
    user_id = sp.current_user()['id']
    canciones_likeadas = obtener_canciones_liked(sp)
    generos_ordenados = organizar_canciones_por_genero(sp, canciones_likeadas)
    generos_seleccionados = seleccionar_generos_para_playlists(generos_ordenados)
    crear_playlists_por_genero(sp, generos_seleccionados, user_id)

if __name__ == "__main__":
    main()

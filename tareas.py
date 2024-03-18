from datetime import datetime, timedelta
from collections import defaultdict
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from prefect import flow, task, get_run_logger
import os

# Asegúrate de que las variables de entorno están configuradas
scope = "user-library-read playlist-modify-public playlist-modify-private user-top-read"

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
def seleccionar_accion():
    print("Selecciona la acción que deseas realizar:")
    print("1. Crear playlist con tus canciones likeadas organizadas por género.")
    print("2. Crear playlist con nuevos lanzamientos de Artistas más escuchados")
    accion = input("Ingresa el número de la acción: ")
    return int(accion)


############ CANCIONES POR GENERO ############

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

############  LANZAMIENTOS TOP DE ARTISTAS ############

@task
def obtener_top_artistas(sp):
    """
    Obtiene los 50 artistas más escuchados en long_term.
    """
    top_artistas = sp.current_user_top_artists(limit=50, time_range='long_term')
    return [artista['id'] for artista in top_artistas['items']]

@task
def buscar_nuevos_lanzamientos(sp, artistas_ids):
    """
    Busca y filtra nuevos lanzamientos de los artistas en los últimos 30 días.

    :param sp: Cliente de Spotipy autenticado.
    :param artistas_ids: Lista de IDs de los artistas a buscar.
    :return: Diccionario de nuevos lanzamientos con el ID del artista como clave y la lista de tracks como valor.
    """
    logger = get_run_logger()
    nuevos_lanzamientos = {}

    # Calcula la fecha de 30 días atrás como límite para considerar "nuevos lanzamientos"
    fecha_limite = datetime.now() - timedelta(days=30)
    
    for artista_id in artistas_ids:
        # Inicializa la lista de lanzamientos del artista
        lanzamientos_artista = []
        try:
            # Obtiene los álbumes del artista
            albums = sp.artist_albums(artista_id, album_type='album,single', limit=20)
            for album in albums['items']:
                # Convierte la fecha de lanzamiento a objeto datetime
                fecha_lanzamiento = datetime.strptime(album['release_date'], '%Y-%m-%d')
                # Si el lanzamiento es reciente, añádelo a la lista
                if fecha_lanzamiento >= fecha_limite:
                    # Obtiene las canciones (tracks) del álbum
                    tracks = sp.album_tracks(album['id'])
                    for track in tracks['items']:
                        lanzamientos_artista.append(track['id'])
        except Exception as e:
            logger.error(f"Error al buscar lanzamientos para el artista {artista_id}: {e}")

        if lanzamientos_artista:
            nuevos_lanzamientos[artista_id] = lanzamientos_artista

    return nuevos_lanzamientos


@task
def crear_playlist_con_nuevos_lanzamientos(sp, user_id, nuevos_lanzamientos):
    """
    Crea una nueva playlist y agrega los nuevos lanzamientos de música.

    :param sp: Cliente de Spotipy autenticado.
    :param user_id: ID del usuario de Spotify.
    :param nuevos_lanzamientos: Diccionario con los artistas como claves y listas de IDs de canciones como valores.
    """
    logger = get_run_logger()

    # Nombre y descripción de la playlist
    nombre_playlist = "Nuevos Lanzamientos - {}".format(datetime.now().strftime("%Y-%m-%d"))
    descripcion_playlist = "Nuevos lanzamientos de tus artistas favoritos, actualizado el {}".format(datetime.now().strftime("%Y-%m-%d"))

    try:
        # Crear la playlist
        playlist = sp.user_playlist_create(user=user_id, name=nombre_playlist, public=True, description=descripcion_playlist)
        playlist_id = playlist['id']
        logger.info(f"Playlist creada: {nombre_playlist}")
        
        # Agregar los nuevos lanzamientos a la playlist
        for lanzamientos in nuevos_lanzamientos.values():
            if lanzamientos:  # Asegurarse de que la lista no esté vacía
                sp.playlist_add_items(playlist_id=playlist_id, items=lanzamientos)
        logger.info("Nuevos lanzamientos agregados a la playlist.")

    except Exception as e:
        logger.error(f"Error al crear la playlist y agregar nuevos lanzamientos: {e}")

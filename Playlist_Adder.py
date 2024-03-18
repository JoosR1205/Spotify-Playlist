from tareas import  autenticar_usuario, obtener_canciones_liked, seleccionar_accion, organizar_canciones_por_genero, seleccionar_generos_para_playlists, crear_playlists_por_genero,obtener_top_artistas,buscar_nuevos_lanzamientos, crear_playlist_con_nuevos_lanzamientos
from datetime import datetime, timedelta
from collections import defaultdict
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from prefect import flow, task, get_run_logger
import os

@flow(name="Crear Playlist por Género")
def flow_genero():
    logger = get_run_logger()

    try:
        # Autenticar al usuario y obtener el cliente de Spotify
        sp = autenticar_usuario()
        
        # Obtener el ID del usuario para crear la playlist más adelante
        user_id = sp.current_user()['id']
        
        # Paso 1: Obtener canciones likeadas
        canciones_likeadas = obtener_canciones_liked(sp)
        
        # Paso 2: Organizar canciones por género
        generos_ordenados = organizar_canciones_por_genero(sp, canciones_likeadas)
        
        # Paso 3: Permitir al usuario seleccionar géneros para las playlists
        generos_seleccionados = seleccionar_generos_para_playlists(generos_ordenados)
        
        # Paso 4: Crear playlists por género seleccionado
        crear_playlists_por_genero(sp, generos_seleccionados, user_id)

        logger.info("Playlist por género creada exitosamente.")
    except Exception as e:
        logger.error(f"Error al crear la playlist por género: {e}")

@flow(name="Nuevos Lanzamientos de Artistas")
def nuevos_lanzamientos():
    logger = get_run_logger()

    # Autenticar al usuario y obtener el cliente de Spotify
    sp = autenticar_usuario()

    # Obtener el ID del usuario para crear la playlist más adelante
    user_id = sp.current_user()['id']

    # Paso 1: Obtener los 50 artistas más escuchados del usuario en long_term
    artistas_ids = obtener_top_artistas(sp)

    # Paso 2: Buscar nuevos lanzamientos de estos artistas en los últimos 30 días
    nuevos_lanzamientos = buscar_nuevos_lanzamientos(sp, artistas_ids)

    # Paso 3: Crear una playlist con estos nuevos lanzamientos
    crear_playlist_con_nuevos_lanzamientos(sp, user_id, nuevos_lanzamientos)

    logger.info("Flujo 'Nuevos Lanzamientos de Artistas' completado exitosamente.")


@flow(name="Flujo Principal de Playlists de Spotify")
def main():
    logger = get_run_logger()
    accion = seleccionar_accion()

    if accion == 1:
        logger.info("Creando playlist basada en género...")
        flow_genero()

    elif accion == 2:
        logger.info("Creando playlist con nuevos lanzamientos...")
        nuevos_lanzamientos()
    else:
        logger.error("Acción no válida. Por favor, reinicia el proceso.")

if __name__ == "__main__":
    main()

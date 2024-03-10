# Playlists de Spotify por Género

Este proyecto permite a los usuarios autenticarse con Spotify, interactuar con la API de Spotify para obtener sus canciones favoritas, organizar estas canciones por género y crear playlists en Spotify basadas en esos géneros.

## Características

- Autenticación de usuario con Spotify a través de OAuth.
- Organización de canciones gustadas por género.
- Creación automática de playlists basadas en géneros seleccionados.

## Pre-requisitos

Antes de comenzar, asegúrate de tener Python 3.6 o superior instalado en tu sistema. También necesitarás una cuenta de desarrollador de Spotify para obtener tus credenciales de cliente.

## Instalación

Clona este repositorio y navega al directorio clonado. Instala las dependencias usando pip:

```bash
pip install -r requirements.txt
```

## Configuración

1. Crea una aplicación en Dashboard de Desarrolladores de Spotify para obtener tu SPOTIFY_CLIENT_ID y SPOTIFY_CLIENT_SECRET.

2.Configura las siguientes variables de entorno en tu sistema:
  -SPOTIFY_CLIENT_ID: El ID de cliente proporcionado por Spotify.
  
  -SPOTIFY_CLIENT_SECRET: El secreto de cliente proporcionado por Spotify.
  
  -FLASK_SECRET_KEY: Una clave secreta para tu aplicación Flask.
  
  -SPOTIPY_REDIRECT_URI: La URI de redirección configurada en tu aplicación de Spotify.

  ## Uso

Para iniciar la aplicación Flask:

```bash
python app.py
```

Para ejecutar el script de Playlist Adder:

```bash
python Playlist_Adder.py
```


# Explicación de Scripts Spotify

## app.py

Este script es una aplicación web Flask diseñada para interactuar con la API de Spotify. Autentica usuarios utilizando `SpotifyOAuth` y maneja rutas para guiarlos a través del proceso de autenticación. Posteriormente, permite realizar acciones específicas en Spotify, como guardar playlists de descubrimiento. Adicionalmente, ejecuta `Playlist_Adder.py` en un hilo separado al inicio de la aplicación, mostrando una integración entre ambos scripts.

## Playlist_Adder.py

`Playlist_Adder.py` utiliza `spotipy` y `prefect` para autenticar usuarios de Spotify, recuperar sus canciones favoritas, organizarlas por género, y finalmente crear playlists basadas en esos géneros. A través de varias tareas decoradas con `@task`, realiza la autenticación, obtención de canciones, clasificación por género, y creación de playlists, coordinando todo el proceso en un flujo principal con `@flow`. Es un ejemplo claro de cómo automatizar la organización y creación de playlists personalizadas en Spotify.



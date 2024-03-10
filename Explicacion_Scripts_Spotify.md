# Explicación de Scripts Spotify

## app.py

Este script es una aplicación web Flask diseñada para interactuar con la API de Spotify. Autentica usuarios utilizando `SpotifyOAuth` y maneja rutas para guiarlos a través del proceso de autenticación. Posteriormente, permite realizar acciones específicas en Spotify, como guardar playlists de descubrimiento. Adicionalmente, ejecuta `Playlist_Adder.py` en un hilo separado al inicio de la aplicación, mostrando una integración entre ambos scripts.

## Playlist_Adder.py

`Playlist_Adder.py` utiliza `spotipy` y `prefect` para autenticar usuarios de Spotify, recuperar sus canciones favoritas, organizarlas por género, y finalmente crear playlists basadas en esos géneros. A través de varias tareas decoradas con `@task`, realiza la autenticación, obtención de canciones, clasificación por género, y creación de playlists, coordinando todo el proceso en un flujo principal con `@flow`. Es un ejemplo claro de cómo automatizar la organización y creación de playlists personalizadas en Spotify.


# Spotify Playlist Automation

Este proyecto permite a los usuarios interactuar con la API de Spotify para obtener sus canciones favoritas y organizarlas en playlists personalizadas por género o crear una playlist con lanzamientos recientes de sus artistas favoritos.

## Características

- Autenticación con Spotify utilizando OAuth 2.0.
- Recuperación de canciones gustadas y top artistas del usuario.
- Organización de canciones gustadas por género y fecha de lanzamiento.
- Creación automática de playlists basadas en géneros seleccionados y nuevos lanzamientos.

## Pre-requisitos

- Python 3.6 o superior.
- Cuenta de desarrollador de Spotify y aplicación registrada.
- `pip` para la instalación de paquetes.

## Instalación

1. Clona este repositorio.
2. Navega al directorio clonado y ejecuta el comando para instalar las dependencias:

    ```bash
    pip install -r requirements.txt
    ```

## Configuración

1. Crea un archivo `.env` en el directorio principal del proyecto con las siguientes variables:

    ```plaintext
    SPOTIFY_CLIENT_ID='tu_spotify_client_id'
    SPOTIFY_CLIENT_SECRET='tu_spotify_client_secret'
    FLASK_SECRET_KEY='una_clave_secreta_aleatoria_para_flask'
    SPOTIPY_REDIRECT_URI='tu_spotify_redirect_uri'
    ```

2. Configura las URI de redirección en el [Dashboard de Desarrolladores de Spotify](https://developer.spotify.com/dashboard/applications).

## Uso

1. Inicia la aplicación Flask ejecutando:

    ```bash
    python app.py
    ```

    Esto abrirá el servidor web Flask y manejará el proceso de autenticación de OAuth con Spotify.

2. Navega a `http://localhost:5000/` en tu navegador para autenticarte con Spotify y comenzar a utilizar la aplicación.

## Explicación de los Scripts

### `app.py`

Una aplicación Flask que sirve como punto de entrada para la autenticación de usuarios y la interacción con la API de Spotify.

### `Playlist_Adder.py`

El script principal que utiliza Prefect para orquestar flujos de trabajo y gestionar la creación de playlists en base a las tareas definidas en `tareas.py`.

### `tareas.py`

Contiene todas las tareas decoradas con `@task` que realizan la lógica necesaria para interactuar con la API de Spotify, como la autenticación de usuarios, la recuperación de canciones likeadas, la organización de canciones por género y fecha de lanzamiento, y la creación de playlists.


## Capturas de Pantalla 
![image](https://github.com/JoosR1205/Spotify-Playlist/assets/160549504/1ec6171d-3332-47ee-a4cb-7bad481739bb)
![image](https://github.com/JoosR1205/Spotify-Playlist/assets/160549504/ce8f6a33-d375-4c57-84be-011f695b6083)
![image](https://github.com/JoosR1205/Spotify-Playlist/assets/160549504/9082592f-f846-41be-a447-d76ca147d63c)


import os
from flask import Flask, request, redirect, session, url_for
from spotipy.oauth2 import SpotifyOAuth
import time
from threading import Thread
import subprocess

app = Flask(__name__)

# Configuración básica de la aplicación Flask
app.config['SESSION_COOKIE_NAME'] = 'sesion_spotify'
app.secret_key = 'tu_secret_key_aqui'
TOKEN_INFO = 'token_info'

# Carga las variables de entorno desde un archivo .env
# Asegúrate de tener un archivo .env con las claves necesarias: SPOTIFY_CLIENT_ID y SPOTIFY_CLIENT_SECRET
from dotenv import load_dotenv
load_dotenv()

# Define la ruta de inicio que redirige al usuario para autenticarse en Spotify
@app.route('/')
def login():
    auth_url = crear_autenticacion().get_authorize_url()
    return redirect(auth_url)

# Define la ruta a la que Spotify redirige después de una autenticación exitosa
@app.route('/redirect')
def redirect_page():
    session.clear()
    code = request.args.get('code')
    token_info = crear_autenticacion().get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('save_discover_weekly'))

# Una ruta de ejemplo que utiliza el token almacenado
@app.route('/saveDiscoverWeekly')
def save_discover_weekly():
    try:
        token_info = get_token()
    except:
        print("Usuario no autenticado")
        return redirect('/')
    
    # Aquí iría la lógica para usar el token y trabajar con Spotify
    return "Descubrimiento semanal guardado"

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        raise Exception("Token no encontrado")
    
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        spotify_oauth = crear_autenticacion()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])
        session[TOKEN_INFO] = token_info
    
    return token_info

def crear_autenticacion():
    return SpotifyOAuth(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
        redirect_uri=url_for('redirect_page', _external=True),
        scope='playlist-modify-public'
    )

def ejecutar_script():
    # Asegúrate de que el script esté en la misma carpeta y tenga el nombre correcto
    subprocess.run(["python", "Playlist_Adder.py"])

# Iniciar el hilo para ejecutar el script de Python al iniciar la aplicación
hilo = Thread(target=ejecutar_script)
hilo.start()

# Ejecutar la aplicación Flask
if __name__ == '__main__':
    app.run(debug=True)

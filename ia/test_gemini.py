from google import genai
from google.genai import types # Importamos los tipos para configurar la versión
from decouple import config

api_key = config('GEMINI_API_KEY')

# Forzamos al cliente a usar la versión 1 estable de la API
client = genai.Client(
    api_key=api_key,
    http_options={'api_version': 'v1'} # <-- ESTA ES LA LLAVE MAESTRA
)

print(f"--- Iniciando prueba en versión estable (v1) ---")

try:
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents='Hola, responde: ¡Funciona!'
    )
    print(f"Respuesta: {response.text}")
except Exception as e:
    print(f"Error: {e}")
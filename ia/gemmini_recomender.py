from google import genai
from decouple import config
import json

# Creamos el cliente de forma simple
client = genai.Client(api_key=config('GEMINI_API_KEY'))

def recomendar_con_gemini(producto_actual, lista_productos):
    stock_texto = ""
    for p in lista_productos:
        stock_texto += f"ID: {p.id} - Nombre: {p.nombre}\n"

    prompt = f"""
    Eres un experto vendedor. El cliente está viendo: {producto_actual.nombre}.
    De la siguiente lista de stock, elige los 3 mejores y explica por qué:
    {stock_texto}
    
    Responde ÚNICAMENTE en este formato JSON:
    [
        {{"id": 1, "razon": "explicación"}}
    ]
    """

    try:
        # Aquí está el cambio clave: llamamos al modelo de forma directa
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        
        # Limpiamos posibles etiquetas de markdown que Gemini a veces añade
        cuerpo = response.text.strip()
        if cuerpo.startswith('```json'):
            cuerpo = cuerpo[7:-3].strip()
            
        return json.loads(cuerpo)
    except Exception as e:
        # Esto nos dirá si es la clave o el modelo lo que falla
        print(f"DEBUG: Error en Gemini -> {e}")
        return []

##python -c "import google.generativeai as genai; genai.configure(api_key='AIzaSyBDASgEgPl62bdtIxFUPodBkyGFI90hx0E'); print(genai.GenerativeModel('gemini-1.5-flash').generate_content('hola').text)"
#http://127.0.0.1:8000/producto/1/
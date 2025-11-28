import requests
import feedparser
from datetime import datetime, timedelta, timezone
import os

# --- CONFIGURACIÓN ---
# CAMBIO CLAVE: Usamos el formato estricto "NombreApp/1.0 (Email)"
HEADERS = {
    "User-Agent": "GarzonRadar/1.0 (agarzon@unh.es)",
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.sec.gov"
}

# Tu lista de tiburones
SHARKS = [
    "ELLIOTT", "STARBOARD", "ICAHN", "PERSHING SQUARE", "THIRD POINT", 
    "TRIAN", "VALUEACT", "CORVEX", "APPALOOSA", "BAUPOST", "GREENLIGHT",
    "DANIEL S. LOEB", "ACKMAN"
]

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")

def send_discord_alert(title, link, date, shark_name):
    data = {
        "username": "Radar SEC 13D",
        "embeds": [{
            "title": f"🚨 TIBURÓN DETECTADO: {shark_name}",
            "description": f"**Archivo:** {title}\n**Fecha:** {date}",
            "url": link,
            "color": 16711680, 
            "footer": {"text": "Sistema de Vigilancia Automático"}
        }]
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=data)
        print(f"Alerta enviada para {shark_name}")
    except Exception as e:
        print(f"Error enviando a Discord: {e}")

def check_sec():
    # URL oficial del feed Atom de EDGAR para 13D
    url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=SC%2013D&company=&dateb=&owner=only&start=0&count=40&output=atom"
    
    print("📡 Conectando con la SEC...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        
        # --- ZONA DE DEBUG ---
        # Si la SEC nos bloquea, suelen mandar un HTML en vez de XML. 
        # Vamos a chivarnos de qué es lo que nos mandan si está vacío.
        if response.status_code != 200:
            print(f"❌ Error de Estado: {response.status_code}")
            return
            
        feed = feedparser.parse(response.content)
        
        cantidad = len(feed.entries)
        print(f"🔎 Analizando {cantidad} archivos recientes...")
        
        # SI SALE 0, IMPRIMIMOS EL CONTENIDO PARA VER QUÉ PASA
        if cantidad == 0:
            print("⚠️ AVISO: La lista está vacía. Respuesta del servidor (primeros 200 caracteres):")
            print(response.text[:200]) 
            # Esto nos dirá si es un bloqueo o si realmente no hay nada hoy (Black Friday).

        # Configuración de tiempo
        now = datetime.now(timezone.utc)
        lookback_window = timedelta(minutes=70) 

        for entry in feed.entries:
            try:
                published_time = datetime.fromisoformat(entry.updated)
            except:
                continue 

            if (now - published_time) > lookback_window:
                continue

            title_upper = entry.title.upper()
            
            for shark in SHARKS:
                if shark in title_upper:
                    print(f"✅ ENCONTRADO: {shark}")
                    send_discord_alert(entry.title, entry.link, entry.updated, shark)
                    break
                    
    except Exception as e:
        print(f"Error crítico: {e}")

if __name__ == "__main__":
    check_sec()

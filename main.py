
import requests
import feedparser
from datetime import datetime, timedelta, timezone
import os

# --- CONFIGURACIÓN ---
# AQUÍ ES DONDE TIENES QUE PONER TU EMAIL REAL
# Si no lo pones, la SEC te devolverá 0 resultados.
HEADERS = {
    "User-Agent": "InvestigadorIndependiente agarzon@unh.es", 
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.sec.gov"
}

# Tu lista de tiburones
SHARKS = [
    "ELLIOTT", "STARBOARD", "ICAHN", "PERSHING SQUARE", "THIRD POINT", 
    "TRIAN", "VALUEACT", "CORVEX", "APPALOOSA", "BAUPOST", "GREENLIGHT",
    "DANIEL S. LOEB", "ACKMAN"
]

# Leemos el secreto de Discord que ya guardaste
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
    url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=SC%2013D&company=&dateb=&owner=only&start=0&count=40&output=atom"
    
    print("📡 Conectando con la SEC...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        
        if response.status_code == 403:
            print("❌ BLOQUEADO (403). Revisa el User-Agent.")
            return

        feed = feedparser.parse(response.content)
        
        # Obtenemos la hora actual en UTC
        now = datetime.now(timezone.utc)
        
        # Miramos 70 mins atrás
        lookback_window = timedelta(minutes=70) 

        print(f"🔎 Analizando {len(feed.entries)} archivos recientes...")

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
    if not DISCORD_WEBHOOK_URL:
        print("⚠️ ERROR: No encuentro el secreto DISCORD_WEBHOOK")
    else:
        check_sec()

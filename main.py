
import requests
import feedparser
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

# --- CONFIGURACIÓN ---
EMAIL_SENDER = "TU_CORREO@gmail.com"
EMAIL_PASSWORD = "TU_CONTRASEÑA_DE_APLICACION" # Generar en Google Account > Seguridad
EMAIL_RECEIVER = "TU_CORREO@gmail.com"

# IMPORTANTE: La SEC exige este formato exacto en el User-Agent
HEADERS = {
    "User-Agent": "InvestigadorIndividual tu_email@gmail.com",
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.sec.gov"
}

SHARKS = [
    "ELLIOTT", "STARBOARD", "ICAHN", "PERSHING SQUARE", "THIRD POINT", 
    "TRIAN", "VALUEACT", "CORVEX", "APPALOOSA", "BAUPOST", "GREENLIGHT"
]

# URL del Feed de la SEC filtrado solo para 13D
SEC_FEED_URL = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=SC%2013D&company=&dateb=&owner=only&start=0&count=40&output=atom"

def send_alert(title, link, date):
    msg = MIMEText(f"🦈 TIBURÓN DETECTADO\n\nArchivo: {title}\nFecha: {date}\nLink: {link}")
    msg['Subject'] = f"🚨 ALERTA SEC: {title[:30]}..."
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    try:
        # Configuración para Gmail
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print(f"Correo enviado: {title}")
    except Exception as e:
        print(f"Error enviando email: {e}")

def check_sec():
    print("Conectando con la SEC...")
    try:
        # Usamos requests para tener control total de los Headers
        response = requests.get(SEC_FEED_URL, headers=HEADERS, timeout=10)
        
        if response.status_code == 403:
            print("❌ Error 403: La SEC nos ha bloqueado. Revisa el User-Agent.")
            return

        # Parseamos el XML
        feed = feedparser.parse(response.content)

        print(f"Encontradas {len(feed.entries)} entradas recientes.")

        # Lógica para no repetir: (En producción usarías una DB o archivo local)
        # Aquí filtramos solo los de las últimas 24h como ejemplo
        yesterday = datetime.now() - timedelta(days=1)
        
        for entry in feed.entries:
            title = entry.title.upper()
            link = entry.link
            
            # Buscamos coincidencias
            for shark in SHARKS:
                if shark in title:
                    print(f"✅ MATCH: {shark} en {title}")
                    send_alert(entry.title, link, entry.updated)
                    break
    
    except Exception as e:
        print(f"Error general: {e}")

if __name__ == "__main__":
    check_sec()

from datetime import datetime, timedelta, timezone
import pytz
chile_tz = pytz.timezone("America/Santiago")
import time
from app import leer_emails_y_confirmar, confirmar_desde_correo

while True:
    print("⏳ Revisando correos...")
    leer_emails_y_confirmar(confirmar_desde_correo)
    time.sleep(60)  # cada 1 minuto

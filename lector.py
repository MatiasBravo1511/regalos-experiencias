from app import leer_emails_y_confirmar, confirmar_desde_correo
import time
import logging
import sys

import logging
from logging.handlers import TimedRotatingFileHandler
import os

log_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(log_dir, "lector.log")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 🔁 Rotación diaria del log, mantener 3 backups
handler = TimedRotatingFileHandler(log_path, when="midnight", interval=1, backupCount=3, encoding="utf-8")
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)

# Evita duplicar handlers si recargas el script
if not logger.handlers:
    logger.addHandler(handler)

sys.stdout = StreamToLogger(logging.getLogger("STDOUT"), logging.INFO)
sys.stderr = StreamToLogger(logging.getLogger("STDERR"), logging.ERROR)

while True:
    print("⏳ Revisando correos...", flush=True)
    leer_emails_y_confirmar(confirmar_desde_correo)
    time.sleep(10)  # cada 10 segundos

from app import leer_emails_y_confirmar, confirmar_desde_correo, cargar_regalos
import time
import logging

# Configura el logging para guardar en un archivo llamado "lector.log"
logging.basicConfig(
    filename="lector.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8"
)


while True:
    cargar_regalos()
    print("⏳ Revisando correos...", flush=True)
    logging.info("⏳ Revisando correos...")
    leer_emails_y_confirmar(confirmar_desde_correo)
    time.sleep(10)  # cada 10 segundos

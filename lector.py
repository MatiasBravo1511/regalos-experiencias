from app import leer_emails_y_confirmar, confirmar_desde_correo
import time
import logging
import sys
import os
import datetime

# Configura el logging para guardar en un archivo llamado "lector.log"
logging.basicConfig(
    filename="lector.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8"
)

# Redirección de stdout y stderr a logging
class StreamToLogger:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())

    def flush(self):
        pass

sys.stdout = StreamToLogger(logging.getLogger("STDOUT"), logging.INFO)
sys.stderr = StreamToLogger(logging.getLogger("STDERR"), logging.ERROR)

while True:
    print("⏳ Revisando correos...", flush=True)
    leer_emails_y_confirmar(confirmar_desde_correo)
    time.sleep(10)  # cada 10 segundos
    
    # Eliminar si el archivo tiene más de 3 días
    try:
        log_file = "lector.log"
        if os.path.exists(log_file):
            modified_time = os.path.getmtime(log_file)
            file_age_days = (datetime.datetime.now() - datetime.datetime.fromtimestamp(modified_time)).days
            if file_age_days > 3:
                os.remove(log_file)
                print("🧹 Log antiguo eliminado", flush=True)
    except Exception as e:
        print(f"⚠️ Error eliminando log: {e}", flush=True)

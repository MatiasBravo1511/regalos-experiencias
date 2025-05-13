from app import leer_emails_y_confirmar, confirmar_desde_correo, cargar_regalos
import time
import logging
import sys

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
    cargar_regalos()
    print("⏳ Revisando correos...", flush=True)
    leer_emails_y_confirmar(confirmar_desde_correo)
    time.sleep(10)  # cada 10 segundos

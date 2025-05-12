from app import leer_emails_y_confirmar, confirmar_desde_correo, cargar_regalos
import time

while True:
    cargar_regalos()
    print("⏳ Revisando correos...")
    leer_emails_y_confirmar(confirmar_desde_correo)
    time.sleep(10)  # cada 10 segundos

from app import leer_emails_y_confirmar, confirmar_desde_correo

while True:
    print("⏳ Revisando correos...", flush=True)
    leer_emails_y_confirmar(confirmar_desde_correo)
    time.sleep(10)  # cada 10 segundos
